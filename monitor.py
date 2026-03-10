#!/usr/bin/env python3
"""
AI Industry Monitor
====================
A daily AI news digest bot that:
1. Collects items from RSS feeds, Hacker News, Reddit, GitHub Trending
2. Deduplicates against previously seen items
3. Sends everything through Claude for relevance scoring & summarization
4. Delivers a prioritized digest via Telegram + local file

Usage:
    python monitor.py              # Run once (for cron)
    python monitor.py --dry-run    # Collect & summarize, but don't send Telegram
    python monitor.py --collect    # Just collect and print items (no API call)

Setup:
    export ANTHROPIC_API_KEY="sk-ant-..."
    export TELEGRAM_BOT_TOKEN="123456:ABC..."  
    export TELEGRAM_CHAT_ID="your_chat_id"

Cron example (run daily at 8am):
    0 8 * * * cd /path/to/ai-monitor && /usr/bin/python3 monitor.py >> /tmp/ai-monitor.log 2>&1
"""

import sys
from datetime import datetime, timezone

from collector import collect_all
from summarizer import build_digest
from notifier import send_telegram, save_local


def main():
    dry_run = "--dry-run" in sys.argv
    collect_only = "--collect" in sys.argv

    print(f"\n{'='*50}")
    print(f"🤖 AI Industry Monitor")
    print(f"📅 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*50}\n")

    # Step 1: Collect
    print("Step 1/3: Collecting items...")
    items = collect_all()

    if not items:
        print("\n✅ No new items found. Nothing to report.")
        return

    if collect_only:
        print(f"\n📋 Collected {len(items)} items:\n")
        for item in items:
            print(f"  [{item['source']}] (p={item['priority']}) {item['title']}")
            print(f"    {item['link']}")
        return

    # Step 2: Summarize
    print("\nStep 2/3: Building digest with Claude...")
    digest = build_digest(items)
    print(f"  Digest length: {len(digest)} chars")

    # Step 3: Deliver
    print("\nStep 3/3: Delivering digest...")

    # Always save locally
    filepath = save_local(digest)

    # Send via Telegram unless dry run
    if dry_run:
        print("  [DRY RUN] Skipping Telegram")
        print(f"\n{'='*50}")
        print("DIGEST PREVIEW:")
        print(f"{'='*50}")
        print(digest)
    else:
        send_telegram(digest)

    print(f"\n✅ Done! Digest saved to {filepath}")


if __name__ == "__main__":
    main()
