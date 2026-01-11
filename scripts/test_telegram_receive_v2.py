"""
Telegram Bot 接收訊息測試腳本 v2
修復 Windows 編碼問題，結果輸出到檔案
"""
import requests
import json
import re
import time
from datetime import datetime
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def get_updates(offset: int = None, timeout: int = 30):
    """使用 Long Polling 獲取新訊息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"timeout": timeout, "allowed_updates": ["message"]}
    if offset:
        params["offset"] = offset

    response = requests.get(url, params=params, timeout=timeout + 10)
    if response.status_code == 200:
        return response.json()
    return None


def extract_urls(text: str) -> list:
    """從文字中提取 URL"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)


def parse_message(message: dict) -> dict:
    """解析訊息內容"""
    result = {
        "message_id": message.get("message_id"),
        "is_forward": False,
        "channel_name": None,
        "channel_username": None,
        "text": "",
        "caption": None,
        "urls": [],
        "has_url": False,
        "date": message.get("date"),
        "raw_forward_data": None
    }

    # 檢查是否為 Forward 訊息
    if "forward_from_chat" in message:
        result["is_forward"] = True
        result["channel_name"] = message["forward_from_chat"].get("title")
        result["channel_username"] = message["forward_from_chat"].get("username")
        result["raw_forward_data"] = message["forward_from_chat"]
    elif "forward_from" in message:
        result["is_forward"] = True
        forward_from = message["forward_from"]
        result["channel_name"] = f"{forward_from.get('first_name', '')} {forward_from.get('last_name', '')}".strip()
        result["raw_forward_data"] = forward_from
    elif "forward_sender_name" in message:
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
    """分類訊息類型"""
    if parsed["has_url"]:
        if parsed["is_forward"]:
            return "Forward_URL"
        else:
            return "URL_Only"
    else:
        if parsed["is_forward"]:
            return "Forward_Text"
        else:
            return "Text_Only"


def send_reply(chat_id: int, text: str):
    """發送回覆訊息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)


def run_test():
    """執行測試"""
    results = []
    output_file = "scripts/test_results.json"

    print("Telegram Bot Receive Test")
    print("=" * 40)
    print("Listening for 60 seconds...")
    print("Please send or Forward messages to the Bot")
    print("")

    offset = None
    start_time = time.time()
    timeout_seconds = 60

    # 清除舊訊息
    result = get_updates(timeout=0)
    if result and result.get("result"):
        old_count = len(result["result"])
        if old_count > 0:
            offset = result["result"][-1]["update_id"] + 1
            print(f"Skipped {old_count} old messages")

    print("Listening for new messages...")
    print("")

    try:
        while time.time() - start_time < timeout_seconds:
            remaining = int(timeout_seconds - (time.time() - start_time))

            result = get_updates(offset=offset, timeout=min(10, remaining))

            if result and result.get("result"):
                for update in result["result"]:
                    offset = update["update_id"] + 1

                    if "message" in update:
                        message = update["message"]
                        parsed = parse_message(message)
                        case_type = classify_message(parsed)

                        msg_result = {
                            "timestamp": datetime.now().isoformat(),
                            "case_type": case_type,
                            "is_forward": parsed["is_forward"],
                            "channel_name": parsed["channel_name"],
                            "channel_username": parsed["channel_username"],
                            "has_url": parsed["has_url"],
                            "urls": parsed["urls"],
                            "text_preview": parsed["text"][:200] if parsed["text"] else "",
                            "raw_forward_data": parsed["raw_forward_data"]
                        }
                        results.append(msg_result)

                        # 簡化的控制台輸出
                        print(f"[{len(results)}] Type: {case_type}")
                        print(f"    Forward: {parsed['is_forward']}")
                        if parsed["channel_name"]:
                            # 用 repr 避免編碼問題
                            print(f"    Channel: {repr(parsed['channel_name'])}")
                        if parsed["urls"]:
                            print(f"    URL: {parsed['urls'][0][:50]}...")
                        print("")

                        # 發送回覆
                        reply = f"Received! Type: {case_type}"
                        if parsed["channel_name"]:
                            reply += f"\nSource: {parsed['channel_name']}"
                        send_reply(message["chat"]["id"], reply)

            if remaining <= 0:
                break

    except KeyboardInterrupt:
        print("\nTest interrupted")

    # 儲存結果到 JSON 檔案
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("=" * 40)
    print(f"Test completed. Received {len(results)} messages")
    print(f"Results saved to: {output_file}")

    # 顯示總結
    if results:
        print("\nSummary:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r['case_type']}")
            if r["channel_name"]:
                print(f"     Channel: {r['channel_name']}")
            if r["urls"]:
                print(f"     URL: {r['urls'][0][:60]}")

    return results


if __name__ == "__main__":
    run_test()
