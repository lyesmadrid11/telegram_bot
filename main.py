from flask import Flask
import requests, time, threading, os
import numpy as np
app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
COINS = ["DEXEUSDT","BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","DOTUSDT","LINKUSDT","MATICUSDT","LTCUSDT","BCHUSDT","XLMUSDT","UNIUSDT","ETCUSDT","FILUSDT","TRXUSDT","VETUSDT","ICPUSDT","NEARUSDT","APTUSDT","ARBUSDT","OPUSDT","SUIUSDT","PEPEUSDT","SHIBUSDT","DOGEUSDT","AAVEUSDT","ATOMUSDT","GRTUSDT","INJUSDT","LDOUSDT","MKRUSDT","RNDRUSDT","STXUSDT","TIAUSDT","WIFUSDT","ARUSDT","FETUSDT","AGIXUSDT","WLDUSDT","JASMYUSDT","BONKUSDT","FLOKIUSDT","SEIUSDT","JUPUSDT","PYTHUSDT","ENAUSDT","WUSDT","TAOUSDT","RENDERUSDT","ONDOUSDT","NOTUSDT","ZKUSDT"]
TIMEFRAMES = ["4h", "1d"]
def send(t):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id":CHAT_ID,"text":t}, timeout=10)
    except:
        pass
def get_klines(s, tf):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={s}&interval={tf}&limit=500"
        r = requests.get(url, timeout=15).json()
        l = np.array([float(x[3]) for x in r])
        c = np.array([float(x[4]) for x in r])
        return l,c
    except:
        return None,None
def ema(a,p):
    k=2/(p+1); e=np.zeros(len(a)); e[0]=a[0]
    for i in range(1,len(a)): e[i]=a[i]*k+e[i-1]*(1-k)
    return e
def macd_line(c):
    return ema(c,12)-ema(c,26)
def pivot_lows(l):
    res=[]
    for i in range(5,len(l)-5):
        ok=True
        for k in range(1,6):
            if not (l[i]<l[i-k] and l[i]<l[i+k]):
                ok=False; break
        if ok:
            res.append(i)
    return res
def check_div_blue(s,tf):
    l,c=get_klines(s,tf)
    if c is None:
        return None
    m=macd_line(c)
    pls=pivot_lows(l)
    if len(pls)<2:
        return None
    for i in range(len(pls)-1,-1,-1):
        p1=pls[i]
        if len(c)-1-p1>10:
            break
        for j in range(i-1,-1,-1):
            p2=pls[j]
            if p1-p2>30:
                break
            if l[p1]<l[p2] and m[p1]>m[p2]:
                return "DIV BLUE " + tf + " " + s + " " + str(round(float(l[p2]),4)) + " -> " + str(round(float(l[p1]),4))
    if l[-1]<l[-2] and l[-1]<l[-3] and l[-1]<l[-4]:
        for p2 in pls[-5:]:
            if l[-1]<l[p2] and m[-1]>m[p2]:
                return "DIV BLUE RT " + tf + " " + s + " NOW"
    return None
def loop():
    send("Bot DIV BLUE 4H+1D ON - 57 coins")
    while True:
        for tf in TIMEFRAMES:
            for co in COINS:
                try:
                    r=check_div_blue(co,tf)
                    if r:
                        send(r)
                except:
                    pass
                time.sleep(0.3)
        time.sleep(1800)
@app.route("/")
def home():
    return "DIV BLUE Live"

threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000))
