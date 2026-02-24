"""
Quick Capture Bot - Zeabur 入口文件
"""
import os
import sys

# 添加 scripts 目錄到路徑
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
sys.path.insert(0, scripts_dir)

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
import requests

# 環境變數
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

# 導入共用邏輯
from capture_service import process_message, format_reply

app = Flask(__name__)


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


def _check_management_secret() -> bool:
    """驗證管理 endpoint 的 secret token（#11）"""
    if not WEBHOOK_SECRET:
        return True  # 未設定時不強制（開發模式）
    token = request.args.get("secret")
    return token == WEBHOOK_SECRET


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok", "service": "Quick Capture Bot"})


@app.route("/webhook", methods=["POST"])
def webhook():
    # Telegram Webhook Secret Token 驗證（#13）
    if WEBHOOK_SECRET:
        incoming_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if incoming_token != WEBHOOK_SECRET:
            return jsonify({"status": "forbidden"}), 403

    try:
        update = request.get_json()
        if "message" in update:
            message = update["message"]
            chat_id = message["chat"]["id"]

            if str(chat_id) != str(TELEGRAM_CHAT_ID):
                return jsonify({"status": "ignored"})

            result = process_message(message)
            send_reply(chat_id, format_reply(result))
            print(f"Processed: {result['case_type']} - {result.get('title', 'N/A')}")

        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error"}), 500


@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    # 管理 endpoint 需認證（#11 #12）
    if not _check_management_secret():
        return jsonify({"status": "forbidden"}), 403

    host = request.args.get("host") or os.getenv("ZEABUR_URL") or request.host
    if not host.startswith("http"):
        webhook_url = f"https://{host}/webhook"
    elif host.startswith("http://"):
        webhook_url = host.replace("http://", "https://") + "/webhook"
    else:
        webhook_url = f"{host}/webhook"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    payload = {"url": webhook_url}
    if WEBHOOK_SECRET:
        payload["secret_token"] = WEBHOOK_SECRET  # 讓 Telegram 帶上 secret header
    r = requests.post(url, json=payload, timeout=15)
    return jsonify({"webhook_url": webhook_url, "result": r.json()})


@app.route("/delete_webhook", methods=["GET"])
def delete_webhook():
    # 管理 endpoint 需認證（#11 #12）
    if not _check_management_secret():
        return jsonify({"status": "forbidden"}), 403

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
    return jsonify(requests.post(url, timeout=15).json())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
