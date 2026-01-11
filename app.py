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
from datetime import datetime
import requests

# 環境變數
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 導入模組
from message_parser import parse_telegram_message, determine_save_action
from reader_client import save_url, save_note
from ai_filter import process_capture_content, detect_domain

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
        "error": None
    }

    try:
        if action["save_method"] == "save_url":
            url = action["url"]
            tags = ["#TG收集"]

            domain = detect_domain(parsed.text)
            if domain != "其他":
                tags.append(f"@{domain}")
            result["domain"] = domain

            user_note = action.get("user_note")
            if parsed.is_forward and parsed.channel_name:
                source_note = f"來源：{parsed.channel_name}"
                user_note = f"{source_note}\n\n{user_note}" if user_note else source_note

            doc = save_url(url=url, tags=tags, notes=user_note)
            if doc:
                result["success"] = True
                result["title"] = doc.get("title") or url[:50]

        elif action["save_method"] == "save_note":
            content = action["content"]
            ai_result = process_capture_content(content)

            result["title"] = ai_result["title"]
            result["domain"] = ai_result["domain"]

            tags = ["#TG收集", ai_result["domain_tag"]]

            doc = save_note(
                content=content,
                title=ai_result["title"],
                source_name=parsed.source_label,
                tags=tags
            )
            if doc:
                result["success"] = True

    except Exception as e:
        result["error"] = str(e)

    return result


def format_reply(result: dict) -> str:
    """格式化回覆訊息"""
    if result["success"]:
        lines = ["<b>OK</b> 已存入 Reader"]
        if result["title"]:
            lines.append(f"<b>{result['title'][:40]}</b>")
        if result["domain"]:
            emoji = {"醫學": "🏥", "AI": "🤖", "國際": "🌍", "知識": "📚",
                     "生產力": "⚡", "生活": "🏠"}.get(result["domain"], "📌")
            lines.append(f"{emoji} {result['domain']}")
        if result["source"] and result["source"] != "我的筆記":
            lines.append(f"📍 {result['source']}")
        return "\n".join(lines)
    return f"Error\n{result.get('error', '未知錯誤')}"


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok", "service": "Quick Capture Bot"})


@app.route("/webhook", methods=["POST"])
def webhook():
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
    # 從環境變數或參數取得 host
    host = request.args.get("host") or os.getenv("ZEABUR_URL") or request.host
    # 確保使用 HTTPS
    if not host.startswith("http"):
        webhook_url = f"https://{host}/webhook"
    elif host.startswith("http://"):
        webhook_url = host.replace("http://", "https://") + "/webhook"
    else:
        webhook_url = f"{host}/webhook"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    r = requests.post(url, json={"url": webhook_url})
    return jsonify({"webhook_url": webhook_url, "result": r.json()})


@app.route("/delete_webhook", methods=["GET"])
def delete_webhook():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
    return jsonify(requests.post(url).json())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
