"""
Readwise Reader API 客戶端
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import READWISE_TOKEN, READWISE_BASE_URL


def get_headers():
    """取得 API headers"""
    return {"Authorization": f"Token {READWISE_TOKEN}"}


def get_recent_documents(hours: int = 24, location: str = "feed") -> List[Dict]:
    """
    獲取最近的文章

    Args:
        hours: 過去幾小時內的文章
        location: 文章位置 (feed, archive, later)

    Returns:
        文章列表
    """
    since = (datetime.now() - timedelta(hours=hours)).isoformat()

    all_docs = []
    next_cursor = None

    while True:
        params = {
            "updatedAfter": since,
            "location": location,
        }
        if next_cursor:
            params["pageCursor"] = next_cursor

        response = requests.get(
            f"{READWISE_BASE_URL}/list/",
            headers=get_headers(),
            params=params
        )

        if response.status_code != 200:
            print(f"Error fetching documents: {response.status_code}")
            break

        data = response.json()
        results = data.get("results", [])

        # 只保留有標題的文章（排除 note, highlight）
        docs = [d for d in results if d.get("title") and d.get("category") in ["rss", "article", "email"]]
        all_docs.extend(docs)

        next_cursor = data.get("nextPageCursor")
        if not next_cursor:
            break

    return all_docs


def get_document_content(doc_id: str) -> Optional[Dict]:
    """
    獲取單篇文章的完整內容

    Args:
        doc_id: 文章 ID

    Returns:
        文章詳細資訊
    """
    response = requests.get(
        f"{READWISE_BASE_URL}/list/",
        headers=get_headers(),
        params={"id": doc_id, "withHtmlContent": True}
    )

    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        return results[0] if results else None

    return None


def update_document_tags(doc_id: str, tags: List[str]) -> bool:
    """
    更新文章的 tags

    Args:
        doc_id: 文章 ID
        tags: 要設定的 tags 列表

    Returns:
        是否成功
    """
    response = requests.patch(
        f"{READWISE_BASE_URL}/update/{doc_id}/",
        headers=get_headers(),
        json={"tags": tags}
    )

    return response.status_code == 200


def add_tag_to_document(doc_id: str, tag: str) -> bool:
    """
    為文章添加單一 tag

    Args:
        doc_id: 文章 ID
        tag: 要添加的 tag

    Returns:
        是否成功
    """
    # 先獲取現有 tags
    doc = get_document_content(doc_id)
    if not doc:
        return False

    tags_data = doc.get("tags", [])
    existing_tags = []
    for t in tags_data:
        if isinstance(t, dict):
            existing_tags.append(t.get("name", ""))
        elif isinstance(t, str):
            existing_tags.append(t)

    if tag not in existing_tags:
        existing_tags.append(tag)

    return update_document_tags(doc_id, existing_tags)


def get_all_tags() -> List[Dict]:
    """
    獲取所有 tags

    Returns:
        Tag 列表
    """
    response = requests.get(
        f"{READWISE_BASE_URL}/tags/",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])

    return []


# ============================================================
# Quick Capture 功能 - Save API
# ============================================================

def save_url(
    url: str,
    tags: List[str] = None,
    notes: str = None,
    summary: str = None
) -> Optional[Dict]:
    """
    存入 URL 到 Reader（文章會自動抓取）

    Args:
        url: 文章 URL
        tags: 標籤列表，例如 ["#TG收集", "@AI"]
        notes: 用戶評論/筆記
        summary: 文章摘要

    Returns:
        成功時返回文章資訊，失敗返回 None
    """
    payload = {"url": url}

    if tags:
        payload["tags"] = tags
    if notes:
        payload["notes"] = notes
    if summary:
        payload["summary"] = summary

    response = requests.post(
        f"{READWISE_BASE_URL}/save/",
        headers=get_headers(),
        json=payload
    )

    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"Error saving URL: {response.status_code}")
        print(response.text)
        return None


def save_note(
    content: str,
    title: str,
    source_name: str = None,
    tags: List[str] = None,
    notes: str = None
) -> Optional[Dict]:
    """
    存入純文字筆記到 Reader

    Args:
        content: 筆記內容
        title: 標題（AI 生成或手動指定）
        source_name: 來源名稱，例如頻道名稱或「我的筆記」
        tags: 標籤列表
        notes: 額外的用戶評論

    Returns:
        成功時返回文章資訊，失敗返回 None
    """
    # 組裝來源標記
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    if source_name:
        author = f"[{source_name}] {now}"
    else:
        author = f"[我的筆記] {now}"

    # 將純文字轉換為 HTML（保留換行）
    html_lines = content.replace("\n", "<br>")
    html_content = f"<article><p>{html_lines}</p></article>"

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
    if notes:
        payload["notes"] = notes

    response = requests.post(
        f"{READWISE_BASE_URL}/save/",
        headers=get_headers(),
        json=payload
    )

    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"Error saving note: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    # 測試
    print("Testing Reader Client...")
    docs = get_recent_documents(hours=24)
    print(f"Found {len(docs)} documents in the last 24 hours")

    if docs:
        print(f"\nFirst document: {docs[0].get('title', 'No title')[:50]}")
