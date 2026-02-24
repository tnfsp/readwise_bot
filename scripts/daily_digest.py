"""
每日推播主程式

功能：
1. 從 Readwise Reader 獲取過去 24 小時的新文章
2. 使用 AI 篩選並產生摘要
3. 推送精選到 Telegram
4. 更新文章的 Tag
"""
import sys
from datetime import datetime

# 設定 stdout 編碼
sys.stdout.reconfigure(encoding='utf-8')

from config import validate_config
from reader_client import get_recent_documents, add_tag_to_document
from ai_filter import filter_and_summarize_batch, simple_filter
from telegram_bot import send_message, format_daily_digest


def run_daily_digest(use_ai: bool = True, dry_run: bool = False):
    """
    執行每日推播

    Args:
        use_ai: 是否使用 AI 篩選
        dry_run: 測試模式，不實際發送
    """
    print("=" * 60)
    print("每日推播系統啟動")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"模式: {'AI 篩選' if use_ai else '簡單規則'} | {'測試模式' if dry_run else '正式執行'}")
    print("=" * 60)

    # 1. 驗證配置
    print("\n[1/5] 驗證配置...")
    try:
        validate_config()
        print("  ✓ 配置驗證通過")
    except ValueError as e:
        print(f"  ✗ 配置錯誤: {e}")
        return False

    # 2. 獲取新文章
    print("\n[2/5] 獲取新文章...")
    articles = get_recent_documents(hours=24, location="inbox")
    print(f"  ✓ 找到 {len(articles)} 篇新文章")

    if not articles:
        print("  沒有新文章，結束執行")
        if not dry_run:
            send_message("📭 今日沒有新文章")
        return True

    # 3. AI 篩選
    print("\n[3/5] 篩選文章...")
    if use_ai:
        try:
            filtered = filter_and_summarize_batch(articles, max_articles=10)
            print(f"  ✓ AI 篩選完成，精選 {len(filtered)} 篇")
        except Exception as e:
            print(f"  ⚠ AI 篩選失敗: {e}")
            print("  → 降級為簡單規則篩選")
            filtered = simple_filter(articles, max_articles=10)
    else:
        filtered = simple_filter(articles, max_articles=10)
        print(f"  ✓ 簡單篩選完成，精選 {len(filtered)} 篇")

    # 4. 準備推播內容
    print("\n[4/5] 準備推播內容...")
    today = datetime.now().strftime("%Y-%m-%d")

    # 轉換格式
    push_articles = []
    for article in filtered:
        push_articles.append({
            "title": article.get("title", ""),
            "summary": article.get("ai_summary") or article.get("summary", "")[:100],
            "domain": article.get("domain", "其他"),
            "url": article.get("source_url") or article.get("url", ""),
            "source": article.get("site_name", ""),
            "importance": article.get("importance", 3),
            "id": article.get("id")
        })

    message = format_daily_digest(push_articles, today)
    print(f"  ✓ 訊息準備完成 ({len(message)} 字)")

    # 顯示預覽
    print("\n  --- 推播預覽 ---")
    for article in push_articles:
        print(f"  [{article['domain']}] {article['title'][:40]}...")
    print("  -----------------")

    # 5. 發送推播
    print("\n[5/5] 發送推播...")
    if dry_run:
        print("  (測試模式) 跳過實際發送")
        print("\n  訊息內容：")
        print("  " + message.replace("\n", "\n  "))
    else:
        success = send_message(message)
        if success:
            print("  ✓ 推播發送成功")

            # 更新文章 Tag
            print("\n  更新文章標籤...")
            # 領域對應 Tag
            domain_tags = {
                "AI": "@AI",
                "國際": "@國際",
                "知識": "@知識",
                "醫學": "@醫學",
                "生產力": "@生產力",
                "其他": "@其他"
            }
            for article in push_articles:
                doc_id = article.get("id")
                if doc_id:
                    add_tag_to_document(doc_id, "#推播")
                    # 加入領域 Tag
                    domain = article.get("domain", "其他")
                    domain_tag = domain_tags.get(domain, f"@{domain}")
                    add_tag_to_document(doc_id, domain_tag)
            print("  ✓ 標籤更新完成")
        else:
            print("  ✗ 推播發送失敗")
            return False

    print("\n" + "=" * 60)
    print("每日推播完成")
    print("=" * 60)

    return True


def test_connection():
    """測試各服務連接"""
    print("測試服務連接...")

    # 測試 Readwise
    print("\n[1] Readwise Reader API...")
    try:
        from reader_client import get_recent_documents
        docs = get_recent_documents(hours=24)
        print(f"  ✓ 連接成功，找到 {len(docs)} 篇文章")
    except Exception as e:
        print(f"  ✗ 連接失敗: {e}")

    # 測試 Telegram
    print("\n[2] Telegram Bot...")
    try:
        from telegram_bot import send_test_message
        success = send_test_message()
        print(f"  {'✓ 發送成功' if success else '✗ 發送失敗'}")
    except Exception as e:
        print(f"  ✗ 連接失敗: {e}")

    # 測試 Claude API
    print("\n[3] Claude API...")
    try:
        import anthropic
        from config import ANTHROPIC_API_KEY
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": "Say 'API connection successful' in Chinese"}]
        )
        print(f"  ✓ {message.content[0].text}")
    except Exception as e:
        print(f"  ✗ 連接失敗: {e}")

    print("\n測試完成")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="每日推播系統")
    parser.add_argument("--test", action="store_true", help="測試服務連接")
    parser.add_argument("--dry-run", action="store_true", help="測試模式，不實際發送")
    parser.add_argument("--no-ai", action="store_true", help="不使用 AI 篩選")

    args = parser.parse_args()

    if args.test:
        test_connection()
    else:
        run_daily_digest(use_ai=not args.no_ai, dry_run=args.dry_run)
