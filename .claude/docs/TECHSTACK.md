# 技術棧 (Tech Stack)

> 由 `/concept` 維護

---

## 總覽

這個專案是「方法論 + 工具配置 + 輕量自動化」的混合方案：
- **核心**：設計良好的工作流程與資訊架構
- **工具**：整合現有工具（Readwise/Reader、Heptabase）
- **自動化**：Telegram Bot + 可選的 n8n/Python pipeline

不需要建立全新的應用程式，而是透過配置和腳本串接現有服務。

---

## 核心工具（既有）

### Readwise / Reader
- **用途**：稍後閱讀、高亮標記、RSS 訂閱
- **整合方式**：Tag 系統 + Filter + 狀態管理
- **API**：支援 Readwise API，可用於自動化

### Heptabase
- **用途**：知識整理、視覺化思考、長期記憶
- **整合方式**：卡片模板、白板結構設計
- **特點**：適合處理「想法演變」和「觀點衝突」

---

## 推播與自動化

### Telegram Bot
- **用途**：每日資訊摘要推送、雙向互動
- **技術選項**：
  - Python + python-telegram-bot（推薦）
  - Node.js + telegraf
  - n8n workflow（低程式碼）
- **決定**：使用 Python，配合 Reader API 和 Claude API

### Readwise Reader API
- **文件**：https://readwise.io/reader_api
- **端點**：
  - `GET /api/v3/list/` - 列出文章（支援過濾）
  - `PATCH /api/v3/update/{id}/` - 更新文章（Tag）
  - `GET /api/v3/tags/` - 列出 Tag
- **速率限制**：每分鐘 20 次請求
- **Python 套件**：`readwise-api`（已安裝）

### 自動化 Pipeline（可選）

| 工具 | 優點 | 缺點 | 建議使用時機 |
|------|------|------|-------------|
| n8n | 視覺化、易修改、自架可控 | 需要 host | 複雜多步驟流程 |
| Python Script | 完全可控、靈活 | 需要維護 | 需要 AI 處理時 |
| Zapier/Make | 簡單、現成 | 有限制、付費 | 快速驗證原型 |

---

## AI 工具

### Claude (API / Claude Code)
- **用途**：內容摘要、觀點分析、衝突識別
- **使用原則**：輔助而非取代判斷
- **整合方式**：
  - 手動對話（當前主要方式）
  - API 呼叫（自動化 pipeline 中）
  - Claude Code CLI（專案管理、文件產出）

### 其他 AI 工具考慮
- NotebookLM：對話式二次閱讀
- Perplexity / Exa：主題深掘搜尋

---

## 資訊源類型

| 類型 | 工具/平台 | 整合方式 |
|------|----------|----------|
| RSS | Reader 內建 | 直接訂閱 |
| Newsletter | Reader / Email | 轉發或直接整合 |
| 社群 / Twitter | 手動或 API | 精選帳號轉 RSS |
| Telegram 頻道 | RSShub / 手動 | 重點頻道 |
| Podcast | Reader / 專用 App | 選擇性處理 |

---

## 部署環境

### 必須
- 無（純工具配置 + 文件產出）

### 如果啟用 Telegram Bot
- **選項 A**：本地 Python 腳本（簡單但需開機）
- **選項 B**：Cloud Function（AWS Lambda / GCP Cloud Run）
- **選項 C**：n8n 自架（需 VPS / Docker）
- **選項 D**：使用 Railway / Fly.io 等 PaaS

### 如果啟用 n8n
- Docker self-host（推薦）
- n8n Cloud（付費但省事）

---

## 選擇原因

| 決策 | 選擇 | 原因 |
|------|------|------|
| 稍後閱讀 | Readwise/Reader | 用戶已在使用，功能完整 |
| 知識庫 | Heptabase | 用戶已在使用，適合視覺化思考 |
| 推播 | Telegram Bot | 用戶指定，輕量且靈活 |
| AI 整合 | Claude 為主 | 品質好、用戶熟悉 Claude Code |
| 自動化 | 待定 | MVP 先手動，驗證後再自動化 |

---

## MVP 技術範圍

**Phase 1（純方法論）**：
- 資訊源架構設計文件
- 處理流程設計文件
- Readwise/Reader 配置指南
- Heptabase 使用指南

**Phase 2（加入 Telegram）**：
- Telegram Bot 基礎版
- 每日推播功能

**Phase 3（進階自動化）**：
- AI 摘要 pipeline
- 自動分類與優先級排序

---

## 變更記錄

| 日期 | 變更內容 |
|------|----------|
| 2026-01-11 | 初版建立 |
