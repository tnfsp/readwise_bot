"""
Claude Code 版本更新推播

從 GitHub Releases RSS 獲取 Claude Code 更新，
只推播 major/minor release，跳過 patch。
"""
import sys
import os
import re
import json
import argparse
import feedparser
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Set
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

sys.stdout.reconfigure(encoding='utf-8')

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    ANTHROPIC_API_KEY,
    validate_config
)

# 領域配置：只保留 claude-code
DOMAIN_CONFIG = {
    "claude-code": {
        "name": "Claude Code 更新",
        "emoji": "🔧",
        "feeds": [
            {"name": "Claude Code Releases", "url": "https://github.com/anthropics/claude-code/releases.atom"},
        ],
        "max_items": 5,
        "use_ai_filter": True,
        "default_hours": 168  # 一週內的更新
    },
}


def parse_version(title: str):
    """
    從 release title 解析 semver (major, minor, patch)。
    回傳 (major, minor, patch) 或 None。
    """
    m = re.search(r'(\d+)\.(\d+)\.(\d+)', title)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    return None


def is_major_or_minor(title: str) -> bool:
    """只保留 major/minor release（patch == 0）"""
    ver = parse_version(title)
    if ver is None:
        return True  # 無法解析版本號，保守保留
    return ver[2] == 0


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    retry=retry_if_exception_type(Exception),
    reraise=False
)
def fetch_rss_feed(url: str, hours: int = 24) -> List[Dict]:
    """從 RSS feed 獲取最近的文章"""
    try:
        feed = feedparser.parse(url)
        articles = []
        cutoff = datetime.now() - timedelta(hours=hours)

        for entry in feed.entries[:20]:
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

            if published and published < cutoff:
                continue

            articles.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", "")[:500] if entry.get("summary") else "",
                "published": published
            })

        return articles
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return []


