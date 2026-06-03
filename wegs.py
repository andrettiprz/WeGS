#!/usr/bin/env python3
"""
WeGS CLI — manages the ground station web visualizer.

Usage:
    wegs start              Start all services
    wegs stop               Stop all services
    wegs status             Show system status
    wegs reconfigure        Re-run setup wizard
    wegs add <feature>      Add optional features (telegram, supabase, deploy)
    wegs sync               Sync pending passes to Supabase
    wegs update             Update to latest version
    wegs uninstall          Remove WeGS
"""
import sys
import subprocess
import json
import time
from pathlib import Path

INSTALL_DIR = Path(__file__).parent.resolve()

HELP = """WeGS — Ground Station Web Visualizer v1.0

  wegs start            Start watchdog + web server
  wegs stop             Stop all services
  wegs status           Show system status
  wegs reconfigure      Re-run the setup wizard
  wegs add telegram     Set up Telegram bot notifications
  wegs add supabase     Set up cloud publishing
  wegs add deploy       Deploy web UI to Vercel
  wegs sync             Upload pending passes to Supabase
  wegs update           Update WeGS to latest version
  wegs uninstall        Remove WeGS completely
"""


def main():
    if len(sys.argv) < 2:
        print(HELP)
        return

    cmd = sys.argv[1].lower()
    sub = sys.argv[2] if len(sys.argv) > 2 else ""

    if cmd == "start":
        _start()
    elif cmd == "stop":
        _stop()
    elif cmd == "status":
        _status()
    elif cmd == "reconfigure":
        _reconfigure()
    elif cmd == "add":
        _add(sub)
    elif cmd == "sync":
        _sync()
    elif cmd == "update":
        _update()
    elif cmd == "uninstall":
        _uninstall()
    elif cmd in ("-h", "--help", "help"):
        print(HELP)
    else:
        print(f"Unknown command: {cmd}")
        print(HELP)


def _start():
    import wegs.config as cfg
    config = cfg.get()
    output = config.get("output_folder", "")
    if not output or not Path(output).exists():
        print("⚠️  Output folder not set or not found. Run: wegs reconfigure")
        return

    print("🛰️  Starting watchdog...")
    watchdog_proc = subprocess.Popen(
        [sys.executable, str(INSTALL_DIR / "wegs" / "watchdog.py")],
        cwd=output,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"   PID: {watchdog_proc.pid} — monitoring {output}")

    print("🌐 Starting web server...")
    web_proc = subprocess.Popen(
        ["npm", "run", "dev", "--", "--port", str(config.get("web_port", 5173))],
        cwd=str(INSTALL_DIR / "web"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)
    print(f"   http://localhost:{config.get('web_port', 5173)}")

    # Save PIDs
    pid_file = Path.home() / ".wegs" / "pids.json"
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    with open(pid_file, "w") as f:
        json.dump({"watchdog": watchdog_proc.pid, "web": web_proc.pid}, f)

    print()
    print(f"✅ WeGS running — http://localhost:{config.get('web_port', 5173)}")


def _stop():
    pid_file = Path.home() / ".wegs" / "pids.json"
    if pid_file.exists():
        with open(pid_file) as f:
            pids = json.load(f)
        import signal, os as _os
        for name, pid in pids.items():
            try:
                _os.kill(pid, signal.SIGTERM)
                print(f"✓ Stopped {name} (PID {pid})")
            except ProcessLookupError:
                print(f"  {name} was not running")
            except Exception as e:
                print(f"  Error stopping {name}: {e}")
        pid_file.unlink(missing_ok=True)
    print("✅ WeGS stopped")


def _status():
    import wegs.config as cfg
    config = cfg.get()

    pid_file = Path.home() / ".wegs" / "pids.json"
    running = pid_file.exists()

    # Count passes
    output = config.get("output_folder", "")
    pass_count = 0
    manifest_path = Path(output) / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            m = json.load(f)
            pass_count = len(m.get("passes", []))

    print("── WeGS Status ────────────────────────────")
    print(f"  Status:    {'🟢 Running' if running else '🔴 Stopped'}")
    print(f"  Station:   {config.get('station_name', '?')}")
    print(f"  Folder:    {output or 'not set'}")
    print(f"  Passes:    {pass_count}")
    print(f"  Web:       http://localhost:{config.get('web_port', 5173)}")
    print(f"  Telegram:  {'✅' if config['telegram']['enabled'] else '❌'}")
    print(f"  Supabase:  {'✅' if config['supabase']['enabled'] else '❌'}")


def _reconfigure():
    subprocess.run([sys.executable, str(INSTALL_DIR / "wegs" / "setup_wizard.py")])


def _add(feature):
    wizard = INSTALL_DIR / "wegs" / "setup_wizard.py"
    if feature in ("telegram", "supabase", "deploy"):
        subprocess.run([sys.executable, str(wizard), f"--{feature}"])
    else:
        print(f"Unknown feature: {feature}")
        print("Available: wegs add telegram | supabase | deploy")


def _sync():
    from wegs.supabase import sync_passes
    sync_passes()


def _update():
    import os as _os
    _os.chdir(INSTALL_DIR)
    subprocess.run(["git", "pull", "origin", "main"])
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"])
    _os.chdir(INSTALL_DIR / "web")
    subprocess.run(["npm", "install", "--silent"])
    print("✅ WeGS updated")


def _uninstall():
    _stop()
    import shutil
    home = Path.home()
    shutil.rmtree(home / ".wegs", ignore_errors=True)
    print("✅ WeGS removed")
    print(f"   To fully uninstall, delete: {INSTALL_DIR}")


if __name__ == "__main__":
    main()
