"""
分領域推播系統

根據不同領域從 RSS 獲取內容並推播到 Telegram
支援的領域：AI, 國際, GitHub, 知識
"""
import sys
import argparse
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

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
    "ai": {
        "name": "AI",
        "emoji": "🤖",
        "feeds": [
            {"name": "Simon Willison", "url": "https://simonwillison.net/atom/everything/"},
            {"name": "Anthropic", "url": "https://www.anthropic.com/rss.xml"},
            {"name": "Latent Space", "url": "https://www.latent.space/feed"},
            {"name": "Import AI", "url": "https://importai.substack.com/feed"},
            {"name": "Ben's Bites", "url": "https://bensbites.beehiiv.com/feed"},
        ],
        "max_items": 8,
        "use_ai_filter": True
    },
    "international": {
        "name": "國際情勢",
        "emoji": "🌍",
        "feeds": [
            {"name": "Foreign Affairs", "url": "https://www.foreignaffairs.com/rss.xml"},
            {"name": "Foreign Policy", "url": "https://foreignpolicy.com/feed/"},
            {"name": "Project Syndicate", "url": "https://www.project-syndicate.org/rss"},
        ],
        "max_items": 6,
        "use_ai_filter": True
    },
    "github": {
        "name": "GitHub",
        "emoji": "💻",
        "feeds": [
            {"name": "GitHub Trending (Python)", "url": "https://mshibanami.github.io/GitHubTrendingRSS/daily/python.xml"},
            {"name": "GitHub Trending (All)", "url": "https://mshibanami.github.io/GitHubTrendingRSS/daily/all.xml"},
            {"name": "Claude Code Releases", "url": "https://github.com/anthropics/claude-code/releases.atom"},
        ],
        "max_items": 8,
        "use_ai_filter": False  # GitHub 不需要 AI 過濾
    },
    "knowledge": {
        "name": "知識/生產力",
        "emoji": "📚",
        "feeds": [
            {"name": "電腦玩物", "url": "https://www.playpcesor.com/feeds/posts/default?alt=rss"},
            {"name": "少数派", "url": "https://sspai.com/feed"},
            {"name": "閱讀前哨站", "url": "https://readingoutpost.com/feed/"},
        ],
        "max_items": 6,
        "use_ai_filter": True
    }
}


def fetch_rss_feed(url: str, hours: int = 24) -> List[Dict]:
    """
    從 RSS feed 獲取最近的文章

    Args:
        url: RSS feed URL
        hours: 獲取過去幾小時的文章

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
                published = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6])

            # 如果無法解析時間或文章太舊，跳過
            if published and published < cutoff:
                continue

            articles.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", "")[:200] if entry.get("summary") else "",
                "published": published
            })

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
        articles = fetch_rss_feed(feed["url"], hours)
        for article in articles:
            article["source"] = feed["name"]
        all_articles.extend(articles)
        print(f"    Found {len(articles)} articles")

    return all_articles


def ai_filter_articles(articles: List[Dict], domain: str, max_items: int) -> List[Dict]:
    """
    使用 AI 篩選文章
    """
    if not articles:
        return []

    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # 準備文章列表
    articles_text = []
    for i, article in enumerate(articles[:20]):
        articles_text.append(f"{i+1}. [{article.get('source')}] {article.get('title')}")

    domain_context = {
        "ai": "AI、LLM、Claude、機器學習、深度學習相關",
        "international": "國際情勢、地緣政治、全球事務相關",
        "knowledge": "知識管理、生產力、學習方法、筆記工具相關"
    }

    prompt = f"""你是資訊篩選助手。從以下 {domain_context.get(domain, '')} 文章中，選出最重要的 {max_items} 篇。

文章列表：
{chr(10).join(articles_text)}

請回覆選中的文章編號，用逗號分隔，例如：1,3,5,7
只回覆編號，不要其他說明。"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )

        response = message.content[0].text.strip()
        selected_indices = [int(x.strip()) - 1 for x in response.split(",") if x.strip().isdigit()]

        filtered = [articles[i] for i in selected_indices if 0 <= i < len(articles)]
        return filtered[:max_items]

    except Exception as e:
        print(f"  AI filter error: {e}")
        return articles[:max_items]


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

        lines.append(f"• <b>{title}</b>")
        if source:
            lines.append(f"  📍 {source}")
        if link:
            lines.append(f"  🔗 <a href=\"{link}\">閱讀</a>")
        lines.append("")

    return "\n".join(lines)


def send_telegram_message(text: str) -> bool:
    """發送 Telegram 訊息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    response = requests.post(url, json=payload)
    return response.status_code == 200


def run_domain_digest(domain: str, hours: int = 24, dry_run: bool = False):
    """
    執行特定領域的推播

    Args:
        domain: 領域名稱
        hours: 獲取過去幾小時的文章
        dry_run: 測試模式
    """
    config = DOMAIN_CONFIG.get(domain)
    if not config:
        print(f"Unknown domain: {domain}")
        print(f"Available domains: {', '.join(DOMAIN_CONFIG.keys())}")
        return False

    print("=" * 60)
    print(f"領域推播：{config['emoji']} {config['name']}")
    print(f"時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"模式：{'測試' if dry_run else '正式'}")
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

    # 2. 篩選
    print(f"\n[2/3] 篩選文章...")
    if config.get("use_ai_filter") and len(articles) > config["max_items"]:
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
                       help="領域名稱 (ai, international, github, knowledge, all)")
    parser.add_argument("--hours", type=int, default=24,
                       help="獲取過去幾小時的文章 (預設: 24)")
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
