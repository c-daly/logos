#!/usr/bin/env python3
"""
Demo Capture Script for LOGOS

Records browser sessions, CLI interactions, and system logs for
Phase 2 verification evidence.

Usage:
    python capture_demo.py --mode browser  # Capture browser session
    python capture_demo.py --mode cli      # Capture CLI session
    python capture_demo.py --mode logs     # Aggregate logs
    python capture_demo.py --mode all      # Capture everything
"""

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path


class DemoCapture:
    """Captures demo artifacts for verification."""

    def __init__(self, output_dir: str = "./demo_output"):
        """
        Initialize the demo capture tool.
        
        Args:
            output_dir: Directory to store captured artifacts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    def capture_browser(self, url: str = "http://localhost:3000", duration: int = 60):
        """
        Capture browser session using ffmpeg (screen recording).
        
        Args:
            url: URL to capture
            duration: Recording duration in seconds
        
        Note:
            Requires ffmpeg and X11/Wayland display server.
            For headless environments, use virtual display (Xvfb).
        """
        print(f"[Browser Capture] Starting recording for {duration}s...")
        print(f"Target URL: {url}")
        print("Note: This requires ffmpeg and a display server.")

        output_file = self.output_dir / f"browser_demo_{self.timestamp}.mp4"

        # Check if ffmpeg is available
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: ffmpeg not found. Install with: apt-get install ffmpeg")
            return

        # Record screen using ffmpeg (Linux X11 example)
        # Adjust for your platform (macOS uses avfoundation, Windows uses gdigrab)
        cmd = [
            "ffmpeg",
            "-video_size", "1920x1080",
            "-framerate", "30",
            "-f", "x11grab",
            "-i", ":0.0",
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            str(output_file),
        ]

        print(f"Recording command: {' '.join(cmd)}")
        print("Recording will start in 3 seconds...")
        print("Open your browser and navigate to the Apollo UI.")

        try:
            subprocess.run(cmd, check=True)
            print(f"✓ Browser demo captured: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to capture browser demo: {e}")
            print("\nAlternative: Use OBS Studio or similar screen recording tool")
            print(f"Then save the recording to: {output_file}")

    def capture_cli(self, commands: list[str] | None = None):
        """
        Capture CLI session using script command or manual recording.
        
        Args:
            commands: Optional list of commands to execute
        """
        print("[CLI Capture] Starting CLI session capture...")

        output_file = self.output_dir / f"cli_demo_{self.timestamp}.log"

        if commands:
            print(f"Executing commands and capturing output to: {output_file}")
            with open(output_file, "w") as f:
                for cmd in commands:
                    f.write(f"$ {cmd}\n")
                    try:
                        result = subprocess.run(
                            cmd,
                            shell=True,
                            capture_output=True,
                            text=True,
                            timeout=30,
                        )
                        f.write(result.stdout)
                        if result.stderr:
                            f.write(f"STDERR:\n{result.stderr}")
                        f.write("\n")
                    except Exception as e:
                        f.write(f"ERROR: {e}\n\n")

            print(f"✓ CLI demo captured: {output_file}")
        else:
            print("Use 'script' command to record your CLI session:")
            print(f"  script {output_file}")
            print("Then exit the shell when done: exit")
            print("\nOr use this script with --commands flag:")
            print('  python capture_demo.py --mode cli --commands "logos-cli status" "logos-cli plan ..."')

    def aggregate_logs(self, log_dirs: list[str] | None = None):
        """
        Aggregate logs from various LOGOS components.
        
        Args:
            log_dirs: List of directories containing logs
        """
        print("[Log Aggregation] Collecting logs...")

        if not log_dirs:
            log_dirs = [
                "/tmp/logos_telemetry",
                "./logs",
                "/var/log/logos",
            ]

        output_file = self.output_dir / f"logs_aggregated_{self.timestamp}.json"
        aggregated = {
            "timestamp": datetime.utcnow().isoformat(),
            "logs": [],
        }

        for log_dir in log_dirs:
            log_path = Path(log_dir)
            if not log_path.exists():
                print(f"  Skipping {log_dir} (not found)")
                continue

            print(f"  Scanning {log_dir}...")

            # Find all log files
            for log_file in log_path.glob("**/*.log"):
                try:
                    with open(log_file) as f:
                        lines = f.readlines()
                        aggregated["logs"].append({
                            "file": str(log_file),
                            "lines": len(lines),
                            "content": lines[-100:],  # Last 100 lines
                        })
                except Exception as e:
                    print(f"    ERROR reading {log_file}: {e}")

            # Find JSONL telemetry files
            for jsonl_file in log_path.glob("**/*.jsonl"):
                try:
                    with open(jsonl_file) as f:
                        events = [json.loads(line) for line in f]
                        aggregated["logs"].append({
                            "file": str(jsonl_file),
                            "events": len(events),
                            "content": events[-50:],  # Last 50 events
                        })
                except Exception as e:
                    print(f"    ERROR reading {jsonl_file}: {e}")

        with open(output_file, "w") as f:
            json.dump(aggregated, f, indent=2)

        print(f"✓ Logs aggregated: {output_file}")
        print(f"  Total log sources: {len(aggregated['logs'])}")

    def create_manifest(self):
        """Create a manifest of captured artifacts."""
        manifest = {
            "timestamp": datetime.utcnow().isoformat(),
            "artifacts": [],
        }

        for file in self.output_dir.iterdir():
            if file.is_file():
                manifest["artifacts"].append({
                    "filename": file.name,
                    "size": file.stat().st_size,
                    "path": str(file),
                })

        manifest_file = self.output_dir / "MANIFEST.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"\n✓ Manifest created: {manifest_file}")
        print(f"  Total artifacts: {len(manifest['artifacts'])}")


def main():
    parser = argparse.ArgumentParser(
        description="Capture demo artifacts for LOGOS Phase 2 verification"
    )
    parser.add_argument(
        "--mode",
        choices=["browser", "cli", "logs", "all"],
        default="all",
        help="Capture mode",
    )
    parser.add_argument(
        "--output-dir",
        default="./demo_output",
        help="Output directory for artifacts",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Browser recording duration in seconds",
    )
    parser.add_argument(
        "--commands",
        nargs="+",
        help="CLI commands to execute and capture",
    )
    parser.add_argument(
        "--log-dirs",
        nargs="+",
        help="Directories to scan for logs",
    )

    args = parser.parse_args()

    capture = DemoCapture(output_dir=args.output_dir)

    print("=" * 60)
    print("LOGOS Demo Capture Tool")
    print("=" * 60)
    print()

    if args.mode in ["browser", "all"]:
        capture.capture_browser(duration=args.duration)
        print()

    if args.mode in ["cli", "all"]:
        capture.capture_cli(commands=args.commands)
        print()

    if args.mode in ["logs", "all"]:
        capture.aggregate_logs(log_dirs=args.log_dirs)
        print()

    capture.create_manifest()
    print()
    print("=" * 60)
    print(f"Demo capture complete. Artifacts saved to: {capture.output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
