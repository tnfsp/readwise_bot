# Session Log

> 每次 CLI 啟動時必讀此檔案，了解專案進度與待辦事項

---

## Session: 2025-12-14 初始化

### 變更摘要
- 建立專案模板框架
- 建立 CLAUDE.md 主要說明文件
- 建立 `/concept` subagent (概念設計師)
- 建立 `/pm` subagent (專案經理)
- 建立文件模板：PRD.md, TECHSTACK.md, IMPLEMENTATION-PLAN.md
- 建立 log 系統

### 決策記錄
- 採用 `.claude/` 目錄結構管理所有 Claude Code 相關檔案
- Subagent 使用 slash command 方式實作，放在 `.claude/commands/`
- Log 使用累積式 Markdown 格式，每次 session 新增一個區塊
- 工作流程：Concept 先行 → PM 接手規劃 → 動態建立其他 Subagent

### 待辦事項
- [ ] 使用此模板開始新專案時，執行 `/concept` 討論專案概念
- [ ] 更新 CLAUDE.md 中的 `[PROJECT_NAME]`
- [ ] 填寫 PRD.md
- [ ] 填寫 TECHSTACK.md
- [ ] 執行 `/pm` 建立實作計畫

---

## Session: 2026-01-11 - 概念設計完成

### 變更摘要
- 完成 PRD.md v0.1 初版
- 完成 TECHSTACK.md v0.1 初版
- 完成 SOURCES.md 資訊源架構分析
- 完成 BLUEPRINT.md 系統藍圖
- 更新 CLAUDE.md 專案名稱與概述

### 決策記錄

**痛點確認**：
- 時間碎片化、缺乏輸出、害怕資訊攝取不夠全面（FOMO）

**核心價值定義**：
- 系統目標是「判斷更好」而非「知道更多」
- 強調「暴露不確定性」：保留觀點衝突、追蹤想法演變

**資訊源分析**：
- 現有 RSS 約 70 個（知識/學習/筆記/生產力過飽和）
- 現有 Telegram 頻道約 20 個
- 現有 Pipedream：PubMed（心臟外科/ECMO/VAD）→ AI 摘要 → LINE
- 醫學領域已完善（NEJM, LITFL, EMCrit）
- **待補強**：AI/Claude Code、國際情勢

**核心架構決策：漸進式過渡 A → B**：
- Phase 1：Reader 為主（安全網），推播為輔（每日精選提醒）
- Phase 2：當 AI 篩選信任建立後，推播成為主要入口，Reader 退為深讀工具
- 這個設計可以逐步減少 FOMO，同時保留驗證機制

**技術選擇**：
- 核心工具：Readwise/Reader + Heptabase
- 推播管道：Telegram Bot（待建立）
- AI 輔助：Claude（輔助而非取代判斷）
- 現有自動化：Pipedream（醫學論文），待整合

**輸出框架（Heptabase）**：
- 洞見卡片：標準輸出，含信心度標記
- 衝突卡片：當觀點矛盾時記錄
- 演變追蹤：長期議題的想法變化

### 產出文件
- `.claude/docs/PRD.md` - 產品需求文件
- `.claude/docs/TECHSTACK.md` - 技術棧說明
- `.claude/docs/SOURCES.md` - 資訊源架構
- `.claude/docs/BLUEPRINT.md` - 系統藍圖

### 待辦事項
- [x] 撰寫 PRD.md 初版
- [x] 撰寫 TECHSTACK.md 初版
- [x] 撰寫 SOURCES.md 資訊源分析
- [x] 撰寫 BLUEPRINT.md 系統藍圖
- [x] 更新 CLAUDE.md 專案名稱
- [ ] 執行 `/pm` 建立實作計畫（IMPLEMENTATION-PLAN.md）
- [ ] 補強資訊源：AI/Claude Code、國際情勢
- [ ] 設計 Heptabase 卡片模板
- [ ] 建立 Telegram Bot
- [ ] 整合現有 Pipedream 流程

---

