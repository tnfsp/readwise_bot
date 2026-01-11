"""
Telegram Bot 接收訊息測試腳本 v3
避免所有 print 中文，結果輸出到 JSON 檔案
"""
import requests
import json
import re
import time
import sys
from datetime import datetime
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# 設定輸出編碼
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def get_updates(offset=None, timeout=30):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"timeout": timeout, "allowed_updates": ["message"]}
    if offset:
        params["offset"] = offset
    try:
        response = requests.get(url, params=params, timeout=timeout + 10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None


def extract_urls(text):
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text or "")


def parse_message(message):
    result = {
        "message_id": message.get("message_id"),
        "is_forward": False,
        "channel_name": None,
        "channel_username": None,
        "text": "",
        "urls": [],
        "has_url": False,
        "forward_data": None
    }

    if "forward_from_chat" in message:
        result["is_forward"] = True
        result["channel_name"] = message["forward_from_chat"].get("title")
        result["channel_username"] = message["forward_from_chat"].get("username")
        result["forward_data"] = message["forward_from_chat"]
    elif "forward_from" in message:
        result["is_forward"] = True
        ff = message["forward_from"]
        result["channel_name"] = f"{ff.get('first_name', '')} {ff.get('last_name', '')}".strip()
        result["forward_data"] = ff
    elif "forward_sender_name" in message:
        result["is_forward"] = True
        result["channel_name"] = message["forward_sender_name"]

    result["text"] = message.get("text", "") or message.get("caption", "")
    result["urls"] = extract_urls(result["text"])
    result["has_url"] = len(result["urls"]) > 0

    return result


def classify(parsed):
    if parsed["has_url"]:
        return "Forward_URL" if parsed["is_forward"] else "URL_Only"
    else:
        return "Forward_Text" if parsed["is_forward"] else "Text_Only"


def send_reply(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


def run_test():
    results = []
    output_file = "scripts/test_results.json"

    print("=" * 50)
    print("Telegram Bot Receive Test v3")
    print("=" * 50)
    print("Listening for 60 seconds...")
    print("Please send/Forward messages to the Bot NOW")
    print("")

    offset = None
    start_time = time.time()

    # Clear old messages
    result = get_updates(timeout=0)
    if result and result.get("result"):
        if result["result"]:
            offset = result["result"][-1]["update_id"] + 1
            print(f"Cleared {len(result['result'])} old messages")

    print("Waiting for new messages...\n")

    try:
        while time.time() - start_time < 60:
            remaining = int(60 - (time.time() - start_time))
            result = get_updates(offset=offset, timeout=min(10, remaining))

            if result and result.get("result"):
                for update in result["result"]:
                    offset = update["update_id"] + 1

                    if "message" in update:
                        message = update["message"]
                        parsed = parse_message(message)
                        case_type = classify(parsed)

                        msg_result = {
                            "timestamp": datetime.now().isoformat(),
                            "case_type": case_type,
                            "is_forward": parsed["is_forward"],
                            "channel_name": parsed["channel_name"],
                            "channel_username": parsed["channel_username"],
                            "has_url": parsed["has_url"],
                            "urls": parsed["urls"],
                            "text_preview": parsed["text"][:300] if parsed["text"] else "",
                            "forward_data": parsed["forward_data"]
                        }
                        results.append(msg_result)

                        # Safe print (ASCII only)
                        print(f"[{len(results)}] Type: {case_type}")
                        print(f"    is_forward: {parsed['is_forward']}")
                        print(f"    has_url: {parsed['has_url']}")
                        if parsed["urls"]:
                            print(f"    url: {parsed['urls'][0][:60]}")
                        print("")

                        # Save immediately after each message
                        with open(output_file, "w", encoding="utf-8") as f:
                            json.dump(results, f, ensure_ascii=False, indent=2)

                        # Send reply
                        reply = f"OK! Type: {case_type}"
                        send_reply(message["chat"]["id"], reply)

            if remaining <= 0:
                break

    except KeyboardInterrupt:
        print("\nInterrupted")

    # Final save
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print(f"Done! Received {len(results)} messages")
    print(f"Results: {output_file}")
    print("=" * 50)

    return results


if __name__ == "__main__":
    run_test()
