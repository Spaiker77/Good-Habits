import requests
from django.conf import settings

API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"


def send_message(chat_id: str, text: str):
    if not settings.TELEGRAM_BOT_TOKEN:
        return
    try:
        requests.post(API_URL, data={"chat_id": chat_id, "text": text}, timeout=5)
    except Exception:
        # логируй по желанию
        pass
