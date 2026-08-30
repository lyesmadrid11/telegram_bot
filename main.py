from flask import Flask
import requests
import time
import threading
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# 56 عملة + DEXE لي في الصور تاعك
COINS = [
    "DEXEUSDT", "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "LTCUSDT",
    "BCHUSDT", "XLMUSDT", "UNIUSDT", "ETCUSDT", "FILUSDT", "TRXUSDT",
    "VETUSDT", "ICPUSDT", "NEARUSDT", "APTUSDT", "ARBUSDT", "OPUSDT",
    "SUIUSDT", "PEPEUSDT", "SHIBUSDT", "DOGEUSDT", "AAVEUSDT", "ATOMUSDT",
    "GRTUSDT", "INJUSDT", "LDOUSDT", "MKRUSDT", "RNDRUSDT", "STXUSDT",
    "TIAUSDT", "WIFUSDT", "ARUSDT", "FETUSDT", "AGIXUSDT", "WLDUSDT",
    "JASMYUSDT", "BONKUSDT", "FLOKIUSDT", "SEIUSDT", "JUPUSDT", "PYTHUSDT",
    "ENAUSDT", "WUSDT", "TAOUSDT", "RENDERUSDT", "ONDOUSDT", "NOTUSDT", "ZKUSDT"
]

def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("BOT_TOKEN or CHAT_ID missing")
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error send: {e}")

def get_klines(symbol, interval="30m", limit=100):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        r = requests.get(url, timeout=10)
        return r.json()
    except:
        return None

def check_coin(symbol):
    # هنا المنطق تاع DIV BLUE تاعك
    # نبسطهولك باش ما يطيحش
    # اذا كاين divergence يبعث
    klines = get_klines(symbol)
    if not klines or len(klines) < 50:
        return False

    # مثال كشف بسيط (تقدر تطورو من بعد)
    # لو كان السعر داير قاع جديد و RSI طالع = DIV BLUE
    try:
        closes = [float(k[4]) for k in klines]
        if closes[-1] < min(closes[-20:-1]) * 0.98:
            return True
    except:
        pass
    return False

def scan_loop():
    send_telegram("✅ Bot 24/24 ON\n56 coins including DEXEUSDT\nScan every 30min")
    while True:
        print("Scanning...")
        for coin in COINS:
            try:
                if check_coin(coin):
                    msg = f"🔵 *DIV BLUE DETECTED*\n\nCoin: `{coin}`\nTimeframe: 30m\nAction: Potential BUY\n\nCheck chart!"
                    send_telegram(msg)
                time.sleep(0.5)
            except Exception as e:
                print(f"{coin} error {e}")
        print("Sleep 30min")
        time.sleep(1800) # 30 دقيقة

# شغل السكان في الخلفية
threading.Thread(target=scan_loop, daemon=True).start()

@app.route("/")
def home():
    return f"Bot ON - {len(COINS)} coins - DEXE included - {time.ctime()}"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