## Session: 2026-01-11 - PM 規劃與流程設計

### 變更摘要
- 建立 IMPLEMENTATION-PLAN.md 實作計畫
- 建立 WORKFLOW.md 每日處理流程
- 建立 READER-SETUP.md Reader 配置指南
- 更新 SOURCES.md 加入 GitHub 來源

### 決策記錄

**實作階段規劃**：
- Phase 1：基礎建立（方法論 + 手動驗證 2 週）
- Phase 2：推播自動化（Telegram Bot）
- Phase 3：進階優化

**每日流程設計**：
- 標準版 50 分鐘：掃描(15) → 深讀(25) → 輸出(10)
- 忙碌日版 15 分鐘：只掃描 + 一句話輸出
- 空檔穿插版：分段執行
- 週末深度版：處理「稍後」+ 週回顧

**Reader Tag 系統**：
- 狀態 Tag：必讀 → 已讀 → 已輸出
- 領域 Tag：醫學、AI、國際、知識、生產力
- 建議 Filter：今日待讀、待處理、週末回顧

### 產出文件
- `.claude/docs/IMPLEMENTATION-PLAN.md` - 實作計畫
- `.claude/docs/WORKFLOW.md` - 每日流程指南
- `.claude/docs/READER-SETUP.md` - Reader 配置指南

### 待辦事項
- [x] 建立 IMPLEMENTATION-PLAN.md
- [x] 建立 WORKFLOW.md
- [x] 建立 READER-SETUP.md
- [ ] 建立 HEPTABASE-TEMPLATES.md（Heptabase 卡片模板）
- [ ] 補強資訊源：從 SOURCES.md 選擇 AI/國際情勢來源
- [ ] 開始手動驗證期（2 週）

### Phase 1 進度
| 任務 | 狀態 |
|------|------|
| 1.1 資訊源整理 | 待開始 |
| 1.2 流程設計 | ✅ 完成 |
| 1.3 工具配置 | ✅ 完成 |
| 1.4 輸出框架 | 待開始 |
| 1.5 手動驗證 | 待開始 |

---

## Session: 2026-01-11 - API 探索與 Tag 系統重設計

### 變更摘要
- 探索 Readwise Reader API 功能
- 重新設計 Tag 系統（加入前綴區分）
- 建立 AUTOMATION.md 自動化架構文件
- 建立並測試 Reader API 測試腳本
- 設定 .env 環境變數

### 決策記錄

**Readwise Reader API 能力確認**：
- 支援端點：list（列出文章）、update（更新 Tag）、tags（取得 Tag）、save（存入文章）
- 速率限制：每分鐘 20 次（足夠每日處理）
- 現有資料：19,113 總文章、15,476 未處理（Feed 中）、48 個 Tag

**Tag 系統重新設計**：
- 原有系統：A-（Area）、P-（Project）、R-（Resource）前綴
- 新設計決策：重新設計，同時支援狀態追蹤與領域分類
- 前綴系統：
  - `#` = 狀態（#必讀、#已讀、#已輸出、#略過、#稍後、#推播）
  - `@` = 領域（@醫學、@AI、@國際、@知識、@生產力、@生活）
  - `★` = 特殊標記（★星標）
  - `?` = 待處理（?衝突）

**自動化架構選擇**：
- 決定使用 Python Script 方案（最靈活，適合 AI 整合）
- 暫不使用 readwise-api 套件的高層封裝（功能有限）
- 直接使用 requests 呼叫 REST API

### API 測試結果
- 過去 24 小時新文章：51 篇
- Feed 中未處理：15,476 篇
- 現有 Tag：48 個
- API 連接狀態：正常

### 產出文件
- `.claude/docs/AUTOMATION.md` - 自動化系統架構
- `.claude/docs/READER-SETUP.md` - 更新 Tag 系統設計
- `.env` - 環境變數設定
- `scripts/test_reader_api.py` - API 測試腳本

