"""
Telegram Bot 推播模組
"""
import requests
from typing import List, Dict, Optional
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_message(text: str, parse_mode: str = "HTML") -> bool:
    """
    發送訊息到 Telegram

    Args:
        text: 訊息內容
        parse_mode: 格式化模式 (HTML 或 Markdown)

    Returns:
        是否成功
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }

    response = requests.post(url, json=payload, timeout=15)

    if response.status_code != 200:
        print(f"Error sending message: {response.status_code}")
        print(response.text)
        return False

    return True


def format_daily_digest(articles: List[Dict], date_str: str) -> str:
    """
    格式化每日摘要訊息

    Args:
        articles: 文章列表，每篇包含 title, summary, domain, url, importance
        date_str: 日期字串

    Returns:
        格式化的訊息
    """
    if not articles:
        return f"📭 <b>{date_str} 今日精選</b>\n\n沒有新的重要文章。"

    # 按領域分組
    by_domain = {}
    for article in articles:
        domain = article.get("domain", "其他")
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(article)

    # 領域 emoji 對應
    domain_emoji = {
        "醫學": "🏥",
        "AI": "🤖",
        "國際": "🌍",
        "知識": "📚",
        "生產力": "⚡",
        "生活": "🏠",
        "其他": "📌"
    }

    # 組裝訊息
    lines = [f"📰 <b>{date_str} 今日精選</b>（{len(articles)} 篇）\n"]

    for domain, domain_articles in by_domain.items():
        emoji = domain_emoji.get(domain, "📌")
        lines.append(f"\n{emoji} <b>{domain}</b>")

        for article in domain_articles:
            title = article.get("title", "無標題")
            # 截斷過長的標題
            if len(title) > 50:
                title = title[:47] + "..."

            summary = article.get("summary", "")
            url = article.get("url", "")

            lines.append(f"• {title}")
            if summary:
                lines.append(f"  → {summary}")
            if url:
                lines.append(f"  🔗 <a href=\"{url}\">閱讀全文</a>")

    lines.append(f"\n⏰ 推播時間：{date_str}")

    return "\n".join(lines)


def format_single_article(article: Dict) -> str:
    """
    格式化單篇文章訊息

    Args:
        article: 文章資訊

    Returns:
        格式化的訊息
    """
    domain_emoji = {
        "醫學": "🏥",
        "AI": "🤖",
        "國際": "🌍",
        "知識": "📚",
        "生產力": "⚡",
        "生活": "🏠",
        "其他": "📌"
    }

    domain = article.get("domain", "其他")
    emoji = domain_emoji.get(domain, "📌")
    title = article.get("title", "無標題")
    summary = article.get("summary", "")
    url = article.get("url", "")
    source = article.get("source", "")

    lines = [
        f"{emoji} <b>{domain}</b>",
        f"<b>{title}</b>",
    ]

    if source:
        lines.append(f"📍 {source}")

    if summary:
        lines.append(f"\n{summary}")

    if url:
        lines.append(f"\n🔗 <a href=\"{url}\">閱讀全文</a>")

    return "\n".join(lines)


def send_daily_digest(articles: List[Dict], date_str: str) -> bool:
    """
    發送每日摘要

    Args:
        articles: 精選文章列表
        date_str: 日期字串

    Returns:
        是否成功
    """
    message = format_daily_digest(articles, date_str)
    return send_message(message)


def send_test_message() -> bool:
    """發送測試訊息"""
    return send_message("🔔 <b>測試訊息</b>\n\n個人訊息流系統已連接成功！")


if __name__ == "__main__":
    # 測試發送
    print("Sending test message...")
    success = send_test_message()
    print(f"Result: {'Success' if success else 'Failed'}")
