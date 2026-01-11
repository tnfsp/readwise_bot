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


if __name__ == "__main__":
    # 測試
    print("Testing Reader Client...")
    docs = get_recent_documents(hours=24)
    print(f"Found {len(docs)} documents in the last 24 hours")

    if docs:
        print(f"\nFirst document: {docs[0].get('title', 'No title')[:50]}")
