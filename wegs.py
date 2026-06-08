#!/usr/bin/env python3
"""
WeGS CLI  Ground Station Web Visualizer.

Usage:
    wegs start       Start the server + monitor
    wegs dashboard   Open web UI in browser
    wegs stop        Stop the server
    wegs status      Show system info
    wegs reconfigure Re-run setup wizard
    wegs uninstall   Remove WeGS completely
"""
import sys
import os
import json
import signal
import webbrowser
from pathlib import Path

INSTALL_DIR = Path(__file__).parent.resolve()
PID_FILE = Path.home() / ".wegs" / "wegs.pid"

HELP = """WeGS  Ground Station Web Visualizer v1.0

  wegs start        Start server + monitor
  wegs dashboard    Open http://localhost:5173
  wegs stop         Stop all services
  wegs status       Show system status
  wegs reconfigure  Re-run setup wizard
  wegs uninstall    Remove WeGS completely"""


def main():
    if len(sys.argv) < 2:
        print(HELP)
        return

    cmd = sys.argv[1].lower()

    if cmd in ("-h", "--help", "help"):
        print(HELP)
    elif cmd == "start":
        _start()
    elif cmd == "dashboard":
        _dashboard()
    elif cmd == "stop":
        _stop()
    elif cmd == "status":
        _status()
    elif cmd == "reconfigure":
        _reconfigure()
    elif cmd == "uninstall":
        _uninstall()
    else:
        print(f"Unknown command: {cmd}")
        print(HELP)


def _start():
    import wegs.config as cfg
    config = cfg.get()
    output = config.get("output_folder", "")
    port = config.get("web_port", 5173)

    if not output or not Path(output).exists():
        print(f"[!] Output folder not set. Run: wegs reconfigure")
        return

    print(f"WeGS  {config['station_name']}")
    print(f"   Starting on http://localhost:{port}")
    print()

    if PID_FILE.exists():
        print("[!] WeGS appears to be running already. Run: wegs stop")
        return

    from wegs.serve import run_serve
    run_serve(output, port)


def _dashboard():
    _load_config()
    port = _load_config().get("web_port", 5173)
    url = f"http://localhost:{port}"
    print(f"Opening {url}...")
    webbrowser.open(url)


def _stop():
    if PID_FILE.exists():
        with open(PID_FILE) as f:
            pid = json.load(f).get("pid")
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"Stopped (PID {pid})")
            except ProcessLookupError:
                print("Was not running")
            except Exception as e:
                print(f"Error: {e}")
        PID_FILE.unlink(missing_ok=True)
    else:
        # Try to find and kill python processes on the port
        import subprocess
        config = _load_config()
        port = config.get("web_port", 5173)
        try:
            result = subprocess.run(
                ["netstat", "-ano"], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split("\n"):
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    pid = int(parts[-1])
                    try:
                        os.kill(pid, signal.SIGTERM)
                        print(f"Stopped (PID {pid})")
                    except:
                        pass
        except:
            pass
    print("WeGS stopped")


def _status():
    config = _load_config()
    output = config.get("output_folder", "")
    port = config.get("web_port", 5173)

    print(f"Station:  {config['station_name']}")
    print(f"Folder:   {output}")
    print(f"Web:      http://localhost:{port}")
    print(f"Telegram: {'on' if config['telegram']['enabled'] else 'off'}")
    print(f"Supabase: {'on' if config['supabase']['enabled'] else 'off'}")

    # Count passes
    manifest_path = Path(output) / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            m = json.load(f)
        print(f"Passes:   {len(m.get('passes', []))}")
    else:
        print("Passes:   no manifest yet")


def _reconfigure():
    import subprocess
    subprocess.run([sys.executable, str(INSTALL_DIR / "wegs" / "setup_wizard.py")])


def _uninstall():
    print("Removing WeGS...")
    _stop()

    # Remove from PATH
    home = Path.home()
    wegs_dir = home / ".wegs"
    try:
        import subprocess
        user_path = subprocess.run(
            ["powershell", "-Command", "[Environment]::GetEnvironmentVariable('Path','User')"],
            capture_output=True, text=True
        ).stdout.strip()
        new_path = ";".join(p for p in user_path.split(";") if str(wegs_dir) not in p)
        subprocess.run(
            ["powershell", "-Command", f"[Environment]::SetEnvironmentVariable('Path','{new_path}','User')"],
            capture_output=True
        )
    except:
        pass

    import shutil
    if wegs_dir.exists():
        shutil.rmtree(wegs_dir, ignore_errors=True)

    print("WeGS removed.")
    print(f"   The source code is still at: {INSTALL_DIR}")
    print(f"   Delete this folder manually to fully uninstall.")


def _load_config():
    import wegs.config as cfg
    return cfg.get()


if __name__ == "__main__":
    main()
