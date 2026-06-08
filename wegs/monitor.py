"""
WeGS Watchdog  monitors SatDump output folders.
Generates thumbnails, HDR headers, and maintains the local manifest.
Optionally sends Telegram notifications and syncs to Supabase.
"""
import os
import re
import time
import json
import datetime
import threading
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    Image = None

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from . import config
from . import manifest
from .telegram import TelegramBot
from .supabase import SupabaseClient

#  Helper: identify satellite from folder name 

def identify_satellite(name):
    n = name.lower()
    if "m2-x" in n or "m2_x" in n: return "METEOR M2-X"
    if "m2-3" in n or "m2_3" in n: return "METEOR M2-3"
    if "m2-4" in n or "m2_4" in n: return "METEOR M2-4"
    if "noaa" in n:
        for num in ["15", "18", "19"]:
            if num in n: return f"NOAA {num}"
        return "NOAA"
    return "UNKNOWN"


#  Helper: count PNGs recursively 

def count_pngs(folder):
    c = 0
    if not os.path.isdir(folder):
        return 0
    for root, dirs, files in os.walk(folder):
        c += sum(1 for f in files if f.lower().endswith(".png") and os.path.getsize(os.path.join(root, f)) > 0)
    return c


#  Helper: classify image 

def classify_image(rel_path, filename):
    path = rel_path.replace("\\", "/").lower()
    fname = filename.lower()
    if "thumb" in fname or fname.startswith("hdr_"):
        return None, None
    if "filled" in path or "(filled)" in path:
        if "mcir_map" in fname: return ("FILLED", "MCIR Map")
        if "mcir" in fname: return ("FILLED", "MCIR Filled")
        if "321" in fname or "natural" in fname: return ("FILLED", "Natural Color (321)")
        if "221" in fname: return ("FILLED", "Water/Ice (221)")
        if "equalized" in fname: return ("FILLED", "Equalized")
        return ("FILLED", filename)
    # RAW
    if "mcir_corrected" in fname: return ("RAW", "MCIR Corrected")
    if "mcir" in fname: return ("RAW", "MCIR Raw")
    for ch in range(1, 7):
        if f"msu-mr-{ch}" in fname: return ("RAW", f"MSU-MR Channel {ch}")
    if "321" in fname: return ("RAW", "Natural Color (321)")
    if "221" in fname: return ("RAW", "Water/Ice (221)")
    if "rgb" in fname: return ("RAW", filename)
    return ("RAW", filename)


#  Thumbnail generation 

def generate_thumbnail(image_path, thumb_dir, width=400, quality=70):
    """Generate a JPEG thumbnail, save to thumb_dir. Returns path or None."""
    if Image is None:
        return None
    try:
        img = Image.open(image_path).convert("RGB")
        w, h = img.size
        if w > width:
            new_h = int(h * width / w)
            img = img.resize((width, new_h), Image.Resampling.LANCZOS)
        os.makedirs(thumb_dir, exist_ok=True)
        out_name = Path(image_path).stem + ".jpg"
        out_path = os.path.join(thumb_dir, out_name)
        img.save(out_path, "JPEG", quality=quality)
        return out_path
    except Exception as e:
        print(f"     Thumbnail error: {e}")
        return None


#  Main pass processor 

