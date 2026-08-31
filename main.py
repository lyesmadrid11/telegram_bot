from flask import Flask
import requests, time, threading, os

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

COINS = ["DEXEUSDT","BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","DOTUSDT","LINKUSDT","MATICUSDT","LTCUSDT","BCHUSDT","XLMUSDT","UNIUSDT","ETCUSDT","FILUSDT","TRXUSDT","VETUSDT","ICPUSDT","NEARUSDT","APTUSDT","ARBUSDT","OPUSDT","SUIUSDT","PEPEUSDT","SHIBUSDT","DOGEUSDT","AAVEUSDT","ATOMUSDT","GRTUSDT","INJUSDT","LDOUSDT","MKRUSDT","RNDRUSDT","STXUSDT","TIAUSDT","WIFUSDT","ARUSDT","FETUSDT","AGIXUSDT","WLDUSDT","JASMYUSDT","BONKUSDT","FLOKIUSDT","SEIUSDT","JUPUSDT","PYTHUSDT","ENAUSDT","WUSDT","TAOUSDT","RENDERUSDT","ONDOUSDT","NOTUSDT","ZKUSDT"]

def send(t):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":t}, timeout=15)
    except: pass

def get_klines(s, tf):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/klines?symbol={s}&interval={tf}&limit=300", timeout=15).json()
        c = [float(x[4]) for x in r]
        return c
    except:
        return None

def check_div(c):
    if c is None or len(c) < 200: return False
    # تبسيط: اذا السعر كسر قاع 20 شمعة و رجع طلع بقوة = اشارة مؤقتة للتيست
    last = c[-1]
    low20 = min(c[-21:-1])
    if last > low20 * 1.02 and
