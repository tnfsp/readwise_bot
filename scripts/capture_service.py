"""
capture_service.py - 共用的訊息處理邏輯

統一 app.py、quick_capture_webhook.py、quick_capture.py 的 process_message 邏輯。
所有入口都透過此模組完成「解析 → 存入 → 回傳結果」，確保行為一致。

功能一致性：
- URL 訊息：加 #TG收集 + 領域 tag
- 文字訊息：AI 生成標題 + 加 #TG收集 + 領域 tag
"""
import os
import sys

# 確保可以 import 同目錄的模組
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from message_parser import parse_telegram_message, determine_save_action
from reader_client import save_url, save_note
from ai_filter import process_capture_content, detect_domain


def process_message(message: dict) -> dict:
    """
    處理單一 Telegram 訊息，統一三個入口的邏輯。

    所有入口都會：
    - 加 #TG收集 tag（任務 #1 & #3 修復）
    - 對 URL 訊息加領域 tag
    - 對文字訊息用 AI 生成標題與領域 tag

    Args:
        message: Telegram Bot API 返回的 message 物件

    Returns:
        result dict:
            success (bool): 是否成功
            case_type (str): 訊息分類
            title (str | None): 文章/筆記標題
            domain (str | None): 領域
            source (str): 來源標記
            url (str | None): 目標 URL（只有 save_url 時有值）
            doc_id (str | None): Reader 文件 ID
            error (str | None): 錯誤訊息
    """
    parsed = parse_telegram_message(message)
    action = determine_save_action(parsed)

    result = {
        "success": False,
        "case_type": parsed.case_type,
        "title": None,
        "domain": None,
        "source": parsed.source_label,
        "url": None,
        "doc_id": None,
        "error": None
    }

    try:
        if action["save_method"] == "save_url":
            url = action["url"]
            result["url"] = url

            # 必加 #TG收集（修 #1 & #3）
            tags = ["#TG收集"]

            # 偵測領域並加 tag
            domain = detect_domain(parsed.text)
            if domain != "其他":
                tags.append(f"@{domain}")
            result["domain"] = domain

            # 處理用戶評論與轉發來源
            user_note = action.get("user_note")
            if parsed.is_forward and parsed.channel_name:
                source_note = f"來源：{parsed.channel_name}"
                user_note = f"{source_note}\n\n{user_note}" if user_note else source_note

            doc = save_url(url=url, tags=tags, notes=user_note)
            if doc:
                result["success"] = True
                result["doc_id"] = doc.get("id")
                result["title"] = doc.get("title") or url[:50]
            else:
                result["error"] = "存入失敗"

        elif action["save_method"] == "save_note":
            content = action["content"]
            ai_result = process_capture_content(content)
            title = ai_result["title"]
            domain = ai_result["domain"]
            domain_tag = ai_result["domain_tag"]

            result["title"] = title
            result["domain"] = domain

            # 必加 #TG收集（修 #1 & #3）
            tags = ["#TG收集"]
            if domain_tag:
                tags.append(domain_tag)

            doc = save_note(
                content=content,
                title=title,
                source_name=parsed.source_label,
                tags=tags
            )
            if doc:
                result["success"] = True
                result["doc_id"] = doc.get("id")
            else:
                result["error"] = "存入失敗"

    except Exception as e:
        result["error"] = str(e)

    return result


def format_reply(result: dict) -> str:
    """
    格式化 Telegram 回覆訊息（所有入口共用）。

    Args:
        result: process_message 的回傳值

    Returns:
        HTML 格式的回覆字串
    """
    if result["success"]:
        lines = ["<b>OK</b> 已存入 Reader"]

        if result["title"]:
            lines.append(f"<b>{result['title'][:40]}</b>")

        if result["domain"]:
            domain_emoji = {
                "醫學": "🏥", "AI": "🤖", "國際": "🌍",
                "知識": "📚", "生產力": "⚡", "生活": "🏠",
                "投資": "💰", "系統效率": "⚡", "其他": "📌"
            }
            emoji = domain_emoji.get(result["domain"], "📌")
            lines.append(f"{emoji} {result['domain']}")

        if result["source"] and result["source"] != "我的筆記":
            lines.append(f"📍 {result['source']}")

        return "\n".join(lines)
    else:
        return f"Error 存入失敗\n{result.get('error', '未知錯誤')}"
