"""
AI Industry Monitor - Summarizer
==================================
Sends collected items to Claude for relevance scoring,
categorization, and digest generation.
"""

import anthropic
from datetime import datetime, timezone
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, USER_INTERESTS


def build_digest(items: list[dict]) -> str:
    """
    Send collected items to Claude and get back a structured daily digest.
    Returns formatted Markdown/text suitable for Telegram.
    """
    if not items:
        return "🤷 No new AI items found in the last cycle. Quiet day!"

    if not ANTHROPIC_API_KEY:
        return _fallback_digest(items)

    # Format items for the prompt
    items_text = ""
    for i, item in enumerate(items, 1):
        items_text += f"""
---
Item {i}:
Source: {item['source']}
Title: {item['title']}
Link: {item['link']}
Summary: {item['summary'][:300]}
Published: {item.get('published', 'unknown')}
---
"""

    prompt = f"""You are an AI industry analyst creating a daily briefing for a solo entrepreneur 
who builds AI-powered tools and runs multiple small businesses. He uses Claude extensively 
and wants to stay ahead of AI trends.

His specific interests:
{USER_INTERESTS}

Below are {len(items)} items collected from RSS feeds, Hacker News, Reddit, GitHub trending, 
and AI blogs in the last 24 hours.

YOUR TASK:
1. Filter out noise — skip items that are low-value, duplicate topics, or irrelevant.
2. Group the remaining items into these categories:
   - 🔴 URGENT: Breaking changes, major releases, things he should act on today
   - 🟡 IMPORTANT: Significant updates worth reading this week  
   - 🔵 INTERESTING: Cool tools, trends, or research worth knowing about
   - 🟢 ANTHROPIC/CLAUDE: Anything related to Anthropic or Claude (always include)
3. For each item, write a 1-2 sentence summary explaining WHY it matters to him.
4. At the end, add a "💡 Action Items" section if any items require action.
5. Add a "📈 Trend Watch" one-liner about the overarching theme you notice.

FORMAT: Use Telegram-friendly formatting (bold with *, minimal markdown).
Keep the total digest under 3000 characters for readability.
If fewer than 3 items are truly noteworthy, say so — don't pad.

ITEMS:
{items_text}
"""

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        digest_text = response.content[0].text

        # Add header
        now = datetime.now(timezone.utc).strftime("%B %d, %Y %H:%M UTC")
        header = f"🤖 *AI Monitor Daily Digest*\n📅 {now}\n{'─' * 30}\n\n"
        footer = f"\n\n{'─' * 30}\n📊 {len(items)} items scanned | Powered by Claude"

        return header + digest_text + footer

    except Exception as e:
        print(f"  [ERROR] Claude API failed: {e}")
        return _fallback_digest(items)


def _fallback_digest(items: list[dict]) -> str:
    """Simple digest without AI summarization (fallback if API fails)."""
    now = datetime.now(timezone.utc).strftime("%B %d, %Y %H:%M UTC")
    lines = [
        f"🤖 *AI Monitor Digest* (raw - API unavailable)",
        f"📅 {now}",
        f"{'─' * 30}",
        "",
    ]

    # Group by priority
    urgent = [i for i in items if i["priority"] >= 5]
    important = [i for i in items if 2 <= i["priority"] < 5]
    other = [i for i in items if i["priority"] < 2]

    if urgent:
        lines.append("🔴 *HIGH PRIORITY*")
        for item in urgent[:5]:
            lines.append(f"• [{item['source']}] {item['title']}")
            lines.append(f"  {item['link']}")
        lines.append("")

    if important:
        lines.append("🟡 *NOTABLE*")
        for item in important[:10]:
            lines.append(f"• [{item['source']}] {item['title']}")
            lines.append(f"  {item['link']}")
        lines.append("")

    if other:
        lines.append(f"🔵 *OTHER* ({len(other)} items)")
        for item in other[:5]:
            lines.append(f"• [{item['source']}] {item['title']}")
        lines.append("")

    lines.append(f"{'─' * 30}")
    lines.append(f"📊 {len(items)} total items")

    return "\n".join(lines)