### 待辦事項
- [x] 探索 Reader API
- [x] 重新設計 Tag 系統
- [x] 建立測試腳本
- [x] 測試 API 連接
- [ ] 建立 Telegram Bot（@BotFather）
- [ ] 設計 AI 篩選 prompt
- [ ] 完成每日推播腳本
- [ ] 建立 HEPTABASE-TEMPLATES.md

---

## Session: 2026-01-11 深夜 - 完成自動化推播系統

### 變更摘要
- 討論並調整 WORKFLOW.md（降低每日門檻、週輸出）
- 完成 Telegram Bot 設定
- 完成所有自動化腳本
- 首次成功推播測試
- 更新 allow 權限設定

### 決策記錄

**工作流調整**：
- 原設計：每日 50 分鐘、每日輸出
- 新設計：分層設計
  - 最小可行：15 分鐘/每日（底線）
  - 標準版：30 分鐘（有空時）
  - 完整版：50 分鐘（週末）
- 輸出改為：每週 3 張卡片（降低壓力）

**Telegram Bot 建立**：
- Bot Token: 已設定
- Chat ID: [已設定]
- 測試推播：成功

**自動化腳本完成**：
- `scripts/config.py` - 配置管理
- `scripts/reader_client.py` - Readwise API 封裝
- `scripts/telegram_bot.py` - Telegram 推播
- `scripts/ai_filter.py` - Claude AI 篩選
- `scripts/daily_digest.py` - 主程式

**AI 篩選效果**：
- 輸入：33 篇新文章
- 輸出：7-8 篇精選
- 自動分類領域、產生中文摘要
- 使用 Claude Sonnet 模型

**Allow 設定更新**：
- 全部操作已允許（Bash、Read、Write、Edit、Glob、Grep）

### 首次推播結果
- 時間：2026-01-11 23:41
- 精選文章：8 篇
- 領域分布：AI (6)、知識 (2)
- 推播狀態：成功

### 產出文件
- `scripts/config.py`
- `scripts/reader_client.py`
- `scripts/telegram_bot.py`
- `scripts/ai_filter.py`
- `scripts/daily_digest.py`
- `requirements.txt`
- `.env`（更新）
- `.claude/settings.local.json`（更新）
- `.claude/docs/WORKFLOW.md`（更新）

### 使用方式
```bash
# 測試所有連接
python scripts/daily_digest.py --test

# 測試模式（不發送）
python scripts/daily_digest.py --dry-run

# 正式推播
python scripts/daily_digest.py

# 不使用 AI（簡單規則）
python scripts/daily_digest.py --no-ai
```

### 待辦事項
- [x] 建立 Telegram Bot
- [x] 完成所有自動化腳本
- [x] 測試完整推播流程
- [x] 更新 allow 設定
- [x] 設定每日定時執行（GitHub Actions）
- [ ] 建立 HEPTABASE-TEMPLATES.md
- [ ] 觀察 1-2 週，調整 AI 篩選參數

---

## Session: 2026-01-11 深夜續 - 分領域推播 + GitHub Actions

### 變更摘要
- 討論並確認全球頂級訊息源
- 新增分領域推播功能
- 建立 GitHub Actions 自動排程
- 測試 GitHub 領域推播成功

### 決策記錄

**訊息源更新**：
- AI 領域（5 個）：Simon Willison, Import AI, Latent Space, Anthropic Blog, Ben's Bites
- 國際情勢（4 個）：Foreign Affairs, Foreign Policy, 敏迪選讀, Project Syndicate
- GitHub（2 個）：GitHub Trending RSS, claude-code releases
- 醫學：維持使用 PubMed Pipedream，不加入 Reader

**分領域推播時間**：
| 時間 | 領域 |
|------|------|
| 06:00 | 🤖 AI |
| 07:00 | 🌍 國際 |
| 08:00 | 💻 GitHub |
| 12:00 | 📚 知識 |

**部署方案**：
- 選擇 GitHub Actions（免費、簡單、可靠）
- 使用 cron 排程觸發
- 支援手動執行特定領域

