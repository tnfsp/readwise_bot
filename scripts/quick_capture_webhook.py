"""
Quick Capture - Webhook 版本（適用於 Zeabur 部署）

部署步驟：
1. 推送到 GitHub
2. 在 Zeabur 連接 GitHub repo
3. 設定環境變數（READWISE_TOKEN, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, ANTHROPIC_API_KEY,
   WEBHOOK_SECRET）
4. 部署後取得 URL，設定 Telegram Webhook
"""
import os
import sys
from datetime import datetime

# 確保可以 import 同目錄的模組
scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)

# 載入環境變數（從專案根目錄）
from dotenv import load_dotenv
root_dir = os.path.dirname(scripts_dir)
load_dotenv(os.path.join(root_dir, '.env'))

from flask import Flask, request, jsonify
import requests

# 直接從環境變數讀取（避免 config.py 路徑問題）
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

# 共用邏輯從 capture_service 引入
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
    """健康檢查"""
    return jsonify({
        "status": "ok",
        "service": "Quick Capture Bot",
        "time": datetime.utcnow().isoformat() + "Z"
    })


@app.route("/webhook", methods=["POST"])
def webhook():
    """Telegram Webhook 端點"""
    # Telegram Webhook Secret Token 驗證（#13）
    if WEBHOOK_SECRET:
        incoming_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if incoming_token != WEBHOOK_SECRET:
            print(f"Webhook forbidden: invalid secret token")
            return jsonify({"status": "forbidden"}), 403

    try:
        update = request.get_json()

        if "message" in update:
            message = update["message"]
            chat_id = message["chat"]["id"]

            # 只處理來自授權用戶的訊息
            if str(chat_id) != str(TELEGRAM_CHAT_ID):
                print(f"Ignored message from unauthorized chat: {chat_id}")
                return jsonify({"status": "ignored"})

            # 處理訊息（使用 capture_service 共用邏輯）
            result = process_message(message)

            # 發送回覆
            reply = format_reply(result)
            send_reply(chat_id, reply)

            print(f"Processed: {result['case_type']} - {result['title']}")

        return jsonify({"status": "ok"})

    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    """設定 Webhook（部署後訪問此端點一次）"""
    # 管理 endpoint 需認證（#11 #12）
    if not _check_management_secret():
        return jsonify({"status": "forbidden"}), 403

    host = request.host_url.rstrip("/")
    webhook_url = f"{host}/webhook"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    payload = {"url": webhook_url}
    if WEBHOOK_SECRET:
        payload["secret_token"] = WEBHOOK_SECRET  # 讓 Telegram 帶上 secret header

    response = requests.post(url, json=payload, timeout=15)
    if response.status_code == 200:
        return jsonify({
            "status": "ok",
            "webhook_url": webhook_url,
            "telegram_response": response.json()
        })
    else:
        return jsonify({
            "status": "error",
            "message": response.text
        }), 500


@app.route("/delete_webhook", methods=["GET"])
def delete_webhook():
    """刪除 Webhook（切換回 Polling 模式時使用）"""
    # 管理 endpoint 需認證（#11 #12）
    if not _check_management_secret():
        return jsonify({"status": "forbidden"}), 403

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
    response = requests.post(url, timeout=15)
    return jsonify(response.json())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Quick Capture Webhook on port {port}")
    app.run(host="0.0.0.0", port=port)
