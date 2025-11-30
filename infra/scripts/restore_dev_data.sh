#!/usr/bin/env bash

# LOGOS HCG Development Data Restore Script
# Restores Neo4j and Milvus volumes from a backup archive
# See Project LOGOS spec: Section 4.1 (Core Ontology), Section 5.2 (Vector Store)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${INFRA_DIR}/.." && pwd)"
COMPOSE_FILE="${INFRA_DIR}/docker-compose.hcg.dev.yml"

# Configuration
BACKUP_ARCHIVE=""
FORCE_RESTORE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to show usage
usage() {
    cat << EOF
Usage: $0 BACKUP_ARCHIVE [OPTIONS]

Restore LOGOS development data (Neo4j + Milvus volumes) from a backup archive.

ARGUMENTS:
    BACKUP_ARCHIVE     Path to the backup archive (.tar.gz file)

OPTIONS:
    --force           Skip confirmation prompt
    -h, --help        Show this help message

EXAMPLES:
    # Restore from backup (with confirmation)
    $0 infra/backups/backup-20240118-1430.tar.gz

    # Restore without confirmation
    $0 infra/backups/backup-20240118-1430.tar.gz --force

NOTES:
    - This will OVERWRITE existing data in the volumes
    - Services will be stopped during restore and restarted afterwards
    - Backup must contain: neo4j-data, neo4j-logs, neo4j-plugins, milvus-data
    - Development use only; not suitable for production

EOF
}

# Parse command line arguments
parse_args() {
    # Check for help flag first
    for arg in "$@"; do
        if [ "$arg" = "-h" ] || [ "$arg" = "--help" ]; then
            usage
            exit 0
        fi
    done
    
    if [ $# -eq 0 ]; then
        print_error "Missing backup archive argument"
        usage
        exit 1
    fi
    
    BACKUP_ARCHIVE="$1"
    shift
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                FORCE_RESTORE=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
}

# Function to check if docker compose is available
check_docker_compose() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available"
        exit 1
    fi
}

# Function to get project name from compose file
get_project_name() {
    local dir_name=$(basename "${INFRA_DIR}")
    echo "${dir_name}"
}

# Function to verify backup archive
verify_backup_archive() {
    print_info "Verifying backup archive..."
    
    # Check if file exists
    if [ ! -f "${BACKUP_ARCHIVE}" ]; then
        print_error "Backup archive not found: ${BACKUP_ARCHIVE}"
        exit 1
    fi
    
    # Check if it's a valid tar.gz file
    if ! tar tzf "${BACKUP_ARCHIVE}" &> /dev/null; then
        print_error "Invalid or corrupted backup archive"
        exit 1
    fi
    
    # Check for required volume backups
    local required_files=("volumes/neo4j-data.tar.gz" "volumes/neo4j-logs.tar.gz" "volumes/neo4j-plugins.tar.gz" "volumes/milvus-data.tar.gz")
    local missing_files=()
    
    for file in "${required_files[@]}"; do
        # Try both with and without leading ./
        if ! tar tzf "${BACKUP_ARCHIVE}" "${file}" &> /dev/null && \
           ! tar tzf "${BACKUP_ARCHIVE}" "./${file}" &> /dev/null; then
            missing_files+=("${file}")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        print_error "Backup archive is missing required files:"
        for file in "${missing_files[@]}"; do
            echo "  - ${file}"
        done
        exit 1
    fi
    
    print_info "✓ Backup archive is valid"
    
    # Show metadata if available
    if tar tzf "${BACKUP_ARCHIVE}" "backup-metadata.txt" &> /dev/null || \
       tar tzf "${BACKUP_ARCHIVE}" "./backup-metadata.txt" &> /dev/null; then
        echo ""
        print_info "Backup metadata:"
        tar xzf "${BACKUP_ARCHIVE}" --to-stdout "./backup-metadata.txt" 2>/dev/null | sed 's/^/  /'
        echo ""
    fi
}

# Function to get volume names with project prefix
get_volume_names() {
    local project_name=$(get_project_name)
    
    NEO4J_DATA_VOLUME="${project_name}_neo4j-data"
    NEO4J_LOGS_VOLUME="${project_name}_neo4j-logs"
    NEO4J_PLUGINS_VOLUME="${project_name}_neo4j-plugins"
    MILVUS_DATA_VOLUME="${project_name}_milvus-data"
}

# Function to confirm restore
confirm_restore() {
    if [ "${FORCE_RESTORE}" = true ]; then
        return 0
    fi
    
    echo ""
    print_warn "⚠️  WARNING: This will OVERWRITE existing data in the following volumes:"
    echo "  - ${NEO4J_DATA_VOLUME}"
    echo "  - ${NEO4J_LOGS_VOLUME}"
    echo "  - ${NEO4J_PLUGINS_VOLUME}"
    echo "  - ${MILVUS_DATA_VOLUME}"
    echo ""
    print_warn "This action cannot be undone!"
    echo ""
    read -p "Do you want to continue? (yes/no): " -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_info "Restore cancelled"
        exit 0
    fi
}

