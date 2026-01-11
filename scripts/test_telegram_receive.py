"""
Telegram Bot 接收訊息測試腳本
測試 Quick Capture 功能所需的訊息接收能力
"""
import requests
import json
import re
import time
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def get_updates(offset: int = None, timeout: int = 30):
    """
    使用 Long Polling 獲取新訊息
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"

    params = {
        "timeout": timeout,
        "allowed_updates": ["message"]
    }

    if offset:
        params["offset"] = offset

    response = requests.get(url, params=params, timeout=timeout + 10)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def extract_urls(text: str) -> list:
    """從文字中提取 URL"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)


def parse_message(message: dict) -> dict:
    """
    解析訊息內容

    Returns:
        {
            "message_id": int,
            "is_forward": bool,
            "forward_from_chat": dict or None,  # 頻道資訊
            "channel_name": str or None,        # 頻道名稱
            "channel_username": str or None,    # 頻道 username
            "text": str,                        # 訊息文字
            "caption": str or None,             # 媒體訊息的說明文字
            "urls": list,                       # 提取的 URL 列表
            "has_url": bool,
            "date": int,                        # Unix timestamp
        }
    """
    result = {
        "message_id": message.get("message_id"),
        "is_forward": False,
        "forward_from_chat": None,
        "channel_name": None,
        "channel_username": None,
        "text": "",
        "caption": None,
        "urls": [],
        "has_url": False,
        "date": message.get("date"),
    }

    # 檢查是否為 Forward 訊息
    if "forward_from_chat" in message:
        result["is_forward"] = True
        result["forward_from_chat"] = message["forward_from_chat"]
        result["channel_name"] = message["forward_from_chat"].get("title")
        result["channel_username"] = message["forward_from_chat"].get("username")
    elif "forward_from" in message:
        # 從個人用戶轉發
        result["is_forward"] = True
        forward_from = message["forward_from"]
        result["channel_name"] = f"{forward_from.get('first_name', '')} {forward_from.get('last_name', '')}".strip()
    elif "forward_sender_name" in message:
        # 從隱藏用戶轉發
        result["is_forward"] = True
        result["channel_name"] = message["forward_sender_name"]

    # 提取文字內容
    result["text"] = message.get("text", "")
    result["caption"] = message.get("caption")

    # 合併所有文字來提取 URL
    all_text = result["text"] + " " + (result["caption"] or "")
    result["urls"] = extract_urls(all_text)
    result["has_url"] = len(result["urls"]) > 0

    return result


def classify_message(parsed: dict) -> str:
    """
    分類訊息類型（對應 Quick Capture 的三種案例）
    """
    if parsed["has_url"]:
        if parsed["is_forward"]:
            return "案例2: Forward + 有連結"
        else:
            return "案例: 貼連結（可能有評論）"
    else:
        if parsed["is_forward"]:
            return "案例1: Forward + 純文字"
        else:
            return "案例3: 自己打的純文字"


def print_message_analysis(parsed: dict):
    """印出訊息分析結果"""
    print("\n" + "="*60)
    print("訊息分析結果")
    print("="*60)

    case_type = classify_message(parsed)
    print(f"分類: {case_type}")
    print(f"是否為 Forward: {parsed['is_forward']}")

    if parsed["is_forward"]:
        print(f"來源頻道/用戶: {parsed['channel_name']}")
        if parsed["channel_username"]:
            print(f"頻道 Username: @{parsed['channel_username']}")

    print(f"\n文字內容:")
    text_preview = parsed["text"][:200] + "..." if len(parsed["text"]) > 200 else parsed["text"]
    print(f"  {text_preview}")

    if parsed["caption"]:
        print(f"\nCaption (媒體說明):")
        print(f"  {parsed['caption']}")

    if parsed["has_url"]:
        print(f"\n提取的 URL ({len(parsed['urls'])} 個):")
        for url in parsed["urls"]:
            print(f"  - {url}")

    print("\n" + "-"*60)
    print("Quick Capture 處理建議:")

    if parsed["has_url"]:
        print(f"  -> 使用 save_url() 存入 Reader")
        print(f"  -> URL: {parsed['urls'][0]}")
        if parsed["is_forward"]:
            print(f"  -> 來源標記: [{parsed['channel_name']}]")
    else:
        print(f"  -> 使用 save_note() 存入 Reader")
        print(f"  -> 需要 AI 生成標題")
        if parsed["is_forward"]:
            print(f"  -> 來源標記: [{parsed['channel_name']}] + 日期")
        else:
            print(f"  -> 來源標記: [我的筆記] + 日期")


