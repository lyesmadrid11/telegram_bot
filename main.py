from flask import Flask, request
import requests, os
app = Flask(__name__)
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

@app.route('/')
def home():
    return "Bot 24h ON ✅"

@app.route('/webhook', methods=['POST','GET'])
def webhook():
    if request.method == 'GET':
        return "Webhook شغال"
    data = request.get_json(force=True)
    text = str(data.get("text", data))
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
