"""
分領域推播系統

根據不同領域從 RSS 獲取內容並推播到 Telegram
支援的領域：醫學, AI, 國際, GitHub, 知識
"""
import sys
import argparse
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# 設定 stdout 編碼
sys.stdout.reconfigure(encoding='utf-8')

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    ANTHROPIC_API_KEY,
    validate_config
)

# 領域配置
DOMAIN_CONFIG = {
    "medical": {
        "name": "醫學",
        "emoji": "🏥",
        "feeds": [
            {"name": "PubMed (ECMO/VAD/Cardiac)", "url": "https://pubmed.ncbi.nlm.nih.gov/rss/search/1V_PRf-wigmmSOdeKS_0FLDNjB4gkI0R2Ppj3T0WTkRZDZugxK/?limit=15&utm_campaign=pubmed-2&fc=20250126040620"},
        ],
        "max_items": 10,
        "use_ai_filter": True,
        "default_hours": 48  # PubMed 更新較慢，使用 48 小時
    },
    "ai": {
        "name": "AI",
        "emoji": "🤖",
        "feeds": [
            # 核心 Blog（必讀）
            {"name": "Simon Willison", "url": "https://simonwillison.net/atom/everything/"},
            {"name": "Anthropic", "url": "https://www.anthropic.com/rss.xml"},
            {"name": "AI Snake Oil", "url": "https://www.aisnakeoil.com/feed"},
            # 公司官方（重要更新）
            {"name": "OpenAI", "url": "https://openai.com/blog/rss.xml"},
            {"name": "Google AI", "url": "https://blog.google/technology/ai/rss/"},
            # Newsletter（精選）
            {"name": "Latent Space", "url": "https://www.latent.space/feed"},
            {"name": "Import AI", "url": "https://importai.substack.com/feed"},
            # Agent 開發
            {"name": "LangChain Blog", "url": "https://blog.langchain.dev/rss/"},
            # Reddit
            {"name": "r/ClaudeAI", "url": "https://www.reddit.com/r/ClaudeAI/top/.rss?t=day"},
        ],
        "max_items": 8,
        "use_ai_filter": True
    },
    "international": {
        "name": "國際情勢",
        "emoji": "🌍",
        "feeds": [
            # 深度分析
            {"name": "Foreign Affairs", "url": "https://www.foreignaffairs.com/rss.xml"},
            {"name": "Foreign Policy", "url": "https://foreignpolicy.com/feed/"},
            {"name": "Project Syndicate", "url": "https://www.project-syndicate.org/rss"},
            # 即時新聞
            {"name": "Reuters World", "url": "https://www.rss.reuters.com/news/worldnews"},
            {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
            {"name": "AP News", "url": "https://apnews.com/world-news.rss"},
            # Reddit
            {"name": "r/geopolitics", "url": "https://www.reddit.com/r/geopolitics/top/.rss?t=day"},
            {"name": "r/worldnews", "url": "https://www.reddit.com/r/worldnews/top/.rss?t=day"},
        ],
        "max_items": 10,
        "use_ai_filter": True
    },
    "github": {
        "name": "GitHub/開發",
        "emoji": "💻",
        "feeds": [
            {"name": "GitHub Trending (Python)", "url": "https://mshibanami.github.io/GitHubTrendingRSS/daily/python.xml"},
            {"name": "GitHub Trending (All)", "url": "https://mshibanami.github.io/GitHubTrendingRSS/daily/all.xml"},
            {"name": "Claude Code Releases", "url": "https://github.com/anthropics/claude-code/releases.atom"},
            # Reddit
            {"name": "r/programming", "url": "https://www.reddit.com/r/programming/top/.rss?t=day"},
            {"name": "r/webdev", "url": "https://www.reddit.com/r/webdev/top/.rss?t=day"},
            {"name": "r/Python", "url": "https://www.reddit.com/r/Python/top/.rss?t=day"},
        ],
        "max_items": 10,
        "use_ai_filter": True
    },
    "knowledge": {
        "name": "知識/生產力",
        "emoji": "📚",
        "feeds": [
            # 高頻來源（每日更新）
            {"name": "Hacker News Best", "url": "https://hnrss.org/best"},
            {"name": "少数派", "url": "https://sspai.com/feed"},
            {"name": "閱讀前哨站", "url": "https://readingoutpost.com/feed/"},
            # 中頻來源（每週更新）
            {"name": "Farnam Street", "url": "https://fs.blog/feed/"},
            # 低頻高質量（數月一篇，但篇篇經典）
            {"name": "Paul Graham", "url": "http://www.aaronsw.com/2002/feeds/pgessays.rss", "max_articles": 2},
            {"name": "Derek Sivers", "url": "https://sive.rs/en.atom"},
        ],
        "max_items": 6,
        "use_ai_filter": True
    },
    "claude-code": {
        "name": "Claude Code 更新",
        "emoji": "⚡",
        "feeds": [
            {"name": "Claude Code Releases", "url": "https://github.com/anthropics/claude-code/releases.atom"},
        ],
        "max_items": 5,
        "use_ai_filter": True,  # 產生版本摘要
        "default_hours": 168  # 一週內的更新
    },
    "finance": {
        "name": "投資理財",
        "emoji": "💰",
        "feeds": [
            # 每日商業新聞
            {"name": "Morning Brew", "url": "https://www.morningbrew.com/daily/rss"},
            {"name": "Finimize", "url": "https://www.finimize.com/wp/feed/"},
            # 投資觀點
            {"name": "A Wealth of Common Sense", "url": "https://awealthofcommonsense.com/feed/"},
            {"name": "Of Dollars And Data", "url": "https://ofdollarsanddata.com/feed/"},
            {"name": "Collaborative Fund", "url": "https://collabfund.com/feed/"},
            # Reddit
            {"name": "r/investing", "url": "https://www.reddit.com/r/investing/top/.rss?t=day"},
            {"name": "r/Bogleheads", "url": "https://www.reddit.com/r/Bogleheads/top/.rss?t=day"},
        ],
        "max_items": 8,
        "use_ai_filter": True
    },
    "creator": {
        "name": "系統效率",
        "emoji": "🎯",
        "feeds": [
            # 系統思維 & 效率
            {"name": "Ali Abdaal", "url": "https://aliabdaal.com/feed/"},
            {"name": "Tiago Forte", "url": "https://fortelabs.com/feed/"},
            {"name": "Cal Newport", "url": "https://calnewport.com/feed/"},
            {"name": "James Clear", "url": "https://jamesclear.com/feed"},
            # 創作者經濟
            {"name": "The Publish Press", "url": "https://www.publishpress.com/feed/"},
            # Reddit
            {"name": "r/productivity", "url": "https://www.reddit.com/r/productivity/top/.rss?t=week"},
        ],
        "max_items": 6,
        "use_ai_filter": True
    }
}


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    retry=retry_if_exception_type(Exception),
    reraise=False  # RSS 失敗不中斷整個流程
)
def fetch_rss_feed(url: str, hours: int = 24, max_articles: int = None) -> List[Dict]:
    """
    從 RSS feed 獲取最近的文章（帶 retry）

    Args:
        url: RSS feed URL
        hours: 獲取過去幾小時的文章
        max_articles: 最多返回幾篇文章（用於無時間戳記的 feed）

    Returns:
        文章列表
    """
    try:
        feed = feedparser.parse(url)
        articles = []
        cutoff = datetime.now() - timedelta(hours=hours)

        for entry in feed.entries[:20]:  # 最多處理 20 篇
            # 解析發布時間
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    published = datetime(*entry.published_parsed[:6])
                except (TypeError, ValueError):
                    pass
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                try:
                    published = datetime(*entry.updated_parsed[:6])
                except (TypeError, ValueError):
                    pass

            # 如果無法解析時間，保留文章（假設是新的）
            # 如果有時間但太舊，則跳過
            if published and published < cutoff:
                continue

            articles.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", "")[:200] if entry.get("summary") else "",
                "published": published
            })

        # 如果設定了 max_articles，限制返回數量
        if max_articles:
            articles = articles[:max_articles]

        return articles
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return []


