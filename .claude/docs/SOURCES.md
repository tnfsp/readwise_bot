# 資訊源架構 (Sources Architecture)

> 由 `/concept` 維護，記錄現有來源分析與推薦補充

---

## 總覽

### 六大關注領域
1. 知識/學習/筆記
2. 生產力/工作流
3. 醫學
4. AI（特別是 Claude Code CLI）
5. 國際情勢
6. 其他（科技、數位生活）

### 當前狀態

| 領域 | 狀態 | 數量 | 說明 |
|------|------|------|------|
| 知識/學習/筆記/生產力 | 過飽和 | ~50 | 需要分層但暫不處理 |
| 醫學 | 良好 | ~5 | NEJM、LITFL、EMCrit + Pipedream 論文推播 |
| AI/Claude Code | 不足 | ~2 | 只有 Simon Willison，需補強 |
| 國際情勢 | 空缺 | 0 | 完全沒有，需建立 |

---

## 現有來源清單

### 醫學（RSS + Pipedream）

| 來源 | 類型 | 品質評估 |
|------|------|----------|
| NEJM (New England Journal of Medicine) | RSS | 頂級，必讀 |
| LITFL (Life in the Fast Lane) | RSS | 急診醫學佳 |
| EMCrit Project | RSS | 重症醫學佳 |
| NEJS | RSS | NEJM 相關 |
| Karen醫生の日常 | Telegram | 日常醫學分享 |
| **Pipedream → LINE** | 自動化 | PubMed RSS：心臟外科/ECMO/VAD 論文，每次 15 篇 |

### 知識/學習/筆記/生產力（RSS，約 50 個）

**中文優質來源**：
- 閱讀前哨站、電腦玩物、少数派、产品沉思录
- Pin 起來！、PJ Wu、朱騏、Owen的博客
- 大人學、專案管理生活思維

**英文優質來源**：
- Stratechery、ribbonfarm、Collab Fund
- bookbear express、A Life of Productivity
- Tools for Thought Newsletter

**筆記工具專門**：
- Logseq Blog、Obsidian 鐵人賽、Know Your Knowledge

> 完整清單見 Reader OPML 匯出

### AI 相關（現有）

| 來源 | 類型 | 說明 |
|------|------|------|
| Simon Willison's Weblog | RSS | ✅ 極佳，AI 工具實測專家 |
| Learn Prompting | RSS | Prompt 教學 |
| Gold Penguin AI | RSS | AI 相關文章 |

### Telegram 頻道（現有）

**技術/數位生活**：
- Newlearnerの自留地、NewlearnerのIT社群
- 椒盐豆豉剪报、APPDO 数字生活指南
- 每日消费电子观察、codedump的电报频道
- Hexagram Daily、青鸟的频道、Alan的小纸箱
- 不求甚解

**其他**：
- 股癌 Gooaye（財經）
- hayami's blog（生活）
- Leslie和朋友们、小破不入渠、gledos

---

## AI / Claude Code（2026-01-14 更新）

### 已加入 ✅

| 來源 | 類型 | RSS/連結 | 推播時段 |
|------|------|----------|----------|
| Simon Willison's Weblog | Blog | simonwillison.net | 06:00 AI |
| Import AI | Newsletter | importai.substack.com | 06:00 AI |
| Latent Space | Newsletter | latent.space | 06:00 AI |
| Anthropic Blog | 官方 | anthropic.com/news | 06:00 AI |
| Ben's Bites | Newsletter | bensbites.beehiiv.com | 06:00 AI |
| OpenAI Blog | 官方 | openai.com/blog | 06:00 AI |
| Google AI Blog | 官方 | blog.google/technology/ai | 06:00 AI |
| Hugging Face Blog | 官方 | huggingface.co/blog | 06:00 AI |
| AI Snake Oil | Blog | aisnakeoil.com | 06:00 AI（批判性觀點）|
| r/ClaudeAI | Reddit | reddit.com/r/ClaudeAI | 06:00 AI |

### Agent 開發區塊（06:00 AI 內獨立區塊）

| 來源 | 類型 | 連結 | 說明 |
|------|------|------|------|
| LangChain Blog | Blog | blog.langchain.dev | Agent 框架動態 |
| LlamaIndex Blog | Blog | llamaindex.ai/blog | RAG + Agent |
| e2b.dev Blog | Blog | e2b.dev/blog | Code sandbox、Agent 執行環境 |

### 已移除

| 來源 | 原因 |
|------|------|
| r/LocalLLaMA | 本地 LLM 討論，與 Claude API 使用場景相關性低 |
| r/MachineLearning | 精簡 Reddit 來源 |
| r/ChatGPT | 精簡 Reddit 來源 |
| r/artificial | 精簡 Reddit 來源 |

### 待觀察

| 來源 | 類型 | 連結 | 狀態 |
|------|------|------|------|
| The Neuron | Newsletter | theneurondaily.com | [ ] 待評估 |
| @alexalbert__ | Twitter | Claude prompting 專家（需 RSS 橋接）| [ ] 待評估 |
| Interconnects (Nathan Lambert) | Newsletter | interconnects.ai | [ ] 待評估 |

---

## GitHub 專案（2026-01-11 新增）

### 已加入 ✅

| 來源 | 類型 | RSS 連結 | 推播時段 |
|------|------|----------|----------|
| GitHub Trending (Python) | 每日精選 | mshibanami.github.io/GitHubTrendingRSS | 08:00 GitHub |
| anthropics/claude-code Releases | Release | github.com/.../releases.atom | 08:00 GitHub |

---

## 國際情勢（2026-01-11 更新）

### 已加入 ✅

| 來源 | 類型 | 連結 | 推播時段 |
|------|------|------|----------|
| Foreign Affairs | 期刊 | foreignaffairs.com | 07:00 國際 |
| Foreign Policy | 雜誌 | foreignpolicy.com | 07:00 國際 |
| 敏迪選讀 | Newsletter | 台灣視角國際新聞 | 07:00 國際 |
| Project Syndicate | 評論 | project-syndicate.org | 07:00 國際 |

### 待觀察

| 來源 | 類型 | 連結 | 狀態 |
|------|------|------|------|
| 轉角國際 | 中文 | udn 旗下國際深度 | [ ] 待評估 |
| 報導者 - 國際 | 中文 | 獨立媒體國際專題 | [ ] 待評估 |
| The Wire China | 英文 | 中國議題深度 | [ ] 待評估 |

---

## 分層策略（未來實施）

當資訊源整理完成後，建議採用三層處理：

### 第一層：必讀（每日必看）
- 高信號來源，產出穩定且品質高
- 數量控制：每領域 1-3 個
- 處理方式：深度閱讀

### 第二層：值得看（有時間就看）
- 中等信號，偶有佳作
- 數量控制：每領域 3-5 個
- 處理方式：快速掃描標題，選擇性深入

### 第三層：探索性（週末批次處理）
- 低信號但可能有意外發現
- 定期評估是否升級或移除
- 處理方式：每週一次批次瀏覽

---

## 技術整合筆記

### Readwise Reader
- 主要 RSS 訂閱入口
- Tag 系統可用於分層標記
- 偶有同步問題（502 錯誤）

### Pipedream
- 用於醫學論文自動推播
- 可擴展用於其他自動化

### Telegram
- 作為推播接收端
- 部分資訊源本身就是 Telegram 頻道

---

## 變更記錄

| 日期 | 變更內容 |
|------|----------|
| 2026-01-11 | 初版建立，完成現有來源分析與推薦 |
