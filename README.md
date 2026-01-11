# Claude Code 專案模板

這是一個使用 Claude Code 進行開發的專案模板框架。透過 Subagent 架構，讓 AI 協助你從概念設計到專案完成。

## 快速開始

### 1. 複製此模板
將此資料夾複製到你的新專案目錄。

### 2. 啟動 Claude Code
```bash
cd your-project
claude
```

### 3. 開始設計專案
```
/concept
```
與 Concept 設計師討論你的專案概念、需求與技術選擇。

### 4. 規劃與執行
```
/pm
```
讓 Project Manager 建立實作計畫，並協調各個 subagent 完成任務。

## 架構說明

```
.claude/
├── commands/           # Subagent 指令
│   ├── concept.md      # 概念設計師 - 負責 PRD、技術棧設計
│   └── pm.md           # 專案經理 - 負責規劃、調度、追蹤
├── docs/               # 專案文件
│   ├── PRD.md          # 產品需求文件
│   ├── TECHSTACK.md    # 技術棧說明
│   └── IMPLEMENTATION-PLAN.md  # 實作計畫
└── logs/
    └── SESSION-LOG.md  # 工作記錄（每次 session 累積）

CLAUDE.md               # Claude Code 讀取的專案說明
README.md               # 本檔案（給人類讀取）
```

## 工作流程

```
1. /concept  →  討論專案概念，產出 PRD + TECHSTACK
        ↓
2. /pm       →  制定 IMPLEMENTATION-PLAN，建立需要的 subagent
        ↓
3. /xxx      →  PM 調動各 subagent 執行任務
        ↓
4. 更新 Log  →  記錄進度，方便接力開發
        ↓
5. Git Push  →  保存變更
```

## Subagent 說明

### /concept - 概念設計師
- 與你討論專案的目標、功能、用戶
- 撰寫與維護 PRD（產品需求文件）
- 決定技術棧，撰寫 TECHSTACK
- 設計專案需要的其他 subagent

### /pm - 專案經理
- 根據 PRD 撰寫實作計畫
- 動態建立新的 subagent（如 /coder, /tester）
- 調度 subagent 完成任務
- 追蹤進度，維護 log

### 動態 Subagent
PM 可根據專案需求建立其他 subagent，例如：
- `/coder` - 撰寫程式碼
- `/tester` - 撰寫測試
- `/reviewer` - Code review
- `/devops` - 部署相關

## Log 系統

每次使用 Claude Code 工作後，會在 `.claude/logs/SESSION-LOG.md` 記錄：
- **變更摘要**：完成了什麼
- **決策記錄**：做了什麼決定、為什麼
- **待辦事項**：下次要繼續的工作

這讓你可以隨時中斷，下次繼續接力開發。

## 自訂與擴展

### 新增 Subagent
在 `.claude/commands/` 建立新的 `.md` 檔案即可。

### 修改流程
編輯 `CLAUDE.md` 或各 subagent 的 `.md` 檔案來調整行為。

## License

MIT
