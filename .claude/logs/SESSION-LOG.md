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

<!-- 新的 session 記錄請加在這裡 -->
