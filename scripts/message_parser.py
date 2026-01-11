"""
Telegram 訊息解析模組
用於 Quick Capture 功能
"""
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ParsedMessage:
    """解析後的訊息結構"""
    message_id: int
    is_forward: bool
    channel_name: Optional[str]
    channel_username: Optional[str]
    text: str
    urls: List[str]
    has_url: bool
    user_comment: Optional[str]  # Forward 時用戶額外加的評論
    timestamp: datetime

    @property
    def case_type(self) -> str:
        """返回訊息分類"""
        if self.has_url:
            return "forward_url" if self.is_forward else "url_only"
        else:
            return "forward_text" if self.is_forward else "text_only"

    @property
    def source_label(self) -> str:
        """返回來源標記"""
        if self.is_forward and self.channel_name:
            return self.channel_name
        return "我的筆記"


def extract_urls(text: str) -> List[str]:
    """
    從文字中提取 URL

    Args:
        text: 輸入文字

    Returns:
        URL 列表
    """
    if not text:
        return []
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)


def parse_telegram_message(message: Dict) -> ParsedMessage:
    """
    解析 Telegram 訊息

    Args:
        message: Telegram Bot API 返回的 message 物件

    Returns:
        ParsedMessage 物件
    """
    # 基本資訊
    message_id = message.get("message_id", 0)
    timestamp = datetime.fromtimestamp(message.get("date", 0))

    # Forward 資訊
    is_forward = False
    channel_name = None
    channel_username = None

    if "forward_from_chat" in message:
        # 從頻道/群組轉發
        is_forward = True
        forward_chat = message["forward_from_chat"]
        channel_name = forward_chat.get("title")
        channel_username = forward_chat.get("username")
    elif "forward_from" in message:
        # 從個人用戶轉發
        is_forward = True
        forward_from = message["forward_from"]
        first_name = forward_from.get("first_name", "")
        last_name = forward_from.get("last_name", "")
        channel_name = f"{first_name} {last_name}".strip()
    elif "forward_sender_name" in message:
        # 從隱藏用戶轉發
        is_forward = True
        channel_name = message["forward_sender_name"]

    # 文字內容
    text = message.get("text", "") or ""
    caption = message.get("caption", "") or ""

    # 合併文字（有些訊息的文字在 caption 裡）
    full_text = text or caption

    # 提取 URL
    urls = extract_urls(full_text)
    has_url = len(urls) > 0

    # 用戶評論（Forward 時，用戶在轉發時加的文字）
    # 注意：Telegram 的 Forward 訊息中，用戶無法直接加評論
    # 如果用戶想加評論，需要先轉發再回覆，這裡暫不處理
    user_comment = None

    return ParsedMessage(
        message_id=message_id,
        is_forward=is_forward,
        channel_name=channel_name,
        channel_username=channel_username,
        text=full_text,
        urls=urls,
        has_url=has_url,
        user_comment=user_comment,
        timestamp=timestamp
    )


def determine_save_action(parsed: ParsedMessage) -> Dict:
    """
    根據解析結果決定存儲動作

    Args:
        parsed: 解析後的訊息

    Returns:
        動作描述字典
    """
    action = {
        "case_type": parsed.case_type,
        "save_method": None,
        "needs_ai_title": False,
        "source_label": parsed.source_label,
        "url": None,
        "content": None,
        "suggested_tags": ["#TG收集"]
    }

    if parsed.has_url:
        # 有 URL：存入文章
        action["save_method"] = "save_url"
        action["url"] = parsed.urls[0]  # 取第一個 URL
        action["needs_ai_title"] = False  # Reader 會自動抓取標題

        # 如果文字不只是 URL，可能有用戶評論
        text_without_urls = parsed.text
        for url in parsed.urls:
            text_without_urls = text_without_urls.replace(url, "").strip()
        if text_without_urls:
            action["user_note"] = text_without_urls
    else:
        # 純文字：存入筆記
        action["save_method"] = "save_note"
        action["content"] = parsed.text
        action["needs_ai_title"] = True  # 需要 AI 生成標題

    return action


if __name__ == "__main__":
    # 測試
    test_messages = [
        # 案例 1: Forward 純文字
        {
            "message_id": 1,
            "date": 1736640000,
            "forward_from_chat": {
                "id": -1001515089840,
                "title": "Leslie和朋友们",
                "username": "justgoidea",
                "type": "channel"
            },
            "text": "在 2026 年的股市投资中，不要去赌「AI 会不会成功」..."
        },
        # 案例 2: Forward 有連結
        {
            "message_id": 2,
            "date": 1736640100,
            "forward_from_chat": {
                "title": "Tech News",
                "username": "technews"
            },
            "text": "推薦這篇文章 https://example.com/article"
        },
        # 案例 3: 自己打的純文字
        {
            "message_id": 3,
            "date": 1736640200,
            "text": "今天看了一百公尺這部電影，我覺得挺有趣的"
        }
    ]

    for msg in test_messages:
        parsed = parse_telegram_message(msg)
        action = determine_save_action(parsed)
        print(f"\n案例: {parsed.case_type}")
        print(f"  是否 Forward: {parsed.is_forward}")
        print(f"  頻道名稱: {parsed.channel_name}")
        print(f"  有 URL: {parsed.has_url}")
        print(f"  存儲方式: {action['save_method']}")
        print(f"  需要 AI 標題: {action['needs_ai_title']}")
        print(f"  來源標記: {action['source_label']}")
