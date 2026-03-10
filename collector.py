"""
AI Industry Monitor - Feed Collector
=====================================
Fetches items from RSS feeds and GitHub trending, deduplicates, 
and returns structured items for summarization.
"""

import feedparser
import requests
import json
import os
import re
import hashlib
import html
from datetime import datetime, timedelta, timezone
from time import mktime
from config import (
    RSS_FEEDS, GITHUB_TRENDING_URL, LOOKBACK_HOURS,
    MAX_ITEMS_PER_RUN, PRIORITY_KEYWORDS, SEEN_DB_PATH
)


def _ensure_dirs():
    os.makedirs(os.path.dirname(SEEN_DB_PATH), exist_ok=True)


def _load_seen() -> dict:
    """Load previously seen item hashes with timestamps."""
    _ensure_dirs()
    if os.path.exists(SEEN_DB_PATH):
        try:
            with open(SEEN_DB_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_seen(seen: dict):
    """Save seen items, pruning entries older than 7 days."""
    _ensure_dirs()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    pruned = {k: v for k, v in seen.items() if v.get("ts", "") > cutoff}
    with open(SEEN_DB_PATH, "w") as f:
        json.dump(pruned, f, indent=2)


def _item_hash(title: str, link: str) -> str:
    """Create a stable hash for deduplication."""
    raw = f"{title.strip().lower()}|{link.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _clean_html(text: str) -> str:
    """Strip HTML tags and decode entities."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:500]  # Cap description length


def _priority_score(title: str, summary: str) -> int:
    """Score an item by keyword relevance. Higher = more relevant."""
    combined = f"{title} {summary}".lower()
    score = 0
    for kw in PRIORITY_KEYWORDS:
        if kw.lower() in combined:
            score += 1
    # Boost Anthropic/Claude items heavily
    if any(w in combined for w in ["anthropic", "claude"]):
        score += 5
    return score


def _parse_date(entry) -> datetime | None:
    """Extract published date from a feed entry."""
    for field in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, field, None)
        if parsed:
            try:
                return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
            except (ValueError, OverflowError):
                continue
    return None


def fetch_rss_feeds() -> list[dict]:
    """Fetch all configured RSS feeds and return structured items."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    items = []

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:20]:  # Cap per feed
                pub_date = _parse_date(entry)

                # If we can determine date and it's too old, skip
                if pub_date and pub_date < cutoff:
                    continue

                title = _clean_html(getattr(entry, "title", ""))
                link = getattr(entry, "link", "")
                summary = _clean_html(getattr(entry, "summary", ""))

                if not title:
                    continue

                items.append({
                    "source": source_name,
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "published": pub_date.isoformat() if pub_date else "",
                    "priority": _priority_score(title, summary),
                })
        except Exception as e:
            print(f"  [WARN] Failed to fetch {source_name}: {e}")

    return items


def fetch_github_trending() -> list[dict]:
    """Scrape GitHub trending for AI-related repos."""
    items = []
    try:
        headers = {"User-Agent": "AI-Monitor-Bot/1.0"}
        resp = requests.get(GITHUB_TRENDING_URL, headers=headers, timeout=15)
        resp.raise_for_status()

        # Extract repo paths from trending page
        # Match the main repo link (not stargazer/fork sub-links)
        repo_pattern = re.compile(
            r'<h2 class="h3 lh-condensed">\s*<a href="(/[^/]+/[^/"]+)"',
            re.DOTALL
        )
        desc_pattern = re.compile(
            r'<p class="col-9[^"]*?">\s*(.*?)\s*</p>',
            re.DOTALL
        )

        repos = repo_pattern.findall(resp.text)
        descs = desc_pattern.findall(resp.text)

        ai_keywords = {"ai", "llm", "gpt", "ml", "neural", "transformer",
                        "agent", "claude", "openai", "langchain", "rag",
                        "embedding", "diffusion", "model", "inference"}

        for i, repo_path in enumerate(repos[:30]):
            desc = _clean_html(descs[i]) if i < len(descs) else ""
            combined = f"{repo_path} {desc}".lower()

            if any(kw in combined for kw in ai_keywords):
                items.append({
                    "source": "GitHub Trending",
                    "title": repo_path.strip("/"),
                    "link": f"https://github.com{repo_path}",
                    "summary": desc,
                    "published": datetime.now(timezone.utc).isoformat(),
                    "priority": _priority_score(repo_path, desc),
                })
    except Exception as e:
        print(f"  [WARN] Failed to fetch GitHub trending: {e}")

    return items


def collect_all() -> list[dict]:
    """
    Collect from all sources, deduplicate, sort by priority, 
    and return top items.
    """
    seen = _load_seen()
    all_items = []

    print("📡 Fetching RSS feeds...")
    all_items.extend(fetch_rss_feeds())

    print("📡 Fetching GitHub trending...")
    all_items.extend(fetch_github_trending())

    # Deduplicate against previously seen items
    new_items = []
    for item in all_items:
        h = _item_hash(item["title"], item["link"])
        if h not in seen:
            new_items.append(item)
            seen[h] = {"ts": datetime.now(timezone.utc).isoformat()}

    _save_seen(seen)

    # Sort: highest priority first, then by publish date (newest first)
    new_items.sort(key=lambda x: (-x["priority"], x.get("published", "")), reverse=False)

    print(f"📊 Found {len(all_items)} total items, {len(new_items)} are new")
    return new_items[:MAX_ITEMS_PER_RUN]


if __name__ == "__main__":
    items = collect_all()
    for item in items[:10]:
        print(f"  [{item['source']}] (p={item['priority']}) {item['title']}")
        print(f"    {item['link']}")
        print()
