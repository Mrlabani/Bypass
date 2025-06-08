import os
import requests
from urllib.parse import urlparse
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GPLINKS_API_KEY = os.environ.get("GPLINKS_API_KEY")

def bypass_gplink(url):
    session = requests.Session()
    domain = urlparse(url).netloc
    if "gplinks.co" not in domain:
        return None
    api_url = "https://gplinks.co/api"
    resp = session.get(f"{api_url}?api={GPLINKS_API_KEY}&url={url}")
    data = resp.json()
    return data.get("shortenedUrl")

def send_telegram_message(text, chat_id=None):
    payload = {
        "chat_id": chat_id or CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    return requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=payload)

@app.route("/", methods=["GET"])
def home():
    return "GPLinks Bypass Bot API is running"

@app.route("/bypass", methods=["POST"])
def bypass():
    data = request.json
    original_link = data.get("url")
    requested_by = data.get("user", "Unknown")
    user_id = data.get("user_id", "N/A")
    chat_id = data.get("chat_id", CHAT_ID)

    if not original_link:
        return jsonify({"error": "Missing URL"}), 400

    bypassed = bypass_gplink(original_link)
    if not bypassed:
        return jsonify({"error": "Bypass failed"}), 500

    message = f"""┎ 🔗 Original Link :- {original_link}
┃
┖ 🔓 Bypassed Link : [Click Here]({bypassed})

━━━━━━━✦✗✦━━━━━━━

👤 Requested By :- {requested_by} (#ID_{user_id})
"""
    send_telegram_message(message, chat_id)
    return jsonify({"status": "sent", "bypassed_link": bypassed})
  
