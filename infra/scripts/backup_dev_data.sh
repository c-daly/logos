#!/usr/bin/env bash

# LOGOS HCG Development Data Backup Script
# Backs up Neo4j and Milvus volumes from the development stack
# See Project LOGOS spec: Section 4.1 (Core Ontology), Section 5.2 (Vector Store)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${INFRA_DIR}/.." && pwd)"
COMPOSE_FILE="${INFRA_DIR}/docker-compose.hcg.dev.yml"
BACKUP_DIR="${INFRA_DIR}/backups"

# Configuration
PROJECT_NAME="${PROJECT_NAME:-infra}"
OUTPUT_PATH=""

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
Usage: $0 [OPTIONS]

Backup LOGOS development data (Neo4j + Milvus volumes).

OPTIONS:
    --output PATH       Custom output path for backup archive (default: infra/backups/backup-YYYYMMDD-HHMM.tar.gz)
    -h, --help         Show this help message

EXAMPLES:
    # Create timestamped backup in default location
    $0

    # Create backup with custom path
    $0 --output /tmp/my-backup.tar.gz

NOTES:
    - Services will be paused during backup and automatically resumed
    - Backup includes: neo4j-data, neo4j-logs, neo4j-plugins, milvus-data
    - Backups are stored in infra/backups/ by default (gitignored)
    - Development use only; not suitable for production

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --output)
                OUTPUT_PATH="$2"
                shift 2
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
    # Try to extract from compose file or use directory name
    local dir_name=$(basename "${INFRA_DIR}")
    echo "${dir_name}"
}

# Function to check if services are running
check_services() {
    print_info "Checking if services are running..."
    
    if ! docker compose -f "${COMPOSE_FILE}" ps --quiet neo4j milvus-standalone 2>/dev/null | grep -q .; then
        print_error "Services are not running"
        print_info "Start the HCG cluster first:"
        print_info "  docker compose -f ${COMPOSE_FILE} up -d"
        exit 1
    fi
    
    print_info "✓ Services are running"
}

# Function to get volume names with project prefix
get_volume_names() {
    local project_name=$(get_project_name)
    
    # Volume names are prefixed with project name by docker compose
    NEO4J_DATA_VOLUME="${project_name}_neo4j-data"
    NEO4J_LOGS_VOLUME="${project_name}_neo4j-logs"
    NEO4J_PLUGINS_VOLUME="${project_name}_neo4j-plugins"
    MILVUS_DATA_VOLUME="${project_name}_milvus-data"
}

