# Personal Information Flow System

> AI-powered RSS digest with Telegram push notifications & Readwise Reader integration.

解決資訊焦慮（FOMO），用 AI 篩選 + 分領域推播，讓你專注在真正重要的內容。

## Features

### 1. AI-Powered Daily Digest
- **Smart Filtering**: Claude AI evaluates article importance based on your interests
- **Personalized Summary**: Each article includes a one-line highlight explaining why it matters to you
- **Multi-domain Support**: AI, International Affairs, GitHub/Dev, Knowledge, Medical

### 2. Scheduled Push Notifications
| Time (UTC+8) | Domain | Sources |
|--------------|--------|---------|
| 06:00 | 🤖 AI | Simon Willison, Anthropic, OpenAI, Reddit |
| 07:00 | 🌍 International | Foreign Affairs, Reuters, BBC |
| 08:00 | 💻 GitHub/Dev | Trending repos, r/programming |
| 09:00 | ⚡ Claude Code | Release notes |
| 12:00 | 📚 Knowledge | Hacker News, Farnam Street |

### 3. Quick Capture (Telegram → Readwise Reader)
Forward any message to your bot → AI generates title → Saved to Reader
- Forward channel posts
- Share URLs
- Send text notes

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Actions                        │
│              (Scheduled Push Notifications)              │
├─────────────────────────────────────────────────────────┤
│  06:00 AI │ 07:00 Intl │ 08:00 GitHub │ 12:00 Knowledge │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                      RSS Feeds                           │
│         (Blogs, Reddit, News, GitHub Trending)           │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Claude AI Filter                      │
│     (Evaluate importance + Generate highlights)          │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Telegram Bot                          │
│                  (Push to your chat)                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                 Zeabur (24/7 Webhook)                    │
│                   Quick Capture Bot                      │
├─────────────────────────────────────────────────────────┤
│  Telegram Message → AI Title → Readwise Reader          │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.11+
- Telegram Bot (create via [@BotFather](https://t.me/BotFather))
- [Anthropic API Key](https://console.anthropic.com/)
- [Readwise Reader Token](https://readwise.io/access_token)

### Installation

```bash
# Clone
git clone https://github.com/tnfsp/readwise_bot.git
cd readwise_bot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Create `.env` file:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Anthropic (Claude AI)
ANTHROPIC_API_KEY=sk-ant-xxx

# Readwise Reader
READWISE_TOKEN=your_token
```

### Usage

```bash
# Test connection
python scripts/domain_digest.py ai --dry-run

# Push specific domain
python scripts/domain_digest.py ai
python scripts/domain_digest.py github
python scripts/domain_digest.py international

# Push all domains
python scripts/domain_digest.py all

# List available domains
python scripts/domain_digest.py --list
```

## Deployment

### Option 1: GitHub Actions (Recommended for scheduled push)

1. Fork this repo
2. Go to Settings → Secrets and variables → Actions
3. Add secrets:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `ANTHROPIC_API_KEY`
   - `READWISE_TOKEN`
4. Enable Actions (Actions tab → Enable)
5. Workflows will run automatically on schedule

### Option 2: Zeabur (For Quick Capture webhook)

1. Connect your GitHub repo to [Zeabur](https://zeabur.com)
2. Set environment variables
3. Deploy

## Project Structure

```
├── scripts/
│   ├── domain_digest.py     # Domain-based push (main)
│   ├── daily_digest.py      # Readwise integration
│   ├── ai_filter.py         # Claude AI filtering
│   ├── reader_client.py     # Readwise Reader API
│   ├── telegram_bot.py      # Telegram notifications
│   ├── quick_capture.py     # Quick capture bot
│   └── config.py            # Configuration
├── app.py                   # Webhook entry point
├── .github/workflows/
│   └── daily-digest.yml     # GitHub Actions schedule
├── requirements.txt
└── .env.example
```

## Customization

### Add/Modify RSS Sources

Edit `DOMAIN_CONFIG` in `scripts/domain_digest.py`:

```python
DOMAIN_CONFIG = {
    "ai": {
        "name": "AI",
        "emoji": "🤖",
        "feeds": [
            {"name": "Your Blog", "url": "https://example.com/feed.xml"},
        ],
        "max_items": 10,
        "use_ai_filter": True
    },
}
```

### Customize AI Filtering

Edit `USER_PROFILE` in `scripts/domain_digest.py` to personalize AI recommendations.

## License

MIT

## Acknowledgments

- [Readwise Reader API](https://readwise.io/reader_api)
- [Anthropic Claude](https://www.anthropic.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