### 測試結果
- GitHub 領域推播：成功（34 篇 → 精選 8 篇）
- AI 領域測試：成功（3 篇，部分 RSS 無更新）

### 產出文件
- `scripts/domain_digest.py` - 分領域推播腳本
- `.github/workflows/daily-digest.yml` - GitHub Actions 設定
- `requirements.txt` - 新增 feedparser
- `.claude/docs/SOURCES.md` - 更新訊息源清單

### GitHub Actions 部署步驟
1. 推送到 GitHub 後，進入 Settings → Secrets and variables → Actions
2. 新增以下 secrets：
   - `READWISE_TOKEN`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `ANTHROPIC_API_KEY`
3. Actions 會自動按排程執行

### 使用方式
```bash
# 列出領域
python scripts/domain_digest.py --list

# 測試特定領域
python scripts/domain_digest.py ai --dry-run

# 正式推播
python scripts/domain_digest.py github

# 推播所有領域
python scripts/domain_digest.py all
```

### 待辦事項
- [x] 確認訊息源
- [x] 建立分領域推播
- [x] 建立 GitHub Actions
- [x] 測試推播
- [ ] 推送到 GitHub 並設定 Secrets
- [ ] 建立 HEPTABASE-TEMPLATES.md

---

## Session: 2026-01-12 - AI 摘要 + Reddit 整合

### 變更摘要
- 新增醫學領域推播（PubMed RSS）
- 新增 Readwise 每日精選排程（台灣 20:00）
- AI 篩選功能增強：每篇文章都產生重點摘要（💡）
- 整合 Reddit 訊息源到 AI、國際、GitHub/開發 領域
- 修復 AI 摘要未顯示的問題（JSON markdown 包裝處理）

### 決策記錄

**AI 摘要增強**：
- 原本 AI 只做「篩選」（選擇文章）
- 現在加入「摘要」：每篇文章產生一句話重點，幫助判斷是否要點進去
- 使用 JSON 格式回傳：`{"selected": [...], "highlights": {...}}`

**Reddit 訊息源**：
- AI 領域：r/MachineLearning, r/LocalLLaMA, r/ClaudeAI, r/ChatGPT, r/artificial
- 國際領域：r/geopolitics, r/worldnews
- GitHub/開發：r/programming, r/webdev, r/Python
- 使用每日熱門（`/top/.rss?t=day`）而非最新文章

**推播排程更新**：
| 時間 | 領域 |
|------|------|
| 05:30 | 🏥 醫學 |
| 06:00 | 🤖 AI |
| 07:00 | 🌍 國際 |
| 08:00 | 💻 GitHub/開發 |
| 12:00 | 📚 知識 |
| 20:00 | 📖 Readwise 精選 |

### 產出/修改文件
- `scripts/domain_digest.py` - 增強 AI 摘要、新增 Reddit feeds
- `.github/workflows/daily-digest.yml` - 新增醫學、Readwise 排程

### 待辦事項
- [x] 新增醫學領域
- [x] 新增 Readwise 排程
- [x] AI 摘要功能
- [x] Reddit 訊息源
- [x] 推送到 GitHub 並設定 Secrets
- [ ] 建立 HEPTABASE-TEMPLATES.md

---

## Session: 2026-01-12 深夜 - 個人化 AI 篩選 + 訊息源補強

### 變更摘要
- 補強各領域訊息源（OpenAI、Google AI、BBC、Reuters、Hacker News 等）
- 新增 Claude Code 獨立推播（每日 09:00）
- 實作個人化 AI 篩選（USER_PROFILE）
- Readwise 推播自動標記領域 Tag（@AI、@國際、@知識）
- 探索用戶 Readwise Reader + Heptabase 資料建立偏好畫像

### 決策記錄

**訊息源補強**：
| 領域 | 新增來源 |
|------|----------|
| AI | OpenAI Blog, Google AI, Hugging Face |
| 國際 | Reuters World, BBC World, AP News |
| 知識 | Hacker News Best, Farnam Street, Wait But Why |