# Function to verify volumes exist
verify_volumes() {
    print_info "Verifying volumes exist..."
    
    local missing_volumes=()
    
    for volume in "${NEO4J_DATA_VOLUME}" "${NEO4J_LOGS_VOLUME}" "${NEO4J_PLUGINS_VOLUME}" "${MILVUS_DATA_VOLUME}"; do
        if ! docker volume inspect "${volume}" &> /dev/null; then
            missing_volumes+=("${volume}")
        fi
    done
    
    if [ ${#missing_volumes[@]} -gt 0 ]; then
        print_error "The following volumes do not exist:"
        for vol in "${missing_volumes[@]}"; do
            echo "  - ${vol}"
        done
        print_info "Make sure the dev stack has been started at least once"
        exit 1
    fi
    
    print_info "✓ All volumes exist"
}

# Function to pause services
pause_services() {
    print_step "Pausing services..."
    docker compose -f "${COMPOSE_FILE}" pause neo4j milvus-standalone shacl-validation 2>/dev/null || true
    print_info "✓ Services paused"
}

# Function to resume services
resume_services() {
    print_step "Resuming services..."
    docker compose -f "${COMPOSE_FILE}" unpause neo4j milvus-standalone shacl-validation 2>/dev/null || true
    print_info "✓ Services resumed"
}

# Function to create backup
create_backup() {
    local backup_path="$1"
    local temp_dir=$(mktemp -d)
    
    print_step "Creating backup..."
    print_info "Temporary directory: ${temp_dir}"
    
    # Create volume backup directory structure
    mkdir -p "${temp_dir}/volumes"
    
    # Backup each volume using docker run with volume mounted
    print_info "Backing up neo4j-data volume..."
    docker run --rm \
        -v "${NEO4J_DATA_VOLUME}:/source:ro" \
        -v "${temp_dir}/volumes:/backup" \
        alpine:latest \
        tar czf /backup/neo4j-data.tar.gz -C /source .
    
    print_info "Backing up neo4j-logs volume..."
    docker run --rm \
        -v "${NEO4J_LOGS_VOLUME}:/source:ro" \
        -v "${temp_dir}/volumes:/backup" \
        alpine:latest \
        tar czf /backup/neo4j-logs.tar.gz -C /source .
    
    print_info "Backing up neo4j-plugins volume..."
    docker run --rm \
        -v "${NEO4J_PLUGINS_VOLUME}:/source:ro" \
        -v "${temp_dir}/volumes:/backup" \
        alpine:latest \
        tar czf /backup/neo4j-plugins.tar.gz -C /source .
    
    print_info "Backing up milvus-data volume..."
    docker run --rm \
        -v "${MILVUS_DATA_VOLUME}:/source:ro" \
        -v "${temp_dir}/volumes:/backup" \
        alpine:latest \
        tar czf /backup/milvus-data.tar.gz -C /source .
    
    # Create metadata file
    cat > "${temp_dir}/backup-metadata.txt" << EOF
LOGOS Development Data Backup
Created: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Project: $(get_project_name)

Volumes backed up:
- ${NEO4J_DATA_VOLUME}
- ${NEO4J_LOGS_VOLUME}
- ${NEO4J_PLUGINS_VOLUME}
- ${MILVUS_DATA_VOLUME}

Docker Compose File: ${COMPOSE_FILE}
EOF
    
    # Create final backup archive
    print_info "Creating final backup archive..."
    mkdir -p "$(dirname "${backup_path}")"
    tar czf "${backup_path}" -C "${temp_dir}" .
    
    # Get backup size
    local backup_size=$(du -h "${backup_path}" | cut -f1)
    
    # Cleanup temp directory
    rm -rf "${temp_dir}"
    
    print_info "✓ Backup created successfully"
    echo ""
    print_info "Backup location: ${backup_path}"
    print_info "Backup size: ${backup_size}"
}

# Main execution
main() {
    echo ""
    echo "=========================================="
    echo "LOGOS Development Data Backup"
    echo "=========================================="
    echo ""
    
    # Parse arguments
    parse_args "$@"
    
    # Check prerequisites
    check_docker_compose
    
    # Check if services are running
    check_services
    
    # Get volume names
    get_volume_names
    
    # Verify volumes exist
    verify_volumes
    
    # Determine output path
    if [ -z "${OUTPUT_PATH}" ]; then
        local timestamp=$(date +"%Y%m%d-%H%M")
        OUTPUT_PATH="${BACKUP_DIR}/backup-${timestamp}.tar.gz"
    fi
    
    # Ensure backup directory exists
    mkdir -p "${BACKUP_DIR}"
    
    print_info "Backup will be saved to: ${OUTPUT_PATH}"
    echo ""
    
    # Pause services
    pause_services
    
    # Create backup (with error handling to ensure services are resumed)
    if create_backup "${OUTPUT_PATH}"; then
        resume_services
        echo ""
        echo "=========================================="
        print_info "✓ Backup completed successfully!"
        echo "=========================================="
        echo ""
        print_info "To restore this backup, run:"
        print_info "  ${SCRIPT_DIR}/restore_dev_data.sh ${OUTPUT_PATH}"
        echo ""
        exit 0
    else
        print_error "Backup failed"
        resume_services
        exit 1
    fi
}

# Trap errors to ensure services are resumed
trap 'resume_services' ERR

# Run main function
main "$@"