def fetch_domain_articles(domain: str, hours: int = 24) -> List[Dict]:
    """
    獲取特定領域的所有文章

    Args:
        domain: 領域名稱 (ai, international, github, knowledge)
        hours: 獲取過去幾小時的文章

    Returns:
        文章列表
    """
    config = DOMAIN_CONFIG.get(domain)
    if not config:
        print(f"Unknown domain: {domain}")
        return []

    all_articles = []

    for feed in config["feeds"]:
        print(f"  Fetching {feed['name']}...")
        max_articles = feed.get("max_articles")  # 取得自訂的最大文章數
        articles = fetch_rss_feed(feed["url"], hours, max_articles=max_articles)
        for article in articles:
            article["source"] = feed["name"]
        all_articles.extend(articles)
        print(f"    Found {len(articles)} articles")

    return all_articles


# 用戶偏好 Profile（根據閱讀歷史和筆記庫分析）
USER_PROFILE = """
## 用戶背景
- 身份：心臟外科醫師
- 專業領域：ECMO、VAD、瓣膜手術（Morrow technique、AVR）、術後重症照護

## 興趣偏好
- 醫學：心臟外科新技術、ECMO/VAD 管理、術後併發症處理、藥物使用（Vancomycin、Meropenem、Milrinone）
- AI/技術：Claude Code、LLM 應用、自動化工作流（n8n）、AI Agent
- 知識管理：Zettelkasten、Heptabase、第二大腦、筆記方法論
- 思考：喜歡深度分析和實用案例，偏好有洞見的內容而非純新聞

## 篩選原則
- 優先：有實際應用價值、技術深度、獨特觀點的文章
- 次要：產業趨勢、工具更新
- 避免：純粹的新聞速報、標題黨、重複內容
"""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, Exception)),
    reraise=True
)
def _call_claude_api(client, prompt: str) -> str:
    """呼叫 Claude API（帶 retry）"""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=800,  # 增加 token 數，確保有足夠空間生成摘要
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def ai_filter_articles(articles: List[Dict], domain: str, max_items: int) -> List[Dict]:
    """
    使用 AI 篩選文章並產生摘要（根據用戶偏好）
    帶 retry 機制，確保摘要不為空
    """
    if not articles:
        return []

    import anthropic
    import json

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # 準備文章列表（包含摘要以提供更多上下文）
    articles_text = []
    for i, article in enumerate(articles[:20]):
        summary = article.get('summary', '')[:100] if article.get('summary') else ''
        articles_text.append(f"{i+1}. [{article.get('source')}] {article.get('title')}\n   摘要: {summary}")

    domain_context = {
        "medical": "ECMO、VAD、心臟外科、重症醫學相關",
        "ai": "AI、LLM、Claude、機器學習、深度學習相關",
        "international": "國際情勢、地緣政治、全球事務相關",
        "github": "GitHub 開源專案、程式開發、技術工具相關",
        "knowledge": "知識管理、生產力、學習方法、筆記工具相關",
        "claude-code": "Claude Code 版本更新、新功能、bug 修復"
    }

    prompt = f"""你是個人化資訊篩選助手。根據用戶的背景和偏好，從文章中選出最符合他興趣的內容。

{USER_PROFILE}

## 本次任務
領域：{domain_context.get(domain, '')}
從以下文章中選出最符合用戶興趣的 {max_items} 篇：

{chr(10).join(articles_text)}

請用 JSON 格式回覆，包含：
1. 選中的文章編號
2. 每篇文章的一句話核心論點（這篇文章的主要觀點或內容是什麼，不要說為什麼適合用戶）

**重要**：highlights 中的每個值都必須是有意義的摘要，不可為空字串。

格式範例：
{{"selected": [1, 3, 5], "highlights": {{"1": "作者認為...", "3": "研究發現...", "5": "新功能可以..."}}}}

只回覆 JSON，不要其他說明。"""

    try:
        response = _call_claude_api(client, prompt)

        # 移除 markdown 程式碼區塊包裝
        if response.startswith("```"):
            lines = response.split("\n")
            # 移除首行 ```json 和尾行 ```
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            response = "\n".join(lines)

        # 嘗試解析 JSON
        try:
            data = json.loads(response)
            selected_indices = [int(x) - 1 for x in data.get("selected", [])]
            highlights = data.get("highlights", {})

            # 檢查是否有空的 highlight
            empty_highlights = [k for k, v in highlights.items() if not v or not v.strip()]
            if empty_highlights:
                print(f"  警告：偵測到空的 highlight: {empty_highlights}")

            filtered = []
            for i in selected_indices:
                if 0 <= i < len(articles):
                    article = articles[i].copy()
                    # 加入 AI 生成的重點摘要，如果為空則使用 fallback
                    highlight = highlights.get(str(i + 1), "").strip()
                    if not highlight:
                        # Fallback：使用原文摘要或「待補充」
                        highlight = article.get('summary', '')[:80] or "（AI 摘要生成失敗）"
                        print(f"  使用 fallback highlight: {article.get('title', '')[:30]}")
                    article["highlight"] = highlight
                    filtered.append(article)

            if not filtered:
                print(f"  警告：AI 篩選後沒有文章，使用前 {max_items} 篇")
                return articles[:max_items]

            return filtered[:max_items]

        except json.JSONDecodeError as e:
            print(f"  JSON 解析失敗: {e}")
            print(f"  Response: {response[:200]}")
            # Fallback：返回前 N 篇，使用原文摘要
            fallback_articles = []
            for article in articles[:max_items]:
                article_copy = article.copy()
                summary = article.get('summary', '')[:80]
                article_copy["highlight"] = summary if summary else "（JSON 解析失敗）"
                fallback_articles.append(article_copy)
            return fallback_articles

    except Exception as e:
        print(f"  AI filter error (已重試 3 次): {e}")
        # Fallback：返回前 N 篇，使用原文摘要作為 highlight
        fallback_articles = []
        for article in articles[:max_items]:
            article_copy = article.copy()
            # 使用原文摘要或標題作為 fallback highlight
            summary = article.get('summary', '')[:80]
            article_copy["highlight"] = summary if summary else "（無法生成 AI 摘要）"
            fallback_articles.append(article_copy)
        return fallback_articles


