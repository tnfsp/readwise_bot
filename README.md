# 個人訊息流強化系統

> 每天 30 分鐘，精準掌握 AI、國際、GitHub、知識領域的重要資訊。

解決資訊焦慮（FOMO），用 AI 篩選 + 分領域推播，讓你專注在真正重要的內容。

## 功能

- 🤖 **AI 智慧篩選**：Claude 自動評估文章重要性
- 📬 **Telegram 推播**：每日定時推送精選內容
- 🏷️ **分領域推播**：不同時段推送不同主題
- 📊 **多來源整合**：RSS、Readwise Reader、GitHub Trending

## 推播時間表

| 時間 | 領域 | 來源 |
|------|------|------|
| 06:00 | 🤖 AI | Simon Willison, Anthropic, Latent Space, Import AI |
| 07:00 | 🌍 國際 | Foreign Affairs, Foreign Policy, Project Syndicate |
| 08:00 | 💻 GitHub | Trending, claude-code releases |
| 12:00 | 📚 知識 | 電腦玩物, 少数派, 閱讀前哨站 |

## 快速開始

```bash
# 安裝
pip install -r requirements.txt

# 設定環境變數（複製 .env.example 並填入 API keys）
cp .env.example .env

# 測試
python scripts/domain_digest.py github --dry-run

# 執行
python scripts/domain_digest.py ai
```

## 部署（GitHub Actions）

1. Fork 此 repo
2. 設定 Secrets（Settings → Secrets → Actions）：
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `ANTHROPIC_API_KEY`
   - `READWISE_TOKEN`
3. 自動按排程執行

## 專案結構

```
scripts/
├── domain_digest.py    # 分領域推播（主程式）
├── daily_digest.py     # Readwise 整合推播
├── ai_filter.py        # Claude AI 篩選
├── reader_client.py    # Readwise API
└── telegram_bot.py     # Telegram 推播

.github/workflows/
└── daily-digest.yml    # GitHub Actions 排程
```

## License

MIT
