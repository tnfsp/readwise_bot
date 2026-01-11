"""
Quick Capture - Webhook 版本（適用於 Zeabur 部署）

部署步驟：
1. 推送到 GitHub
2. 在 Zeabur 連接 GitHub repo
3. 設定環境變數（READWISE_TOKEN, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, ANTHROPIC_API_KEY）
4. 部署後取得 URL，設定 Telegram Webhook
"""
import os
import sys

# 確保可以 import 同目錄的模組
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from datetime import datetime

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from message_parser import parse_telegram_message, determine_save_action
from reader_client import save_url, save_note
from ai_filter import process_capture_content, detect_domain
import requests

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
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending reply: {e}")


def process_message(message: dict) -> dict:
    """處理單一訊息"""
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
            tags = ["#TG收集"]

            domain = detect_domain(parsed.text)
            domain_tag = f"@{domain}" if domain != "其他" else None
            if domain_tag:
                tags.append(domain_tag)
            result["domain"] = domain

            user_note = action.get("user_note")
            if parsed.is_forward and parsed.channel_name:
                source_note = f"來源：{parsed.channel_name}"
                if user_note:
                    user_note = f"{source_note}\n\n{user_note}"
                else:
                    user_note = source_note

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
    """格式化回覆訊息"""
    if result["success"]:
        lines = ["<b>OK</b> 已存入 Reader"]

        if result["title"]:
            title = result["title"][:40]
            lines.append(f"<b>{title}</b>")

        if result["domain"]:
            domain_emoji = {
                "醫學": "🏥", "AI": "🤖", "國際": "🌍",
                "知識": "📚", "生產力": "⚡", "生活": "🏠", "其他": "📌"
            }
            emoji = domain_emoji.get(result["domain"], "📌")
            lines.append(f"{emoji} {result['domain']}")

        if result["source"] and result["source"] != "我的筆記":
            lines.append(f"📍 {result['source']}")

        return "\n".join(lines)
    else:
        return f"Error 存入失敗\n{result.get('error', '未知錯誤')}"


@app.route("/", methods=["GET"])
def index():
    """健康檢查"""
    return jsonify({
        "status": "ok",
        "service": "Quick Capture Bot",
        "time": datetime.now().isoformat()
    })


@app.route("/webhook", methods=["POST"])
def webhook():
    """Telegram Webhook 端點"""
    try:
        update = request.get_json()

        if "message" in update:
            message = update["message"]
            chat_id = message["chat"]["id"]

            # 只處理來自授權用戶的訊息
            if str(chat_id) != str(TELEGRAM_CHAT_ID):
                print(f"Ignored message from unauthorized chat: {chat_id}")
                return jsonify({"status": "ignored"})

            # 處理訊息
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
    # 從請求中獲取 host
    host = request.host_url.rstrip("/")
    webhook_url = f"{host}/webhook"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    response = requests.post(url, json={"url": webhook_url})

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
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
    response = requests.post(url)
    return jsonify(response.json())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Quick Capture Webhook on port {port}")
    app.run(host="0.0.0.0", port=port)