def format_domain_message(articles: List[Dict], domain: str, date_str: str) -> str:
    """
    格式化領域推播訊息
    """
    config = DOMAIN_CONFIG.get(domain, {})
    emoji = config.get("emoji", "📰")
    name = config.get("name", domain)

    if not articles:
        return f"{emoji} <b>{name} - {date_str}</b>\n\n目前沒有新內容。"

    lines = [f"{emoji} <b>{name} - {date_str}</b>（{len(articles)} 篇）\n"]

    for article in articles:
        title = article.get("title", "無標題")
        if len(title) > 60:
            title = title[:57] + "..."

        source = article.get("source", "")
        link = article.get("link", "")
        highlight = article.get("highlight", "")

        lines.append(f"• <b>{title}</b>")
        if highlight:
            lines.append(f"  💡 {highlight}")
        if source:
            lines.append(f"  📍 {source}")
        if link:
            lines.append(f"  🔗 <a href=\"{link}\">閱讀</a>")
        lines.append("")

    return "\n".join(lines)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    reraise=True
)
def send_telegram_message(text: str) -> bool:
    """發送 Telegram 訊息（帶 retry）"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    response = requests.post(url, json=payload, timeout=10)
    if response.status_code != 200:
        print(f"  Telegram API 錯誤: {response.status_code}")
        print(f"  Response: {response.text}")
        # 不記錄敏感資訊（Chat ID, Token）
        response.raise_for_status()  # 觸發 retry
    return True


def run_domain_digest(domain: str, hours: int = None, dry_run: bool = False):
    """
    執行特定領域的推播

    Args:
        domain: 領域名稱
        hours: 獲取過去幾小時的文章（若未指定則使用領域預設值）
        dry_run: 測試模式
    """
    config = DOMAIN_CONFIG.get(domain)
    if not config:
        print(f"Unknown domain: {domain}")
        print(f"Available domains: {', '.join(DOMAIN_CONFIG.keys())}")
        return False

    # 使用領域預設時間窗口或預設 24 小時
    if hours is None:
        hours = config.get("default_hours", 24)

    print("=" * 60)
    print(f"領域推播：{config['emoji']} {config['name']}")
    print(f"時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"模式：{'測試' if dry_run else '正式'}，時間窗口：{hours}h")
    print("=" * 60)

    # 1. 獲取文章
    print(f"\n[1/3] 獲取文章...")
    articles = fetch_domain_articles(domain, hours)
    print(f"  共找到 {len(articles)} 篇文章")

    if not articles:
        print("  沒有新文章")
        if not dry_run:
            send_telegram_message(f"{config['emoji']} <b>{config['name']}</b>\n\n過去 {hours} 小時沒有新內容。")
        return True

    # 2. 篩選並產生摘要
    print(f"\n[2/3] 篩選文章...")
    if config.get("use_ai_filter"):
        print("  使用 AI 篩選...")
        filtered = ai_filter_articles(articles, domain, config["max_items"])
    else:
        filtered = articles[:config["max_items"]]
    print(f"  精選 {len(filtered)} 篇")

    # 3. 推播
    print(f"\n[3/3] 推播...")
    date_str = datetime.now().strftime("%Y-%m-%d")
    message = format_domain_message(filtered, domain, date_str)

    if dry_run:
        print("  (測試模式) 訊息內容：")
        print("-" * 40)
        # 移除 HTML tags 顯示
        import re
        clean_msg = re.sub(r'<[^>]+>', '', message)
        print(clean_msg)
        print("-" * 40)
    else:
        success = send_telegram_message(message)
        print(f"  {'✓ 推播成功' if success else '✗ 推播失敗'}")

    print("\n" + "=" * 60)
    print("完成")
    print("=" * 60)

    return True


def run_all_domains(dry_run: bool = False):
    """執行所有領域的推播"""
    for domain in DOMAIN_CONFIG.keys():
        run_domain_digest(domain, dry_run=dry_run)
        print("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="分領域推播系統")
    parser.add_argument("domain", nargs="?", default="all",
                       help="領域名稱 (medical, ai, international, github, knowledge, all)")
    parser.add_argument("--hours", type=int, default=None,
                       help="獲取過去幾小時的文章 (預設依領域設定)")
    parser.add_argument("--dry-run", action="store_true",
                       help="測試模式，不實際發送")
    parser.add_argument("--list", action="store_true",
                       help="列出所有可用領域")

    args = parser.parse_args()

    if args.list:
        print("可用領域：")
        for key, config in DOMAIN_CONFIG.items():
            print(f"  {config['emoji']} {key}: {config['name']}")
        sys.exit(0)

    # 驗證配置
    try:
        validate_config()
    except ValueError as e:
        print(f"配置錯誤: {e}")
        sys.exit(1)

    if args.domain == "all":
        run_all_domains(dry_run=args.dry_run)
    else:
        run_domain_digest(args.domain, hours=args.hours, dry_run=args.dry_run)
