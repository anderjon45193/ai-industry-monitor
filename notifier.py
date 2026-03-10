"""
AI Industry Monitor - Notifier
================================
Delivers the digest via Telegram and saves a local copy.
"""

import os
import requests
from datetime import datetime, timezone
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, DIGEST_OUTPUT_DIR


def send_telegram(digest: str) -> bool:
    """Send digest to Telegram. Splits long messages if needed."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("  [SKIP] Telegram not configured — skipping notification")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    # Telegram has a 4096 char limit per message
    chunks = _split_message(digest, max_len=4000)

    success = True
    for chunk in chunks:
        try:
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": chunk,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            }
            resp = requests.post(url, json=payload, timeout=15)

            if resp.status_code != 200:
                # Retry without Markdown if parsing fails
                payload["parse_mode"] = ""
                resp = requests.post(url, json=payload, timeout=15)

            if resp.status_code == 200:
                print("  [OK] Telegram message sent")
            else:
                print(f"  [ERROR] Telegram returned {resp.status_code}: {resp.text[:200]}")
                success = False
        except Exception as e:
            print(f"  [ERROR] Telegram send failed: {e}")
            success = False

    return success


def save_local(digest: str) -> str:
    """Save digest to a local file for reference."""
    os.makedirs(DIGEST_OUTPUT_DIR, exist_ok=True)
    filename = datetime.now(timezone.utc).strftime("digest_%Y%m%d_%H%M.md")
    filepath = os.path.join(DIGEST_OUTPUT_DIR, filename)

    with open(filepath, "w") as f:
        f.write(digest)

    print(f"  [OK] Saved to {filepath}")
    return filepath


def _split_message(text: str, max_len: int = 4000) -> list[str]:
    """Split a long message into chunks at line boundaries."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    current = ""

    for line in text.split("\n"):
        if len(current) + len(line) + 1 > max_len:
            if current:
                chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line

    if current:
        chunks.append(current)

    return chunks
