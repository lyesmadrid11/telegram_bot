from flask import Flask
import requests, os, threading, time
import numpy as np

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

COINS = ["HEMIUSDT","SOMIUSDT","DCRUSDT","ENSOUSDT","EURUSDT","BTCUSDT","SPKUSDT","REQUSDT","SFPUSDT","BNBUSDT","FILUSDT","ETHUSDT","EPICUSDT","SKLUSDT","NEARUSDT","LINKUSDT","TRBUSDT","LDOUSDT","SOLUSDT","ARUSDT","MASKUSDT","ICPUSDT","KSMUSDT","LTCUSDT","BATUSDT","NILUSDT","XRPUSDT","DOTUSDT","AVAXUSDT","ORDIUSDT","ADAUSDT","BEAMXUSDT","CHZUSDT","BIOUSDT","MOVRUSDT","PEPEUSDT","APTUSDT","GLMUSDT","METISUSDT","BLURUSDT","WLDUSDT","DEXEUSDT","EDENUSDT","TNSRUSDT","PROMUSDT","PHAUSDT","DOGEUSDT","ALLOUSDT","RENDERUSDT","VETUSDT"]

LEFT=5
RIGHT=5
SMA_LEN=200
MAX_DIV=30
CONF_BARS=2

def send(t):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id":CHAT_ID,"text":t,"parse_mode":"Markdown"}, timeout=10)
        print(f"Sent: {t[:100]}")
    except Exception as e:
        print(f"Send err: {e}")

def get_ohlc(symbol, tf):
    try:
        url = f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval={tf}&limit=500"
        r = requests.get(url, timeout=15).json()
        if not isinstance(r, list):
            return None,None,None
        h = np.array([float(x[2]) for x in r])
        l = np.array([float(x[3]) for x in r])
        c = np.array([float(x[4]) for x in r])
        return h,l,c
    except Exception as e:
        print(f"OHLC {symbol} err: {e}")
        return None,None,None

def sma(arr, n):
    if len(arr) < n:
        return np.array([0]*len(arr))
    ret = np.cumsum(arr, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret / n

def find_lows(l):
    res=[]
    for i in range(LEFT, len(l)-RIGHT):
        window = l[i-LEFT:i+RIGHT+1]
        if l[i] == np.min(window):
            res.append(i)
    return res

def check(coin):
    try:
        h,l,c = get_ohlc(coin, "4h")
        if h is None:
            return None
        if len(c) < 210:
            return None
        s = sma(c, SMA_LEN)
        lows = find_lows(l)
        if len(lows) < 2:
            return None
        last = lows[-1]
        prev = lows[-2]
        if len(c)-last-1 < CONF_BARS:
            return None
        if c[last] < s[last]:
            return None
        if l[last] >= l[prev]:
            return None
        if last-prev > MAX_DIV:
            return None
        price = c[-1]
        txt = f"🟢 *DIV BLUE RT*\nCoin: {coin}\nPrice: {price:.4f}\nTF: 4H + SMA200"
        return txt
    except Exception as e:
        print(f"Check {coin} err: {e}")
        return None

def scanner():
    time.sleep(5)
    send(f"✅ SwingPro RT ON - {len(COINS)} coins")
    while True:
        try:
            for coin in COINS:
                sig = check(coin)
                if sig:
                    send(sig)
                time.sleep(1)
            print("Cycle done - sleep 2 min")
            time.sleep(120)
        except Exception as e:
            print(f"Loop err: {e}")
            time.sleep(10)

@app.route('/')
def home():
    return "SwingPro RT - 51 coins running!"

@app.route('/test')
def test():
    send("✅ TEST OK - البوت يخدم!")
    return "TEST SENT"

threading.Thread(target=scanner, daemon=True).start()
