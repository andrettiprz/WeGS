"""
Telegram integration — optional bot for satellite pass notifications.
"""
import time
import requests

TELEGRAM_API = "https://api.telegram.org/bot"


class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.api = f"{TELEGRAM_API}{token}"

    def send_message(self, text, parse_mode="Markdown"):
        try:
            requests.post(
                f"{self.api}/sendMessage",
                data={"chat_id": self.chat_id, "text": text, "parse_mode": parse_mode},
                timeout=10,
            )
        except Exception as e:
            print(f"  ⚠️ Telegram error: {e}")

    def send_photo(self, path, caption=""):
        try:
            with open(path, "rb") as f:
                requests.post(
                    f"{self.api}/sendPhoto",
                    data={"chat_id": self.chat_id, "caption": caption, "parse_mode": "Markdown"},
                    files={"photo": f},
                    timeout=60,
                )
        except Exception as e:
            print(f"  ⚠️ Telegram photo error: {e}")

    def send_album(self, media_list):
        """media_list: list of (path, caption) tuples."""
        files = {}
        payload = []
        for idx, (path, caption) in enumerate(media_list):
            field = f"photo{idx}"
            files[field] = open(path, "rb")
            payload.append({
                "type": "photo",
                "media": f"attach://{field}",
                "caption": caption,
                "parse_mode": "Markdown",
            })
        try:
            resp = requests.post(
                f"{self.api}/sendMediaGroup",
                data={"chat_id": self.chat_id, "media": json.dumps(payload)},
                files=files,
                timeout=120,
            )
        except Exception as e:
            print(f"  ⚠️ Telegram album error: {e}")
        finally:
            for f in files.values():
                f.close()

    @staticmethod
    def from_config(config):
        tg = config.get("telegram", {})
        if tg.get("enabled") and tg.get("bot_token") and tg.get("chat_id"):
            return TelegramBot(tg["bot_token"], tg["chat_id"])
        return None