# Function to stop services
stop_services() {
    print_step "Stopping services..."
    docker compose -f "${COMPOSE_FILE}" stop neo4j milvus-standalone shacl-validation 2>/dev/null || true
    print_info "✓ Services stopped"
}

# Function to start services
start_services() {
    print_step "Starting services..."
    docker compose -f "${COMPOSE_FILE}" up -d neo4j milvus-standalone shacl-validation 2>/dev/null || true
    print_info "✓ Services started"
}

# Function to restore volume
restore_volume() {
    local volume_name="$1"
    local archive_file="$2"
    local temp_dir="$3"
    
    print_info "Restoring ${volume_name}..."
    
    # Extract the volume archive from backup
    # Try both with and without leading ./
    if ! tar xzf "${BACKUP_ARCHIVE}" -C "${temp_dir}" "${archive_file}" 2>/dev/null; then
        tar xzf "${BACKUP_ARCHIVE}" -C "${temp_dir}" "./${archive_file}"
    fi
    
    # Remove existing volume content and restore from backup
    docker run --rm \
        -v "${volume_name}:/target" \
        -v "${temp_dir}:/backup:ro" \
        alpine:latest \
        sh -c "rm -rf /target/* /target/.[!.]* 2>/dev/null || true; tar xzf /backup/${archive_file} -C /target"
    
    print_info "✓ ${volume_name} restored"
}

# Function to restore all volumes
restore_volumes() {
    print_step "Restoring volumes..."
    
    local temp_dir=$(mktemp -d)
    
    # Restore each volume
    restore_volume "${NEO4J_DATA_VOLUME}" "volumes/neo4j-data.tar.gz" "${temp_dir}"
    restore_volume "${NEO4J_LOGS_VOLUME}" "volumes/neo4j-logs.tar.gz" "${temp_dir}"
    restore_volume "${NEO4J_PLUGINS_VOLUME}" "volumes/neo4j-plugins.tar.gz" "${temp_dir}"
    restore_volume "${MILVUS_DATA_VOLUME}" "volumes/milvus-data.tar.gz" "${temp_dir}"
    
    # Cleanup temp directory
    rm -rf "${temp_dir}"
    
    print_info "✓ All volumes restored"
}

# Function to wait for services to be healthy
wait_for_services() {
    print_step "Waiting for services to be ready..."
    
    # Wait for Neo4j
    local max_attempts=30
    local attempt=1
    
    print_info "Waiting for Neo4j..."
    while [ $attempt -le $max_attempts ]; do
        if docker exec logos-hcg-neo4j cypher-shell -u neo4j -p neo4jtest "RETURN 1;" &> /dev/null; then
            print_info "✓ Neo4j is ready"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_warn "Neo4j may not be fully ready yet"
            print_info "Check status with: docker logs logos-hcg-neo4j"
        fi
        
        sleep 2
        ((attempt++))
    done
    
    # Wait for Milvus (check if port is accessible)
    attempt=1
    print_info "Waiting for Milvus..."
    while [ $attempt -le $max_attempts ]; do
        if timeout 2 bash -c "echo > /dev/tcp/localhost/19530" 2>/dev/null; then
            print_info "✓ Milvus is ready"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_warn "Milvus may not be fully ready yet"
            print_info "Check status with: docker logs logos-hcg-milvus"
        fi
        
        sleep 2
        ((attempt++))
    done
}

# Main execution
main() {
    echo ""
    echo "=========================================="
    echo "LOGOS Development Data Restore"
    echo "=========================================="
    echo ""
    
    # Parse arguments
    parse_args "$@"
    
    # Check prerequisites
    check_docker_compose
    
    # Verify backup archive
    verify_backup_archive
    
    # Get volume names
    get_volume_names
    
    # Confirm restore
    confirm_restore
    
    # Stop services
    stop_services
    
    # Restore volumes
    if restore_volumes; then
        # Start services
        start_services
        
        # Wait for services
        wait_for_services
        
        echo ""
        echo "=========================================="
        print_info "✓ Restore completed successfully!"
        echo "=========================================="
        echo ""
        print_info "Services have been restarted"
        print_info "Neo4j Browser: http://localhost:7474"
        print_info "  Username: neo4j"
        print_info "  Password: neo4jtest"
        echo ""
        print_info "Verify your data:"
        print_info "  docker exec logos-hcg-neo4j cypher-shell -u neo4j -p neo4jtest 'MATCH (n) RETURN count(n);'"
        echo ""
        exit 0
    else
        print_error "Restore failed"
        print_info "Attempting to restart services..."
        start_services
        exit 1
    fi
}

# Run main function
main "$@"
