# Readwise Bot FOMO 優化分析報告

> 作者: Owl | 日期: 2026-02-06 | Bead: owl-002

## 🎯 分析目標

根據 Wilson 四大人生目標，分析現有資訊源配置，找出：
1. 與目標對應的覆蓋情況
2. 過度飽和的區域（造成 FOMO）
3. 缺失的重要領域

---

## 📊 Wilson 四大目標 vs 現有配置

| 目標 | 現有覆蓋 | 狀態 | 問題 |
|------|----------|------|------|
| **醫學** | PubMed (ECMO/VAD/Cardiac) | ✅ 良好 | - |
| **生活** | 僅關鍵字「理財、健康」 | ⚠️ 不足 | 無專屬 feed，被動覆蓋 |
| **財務** | 無專屬領域 | ❌ 缺失 | 完全沒有投資/理財 feed |
| **內容創作** | 無 | ❌ 缺失 | 完全沒有 Creator Economy 相關 |

---

## 🔥 過度飽和區域（FOMO 元兇）

### 知識/生產力 (knowledge) - 9 個 sources

**問題**：這是 FOMO 的主要來源。Wilson 已經有成熟的知識系統，不需要每天接收 PKM/筆記方法論的資訊。

**現有 feeds：**
| Feed | 更新頻率 | 建議 |
|------|----------|------|
| Hacker News Best | 高 | ⭐ 保留（綜合價值高） |
| 電腦玩物 | 高 | 🗑️ 移除（內容偏工具介紹） |
| 少数派 | 高 | ⚠️ 降級（部分有價值） |
| 閱讀前哨站 | 中 | ⭐ 保留（書評有價值） |
| Ness Labs | 中 | 🗑️ 移除（PKM 過飽和） |
| Farnam Street | 中 | ⭐ 保留（心智模型） |
| Paul Graham | 低 | ⭐ 保留（經典） |
| Derek Sivers | 低 | ⭐ 保留（經典） |
| Wait But Why | 低 | 🗑️ 移除（更新太少） |

**建議**：從 9 → 5 個 feeds

### AI - 13 個 sources

**問題**：數量龐大，且 Wilson 主要關注 Claude Code CLI，不需要追蹤所有 AI 動態。

**精簡建議：**
| 類別 | 現有 | 建議保留 |
|------|------|----------|
| 核心 Blog | 6 | 3 (Simon Willison, Anthropic, AI Snake Oil) |
| Newsletter | 3 | 1 (Latent Space) |
| Agent 開發 | 3 | 1 (LangChain) |
| Reddit | 1 | 1 (r/ClaudeAI) |

**建議**：從 13 → 6 個 feeds

---

## ❌ 缺失領域

### 1. 財務/投資

Wilson 目標：10 年內從財富階梯 3 達到階梯 6

**建議新增的 feeds：**
| 來源 | 說明 | 頻率 |
|------|------|------|
| Morning Brew | 每日商業摘要 | 高 |
| The Hustle | 商業/創業趨勢 | 高 |
| Finimize | 投資理財簡報 | 高 |
| 財報狗 | 台股投資分析 | 中 |
| Mr. Money Mustache | FIRE 生活方式 | 低 |
| 投資客日誌 | 台灣投資觀點 | 中 |

### 2. 內容創作 / Creator Economy

Wilson 經營：Instagram @momobear_doctor + wilsonchao.com

**建議新增的 feeds：**
| 來源 | 說明 | 頻率 |
|------|------|------|
| The Creator Economy | Creator 商業模式 | 中 |
| Growth.Design | 設計思維案例 | 低 |
| Ali Abdaal Newsletter | 醫師轉 Creator 的典範 | 中 |
| Chenyi 的自媒體經營學 | 中文 Creator 觀點 | 中 |
| 電商人妻 | 社群經營 | 中 |

---

## 🔄 建議的領域重組

### 現有結構（6 domains）
```
medical, ai, international, github, knowledge, claude-code
```

### 建議新結構（7 domains）
```
medical      → 維持，核心不動
ai           → 精簡到 6 feeds
international → 維持
dev          → 合併 github + claude-code
knowledge    → 精簡到 5 feeds
finance      → 新增！
creator      → 新增！
```

---

## 📝 USER_INTERESTS 建議更新

```python
USER_INTERESTS = """
用戶關注領域（依優先序）：

1. 醫學（核心專業）：
   - 心臟外科、ECMO、VAD、葉克膜
   - 臨床研究、手術技術

2. 財務（財富建設）：
   - 長期投資策略、ETF、指數投資
   - 台股、美股基本面分析
   - FIRE 理財、被動收入

3. 內容創作（個人品牌）：
   - Creator Economy、自媒體經營
   - 醫療科普內容策略
   - Instagram / 部落格經營

4. AI（效率工具）：
   - Claude Code CLI、AI Agent 開發
   - 醫療 AI 應用
   - 生產力工具整合

5. 國際情勢（世界觀）：
   - 地緣政治、台海情勢
   - 全球經濟趨勢

不關注 / 降低優先：
- 泛 PKM / 筆記方法論（系統已成熟）
- 純技術新聞（非直接相關）
- 生產力工具評測（工具太多反而分心）
"""
```

---

## ⚡ 執行計畫

| 階段 | 任務 | Bead |
|------|------|------|
| 1 | 本分析報告 | owl-002 task 1 ✅ |
| 2 | 補充財務/投資 feeds | owl-002 task 2 |
| 3 | 補充內容創作 feeds | owl-002 task 3 |
| 4 | 精簡 knowledge feeds | owl-002 task 4 |
| 5 | 更新 config.py USER_INTERESTS | owl-002 task 5 |
| 6 | 設定資訊源分層 | owl-002 task 6 |

---

## 🤔 需要 Wilson 確認

1. **財務領域優先級**：投資知識 vs 省錢技巧 vs 創業/副業？
2. **內容創作重點**：醫療科普 vs 泛生活 vs 系統/效率類？
3. **精簡幅度**：激進（-50%）還是保守（-30%）？

---

*分析完成：2026-02-06 12:15 (Taiwan)*
