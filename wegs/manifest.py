"""
Manifest -- reads/writes the local pass index (manifest.json).
Thread-safe with atomic writes. No database required.
"""
import json
import os
import threading
from pathlib import Path

_lock = threading.Lock()


def _atomic_write(path, data):
    """Write to temp file, then rename atomically."""
    tmp = str(path) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def load(output_folder):
    """Load manifest.json from the output folder. Returns dict with 'passes' list."""
    path = Path(output_folder) / "manifest.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"passes": [], "updated": None}


def save(output_folder, data):
    """Write manifest.json to the output folder. Thread-safe."""
    import datetime
    data["updated"] = datetime.datetime.utcnow().isoformat()
    path = Path(output_folder) / "manifest.json"
    with _lock:
        _atomic_write(path, data)


def add_pass(output_folder, pass_data, pass_images):
    """
    Add a pass to the manifest. Thread-safe.
    Sorted by timestamp descending (newest first) regardless of insertion order.
    """
    with _lock:
        manifest = load(output_folder)
        entry = {
            **pass_data,
            "images": pass_images,
        }
        manifest["passes"].append(entry)
        # Sort by timestamp descending so newest is always first
        manifest["passes"].sort(key=lambda p: p.get("timestamp", ""), reverse=True)
        _atomic_write(Path(output_folder) / "manifest.json", manifest)


def pass_exists(output_folder, folder_name):
    """Check if a pass folder is already in the manifest."""
    manifest = load(output_folder)
    return any(p.get("folder_name") == folder_name for p in manifest["passes"])


def count_passes(output_folder):
    """Return total number of passes in manifest."""
    manifest = load(output_folder)
    return len(manifest["passes"])


def get_stats(output_folder):
    """Return aggregate statistics from the manifest."""
    manifest = load(output_folder)
    passes = manifest["passes"]
    successful = [p for p in passes if p.get("status") == "completed"]
    total_images = sum(p.get("png_count", 0) for p in passes)
    satellites = set(p.get("satellite", "") for p in passes)
    return {
        "total_passes": len(passes),
        "successful_passes": len(successful),
        "total_images": total_images,
        "satellites": sorted(satellites),
    }
