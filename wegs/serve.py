#!/usr/bin/env python3
"""
WeGS Server  single process that serves the SPA, output files,
and runs the file monitor. No file copying. No external deps.
"""
import os
import sys
import json
import threading
import mimetypes
from socket import SOL_SOCKET, SO_REUSEADDR
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

INSTALL_DIR = Path(__file__).parent.parent.resolve()

_empty_manifest_cache = None

def _empty_manifest():
    """Return a temp file with empty manifest JSON."""
    global _empty_manifest_cache
    if _empty_manifest_cache and Path(_empty_manifest_cache).exists():
        return _empty_manifest_cache
    tmp = INSTALL_DIR / "web" / "dist" / "_empty_manifest.json"
    with open(tmp, "w") as f:
        json.dump({"passes": [], "updated": None}, f)
    _empty_manifest_cache = str(tmp)
    return _empty_manifest_cache

class WeGSHandler(SimpleHTTPRequestHandler):
    """Serves SPA from web/dist/ and output files from the configured folder."""

    def __init__(self, *args, output_folder=None, **kwargs):
        self.output_folder = output_folder
        # Set base for SPA files
        self.wegspath = Path.cwd()
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        """Map URL paths to filesystem paths."""
        from urllib.parse import unquote
        path = unquote(path, errors="surrogatepass")
        path = path.split("?", 1)[0].split("#", 1)[0]
        path = path.lstrip("/")

        # SPA routes  index.html
        if not path or path == "index.html":
            return str(INSTALL_DIR / "web" / "dist" / "index.html")

        # Config file  serve public fields only (no tokens/keys)
        if path == "config.json":
            cfg = INSTALL_DIR / "config.json"
            if cfg.exists():
                with open(cfg) as f:
                    data = json.load(f)
                public = {k: v for k, v in data.items() if k not in ("telegram", "supabase")}
                # Serve from temp location
                tmp = INSTALL_DIR / "web" / "dist" / "_config.json"
                with open(tmp, "w") as f:
                    json.dump(public, f)
                return str(tmp)

        # Output folder files (passes, thumbs, manifest)
        if self.output_folder:
            out = Path(self.output_folder)
            candidate = out / path
            if candidate.exists():
                return str(candidate)
            # manifest.json not ready yet -> serve empty placeholder
            if path == "manifest.json":
                return str(_empty_manifest())

        # SPA static files (JS, CSS, etc.)
        spa = INSTALL_DIR / "web" / "dist" / path
        if spa.exists():
            return str(spa)

        # SPA fallback  React Router
        if "." not in Path(path).suffix and path != "favicon.ico":
            return str(INSTALL_DIR / "web" / "dist" / "index.html")

        # 404
        return str(INSTALL_DIR / "web" / "dist" / "index.html")

    def log_message(self, format, *args):
        """Quieter logging."""
        if "/thumbs/" not in str(args[0]):
            print(f"  {args[0]}")

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


def run_serve(output_folder, port=5173):
    """Start the WeGS HTTP server."""
    handler = lambda *args: WeGSHandler(*args, output_folder=output_folder)
    server = HTTPServer(("0.0.0.0", port), handler)
    server.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    print(f"   Web UI:    http://localhost:{port}")
    print(f"   Data:      {output_folder}")
    print(f"   Config:    {INSTALL_DIR / 'config.json'}")

    # Start monitor in background
    from .monitor import run as run_monitor
    mon = threading.Thread(target=run_monitor, daemon=True)
    mon.start()
    print(f"   Monitor:   watching {output_folder}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