**Claude Code 獨立推播**：
- 從 GitHub 領域分離，確保版本更新不被篩掉
- 每日 09:00 推播，使用 AI 產生版本摘要

**個人化篩選（核心功能）**：
- 分析用戶 Heptabase 筆記庫 → 建立偏好畫像
- USER_PROFILE 包含：身份（心臟外科醫師）、專業領域、興趣偏好、篩選原則
- AI 摘要現在會說明「為什麼這篇對你有價值」而非通用描述
- 例：「適合製作醫學筆記、手術流程圖」而非「這是個 Markdown 編輯器」

**Readwise Tag 策略**：
- 只標記推播文章（輕量化）
- 自動加入：#推播 + @領域（AI/國際/知識）

### 推播排程（最終版）
| 時間 | 領域 | 來源數 |
|------|------|--------|
| 05:30 | 🏥 醫學 | 1 (PubMed) |
| 06:00 | 🤖 AI | 13 (Blog + Reddit) |
| 07:00 | 🌍 國際 | 8 (媒體 + Reddit) |
| 08:00 | 💻 GitHub/開發 | 6 (Trending + Reddit) |
| 09:00 | ⚡ Claude Code | 1 (Releases) |
| 12:00 | 📚 知識 | 6 (中英文) |
| 20:00 | 📖 Readwise | 動態 |

### 產出/修改文件
- `scripts/domain_digest.py` - USER_PROFILE、訊息源補強、Claude Code 領域
- `scripts/daily_digest.py` - 領域 Tag 自動標記
- `.github/workflows/daily-digest.yml` - Claude Code 排程

### 已完成
- [x] 補強訊息源
- [x] Claude Code 獨立推播
- [x] 個人化 AI 篩選
- [x] Readwise 領域 Tag
- [x] 全領域測試推播

### 未來進化方向（TODO）
- [ ] **動態偏好學習**：根據點擊/閱讀行為自動調整 USER_PROFILE
- [ ] **從 Readwise 標籤學習**：分析 `#必讀` 文章特徵，優化篩選
- [ ] **Heptabase 整合**：讀取最新卡片主題，動態更新興趣領域
- [ ] **Agentic Search**：Telegram Bot 支援提問「今天有什麼 Claude 更新？」
- [ ] **向量推薦**：訓練個人化 Embedding 模型（長期）
- [ ] 建立 HEPTABASE-TEMPLATES.md（輸出框架）

---

## Session: 2026-01-12 下午 - Telegram Bot 收集功能設計

### 變更摘要
- 討論並設計 Telegram Bot 收集功能（Quick Capture）
- 更新 PRD v0.2，新增功能 8

### 討論過程

**起點**：用戶提出想法 — Forward TG 頻道文章到 Readwise/Reader

**決策 1：納入現有專案 vs 新專案？**
- 結論：納入現有專案（目標一致、技術共用、避免碎片化）

**決策 2：雙向化現有 Bot vs 獨立收集 Bot？**
- 結論：先雙向化現有 Bot（用戶體驗優先、功能簡單）

**決策 3：存 Readwise vs Reader？**
- 結論：統一存 Reader
- 理由：用戶不常用 Daily Review，且 Reader document 模型更適合筆記

**決策 4：三種案例的處理方式**

| 案例 | 內容 | 處理 |
|------|------|------|
| 1. Forward 純文字 | 別人的觀點 | AI 生成標題，來源標記頻道名稱 |
| 2. Forward 有連結 | 文章連結 | 提取 URL，Reader 抓全文 |
| 3. 自己打的純文字 | 自己的想法 | AI 生成標題，來源標記「我的筆記」 |

**決策 5：標題處理**
- 使用 AI 自動生成有意義的標題（而非固定格式）

**決策 6：來源標記格式**
- Forward：`[頻道名稱] 日期`
- 自己打：`[我的筆記] 日期時間`

