"""
WeGS Configuration — reads/writes config.json.
"""
import json
import os
from pathlib import Path

CONFIG_PATH = Path.home() / ".wegs" / "config.json"
DEFAULTS = {
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


def load():
    """Load config, merge with defaults, return dict."""
    cfg = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            user = json.load(f)
        _deep_merge(cfg, user)
    # Also check legacy repo-local config
    repo_config = Path(__file__).parent.parent / "config.json"
    if repo_config.exists():
        with open(repo_config) as f:
            repo = json.load(f)
        _deep_merge(cfg, repo)
    return cfg


def save(cfg):
    """Save config to disk."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=4)


def _deep_merge(base, override):
    for k, v in override.items():
        if isinstance(v, dict) and k in base and isinstance(base[k], dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


# Module-level config (lazy-loaded)
_config = None


def get():
    global _config
    if _config is None:
        _config = load()
    return _config


def reload():
    global _config
    _config = load()
    return _config
