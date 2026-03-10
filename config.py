"""
AI Industry Monitor - Configuration
====================================
Set your API keys and preferences here.
"""

import os

# ──────────────────────────────────────────────
# API Keys (set via environment variables)
# ──────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# ──────────────────────────────────────────────
# RSS Feeds to Monitor
# ──────────────────────────────────────────────
RSS_FEEDS = {
    # ── Anthropic / Claude ──
    "Anthropic Blog": "https://www.anthropic.com/rss.xml",

    # ── Major AI Labs ──
    "OpenAI Blog": "https://openai.com/blog/rss.xml",
    "Google AI Blog": "https://blog.google/technology/ai/rss/",
    "Meta AI Blog": "https://ai.meta.com/blog/rss/",
    "Microsoft AI Blog": "https://blogs.microsoft.com/ai/feed/",

    # ── Community / Discovery ──
    "Hacker News (AI)": "https://hnrss.org/newest?q=AI+OR+LLM+OR+Claude+OR+GPT+OR+anthropic&points=50",
    "Reddit r/artificial": "https://www.reddit.com/r/artificial/top/.rss?t=day",
    "Reddit r/LocalLLaMA": "https://www.reddit.com/r/LocalLLaMA/top/.rss?t=day",
    "Reddit r/MachineLearning": "https://www.reddit.com/r/MachineLearning/top/.rss?t=day",

    # ── Research ──
    "ArXiv AI": "https://rss.arxiv.org/rss/cs.AI",
    "ArXiv LG (Machine Learning)": "https://rss.arxiv.org/rss/cs.LG",

    # ── Product Launches ──
    "Product Hunt AI": "https://www.producthunt.com/feed?category=artificial-intelligence",

    # ── Industry News ──
    "The Verge AI": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "Ars Technica AI": "https://feeds.arstechnica.com/arstechnica/technology-lab",
}

# ──────────────────────────────────────────────
# GitHub Trending (scraped, not RSS)
# ──────────────────────────────────────────────
GITHUB_TRENDING_URL = "https://github.com/trending?since=daily&spoken_language_code=en"

# ──────────────────────────────────────────────
# Filtering & Summarization
# ──────────────────────────────────────────────

# How many hours back to look for new items
LOOKBACK_HOURS = 24

# Max items to send to Claude for summarization per run
MAX_ITEMS_PER_RUN = 60

# Priority keywords — items matching these get boosted
PRIORITY_KEYWORDS = [
    "anthropic", "claude", "claude code", "sonnet", "opus", "haiku",
    "mcp", "model context protocol",
    "agent", "agentic", "autonomous",
    "open source", "framework", "tool",
    "api", "pricing", "benchmark",
    "openai", "gpt", "gemini", "llama", "mistral",
    "fine-tuning", "rag", "embedding",
    "startup", "funding", "acquisition",
]

# Categories you care about most (used in the Claude prompt)
USER_INTERESTS = """
- Anthropic Claude updates (new models, features, API changes, Claude Code, MCP)
- New AI tools, frameworks, and open-source projects (especially autonomous agents)
- AI business opportunities and trends relevant to a solo entrepreneur
- Practical AI applications (coding assistants, automation, business tools)
- Major moves by OpenAI, Google, Meta, and other labs
- AI regulation and policy changes that affect builders
- Emerging techniques (RAG, fine-tuning, multi-agent systems)
"""

# ──────────────────────────────────────────────
# Output
# ──────────────────────────────────────────────

# Where to store seen items (deduplication)
SEEN_DB_PATH = os.path.expanduser("~/.ai-monitor/seen.json")

# Local digest output (in addition to Telegram)
DIGEST_OUTPUT_DIR = os.path.expanduser("~/.ai-monitor/digests")

# Claude model to use for summarization
CLAUDE_MODEL = "claude-sonnet-4-20250514"
