# 實作計畫 (Implementation Plan)

> 由 `/pm` 維護

---

## 專案資訊

- **專案名稱**: 個人訊息流強化系統
- **PRD 版本**: v0.1
- **計畫建立日期**: 2026-01-11
- **最後更新**: 2026-01-11

### 專案特性

這是「方法論 + 工具配置 + 輕量自動化」的混合專案：
- **不是**純程式開發專案
- **主要產出**：流程文件、配置指南、模板設計
- **次要產出**：Telegram Bot、自動化腳本

---

## 階段規劃

### Phase 1: 基礎建立（方法論 + 手動執行）

> 目標：設計完整的資訊處理系統，手動執行 2 週驗證可行性

#### 1.1 資訊源整理
- [ ] 精簡現有 RSS 訂閱（~70 → 分層管理）
- [ ] 補強 AI/Claude Code 來源（從 SOURCES.md 選擇）
- [ ] 補強國際情勢來源（從 SOURCES.md 選擇）
- [ ] 輸出：更新後的 SOURCES.md（含分層標記）

#### 1.2 每日流程設計
- [ ] 設計 30-60 分鐘標準流程 SOP
- [ ] 設計「快速瀏覽」vs「深度閱讀」決策標準
- [ ] 設計忙碌日/空閒日的彈性版本
- [ ] 輸出：WORKFLOW.md 流程指南

#### 1.3 工具配置
- [ ] 設計 Readwise Reader tag 系統
- [ ] 設計「待處理→已處理→已輸出」狀態流
- [ ] 輸出：READER-SETUP.md 配置指南

#### 1.4 輸出框架設計
- [ ] 設計 Heptabase 洞見卡片模板
- [ ] 設計衝突卡片模板
- [ ] 設計演變追蹤機制
- [ ] 輸出：HEPTABASE-TEMPLATES.md

#### 1.5 手動驗證期
- [ ] 按照設計流程執行 2 週
- [ ] 記錄問題與調整
- [ ] 驗證時間預算是否可行
- [ ] 輸出：驗證報告（記錄在 SESSION-LOG）

---

### Phase 2: 推播自動化

> 目標：建立 Telegram Bot，實現每日精選推播

#### 2.1 Telegram Bot 基礎建立
- [ ] 創建 Telegram Bot（@BotFather）
- [ ] 選擇技術方案（Python/n8n/Pipedream）
- [ ] 設定基礎推播功能
- [ ] 輸出：TELEGRAM-BOT.md 技術文件

#### 2.2 RSS 篩選整合
- [ ] 整合 Readwise API 獲取新內容
- [ ] 設計 AI 篩選邏輯（Claude API）
- [ ] 設計摘要生成 prompt
- [ ] 測試推播格式

#### 2.3 現有流程遷移
- [ ] 將 PubMed 論文推播從 LINE 遷移到 Telegram
- [ ] 整合現有 Pipedream 流程
- [ ] 統一推播管道

#### 2.4 互動功能
- [ ] 實現「稍後讀」標記
- [ ] 實現「略過」回饋
- [ ] 設計回饋收集機制

---

### Phase 2.5: Quick Capture 功能

> 目標：將 Telegram Bot 雙向化，實現快速捕捉到 Reader

#### 技術背景

**現有架構**：
- `telegram_bot.py` - 只有推播功能（sendMessage）
- `reader_client.py` - 有 list/update，缺少 save 功能
- Bot 目前是單向的，無法接收用戶訊息

**需要擴展**：
- Telegram Bot 需要接收訊息（webhook 或 polling）
- Reader API 需要 save 功能（存 URL 和 HTML 內容）

---

#### 2.5.1 技術驗證

- [ ] **Reader API Save 測試**
  - 測試 `POST /save` 存入 URL
  - 測試 `POST /save` 存入 HTML 內容（純文字筆記）
  - 確認 tags 參數格式
  - 確認 note/annotation 如何添加

