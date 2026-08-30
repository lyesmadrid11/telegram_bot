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

def get_klines(s, tf):
    try:
        url=f"https://api.binance.com/api/v3/klines?symbol={s}&interval={tf}&limit=500"
        r=requests.get(url, timeout=15).json()
        h=np.array([float(x[2]) for x in r]); l=np.array([float(x[3]) for x in r]); c=np.array([float(x[4]) for x in r])
        return h,l,c
    except: return None,None,None

def ema(a,p):
    k=2/(p+1); e=np.zeros(len(a)); e[0]=a[0]
    for i in range(1,len(a)): e[i]=a[i]*k+e[i-1]*(1-k)
    return e

def macd_line(c): return ema(c,12)-ema(c,26)

def pivot_lows(l, left=5, right=5):
    res=[]
    for i in range(left, len(l)-right):
        if all(l[i]<l[i-k] for k in range(1,left+1)) and all(l[i]<l[i+k] for k in range(1,right+1)):
            res.append(i)
    return res

def check_div_blue(s, tf):
    h,l,c = get_klines(s, tf)
    if c is None or len(c)<200: return None
    m = macd_line(c)
    pls = pivot_lows(l, 5, 5)

    # --- DIV BLUE CLASSIQUE كيما في كودك ---
    for idx in range(len(pls)-1, -1, -1):
        p1 = pls[idx]
        if len(c)-1 - p1 > 10: break # firstLookbackBull = 10

        # شرط كسر المقاومة تاعك ما نحتاجوهش، نحبو غير DIV
        for jdx in range(idx-1, -1, -1):
            p2 = pls[jdx]
            if p1 - p2 > 30: break # lowerLowLookbackBull = 30

            if l[p1] < l[p2] and m[p1] > m[p2]: # low اقل و macd اعلى
                # فحص الميل باش ما يقطعش السعر الخط
                cross=False
                for x in range(p2+1, p1):
                    y = (l[p1]-l[p2])/(p1-p2)*(x-p2)+l[p2]
                    if l[x] < y: cross=True; break
                if cross: continue
                return f"🔵 *DIV BLUE {