**決策 7：是否區分隨手記 vs 值得整理？**
- 結論：不區分，全部先進 Reader
- 理由：減少摩擦、符合「允許略過」原則、讓未來的自己決定

### 設計原則確認
- **低摩擦**：發訊息就完成，不需要額外指令
- **統一入口**：全部進 Reader，用現有流程處理
- **保留來源**：Forward 內容保留頻道名稱

### 產出文件
- `.claude/docs/PRD.md` - 更新至 v0.2，新增功能 8

### 待辦事項
- [x] `/pm` 規劃 Quick Capture 功能的實作計畫
- [ ] 確認 Reader API 支援存 HTML 內容（純文字筆記）
- [ ] 設計 Telegram Bot 接收訊息的程式邏輯
- [ ] 測試 Forward 訊息時取得頻道名稱
- [ ] 建立 HEPTABASE-TEMPLATES.md

---

## Session: 2026-01-12 下午續 - Quick Capture 實作規劃

### 變更摘要
- 完成 Quick Capture 功能的詳細實作計畫
- 更新 IMPLEMENTATION-PLAN.md 新增 Phase 2.5

### 規劃內容

**Phase 2.5: Quick Capture 功能**

分為 6 個子階段：

| 階段 | 內容 | 產出 |
|------|------|------|
| 2.5.1 | 技術驗證 | Reader save API / TG 接收測試 |
| 2.5.2 | Reader Client 擴展 | save_url(), save_note() |
| 2.5.3 | Telegram Bot 擴展 | 訊息接收 + 解析邏輯 |
| 2.5.4 | AI 輔助功能 | 標題生成 + 領域判斷 |
| 2.5.5 | 整合與測試 | quick_capture.py |
| 2.5.6 | 部署 | Polling / Webhook |

### 技術決策

**Telegram Bot 接收方式**：
- 建議先用 Polling 模式開發測試
- 之後可轉 Webhook 部署到雲端

**程式架構**：
- 擴展現有 `reader_client.py` 和 `telegram_bot.py`
- 新增 `quick_capture.py` 作為主程式
- 新增 `message_parser.py` 處理訊息解析

### 產出文件
- `.claude/docs/IMPLEMENTATION-PLAN.md` - 新增 Phase 2.5

### 下一步
1. 技術驗證：測試 Reader API save 功能
2. 技術驗證：測試 Telegram Bot 接收 Forward 訊息
3. 開始實作 2.5.2 Reader Client 擴展

---

## Session: 2026-01-12 凌晨 - Quick Capture 功能完成

### 變更摘要
- 完成技術驗證（Reader Save API + Telegram 接收）
- 完成 Quick Capture 功能實作
- 整合測試成功

### 技術驗證結果

**Reader Save API**：
- `save_url()` ✅ 可存入連結
- `save_note()` ✅ 可存入 HTML 內容
- Tags 參數 ✅ 正常運作
- Notes 參數 ✅ 可添加用戶評論

**Telegram Bot 接收**：
- Polling 模式 ✅ 正常運作
- Forward 偵測 ✅ `is_forward` 判斷正確
- 頻道名稱 ✅ `forward_from_chat.title` 可獲取
- URL 提取 ✅ 正規表達式提取成功

### 實作內容

| 檔案 | 變更 |
|------|------|
| `scripts/reader_client.py` | 新增 `save_url()`, `save_note()` |
| `scripts/message_parser.py` | 新建，訊息解析模組 |
| `scripts/ai_filter.py` | 新增 `generate_title()`, `detect_domain()`, `process_capture_content()` |
| `scripts/quick_capture.py` | 新建，主程式 |
| `scripts/test_reader_save.py` | 新建，API 測試腳本 |
| `scripts/test_telegram_receive_v3.py` | 新建，接收測試腳本 |

### 測試結果

| 案例 | 類型 | AI 標題 | 領域 | 狀態 |
|------|------|---------|------|------|
| Forward 純文字 | forward_text | AI编程助手冲击下... | AI | ✅ |
| Forward 純文字 | forward_text | TailwindCSS付费产品困境... | AI | ✅ |
| 自己打純文字 | text_only | TG 筆記 | 其他 | ✅ |