def send_reply(chat_id: int, text: str):
    """發送回覆訊息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)


def run_test():
    """執行測試 - 持續監聽訊息"""
    print("\n" + "#"*60)
    print("# Telegram Bot 接收測試")
    print("# Quick Capture Forward 訊息驗證")
    print("#"*60)
    print(f"\nBot Token: {TELEGRAM_BOT_TOKEN[:10]}...{TELEGRAM_BOT_TOKEN[-5:]}")
    print(f"Chat ID: {TELEGRAM_CHAT_ID}")
    print("\n請在 Telegram 中發送或 Forward 訊息給 Bot...")
    print("測試將持續 60 秒，或按 Ctrl+C 結束")
    print("-"*60)

    offset = None
    start_time = time.time()
    timeout_seconds = 60
    messages_received = 0

    # 先清除舊的 updates
    print("\n清除舊訊息...")
    result = get_updates(timeout=0)
    if result and result.get("result"):
        old_count = len(result["result"])
        if old_count > 0:
            offset = result["result"][-1]["update_id"] + 1
            print(f"已跳過 {old_count} 則舊訊息")

    print("\n開始監聽新訊息...\n")

    try:
        while time.time() - start_time < timeout_seconds:
            remaining = int(timeout_seconds - (time.time() - start_time))

            result = get_updates(offset=offset, timeout=min(10, remaining))

            if result and result.get("result"):
                for update in result["result"]:
                    offset = update["update_id"] + 1

                    if "message" in update:
                        message = update["message"]
                        messages_received += 1

                        print(f"\n{'#'*60}")
                        print(f"收到訊息 #{messages_received}")
                        print(f"{'#'*60}")

                        # 解析訊息
                        parsed = parse_message(message)

                        # 印出分析結果
                        print_message_analysis(parsed)

                        # 發送回覆確認
                        case_type = classify_message(parsed)
                        reply = f"收到！\n\n分類: {case_type}"
                        if parsed["is_forward"]:
                            reply += f"\n來源: {parsed['channel_name']}"
                        if parsed["has_url"]:
                            reply += f"\nURL: {parsed['urls'][0][:50]}..."

                        send_reply(message["chat"]["id"], reply)

                        # 輸出原始 JSON（用於調試）
                        print("\n原始訊息 JSON:")
                        # 只顯示關鍵欄位
                        debug_fields = ["message_id", "forward_from_chat", "forward_from",
                                       "forward_sender_name", "text", "caption", "entities"]
                        debug_data = {k: message.get(k) for k in debug_fields if k in message}
                        print(json.dumps(debug_data, ensure_ascii=False, indent=2))

            if remaining <= 0:
                break

    except KeyboardInterrupt:
        print("\n\n使用者中斷測試")

    # 總結
    print("\n" + "#"*60)
    print("# 測試結束")
    print("#"*60)
    print(f"收到訊息數: {messages_received}")

    if messages_received > 0:
        print("\n結論: Telegram Bot 可以正常接收訊息！")
        print("Forward 訊息的頻道名稱可以從 forward_from_chat.title 獲取")
    else:
        print("\n沒有收到訊息，請確認：")
        print("1. Bot 是否已啟動對話（先發送 /start）")
        print("2. 是否發送訊息給正確的 Bot")


if __name__ == "__main__":
    run_test()
