from flask import Flask
import requests, os, threading, time

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send(t):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":t})

def loop():
    send("✅ Bot Live")
    while True:
        time.sleep(3600)

@app.route("/")
def home(): return "Live OK"

@app.route("/test")
def test():
    send("🔵 TEST - البوت خدام")
    return "Test sent"

threading.Thread(target=loop, daemon=True).start()
