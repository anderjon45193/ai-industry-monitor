# 🤖 AI Industry Monitor

A personal AI news digest bot that collects from 15+ sources, filters through Claude, and delivers a prioritized daily briefing via Telegram.

## How It Works

```
RSS Feeds ─┐
Reddit    ─┤
HN        ─┼─→ Collector ─→ Deduplicator ─→ Claude Summarizer ─→ Telegram
GitHub    ─┤                                                   ─→ Local File
AI Blogs  ─┘
```

1. **Collect**: Pulls from RSS feeds, Reddit, Hacker News, GitHub Trending, and major AI blogs
2. **Deduplicate**: Tracks seen items in a local JSON DB so you never get repeats
3. **Prioritize**: Scores items by keyword relevance (Anthropic/Claude items get boosted)
4. **Summarize**: Claude reads all items and produces a categorized digest with action items
5. **Deliver**: Sends to Telegram and saves a local copy

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Copy the bot token you receive
4. Start a chat with your new bot and send any message
5. Get your chat ID:
   ```bash
   curl https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
   Look for `"chat":{"id":123456789}` in the response

### 3. Set Environment Variables

```bash
# Add to your ~/.bashrc or ~/.zshrc
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
export TELEGRAM_BOT_TOKEN="123456789:ABCdef..."
export TELEGRAM_CHAT_ID="your_chat_id"
```

### 4. Test It

```bash
# Collect only (no API call, no Telegram)
python monitor.py --collect

# Full run but skip Telegram
python monitor.py --dry-run

# Full run
python monitor.py
```

### 5. Schedule with Cron

```bash
crontab -e
```

Add this line (runs daily at 8am EST):

```
0 12 * * * cd /path/to/ai-monitor && /usr/bin/python3 monitor.py >> /tmp/ai-monitor.log 2>&1
```

For twice-daily (8am and 6pm EST):

```
0 12,22 * * * cd /path/to/ai-monitor && /usr/bin/python3 monitor.py >> /tmp/ai-monitor.log 2>&1
```

## Customization

### Add/Remove Sources
Edit `RSS_FEEDS` in `config.py`. Any valid RSS feed URL works.

### Change Priority Keywords
Edit `PRIORITY_KEYWORDS` in `config.py` to adjust what gets boosted.

### Adjust Frequency
- `LOOKBACK_HOURS`: How far back to check (default: 24)
- `MAX_ITEMS_PER_RUN`: Cap on items sent to Claude (default: 60)

### Change Your Interest Profile
Edit `USER_INTERESTS` in `config.py` — this is the prompt context that tells Claude what to focus on.

## File Structure

```
ai-monitor/
├── monitor.py        # Main entry point
├── config.py         # All settings and API keys
├── collector.py      # RSS + GitHub scraping + dedup
├── summarizer.py     # Claude API integration
├── notifier.py       # Telegram + local file delivery
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Running on a Server (Optional)

For always-on monitoring, deploy to a cheap VPS ($5/mo DigitalOcean droplet or free Oracle Cloud tier):

```bash
# Clone your repo
git clone your-repo-url ai-monitor
cd ai-monitor
pip install -r requirements.txt

# Set up env vars and cron as above
```

Alternatively, use GitHub Actions for zero-cost scheduling (see below).

### GitHub Actions (Free Cron)

Create `.github/workflows/digest.yml`:

```yaml
name: AI Digest
on:
  schedule:
    - cron: '0 12 * * *'  # 8am EST daily
  workflow_dispatch:       # Manual trigger

jobs:
  digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python monitor.py
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
```

## Cost

- **Claude API**: ~$0.02-0.05 per digest (Sonnet, ~2K input + 1K output tokens)
- **At daily frequency**: ~$1-1.50/month
- **Telegram**: Free
- **Hosting**: Free with GitHub Actions or cron on existing machine

## Troubleshooting

- **No items found**: Check if `LOOKBACK_HOURS` is too small, or if feeds are down
- **Telegram not sending**: Verify bot token and chat ID; make sure you've messaged the bot first
- **Claude API errors**: Check API key and billing; falls back to raw digest automatically
- **Reddit feeds failing**: Reddit rate-limits RSS; the bot handles this gracefully and skips
