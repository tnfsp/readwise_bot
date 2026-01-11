# 自動化系統架構 (Automation Architecture)

> 由 `/pm` 維護

---

## 系統總覽

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              每日推播系統                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐            │
│   │   Readwise   │      │    Claude    │      │   Telegram   │            │
│   │   Reader API │  →   │     API      │  →   │     Bot      │            │
│   │              │      │              │      │              │            │
│   │  獲取新文章  │      │  AI 篩選     │      │  推播精選    │            │
│   │  更新 Tag    │      │  + 摘要      │      │  + 互動      │            │
│   └──────────────┘      └──────────────┘      └──────────────┘            │
│                                                                             │
│                         ┌──────────────┐                                   │
│                         │   排程器     │                                   │
│                         │  (每日 6AM)  │                                   │
│                         └──────────────┘                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## API 能力總結

### Readwise Reader API

| 端點 | 方法 | 用途 | 範例 |
|------|------|------|------|
| `/api/v3/list/` | GET | 列出文章 | 獲取過去 24h 新文章 |
| `/api/v3/update/{id}/` | PATCH | 更新文章 | 自動打 Tag |
| `/api/v3/tags/` | GET | 列出 Tag | 獲取現有分類 |
| `/api/v3/save/` | POST | 存入文章 | 從其他來源存入 |

**過濾參數**：
- `updatedAfter`: ISO 日期，獲取指定時間後更新的文章
- `location`: `feed` / `archive` / `later`
- `category`: `rss` / `article` / `email` / `note`
- `withHtmlContent`: 包含完整 HTML 內容

**速率限制**：每分鐘 20 次請求（足夠每日處理）

### 現有資料

| 項目 | 數量 |
|------|------|
| 總文章數 | 19,113 |
| Feed 中未處理 | 13,770 |
| 現有 Tag | 48 個 |
| 過去 24h 更新 | ~100 篇 |

### 現有 Tag 系統

用戶已有分類系統：
- `A -` 開頭：Area（領域）- AI、學術研究、寫作、醫學知識...
- `P -` 開頭：Project（專案）- learn prompting、個人理財...

**建議**：新增狀態 Tag 與現有系統並存
- `#必讀`、`#已推播`、`#已輸出` 等

---

## 技術選項

### 選項 A：Python Script + Cron

```
優點：完全可控、靈活
缺點：需要本地或伺服器執行

架構：
├── scripts/
│   ├── daily_digest.py    # 主腳本
│   ├── reader_client.py   # Reader API 封裝
│   ├── telegram_bot.py    # Telegram 推播
│   └── ai_filter.py       # Claude 篩選邏輯
├── .env                   # API Keys
└── cron job               # 每日 6AM 執行
```

### 選項 B：n8n Workflow

```
優點：視覺化、易修改、可雲端
缺點：需要 host n8n

架構：
1. Schedule Trigger (每日 6AM)
   ↓
2. HTTP Request (Readwise API)
   ↓
3. Code Node (AI 篩選邏輯)
   ↓
4. HTTP Request (Claude API)
   ↓
5. Telegram Node (推播)
   ↓
6. HTTP Request (更新 Reader Tag)
```

### 選項 C：Pipedream（你已有經驗）

```
優點：已有使用經驗、簡單
缺點：免費版有限制

可直接擴展現有的 PubMed 工作流
```

---

## 推薦架構：Python Script

考慮到你需要 AI 篩選（Claude），Python 是最靈活的選擇。

### 系統流程

