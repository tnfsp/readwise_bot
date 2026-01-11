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
    "AI": ["AI", "Claude", "GPT", "LLM", "機器學習", "deep learning", "anthropic", "openai"],
    "國際": ["國際", "政治", "geopolitics", "china", "taiwan", "war", "經濟"],
    "知識": ["筆記", "PKM", "Obsidian", "Heptabase", "Notion", "知識管理", "學習"],
    "生產力": ["生產力", "效率", "workflow", "automation", "工具"],
    "生活": ["理財", "健康", "生活", "投資"]
}

# 用戶關注領域（用於 AI 篩選）
USER_INTERESTS = """
用戶關注領域：
1. 醫學：心臟外科、ECMO、VAD、葉克膜、臨床研究
2. AI：Claude Code CLI、LLM 應用、AI 工具
3. 國際情勢：地緣政治、國際關係
4. 知識管理：PKM、筆記方法、學習技巧
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
