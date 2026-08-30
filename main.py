
from flask import Flask
import requests, time, threading, os
import numpy as np
app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

COINS = ["DEXEUSDT","BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","DOTUSDT","LINKUSDT","MATICUSDT","LTCUSDT","BCHUSDT","XLMUSDT","UNIUSDT","ETCUSDT","FILUSDT","TRXUSDT","VETUSDT","ICPUSDT","NEARUSDT","APTUSDT","ARBUSDT","OPUSDT","SUIUSDT","PEPEUSDT","SHIBUSDT","DOGEUSDT","AAVEUSDT","ATOMUSDT","GRTUSDT","INJUSDT","LDOUSDT","MKRUSDT","RNDRUSDT","STXUSDT","TIAUSDT","WIFUSDT","ARUSDT","FETUSDT","AGIXUSDT","WLDUSDT","JASMYUSDT","BONKUSDT","FLOKIUSDT","SEIUSDT","JUPUSDT","PYTHUSDT","ENAUSDT","WUSDT","TAOUSDT","RENDERUSDT","ONDOUSDT","NOTUSDT","ZKUSDT"]
TIMEFRAMES = ["4h", "1d"]

def send(t):
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":t,"parse_mode":"Markdown"}, timeout=10)
    except: pass

def get(s, tf):
    try:
        r=requests.get(f"https://api.binance.com/api/v3/klines?symbol={s}&interval={tf}&limit=500", timeout=15).json()
        l=np.array([float(x[3]) for x in r]); c=np.array([float(x[4]) for x in r])
        return l,c
    except: return None,None

def ema(a,p):
    k=2/(p+1); e=np.zeros(len(a)); e[0]=a[0]
    for i in range(1,len(a)): e[i]=a[i]*k+e[i-1]*(1-k)
    return e

def macd_line(c): return ema(c,12)-ema(c,26)

def pivots(l):
    res=[]
    for i in range(5,len(l)-5):
        if all(l[i]<l[i-k] for k in range(1,6)) and all(l[i]<l[i+k] for k in range(1,6)): res.append(i)
    return res

def check_div(s, tf):
    l,c = get(s, tf)
    if c is None or len(c)<100: return None
    m=macd_line(c)
    pls=pivots(l)
    if len(pls)<2: return None

    # DIV BLUE CLASSIQUE
    for i in range(len(pls)-1,0,-1):
        p1=pls[i]
        if len(c)-1-p1>10: break
        for j in range(i-1,-1,-1):
            p2=pls[j]
            if p1-p2>30: break
            if l[p1]<l[p2] and m[p1]>m[p2]:
                return f"🔵 *DIV BLUE {tf.upper()}* `{s}`\nPrice {l[p2]:.4f} -> {l[p1]:.4f}\nTF: {tf}"

    # DIV BLUE RT
    if all(l[-1]<l[-1-k] for k in range(1,4)):
        for p2 in pls[-5:]:
            if l[-1]<l[p2] and m[-1]>m[p2]:
                return f"⚡🔵 *DIV BLUE RT {tf.upper()}* `{s}`\nالان!"
    return None

def loop():
    send("✅ *Bot DIV BLUE ON*\n📊 يراقب: 4H + 1D\n🪙 57 عملة مع DEXE\nيرسل غير 🔵 DIV BLUE")
    while True:
        for tf in TIMEFRAMES:
            for co in COINS:
                try:
                    r=check_div(co, tf)
                    if r: send(r)
                except: pass
                time.sleep(0.3)
        time.sleep(1800) # كل 30 دقيقة يعاود يفحص 4H و 1D

threading.Thread(target=loop, daemon=True).start()
@app.route("/")
def home(): return "DIV BLUE 4H+1D Live"
if __name__=="__main__": app.run(host="0.0.0.0", port=10000)