- [ ] **Telegram Bot 接收測試**
  - 選擇接收方式：Webhook vs Polling
  - 測試接收一般訊息
  - 測試接收 Forward 訊息，確認可取得 `forward_from_chat.title`
  - 測試提取訊息中的 URL

---

#### 2.5.2 Reader Client 擴展

- [ ] **新增 save_url() 函數**
  ```python
  def save_url(url: str, tags: List[str] = None, notes: str = None) -> bool
  ```
  - 存入 URL，Reader 自動抓全文
  - 支援 tags 和 notes 參數

- [ ] **新增 save_note() 函數**
  ```python
  def save_note(
      content: str,
      title: str,
      source_name: str = None,
      tags: List[str] = None
  ) -> bool
  ```
  - 存入純文字內容作為筆記
  - title：AI 生成或手動指定
  - source_name：來源標記（頻道名稱 / 我的筆記）

---

#### 2.5.3 Telegram Bot 擴展

- [ ] **建立訊息接收服務**
  - 選項 A：Polling 模式（簡單，適合測試）
  - 選項 B：Webhook 模式（適合部署）
  - 建議：先用 Polling 開發測試，之後轉 Webhook

- [ ] **訊息解析邏輯**
  ```python
  def parse_message(message):
      # 1. 判斷是否為 Forward
      is_forward = message.get("forward_from_chat") is not None
      channel_name = message.get("forward_from_chat", {}).get("title")

      # 2. 提取文字內容
      text = message.get("text", "")

      # 3. 提取 URL
      urls = extract_urls(text)

      # 4. 判斷用戶評論（Forward 時，用戶額外加的文字）
      user_comment = message.get("caption", "")

      return {
          "is_forward": is_forward,
          "channel_name": channel_name,
          "text": text,
          "urls": urls,
          "user_comment": user_comment
      }
  ```

- [ ] **處理邏輯分流**
  ```
  收到訊息
      ├─ 有 URL → save_url() + 回覆「✅ 已存入」
      │     └─ 有評論 → 加入 notes
      │
      └─ 純文字 → AI 生成標題 → save_note()
            ├─ Forward → 來源標記頻道名稱
            └─ 自己打 → 來源標記「我的筆記」
  ```

---

#### 2.5.4 AI 輔助功能

- [ ] **標題生成 Prompt**
  ```
  根據以下內容生成一個簡潔的標題（10-30 字）：
  - 如果是觀點/分析，標題應反映核心論點
  - 如果是隨手記，標題應反映主題
  - 使用繁體中文

  內容：{text}
  ```

- [ ] **領域判斷 Prompt**
  ```
  判斷以下內容屬於哪個領域：
  - AI、國際、醫學、知識、生產力、生活
  - 回覆領域名稱即可

  內容：{text}
  ```

- [ ] **整合到現有 ai_filter.py 或新建模組**

---

#### 2.5.5 整合與測試

- [ ] **建立 quick_capture.py 主程式**
  - 整合所有模組
  - 啟動 Telegram Bot 監聽

- [ ] **測試三種案例**
  | 案例 | 輸入 | 預期結果 |
  |------|------|----------|
  | Forward + URL | 轉發 Newsletter | 存入 Reader Article |
  | Forward + 純文字 | 轉發觀點分析 | 存入 Reader Note，來源標記頻道 |
  | 自己打的 | 電影觀後感 | 存入 Reader Note，AI 標題 |

- [ ] **回覆訊息格式設計**
  ```
  ✅ 已存入 Reader
  📝 標題：{title}
  📂 領域：{domain}
  🏷️ 來源：{source}
  ```

---

#### 2.5.6 部署

- [ ] **本地測試完成後**
  - 選項 A：本地持續運行（polling）
  - 選項 B：部署到雲端（Railway / Fly.io / VPS）
  - 選項 C：整合到現有 GitHub Actions（需要 webhook）

- [ ] **更新 .env 和 requirements.txt**

---

#### 預估產出檔案

| 檔案 | 說明 |
|------|------|
| `scripts/reader_client.py` | 擴展 save 功能 |
| `scripts/telegram_bot.py` | 擴展接收功能 |
| `scripts/quick_capture.py` | 主程式 |
| `scripts/message_parser.py` | 訊息解析邏輯 |
| `.claude/docs/QUICK-CAPTURE.md` | 技術文件 |