```python
# 每日 6:00 AM 執行

1. 獲取新文章
   ├── Reader API: GET /list/?updatedAfter={yesterday}
   ├── 過濾: location=feed, category=rss
   └── 輸出: 約 50-100 篇新文章

2. AI 篩選 + 摘要
   ├── 對每篇文章:
   │   ├── 標題 + 摘要 + 來源
   │   └── Claude 評估: 重要性 (1-5)、領域、一句話摘要
   ├── 篩選: 只保留重要性 >= 4
   └── 輸出: 5-10 篇精選

3. 推播到 Telegram
   ├── 格式化訊息:
   │   ├── 領域標籤
   │   ├── 標題
   │   ├── AI 摘要
   │   └── 連結
   └── 發送到指定 Chat

4. 更新 Reader Tag
   ├── 精選文章: 加 #必讀
   ├── 其他文章: 加 #已推播
   └── Reader API: PATCH /update/{id}/
```

### 資料夾結構

```
個人訊息流強化/
├── .claude/                    # Claude Code 專案文件
├── scripts/
│   ├── __init__.py
│   ├── config.py               # 設定管理
│   ├── reader_client.py        # Reader API 封裝
│   ├── ai_filter.py            # Claude 篩選邏輯
│   ├── telegram_bot.py         # Telegram Bot
│   ├── daily_digest.py         # 主程式
│   └── test_*.py               # 測試腳本
├── .env                        # API Keys（已建立）
├── requirements.txt            # Python 依賴
└── README.md
```

---

## AI 篩選設計

### Prompt 設計

```
你是一個資訊篩選助手。根據以下文章資訊，評估其重要性。

用戶關注領域：
- 醫學（心臟外科、ECMO、VAD）
- AI（Claude Code、LLM 應用）
- 國際情勢
- 知識管理、筆記方法

文章資訊：
標題：{title}
來源：{source}
摘要：{summary}

請評估：
1. 重要性 (1-5)：5=必讀，4=值得看，3=可看可不看，2=可略過，1=不相關
2. 領域：醫學/AI/國際/知識/生產力/其他
3. 一句話摘要：20字以內

輸出 JSON：
{"importance": 5, "domain": "AI", "summary": "..."}
```

### 批量處理

為了節省 API 調用，可以批量處理：

```python
# 一次處理 10 篇文章
articles_batch = articles[:10]
prompt = f"""
評估以下 {len(articles_batch)} 篇文章...
{format_articles(articles_batch)}
"""
```

---

## Telegram Bot 設計

### 功能

1. **被動接收**：每日早晨收到精選推播
2. **主動互動**（可選）：
   - `/today` - 查看今日精選
   - `/stats` - 查看統計
   - 按鈕回饋：「已讀」「稍後」「略過」

### 訊息格式

```
📰 今日精選 (5 篇)

🏥 醫學
• ECMO 在心源性休克的新證據
  → 多中心研究顯示存活率提升 15%
  🔗 閱讀全文

🤖 AI
• Claude Code 新增 MCP 支援
  → 可透過 MCP 協議連接外部工具
  🔗 閱讀全文

...

⏰ 2026-01-12 07:00
```

---

## 環境變數

`.env` 文件（已建立）：

```env
# Readwise Reader API
READWISE_TOKEN=xxx

# Telegram Bot
TELEGRAM_BOT_TOKEN=    # 待設定
TELEGRAM_CHAT_ID=      # 待設定

# Claude API
ANTHROPIC_API_KEY=     # 待設定
```

---

## 實作順序

### Step 1: 基礎測試
- [x] 安裝 `readwise-api` 套件
- [ ] 測試 Reader API 連接
- [ ] 測試獲取文章列表

### Step 2: AI 篩選
- [ ] 設計 prompt
- [ ] 測試 Claude API 批量評估
- [ ] 調整篩選邏輯

### Step 3: Telegram Bot
- [ ] 創建 Bot (@BotFather)
- [ ] 設計訊息格式
- [ ] 實現推播功能

### Step 4: 整合
- [ ] 串接完整流程
- [ ] 加入錯誤處理
- [ ] 設定排程

### Step 5: 優化
- [ ] 加入互動按鈕
- [ ] 回饋收集
- [ ] Tag 自動更新

---

## 變更記錄

| 日期 | 變更內容 |
|------|----------|
| 2026-01-11 | 初版架構設計 |