### 使用方式
```bash
# 持續運行 Bot
python scripts/quick_capture.py

# 測試模式
python scripts/quick_capture.py --test
```

### 待辦事項
- [x] 部署方案：選擇 Polling 持續運行 或 Webhook
- [ ] 建立 HEPTABASE-TEMPLATES.md
- [ ] 觀察使用情況，調整 AI 標題生成品質

---

## Session: 2026-01-12 凌晨續 - Zeabur 部署完成

### 變更摘要
- 完成 Zeabur 部署配置
- Quick Capture Bot 正式上線

### 部署過程

1. **建立 Webhook 版本**
   - 新增 `app.py` 作為入口
   - 使用 Flask + Gunicorn

2. **Zeabur 配置**
   - `Procfile` - 啟動命令
   - `zeabur.json` - Python 3.11 配置

3. **除錯**
   - 修復模組導入路徑問題
   - 修復 HTTPS webhook URL 問題

### 部署結果

| 項目 | 狀態 |
|------|------|
| 服務 URL | https://readwise-bot.zeabur.app |
| Webhook | https://readwise-bot.zeabur.app/webhook |
| 狀態 | ✅ 運行中 |

### 環境變數（Zeabur）
- `READWISE_TOKEN`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `ANTHROPIC_API_KEY`

### 最終架構

```
GitHub Actions（定時推播）
├── 06:00 AI 領域
├── 07:00 國際領域
├── 08:00 GitHub
├── 09:00 Claude Code
├── 12:00 知識領域
└── 20:00 Readwise 精選

Zeabur（Quick Capture）
└── 24/7 監聽 Telegram
    ├── Forward 頻道文章 → Reader
    ├── 貼連結 → Reader
    └── 純文字 → AI 標題 → Reader
```

### 產出檔案
- `app.py` - Webhook 入口
- `Procfile` - 部署配置
- `zeabur.json` - Zeabur 配置
- `scripts/__init__.py` - 模組初始化

### 待辦事項
- [ ] 建立 HEPTABASE-TEMPLATES.md
- [ ] 觀察 Quick Capture 使用情況
- [ ] 根據使用回饋調整 AI 標題品質

---

## Session: 2026-01-12 下午 - GitHub Actions 推播問題修復

### 變更摘要
- 診斷並修復 GitHub Actions 自動推播失敗問題
- 增加 Telegram API 錯誤日誌輸出

### 問題診斷過程

**症狀**：早上排程的自動推播沒有收到訊息，但 GitHub Actions 顯示 Status: Success

**診斷步驟**：
1. 檢查 workflow 配置 → 正常
2. 本地測試 → 正常運作
3. 檢查 GitHub Actions 詳細日誌 → 發現 `✗ 推播失敗`
4. 增加錯誤日誌輸出 → 發現 `Bad Request: chat not found`

**根本原因**：
- GitHub Secrets 中的 `TELEGRAM_CHAT_ID` 設定有誤（可能有空格或格式問題）

### 解決方案
1. 修改 `scripts/domain_digest.py`，增加 Telegram API 錯誤詳情輸出
2. 用戶重新設定 GitHub Secrets 中的 `TELEGRAM_CHAT_ID`
3. 手動觸發測試，確認推播成功且 AI 摘要正常顯示

### 產出/修改文件
- `scripts/domain_digest.py` - 增加錯誤日誌

### 驗證結果
- AI 領域推播：✅ 成功
- 摘要顯示（💡）：✅ 正常
- 自動排程：待明早驗證

### 待辦事項
- [ ] 觀察明天早上自動排程是否正常（06:00 AI、07:00 國際、08:00 GitHub）
- [ ] 建立 HEPTABASE-TEMPLATES.md
- [ ] 觀察 Quick Capture 使用情況

---

<!-- 新的 session 記錄請加在這裡 -->
