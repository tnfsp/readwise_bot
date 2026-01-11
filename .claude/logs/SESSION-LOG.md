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
- Chat ID: 8271188180
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

<!-- 新的 session 記錄請加在這裡 -->
