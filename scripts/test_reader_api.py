"""
測試 Readwise Reader API 連接
直接使用 requests 呼叫 API
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

# 設定 stdout 編碼
sys.stdout.reconfigure(encoding='utf-8')

# 載入環境變數
load_dotenv()

BASE_URL = "https://readwise.io/api/v3"

def get_headers():
    token = os.getenv("READWISE_TOKEN")
    return {"Authorization": f"Token {token}"}


def test_list_documents():
    """測試獲取文章列表"""
    print("=" * 60)
    print("Test 1: List recent documents")
    print("=" * 60)

    yesterday = (datetime.now() - timedelta(days=1)).isoformat()

    response = requests.get(
        f"{BASE_URL}/list/",
        headers=get_headers(),
        params={
            "updatedAfter": yesterday,
            "pageCursor": None
        }
    )

    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        print(f"Status: SUCCESS")
        print(f"Found: {len(results)} documents in past 24h")
        print()

        # 顯示前 5 篇
        for i, doc in enumerate(results[:5]):
            title = doc.get("title", "(no title)")
            if title and len(title) > 50:
                title = title[:50] + "..."
            print(f"  {i+1}. {title}")
            print(f"     Source: {doc.get('site_name', 'N/A')}")
            print(f"     Category: {doc.get('category')} | Location: {doc.get('location')}")

        if len(results) > 5:
            print(f"  ... and {len(results) - 5} more")
    else:
        print(f"Status: FAILED ({response.status_code})")
        print(f"Error: {response.text}")


def test_list_tags():
    """測試獲取 Tag 列表"""
    print()
    print("=" * 60)
    print("Test 2: List tags")
    print("=" * 60)

    response = requests.get(
        f"{BASE_URL}/tags/",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        # 處理不同的回傳格式
        if isinstance(data, list):
            tags = data
        elif isinstance(data, dict):
            tags = data.get("results", list(data.keys()) if data else [])
        else:
            tags = []

        print(f"Status: SUCCESS")
        print(f"Response type: {type(data).__name__}")
        print(f"Total tags: {len(tags) if isinstance(tags, list) else 'N/A'}")
        print()
        print("Sample data:")
        if isinstance(data, dict):
            for i, (key, value) in enumerate(list(data.items())[:10]):
                print(f"  - {key}: {value}")
        elif isinstance(tags, list):
            for tag in tags[:10]:
                if isinstance(tag, dict):
                    print(f"  - {tag.get('name', tag)}")
                else:
                    print(f"  - {tag}")
    else:
        print(f"Status: FAILED ({response.status_code})")
        print(f"Error: {response.text}")


def test_feed_count():
    """測試 Feed 中的文章數量"""
    print()
    print("=" * 60)
    print("Test 3: Count documents in Feed")
    print("=" * 60)

    response = requests.get(
        f"{BASE_URL}/list/",
        headers=get_headers(),
        params={"location": "feed"}
    )

    if response.status_code == 200:
        data = response.json()
        count = data.get("count", len(data.get("results", [])))
        print(f"Status: SUCCESS")
        print(f"Documents in Feed: {count}")
    else:
        print(f"Status: FAILED ({response.status_code})")


def main():
    token = os.getenv("READWISE_TOKEN")
    if not token:
        print("Error: READWISE_TOKEN not found in .env")
        return

    print("Readwise Reader API Test")
    print(f"Token: {token[:10]}...")
    print()

    test_list_documents()
    test_list_tags()
    test_feed_count()

    print()
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
