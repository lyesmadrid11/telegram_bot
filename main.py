from flask import Flask
import requests, os, threading, time
import numpy as np

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

COINS = ["DEXEUSDT","BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","DOTUSDT","LINKUSDT","MATICUSDT"]

LEFT=5; RIGHT=5; RT_LEFT=3; SMA_LEN=200; MAX_DIV=30; CONF_BARS=2

def send(t):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":t,"parse_mode":"Markdown"}, timeout=10)
        print(f"Sent: {t[:50]}")
    except Exception as e:
        print(f"Send error: {e}")

def get_ohlc(s,tf):
    try:
        # بدّلنا الرابط باش يخدم في Render
        url = f"https://data-api.binance.vision/api/v3/klines?symbol={s}&interval={tf}&limit=500"
        r=requests.get(url,timeout=15).json()
        if not isinstance(r, list): return None,None,None
        h=np.array([float(x[2]) for x in r]); l=np.array([float(x[3]) for x in r]); c=np.array([float(x[4]) for x in r])
        return h,l,c
    except Exception as e:
        print(f"OHLC error {s}: {e}")
        return None,None,None

# هنا تكمل باقي الفنكسيون تاعك sma, swing etc... خليهم كيما راهم

def scanner():
    send("✅ SwingPro RT started on Render!")
    while True:
        try:
            for coin in COINS:
                h,l,c = get_ohlc(coin, "1h")
                if h is None: continue
                # هنا دير اللوجيك تاعك
                time.sleep(1)
            time.sleep(60)
        except Exception as e:
            print(f"Scanner error: {e}")
            time.sleep(10)

@app.route('/')
def home():
    return "SwingPro RT Live - Bot running!"

# هادي هي الصح باش يخدم مع gunicorn
threading.Thread(target=scanner, daemon=True).start()