---

### Phase 3: 進階優化

> 目標：根據使用回饋優化系統

#### 3.1 AI 篩選調優
- [ ] 分析推播 vs 實際閱讀的吻合度
- [ ] 調整篩選權重與 prompt
- [ ] 逐步過渡到「推播為主」模式

#### 3.2 自動化報告
- [ ] 設計週報格式
- [ ] 實現自動週報生成
- [ ] 整合閱讀統計

#### 3.3 系統穩定化
- [ ] 錯誤處理與通知
- [ ] 備份機制
- [ ] 維護 SOP

---

## Subagent 分配

| Subagent | 職責 | 負責任務 | 狀態 |
|----------|------|----------|------|
| `/source-architect` | 資訊源架構設計 | 1.1 | 待建立 |
| `/workflow-designer` | 流程設計 | 1.2 | 待建立 |
| `/tool-integrator` | 工具配置 | 1.3, 1.4 | 待建立 |
| `/telegram-builder` | Bot 開發 | 2.1, 2.2, 2.3, 2.4 | 待建立 |
| `/domain-strategist` | 領域策略 | 按需啟用 | 待建立 |

### 建立優先級

1. **P0（立即建立）**：
   - `/workflow-designer` - Phase 1 核心

2. **P1（Phase 1 中期）**：
   - `/tool-integrator` - 工具配置

3. **P2（Phase 2 開始時）**：
   - `/telegram-builder` - Bot 開發

4. **P3（按需）**：
   - `/source-architect` - 資訊源已在 SOURCES.md，可由 PM 直接處理
   - `/domain-strategist` - 可延後

---

## 進度追蹤

| 階段 | 狀態 | 完成度 | 預計產出 |
|------|------|--------|----------|
| Phase 1.1 資訊源整理 | ✅ 完成 | 100% | SOURCES.md 更新 |
| Phase 1.2 流程設計 | ✅ 完成 | 100% | WORKFLOW.md |
| Phase 1.3 工具配置 | ✅ 完成 | 100% | READER-SETUP.md |
| Phase 1.4 輸出框架 | 未開始 | 0% | HEPTABASE-TEMPLATES.md |
| Phase 1.5 手動驗證 | 未開始 | 0% | 驗證報告 |
| Phase 2 推播自動化 | ✅ 完成 | 100% | Telegram Bot + GitHub Actions |
| **Phase 2.5 Quick Capture** | **待開始** | 0% | quick_capture.py |
| Phase 3 進階優化 | 未開始 | 0% | 優化報告 |

---

## 今日可執行任務

根據優先級，建議從以下開始：

### 選項 A：從流程設計開始
1. 建立 `/workflow-designer` subagent
2. 設計每日處理流程 SOP
3. 產出 WORKFLOW.md

### 選項 B：從資訊源整理開始
1. 根據 SOURCES.md，選擇要加入的 AI/國際情勢來源
2. 設計 Reader 分層 tag 系統
3. 更新 SOURCES.md

### 選項 C：從輸出框架開始
1. 設計 Heptabase 卡片模板
2. 先試用幾天，驗證可行性
3. 產出 HEPTABASE-TEMPLATES.md

---

## 風險與注意事項

| 風險 | 影響程度 | 對應策略 |
|------|----------|----------|
| 設計過度複雜，無法持續執行 | 高 | 先最小化，驗證後再擴展 |
| Readwise API 限制 | 中 | 先確認 API 能力再設計自動化 |
| AI 篩選品質不佳 | 中 | Phase 1 手動驗證，建立基準 |
| 時間預算超支 | 高 | 設計「忙碌日」最小版本 |

---

## 變更記錄

| 日期 | 變更內容 |
|------|----------|
| 2026-01-11 | 初版建立，規劃三階段實作 |
| 2026-01-12 | 新增 Phase 2.5 Quick Capture 功能規劃 |
