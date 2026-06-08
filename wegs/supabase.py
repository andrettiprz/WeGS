"""
Supabase integration  optional cloud publishing backend.
"""
import time
import requests


class SupabaseClient:
    def __init__(self, url, service_key, anon_key, bucket="satellite-images"):
        self.url = url.rstrip("/")
        self.service_key = service_key
        self.anon_key = anon_key
        self.bucket = bucket

    def _headers(self, use_service=True):
        key = self.service_key if use_service else self.anon_key
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
        }

    def upload_image(self, storage_path, data, content_type):
        """Upload bytes to Storage. Returns public URL or None."""
        headers = self._headers()
        headers["Content-Type"] = content_type
        for attempt in range(5):
            try:
                resp = requests.post(
                    f"{self.url}/storage/v1/object/{self.bucket}/{storage_path}",
                    headers=headers,
                    data=data,
                    timeout=120,
                )
                if resp.status_code in (200, 201):
                    return f"{self.url}/storage/v1/object/public/{self.bucket}/{storage_path}"
                if resp.status_code == 429:
                    time.sleep(12)
                    continue
            except Exception:
                time.sleep(5 * (attempt + 1))
        return None

    def insert_pass(self, satellite, timestamp_utc, folder_name, png_count, raw_count, filled_count, status="completed"):
        """Insert a pass record. Returns pass ID or None."""
        headers = self._headers()
        headers["Content-Type"] = "application/json"
        headers["Prefer"] = "return=representation"
        row = {
            "satellite": satellite,
            "timestamp": timestamp_utc.isoformat(),
            "folder_name": folder_name,
            "png_count": png_count,
            "raw_count": raw_count,
            "filled_count": filled_count,
            "status": status,
        }
        try:
            resp = requests.post(f"{self.url}/rest/v1/passes", headers=headers, json=row, timeout=30)
            if resp.status_code in (200, 201):
                data = resp.json()
                return data[0]["id"] if isinstance(data, list) else data.get("id")
        except Exception as e:
            print(f"   Supabase DB error: {e}")
        return None

    def insert_image(self, pass_id, img_type, label, image_url, thumbnail_url=None):
        """Insert an image record linked to a pass."""
        headers = self._headers()
        headers["Content-Type"] = "application/json"
        row = {"pass_id": pass_id, "type": img_type, "label": label, "image_url": image_url, "thumbnail_url": thumbnail_url or image_url}
        try:
            requests.post(f"{self.url}/rest/v1/pass_images", headers=headers, json=row, timeout=30)
        except Exception as e:
            print(f"   Supabase image error: {e}")

    def get_existing_folders(self):
        """Return set of folder_name values already in Supabase."""
        headers = self._headers()
        try:
            resp = requests.get(f"{self.url}/rest/v1/passes?select=folder_name", headers=headers, timeout=30)
            if resp.status_code == 200:
                return {row["folder_name"] for row in resp.json() if row.get("folder_name")}
        except Exception:
            pass
        return set()

    @staticmethod
    def from_config(config):
        sb = config.get("supabase", {})
        if sb.get("enabled") and sb.get("url") and sb.get("service_key"):
            return SupabaseClient(sb["url"], sb["service_key"], sb.get("anon_key", ""), sb.get("bucket", "satellite-images"))
        return None


def sync_passes():
    """CLI entry point: sync pending passes from local to Supabase."""
    import wegs.config as cfg
    config = cfg.get()
    sb = SupabaseClient.from_config(config)
    if not sb:
        print("Supabase not configured. Run: wegs add supabase")
        return

    from wegs.manifest import load, count_passes
    from pathlib import Path
    import os

    output = config["output_folder"]
    manifest = load(output)
    existing = sb.get_existing_folders()

    new_passes = [p for p in manifest["passes"] if p["folder_name"] not in existing]
    print(f"  {len(manifest['passes'])} total, {len(new_passes)} new")

    for i, p in enumerate(new_passes):
        print(f"  [{i+1}/{len(new_passes)}] {p['folder_name']}...")
        pass_id = sb.insert_pass(
            p["satellite"], p["timestamp"], p["folder_name"],
            p["png_count"], p["raw_count"], p["filled_count"], p.get("status", "completed")
        )
        if not pass_id:
            continue

        for img in p.get("images", []):
            img_path = Path(output) / p["folder_name"] / img.get("image_path", img.get("label", "unknown"))
            thumb_path = Path(output) / p["folder_name"] / img.get("thumbnail_path", "")
            if img_path.exists():
                with open(img_path, "rb") as f:
                    url = sb.upload_image(f"passes/{p['folder_name']}/{img_path.name}", f.read(), "image/png")
                if url:
                    sb.insert_image(pass_id, img["type"], img["label"], url)
            time.sleep(0.2)
    print("   Sync complete")
