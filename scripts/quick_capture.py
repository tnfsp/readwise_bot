"""
Quick Capture - Telegram Bot 快速捕捉到 Reader

功能：
- 接收 Telegram 訊息
- 自動判斷訊息類型（Forward/純文字/有連結）
- 存入 Readwise Reader
- 回覆確認訊息

使用方式：
    python quick_capture.py          # 啟動 Bot（持續運行）
    python quick_capture.py --test   # 測試模式（處理一則訊息後退出）
"""
import sys
import argparse
import requests
from datetime import datetime

# 修復 Windows 控制台編碼問題
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from capture_service import process_message, format_reply


# ============================================================
# Telegram Bot 接收功能
# ============================================================

def get_updates(offset=None, timeout=30):
    """使用 Long Polling 獲取新訊息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"timeout": timeout, "allowed_updates": ["message"]}
    if offset:
        params["offset"] = offset

    try:
        response = requests.get(url, params=params, timeout=timeout + 10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error getting updates: {e}")

    return None


def send_reply(chat_id: int, text: str, parse_mode: str = "HTML"):
    """發送回覆訊息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Error sending reply: {e}")


# ============================================================
# 主程式
# ============================================================

def run_bot(test_mode=False):
    """
    運行 Bot

    Args:
        test_mode: 測試模式（處理一則訊息後退出）
    """
    print("=" * 50)
    print("Quick Capture Bot")
    print("=" * 50)
    print(f"Mode: {'Test' if test_mode else 'Production'}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    offset = None
    messages_processed = 0

    # 清除舊訊息
    result = get_updates(timeout=0)
    if result and result.get("result"):
        if result["result"]:
            offset = result["result"][-1]["update_id"] + 1
            print(f"Cleared {len(result['result'])} old messages")

    print("Listening for messages...")
    print("Send a message to the Bot to test")
    print("Press Ctrl+C to stop")
    print("-" * 50)

    try:
        while True:
            result = get_updates(offset=offset, timeout=30)

            if result and result.get("result"):
                for update in result["result"]:
                    offset = update["update_id"] + 1

                    if "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]

                        # 只處理來自授權用戶的訊息
                        if str(chat_id) != str(TELEGRAM_CHAT_ID):
                            print(f"Ignored message from unauthorized chat: {chat_id}")
                            continue

                        messages_processed += 1
                        print(f"\n[{messages_processed}] Processing message...")

                        # 處理訊息
                        process_result = process_message(message)

                        # 顯示結果
                        status = "OK" if process_result["success"] else "FAILED"
                        print(f"    Status: {status}")
                        print(f"    Type: {process_result['case_type']}")
                        if process_result["title"]:
                            print(f"    Title: {process_result['title'][:40]}")
                        if process_result["domain"]:
                            print(f"    Domain: {process_result['domain']}")
                        if process_result["error"]:
                            print(f"    Error: {process_result['error']}")

                        # 發送回覆
                        reply = format_reply(process_result)
                        send_reply(chat_id, reply)

                        # 測試模式：處理一則後退出
                        if test_mode:
                            print("\nTest mode: exiting after first message")
                            return

    except KeyboardInterrupt:
        print("\n\nBot stopped by user")
    finally:
        print(f"\nTotal messages processed: {messages_processed}")


def main():
    parser = argparse.ArgumentParser(description="Quick Capture Bot")
    parser.add_argument("--test", action="store_true", help="Test mode")
    args = parser.parse_args()

    run_bot(test_mode=args.test)


if __name__ == "__main__":
    main()
