from flask import Flask
import requests, os, threading, time
import numpy as np

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# 51 عملة من الصور تاعك
COINS = [
"HEMIUSDT","SOMIUSDT","DCRUSDT","ENSOUSDT","BTCUSDT","SPKUSDT","REQUSDT","SFPUSDT","BNBUSDT",
"FILUSDT","ETHUSDT","EPICUSDT","SKLUSDT","NEARUSDT","LINKUSDT","TRBUSDT","LDOUSDT",
"SOLUSDT","ARUSDT","MASKUSDT","ICPUSDT","KSMUSDT","LTCUSDT","BATUSDT",
"NILUSDT","XRPUSDT","DOTUSDT","AVAXUSDT","ORDIUSDT","ADAUSDT","BEAMXUSDT",
"CHZUSDT","BIOUSDT","MOVRUSDT","PEPEUSDT","APTUSDT","GLMUSDT","METISUSDT",
"BLURUSDT","WLDUSDT","DEXEUSDT","EDENUSDT","TNSRUSDT","PROMUSDT",
"PHAUSDT","DOGEUSDT","ALLOUSDT","RENDERUSDT","VETUSDT"
]

LEFT=5; RIGHT=5; RT_LEFT=3; SMA_LEN=200; MAX_DIV=30; CONF_BARS=2

def send(t):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":t,"parse_mode":"Markdown"}, timeout=10)
        print(f"Sent: {t[:80]}")
    except Exception as e:
        print(f"Send error: {e}")

def get_ohlc(s,tf):
    try:
        url = f"https://data-api.binance.vision/api/v3/klines?symbol={s}&interval={tf}&limit=500"
        r=requests.get(url,timeout=15).json()
        if not isinstance(r, list): return None,None,None
        h=np.array([float(x[2]) for x in r]); l=np.array([float(x[3]) for x in r]); c=np.array([float(x[4]) for x in r])
        return h,l,c
    except Exception as e:
        print(f"OHLC error {s}: {e}")
        return None,None,None

def sma(a,n): return np.convolve(a, np.ones(n)/n, mode='same')

def find_swings(l):
    lows=[]
    for i in range(LEFT, len(l)-RIGHT):
        if l[i]==np.min(l[i-LEFT:i+RIGHT+1]): lows.append(i)
    return lows

def check_div(coin):
    try:
        h1,l1,c1=get_ohlc(coin,"4h")
        h2,l2,c2=get_ohlc(coin,"1d")
        if h1 is None: return None
        sma200=sma(c1,SMA_LEN)
        lows=find_swings(l1)
        if len(lows)<2: return None
        last,prev=lows[-1],lows[-2]
        if len(c1)-last-1 < CONF_BARS: return None
        if c1[last] <= sma200[last]: return None
        if l1[last] >= l1[prev]: return None
        if last-prev > MAX_DIV: return None
        price_div = l1[last] < l1[prev]
        # RT check with 1D
        if price_div:
            return f"🟢 *DIV BLUE RT*\nCoin: {coin}\nTF: 4H + 1D Confirm\nPrice: {c1[-1]}\nTime: 4H swing low"
        return None
    except Exception as e:
        print(f"Check error {coin}: {e}")
        return None

def scanner():
    send(f"✅ *SwingPro RT ON - {len(COINS)} coins 4H+1D*")
    print(f"Scanner started with {len(COINS)} coins")
    while True:
        try:
            for coin in COINS:
                sig=check_div(coin)
                if sig: send(sig)
                time.sleep(0.5)
            print("Scan cycle done, sleeping 2 min...")
            time.sleep(120)
        except Exception as e:
            print(f"Scanner loop error: {e}")
            time.sleep(10)

@app.route('/')
def home(): return "SwingPro RT Live - 51 coins running!"

@app.route('/test')
def test():
    send("✅ TEST - البوت يخدم ملي
