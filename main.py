from flask import Flask, request
import requests, os

app = Flask(__name__)
TOKEN = os.environ.get("BOT_TOKEN")

@app.route('/')
def home():
    return "Bot 24h ON ✅"

@app.route('/webhook', methods=['POST','GET'])
def webhook():
    if request.method == 'GET':
        return "Webhook جاهز"
    
    data = request.get_json(force=True)
    
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text == "/start":
            reply = "مرحبا الياس! البوت راه يخدم ✅ 24/24"
        else:
            reply = f"وصلتني: {text}"
            
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": reply})
    
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
