"""
Reader Save API 測試腳本
測試 Quick Capture 功能所需的 API 能力
"""
import requests
import json
from datetime import datetime
from config import READWISE_TOKEN, READWISE_BASE_URL


def get_headers():
    """取得 API headers"""
    return {"Authorization": f"Token {READWISE_TOKEN}"}


def test_save_url(url: str, tags: list = None, notes: str = None, summary: str = None):
    """
    測試 1: 存入 URL
    """
    print("\n" + "="*50)
    print("測試 1: 存入 URL")
    print("="*50)

    payload = {"url": url}

    if tags:
        payload["tags"] = tags
    if notes:
        payload["notes"] = notes
    if summary:
        payload["summary"] = summary

    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")

    response = requests.post(
        f"{READWISE_BASE_URL}/save/",
        headers=get_headers(),
        json=payload
    )

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        print(f"Success! Document ID: {data.get('id', 'N/A')}")
        print(f"Title: {data.get('title', 'N/A')}")
        print(f"URL: {data.get('url', 'N/A')}")
        return data
    else:
        print(f"Error: {response.text}")
        return None


def test_save_html_note(content: str, title: str, source_name: str = None, tags: list = None):
    """
    測試 2: 存入純文字內容（HTML 格式）
    """
    print("\n" + "="*50)
    print("測試 2: 存入純文字筆記（HTML）")
    print("="*50)

    # 組裝來源標記
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    if source_name:
        author = f"[{source_name}] {now}"
    else:
        author = f"[我的筆記] {now}"

    # 將純文字轉換為 HTML
    html_content = f"<article><p>{content}</p></article>"

    # 使用虛擬 URL（Reader 需要 URL 欄位）
    fake_url = f"https://tg-capture.local/{datetime.now().strftime('%Y%m%d%H%M%S')}"

    payload = {
        "url": fake_url,
        "html": html_content,
        "title": title,
        "author": author,
        "should_clean_html": True,
        "saved_using": "TG Quick Capture"
    }

    if tags:
        payload["tags"] = tags

    print(f"Title: {title}")
    print(f"Author/Source: {author}")
    print(f"Content preview: {content[:100]}...")
    print(f"Tags: {tags}")

    response = requests.post(
        f"{READWISE_BASE_URL}/save/",
        headers=get_headers(),
        json=payload
    )

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        print(f"Success! Document ID: {data.get('id', 'N/A')}")
        print(f"Title: {data.get('title', 'N/A')}")
        print(f"Author: {data.get('author', 'N/A')}")
        return data
    else:
        print(f"Error: {response.text}")
        return None


def test_save_with_annotation(url: str, annotation: str, tags: list = None):
    """
    測試 3: 存入 URL + 用戶評論（annotation）
    """
    print("\n" + "="*50)
    print("測試 3: 存入 URL + 用戶評論")
    print("="*50)

    payload = {
        "url": url,
        "notes": annotation  # 用戶評論存在 notes 欄位
    }

    if tags:
        payload["tags"] = tags

    print(f"URL: {url}")
    print(f"Annotation: {annotation}")
    print(f"Tags: {tags}")

    response = requests.post(
        f"{READWISE_BASE_URL}/save/",
        headers=get_headers(),
        json=payload
    )

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        print(f"Success! Document ID: {data.get('id', 'N/A')}")
        print(f"Title: {data.get('title', 'N/A')}")
        return data
    else:
        print(f"Error: {response.text}")
        return None


def run_all_tests():
    """執行所有測試"""
    print("\n" + "#"*60)
    print("# Reader Save API 測試")
    print("# Quick Capture 功能驗證")
    print("#"*60)

    results = {
        "save_url": False,
        "save_html_note": False,
        "save_with_annotation": False
    }

    # 測試 1: 存入 URL（模擬 Forward 有連結的情況）
    result1 = test_save_url(
        url="https://simonwillison.net/2024/Dec/19/one-shot-python-tools/",
        tags=["#TG收集", "@AI"],
        summary="測試存入 URL"
    )
    results["save_url"] = result1 is not None

    # 測試 2: 存入純文字筆記（模擬 Forward 純文字 / 自己打的情況）
    test_content = """今天看了一百公尺這部電影，我覺得挺有趣的，很青春。

電影講述的是一個多發性硬化症患者挑戰自我的故事，很勵志。"""

    result2 = test_save_html_note(
        content=test_content,
        title="電影《一百公尺》觀後感",
        source_name="我的筆記",
        tags=["#TG收集", "@生活"]
    )
    results["save_html_note"] = result2 is not None

    # 測試 3: 存入 URL + 用戶評論（模擬貼連結 + 評論的情況）
    result3 = test_save_with_annotation(
        url="https://letter.justgoidea.com/p/202602",
        annotation="有趣的觀點，連結的維護確實是被忽略的問題",
        tags=["#TG收集", "@知識"]
    )
    results["save_with_annotation"] = result3 is not None

    # 總結
    print("\n" + "#"*60)
    print("# 測試結果總結")
    print("#"*60)

    for test_name, passed in results.items():
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())
    print(f"\n總結: {'所有測試通過！' if all_passed else '部分測試失敗'}")

    return results


if __name__ == "__main__":
    run_all_tests()
