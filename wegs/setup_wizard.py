"""
Setup wizard  interactive configuration for WeGS.
Run standalone: python wegs/setup_wizard.py
Run for specific feature: python wegs/setup_wizard.py --telegram
"""
import sys
import json
from pathlib import Path

INSTALL_DIR = Path(__file__).parent.parent


def wizard_full():
    """Run the full setup wizard."""
    print()
    print("")
    print("         WeGS v1.0 Setup                  ")
    print("   Ground Station Web Visualizer         ")
    print("")
    print()

    cfg = _load_existing()

    #  Station 
    print(" Station Information ")
    cfg["station_name"] = _ask("Station name", cfg.get("station_name", "My Ground Station"))
    cfg["output_folder"] = _ask("SatDump output folder (where live_output is)", cfg.get("output_folder", ""))
    raw_maps = _ask("Google Maps embed URL (Enter to skip)", cfg.get("maps_embed_url", ""), optional=True)
    # If user pasted a full <iframe>, extract just the src URL
    if raw_maps and "<iframe" in raw_maps:
        import re
        match = re.search(r'src="([^"]+)"', raw_maps)
        if match:
            raw_maps = match.group(1)
    cfg["maps_embed_url"] = raw_maps if raw_maps else ""
    cfg["web_port"] = int(_ask("Web port", str(cfg.get("web_port", 5173))) or 5173)
    cfg["language"] = _ask("Language (en/es)", cfg.get("language", "en"))

    #  Telegram 
    print()
    print(" Telegram (optional) ")
    use_tg = _ask("Set up Telegram notifications? (y/N)", "n").lower()
    if use_tg == "y":
        wizard_telegram(cfg)
    else:
        cfg["telegram"]["enabled"] = False

    #  Supabase 
    print()
    print(" Supabase Cloud (optional) ")
    use_sb = _ask("Set up Supabase cloud publishing? (y/N)", "n").lower()
    if use_sb == "y":
        wizard_supabase(cfg)
    else:
        cfg["supabase"]["enabled"] = False

    #  Save 
    _save(cfg)
    print()
    print(" Done ")
    print(f"    Config saved to: {INSTALL_DIR / 'config.json'}")
    print(f"    Start:  wegs start")
    print(f"   Web:     http://localhost:{cfg['web_port']}")
    if cfg["telegram"]["enabled"]:
        print(f"   Telegram: configured")
    if cfg["supabase"]["enabled"]:
        print(f"    Supabase: configured")
    print()


def wizard_telegram(cfg=None):
    """Set up Telegram notifications."""
    if cfg is None:
        cfg = _load_existing()

    print()
    print("   Telegram Setup ")
    print("  1. Open Telegram and message @BotFather")
    print("  2. Send /newbot and follow instructions")
    print("  3. Copy the bot token you receive")
    print()

    token = _ask("  Bot token", cfg["telegram"].get("bot_token", ""))
    chat = _ask("  Chat ID or @channel_name", cfg["telegram"].get("chat_id", ""))

    cfg["telegram"]["enabled"] = bool(token and chat)
    cfg["telegram"]["bot_token"] = token
    cfg["telegram"]["chat_id"] = chat

    _save(cfg)
    if token and chat:
        print("   Telegram configured!")
    else:
        print("    Telegram disabled (missing token or chat ID)")


def wizard_supabase(cfg=None):
    """Set up Supabase cloud publishing."""
    if cfg is None:
        cfg = _load_existing()

    print()
    print("   Supabase Setup ")
    print("  1. Go to https://supabase.com and create a free project")
    print("  2. Go to Project Settings  API")
    print("  3. Copy your Project URL and keys")
    print()

    url = _ask("  Project URL", cfg["supabase"].get("url", ""))
    anon_key = _ask("  Anon (public) key", cfg["supabase"].get("anon_key", ""))
    service_key = _ask("  Service role key (secret)", cfg["supabase"].get("service_key", ""))

    if url and anon_key:
        bucket = _ask("  Storage bucket name", cfg["supabase"].get("bucket", "satellite-images"))
        cfg["supabase"].update({
            "enabled": True,
            "url": url.strip("/"),
            "anon_key": anon_key,
            "service_key": service_key,
            "bucket": bucket,
        })
        print()
        print("   Supabase configured!")
    else:
        cfg["supabase"]["enabled"] = False
        print("    Supabase disabled (missing URL or key)")

    _save(cfg)


def wizard_deploy(cfg=None):
    """Guide for deploying web UI."""
    print()
    print("   Deploy Web UI ")
    print()
    print("  Option 1: Vercel (recommended, free)")
    print("    1. Go to https://vercel.com and sign up")
    print("    2. Import your WeGS GitHub repo")
    print("    3. Set build command: cd web && npm run build")
    print("    4. Set output directory: web/dist")
    print()
    print("  Option 2: Static file server")
    print(f"    1. cd {INSTALL_DIR / 'web'} && npm run build")
    print("    2. Serve web/dist/ with nginx, apache, or python -m http.server")
    print()
    print("  Option 3: Local only (already working at localhost)")
    print()


#  Helpers 

def _ask(prompt, default="", optional=False):
    """Ask a question, return answer or default."""
    suffix = ""
    if default:
        suffix = f" [{default}]"
    if optional and not default:
        suffix = " (Enter to skip)"
    try:
        answer = input(f"  {prompt}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    return answer if answer else default


def _load_existing():
    """Load existing config or return defaults."""
    config_path = INSTALL_DIR / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {
        "station_name": "My Ground Station",
        "output_folder": "",
        "maps_embed_url": "",
        "web_port": 5173,
        "language": "en",
        "accent_color": "#00c8ff",
        "telegram": {"enabled": False, "bot_token": "", "chat_id": ""},
        "supabase": {"enabled": False, "url": "", "service_key": "", "anon_key": "", "bucket": "satellite-images"},
        "sdr_map": {},
        "processing": {"wait_seconds": 1200, "thumbnail_width": 400, "thumbnail_quality": 70, "timezone": "UTC"},
    }


def _save(cfg):
    """Save config to disk."""
    config_path = INSTALL_DIR / "config.json"
    with open(config_path, "w") as f:
        json.dump(cfg, f, indent=4)


if __name__ == "__main__":
    if "--telegram" in sys.argv:
        wizard_telegram()
    elif "--supabase" in sys.argv:
        wizard_supabase()
    elif "--deploy" in sys.argv:
        wizard_deploy()
    else:
        wizard_full()