def fetch_domain_articles(domain: str, hours: int = 24) -> List[Dict]:
    """獲取特定領域的所有文章"""
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


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, Exception)),
    reraise=True
)
def _call_claude_api(client, prompt: str) -> str:
    """呼叫 Claude API（帶 retry）"""
    message = client.messages.create(
        model="claude-sonnet-4-6-20250217",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def ai_summarize_release(articles: List[Dict]) -> List[Dict]:
    """
    使用 AI 為每個 release 產生 2-3 點核心更新摘要。
    """
    if not articles:
        return []

    import anthropic
    import json

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    results = []
    for article in articles:
        title = article.get("title", "")
        summary = article.get("summary", "")
        link = article.get("link", "")

        prompt = f"""你是 Claude Code release notes 摘要助手。

以下是一個 Claude Code release 的資訊：
標題：{title}
內容：{summary}

請用繁體中文列出 2-3 個核心更新重點，每點一行，用 • 開頭。
只回覆重點列表，不要其他說明。"""

        try:
            highlights = _call_claude_api(client, prompt)
        except Exception as e:
            print(f"  AI summarize error: {e}")
            highlights = "• 詳見 release notes"

        article_copy = article.copy()
        article_copy["highlights"] = highlights
        results.append(article_copy)

    return results


def format_domain_message(articles: List[Dict], domain: str, date_str: str) -> str:
    """
    格式化 Claude Code 推播訊息。

    新格式（每個 release 一則）：
    🔧 Claude Code {version}
    重點：{核心更新 2-3 點}
    📖 Release notes：{link}
    """
    if not articles:
        return "🔧 <b>Claude Code 更新</b>\n\n過去一週沒有新的 major/minor release。"

    messages = []
    for article in articles:
        title = article.get("title", "")
        link = article.get("link", "")
        highlights = article.get("highlights", "• 詳見 release notes")

        # 提取版本號
        ver = parse_version(title)
        version_str = f"{ver[0]}.{ver[1]}.{ver[2]}" if ver else title

        lines = [
            f"🔧 <b>Claude Code {version_str}</b>",
            f"重點：",
            highlights,
            f'📖 <a href="{link}">Release notes</a>',
        ]
        messages.append("\n".join(lines))

    return "\n\n".join(messages)


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
        response.raise_for_status()
    return True


# --------------- 去重機制 ---------------

SENT_RELEASES_PATH = Path(__file__).parent / "data" / "sent_releases.json"


def _load_sent_versions() -> Set[str]:
    """讀取已推播過的版本號"""
    if not SENT_RELEASES_PATH.exists():
        return set()
    try:
        data = json.loads(SENT_RELEASES_PATH.read_text(encoding="utf-8"))
        return set(data.get("versions", []))
    except (json.JSONDecodeError, OSError):
        return set()


def _save_sent_versions(versions: Set[str]):
    """寫入已推播的版本號"""
    SENT_RELEASES_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "versions": sorted(versions),
        "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }
    SENT_RELEASES_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run_domain_digest(domain: str, hours: int = None, dry_run: bool = False):
    """執行 Claude Code 推播"""
    config = DOMAIN_CONFIG.get(domain)
    if not config:
        print(f"Unknown domain: {domain}")
        print(f"Available domains: {', '.join(DOMAIN_CONFIG.keys())}")
        return False

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
            send_telegram_message(f"🔧 <b>Claude Code 更新</b>\n\n過去 {hours} 小時沒有新內容。")
        return True

    # 2. 過濾：只保留 major/minor release
    print(f"\n[2/3] 過濾 patch releases...")
    filtered = [a for a in articles if is_major_or_minor(a.get("title", ""))]
    skipped = len(articles) - len(filtered)
    if skipped:
        print(f"  跳過 {skipped} 個 patch release")
    print(f"  保留 {len(filtered)} 個 major/minor release")

    if not filtered:
        print("  沒有 major/minor release")
        if not dry_run:
            send_telegram_message("🔧 <b>Claude Code 更新</b>\n\n過去一週只有 patch 更新，無 major/minor release。")
        return True

    # 2.5. 去重：排除已推播的版本
    sent_versions = _load_sent_versions()
    before_dedup = len(filtered)
    filtered = [
        a for a in filtered
        if (parse_version(a.get("title", "")) is None)
        or ("{}.{}.{}".format(*parse_version(a.get("title", ""))) not in sent_versions)
    ]
    deduped = before_dedup - len(filtered)
    if deduped:
        print(f"  跳過 {deduped} 個已推播的版本")
    print(f"  去重後剩 {len(filtered)} 個新 release")

    if not filtered:
        print("  所有 release 都已推播過")
        return True

    # 3. AI 摘要 + 推播
    print(f"\n[3/3] 產生摘要並推播...")
    summarized = ai_summarize_release(filtered[:config["max_items"]])

    date_str = datetime.now().strftime("%Y-%m-%d")
    message = format_domain_message(summarized, domain, date_str)

    if dry_run:
        print("  (測試模式) 訊息內容：")
        print("-" * 40)
        clean_msg = re.sub(r'<[^>]+>', '', message)
        print(clean_msg)
        print("-" * 40)
    else:
        success = send_telegram_message(message)
        print(f"  {'✓ 推播成功' if success else '✗ 推播失敗'}")

        if success:
            # 記錄已推播的版本號
            new_versions = set()
            for a in summarized:
                ver = parse_version(a.get("title", ""))
                if ver:
                    new_versions.add(f"{ver[0]}.{ver[1]}.{ver[2]}")
            if new_versions:
                all_versions = sent_versions | new_versions
                _save_sent_versions(all_versions)
                print(f"  已記錄 {len(new_versions)} 個版本號到 sent_releases.json")

    print("\n" + "=" * 60)
    print("完成")
    print("=" * 60)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Claude Code 更新推播")
    parser.add_argument("domain", nargs="?", default="claude-code",
                       help="領域名稱 (claude-code)")
    parser.add_argument("--hours", type=int, default=None,
                       help="獲取過去幾小時的文章")
    parser.add_argument("--dry-run", action="store_true",
                       help="測試模式，不實際發送")

    args = parser.parse_args()

    try:
        validate_config()
    except ValueError as e:
        print(f"配置錯誤: {e}")
        sys.exit(1)

    run_domain_digest(args.domain, hours=args.hours, dry_run=args.dry_run)