class PassProcessor:
    def __init__(self, cfg):
        self.cfg = cfg
        self.output = cfg["output_folder"]
        self.proc = cfg.get("processing", {})
        self.wait = self.proc.get("wait_seconds", 1200)
        self.thumb_w = self.proc.get("thumbnail_width", 400)
        self.thumb_q = self.proc.get("thumbnail_quality", 70)
        self.tz_name = self.proc.get("timezone", "UTC")
        self.tg = TelegramBot.from_config(cfg)
        self.sb = SupabaseClient.from_config(cfg)
        self.sdr_map = cfg.get("sdr_map", {})

    def process(self, pass_path):
        folder_name = os.path.basename(pass_path)
        sat = identify_satellite(folder_name)
        sdr_info = self.sdr_map.get(sat, {"sdr": "Unknown", "antenna": "Unknown"})

        print(f" Processing {folder_name}... waiting {self.wait}s")
        time.sleep(self.wait)

        # Count
        path_msu = os.path.join(pass_path, "MSU-MR")
        path_filled = os.path.join(pass_path, "MSU-MR (Filled)")
        count_raw = count_pngs(path_msu) if os.path.exists(path_msu) else 0
        count_filled = count_pngs(path_filled) if os.path.exists(path_filled) else 0
        count_total = count_raw + count_filled

        # Collect images
        images = self._collect_images(pass_path)

        if not images:
            if self.tg:
                self.tg.send_message(f"*PASS: {sat}*  No images detected.")
            print(f"    No images  skipped")
            return

        # Collect images (no thumbnails  original PNGs served directly)
        img_entries = []
        for abs_path, rel_path, img_type, label in images:
            img_entries.append({
                "type": img_type,
                "label": label,
                "image_path": f"{folder_name}/{rel_path}".replace("\\", "/"),
            })

        # Timestamp
        dt_utc = self._extract_timestamp(folder_name)

        # Manifest  save in output folder only (server serves from there)
        pass_data = {
            "satellite": sat,
            "timestamp": dt_utc.isoformat() if dt_utc else datetime.datetime.utcnow().isoformat(),
            "folder_name": folder_name,
            "png_count": count_total,
            "raw_count": count_raw,
            "filled_count": count_filled,
            "status": "completed",
        }
        manifest.add_pass(self.output, pass_data, img_entries)

        # Telegram
        if self.tg:
            self.tg.send_message(
                f"*AOS DETECTED*\\n"
                f"Satellite: {sat}\\n"
                f"Receiver: {sdr_info['sdr']} | Antenna: {sdr_info['antenna']}\\n"
                f"Status: Processing..."
            )
            report = (
                f"*Report: {sat}*\\n"
                f"Receiver: {sdr_info['sdr']}\\n"
                f"\\n"
                f"RAW: {count_raw} | Filled: {count_filled}\\n"
                f"Total files: {count_total}\\n"
                f"Processing complete."
            )
            self.tg.send_message(report)

        # Supabase
        if self.sb:
            self._upload_supabase(pass_path, folder_name, sat, dt_utc, count_total, count_raw, count_filled, img_entries)

        print(f"  [OK] {len(img_entries)} images  {count_total} PNGs")

    def _collect_images(self, pass_path):
        results = []
        for root, dirs, files in os.walk(pass_path):
            for fname in sorted(files):
                if not fname.lower().endswith(".png"):
                    continue
                abs_path = os.path.join(root, fname)
                if os.path.getsize(abs_path) == 0:
                    continue
                rel_path = os.path.relpath(abs_path, pass_path)
                img_type, label = classify_image(rel_path, fname)
                if img_type:
                    results.append((abs_path, rel_path, img_type, label))
        return results

    def _extract_timestamp(self, folder_name):
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})", folder_name)
        if m:
            a, mo, d, h, mi = map(int, m.groups())
            return datetime.datetime(a, mo, d, h, mi, tzinfo=datetime.timezone.utc)
        return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

    def _upload_supabase(self, pass_path, folder_name, sat, dt_utc, total, raw, filled, img_entries):
        pass_id = self.sb.insert_pass(sat, dt_utc, folder_name, total, raw, filled)
        if not pass_id:
            return
        for img in img_entries:
            img_abs = os.path.join(pass_path, img["image_path"])
            if os.path.exists(img_abs):
                with open(img_abs, "rb") as f:
                    url = self.sb.upload_image(
                        f"passes/{folder_name}/{img['image_path'].replace(chr(92), '/')}",
                        f.read(), "image/png"
                    )
                if url:
                    self.sb.insert_image(pass_id, img["type"], img["label"], url)
                time.sleep(0.2)


#  Filesystem event handler 

class PassHandler(FileSystemEventHandler):
    def __init__(self, cfg):
        self.cfg = cfg
        self.processor = PassProcessor(cfg)
        self.pattern = re.compile(r"^\d{4}-\d{2}-\d{2}")
        self.tg = TelegramBot.from_config(cfg)

    def on_created(self, event):
        if not event.is_directory:
            return
        name = os.path.basename(event.src_path)
        if not self.pattern.match(name):
            return

        sat = identify_satellite(name)
        sdr_info = self.cfg.get("sdr_map", {}).get(sat, {"sdr": "Unknown", "antenna": "Unknown"})

        print(f"  AOS: {name}")
        if self.tg:
            self.tg.send_message(
                f"*AOS DETECTED*\\n"
                f"Satellite: {sat}\\n"
                f"Receiver: {sdr_info['sdr']} | Antenna: {sdr_info['antenna']}\\n"
                f"Status: Recording..."
            )

        t = threading.Thread(target=self.processor.process, args=(event.src_path,), daemon=True)
        t.start()


#  Main entry point 

def run():
    cfg = config.get()
    output = cfg["output_folder"]
    if not output or not os.path.isdir(output):
        print(f"[X] Output folder not found: {output}")
        print("   Run: wegs reconfigure")
        return

    print("=" * 44)
    print("   WeGS Watchdog v1.0")
    print(f"   Station: {cfg['station_name']}")
    print(f"   Folder:  {output}")
    print(f"   Telegram: {'[OK]' if cfg['telegram']['enabled'] else '[X]'}")
    print(f"   Supabase: {'[OK]' if cfg['supabase']['enabled'] else '[X]'}")
    print("=" * 44)

    handler = PassHandler(cfg)
    observer = Observer()
    observer.schedule(handler, output, recursive=False)
    observer.start()

    # Scan existing folders on startup
    import threading as _thr
    def _scan_existing():
        pattern = re.compile(r"^\d{4}-\d{2}-\d{2}")
        existing = sorted(
            [d for d in os.listdir(output) if pattern.match(d) and os.path.isdir(os.path.join(output, d))]
        )
        processor = PassProcessor(cfg)
        for folder_name in existing:
            if not manifest.pass_exists(output, folder_name):
                pass_path = os.path.join(output, folder_name)
                print(f" Scanning existing: {folder_name}")
                try:
                    processor.process(pass_path)
                except Exception as e:
                    print(f"   Error scanning {folder_name}: {e}")
        print(f"[OK] Startup scan complete  {len(existing)} folders checked")

    _thr.Thread(target=_scan_existing, daemon=True).start()

    tg = TelegramBot.from_config(cfg)
    if tg:
        tg.send_message(f"*WeGS Online*\\nStation: {cfg['station_name']}\\nMonitoring: `{output}`")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        observer.stop()
        if tg:
            tg.send_message("*WeGS Offline*\\nWatchdog stopped.")
    observer.join()


if __name__ == "__main__":
    run()
