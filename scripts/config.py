"""
配置管理模組
"""
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# Readwise Reader API
READWISE_TOKEN = os.getenv("READWISE_TOKEN")
READWISE_BASE_URL = "https://readwise.io/api/v3"

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Claude API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Settings
DAILY_PUSH_TIME = os.getenv("DAILY_PUSH_TIME", "06:00")
LANGUAGE = os.getenv("LANGUAGE", "zh-TW")

# 領域分類
DOMAINS = {
    "醫學": ["醫學", "ECMO", "VAD", "心臟", "cardiac", "surgery", "NEJM", "Lancet", "LITFL", "EMCrit", "PubMed"],
    "AI": ["AI", "Claude", "GPT", "LLM", "機器學習", "deep learning", "anthropic", "openai", "agent"],
    "國際": ["國際", "政治", "geopolitics", "china", "taiwan", "war", "經濟", "貿易"],
    "投資": ["投資", "理財", "ETF", "股票", "基金", "資產配置", "財務自由", "FIRE", "investing", "portfolio"],
    "系統效率": ["生產力", "效率", "workflow", "automation", "時間管理", "深度工作", "productivity", "creator"],
    "知識": ["筆記", "PKM", "Obsidian", "Heptabase", "Notion", "知識管理", "學習"],
    "生活": ["健康", "運動", "睡眠", "飲食"]
}

# 用戶關注領域（用於 AI 篩選）
USER_INTERESTS = """
用戶關注領域（依優先序）：

1. 醫學（核心專業）：
   - 心臟外科、ECMO、VAD、葉克膜
   - 臨床研究、手術技術

2. 投資理財（財富建設）：
   - 長期投資策略、ETF、指數投資
   - 資產配置、複利思維
   - 財務獨立、被動收入

3. 系統效率（個人品牌基礎）：
   - 生產力系統、工作流優化
   - 時間管理、深度工作
   - 內容創作方法論

4. AI（效率工具）：
   - Claude Code CLI、AI Agent 開發
   - LLM 實際應用、AI 工作流
   - 醫療 AI 應用

5. 國際情勢（世界觀）：
   - 地緣政治、台海情勢
   - 全球經濟趨勢

降低優先：
- 泛 PKM / 筆記方法論（系統已成熟）
- 純技術新聞（非直接相關）
- 工具評測文（工具太多反而分心）
"""

def validate_config():
    """驗證必要的配置是否存在"""
    missing = []
    if not READWISE_TOKEN:
        missing.append("READWISE_TOKEN")
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_CHAT_ID:
        missing.append("TELEGRAM_CHAT_ID")
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")

    if missing:
        raise ValueError(f"Missing required config: {', '.join(missing)}")

    return True
