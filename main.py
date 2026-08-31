from flask import Flask
import requests, os, threading, time
import numpy as np

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

COINS = ["DEXEUSDT","BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","DOTUSDT","LINKUSDT","MATICUSDT","LTCUSDT","BCHUSDT","XLMUSDT","UNIUSDT","ETCUSDT","FILUSDT","TRXUSDT","VETUSDT","ICPUSDT","NEARUSDT","APTUSDT","ARBUSDT","OPUSDT","SUIUSDT","PEPEUSDT","SHIBUSDT","DOGEUSDT","AAVEUSDT","ATOMUSDT","GRTUSDT","INJUSDT","LDOUSDT","MKRUSDT","RNDRUSDT","STXUSDT","TIAUSDT","WIFUSDT","ARUSDT","FETUSDT","AGIXUSDT","WLDUSDT","JASMYUSDT","BONKUSDT","FLOKIUSDT","SEIUSDT","JUPUSDT","PYTHUSDT","ENAUSDT","WUSDT","TAOUSDT","RENDERUSDT","ONDOUSDT","NOTUSDT","ZKUSDT"]

LEFT=5; RIGHT=5; RT_LEFT=3; SMA_LEN=200; MAX_DIV=30; CONF_BARS=2

def send(t):
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":t,"parse_mode":"Markdown"}, timeout=15)
    except: pass

def get_ohlc(s,tf):
    try:
        r=requests.get(f"https://api.binance.com/api/v3/klines?symbol={s}&interval={tf}&limit=500",timeout=15).json()
        h=np.array([float(x[2]) for x in r]); l=np.array([float(x[3]) for x in r]); c=np.array([float(x[4]) for x in r])
        return h,l,c
    except: return None,None,None

def ema(a,p):
    k=2/(p+1); e=np.zeros(len(a)); e[0]=a[0]
    for i in range(1,len(a)): e[i]=a[i]*k+e[i-1]*(1-k)
    return e

def sma(a,p): return np.convolve(a, np.ones(p)/p, mode='same')

def pivots_low(low):
    res=[]
    for i in range(LEFT, len(low)-RIGHT):
        if low[i] < min(low[i-LEFT:i]) and low[i] < min(low[i+1:i+RIGHT+1]): res.append(i)
    return res

def pivots_high(high):
    res=[]
    for i in range(LEFT, len(high)-RIGHT):
        if high[i] > max(high[i-LEFT:i]) and high[i] > max(high[i+1:i+RIGHT+1]): res.append(i)
    return res

def check_coin(sym,tf):
    high,low,close=get_ohlc(sym,tf)
    if close is None or len(close)<250: return None
    macd=ema(close,12)-ema(close,26)
    ma200=sma(close,SMA_LEN)
    isAbove=close[-1]>ma200[-1]
    lp=pivots_low(low); hp=pivots_high(high)
    if len(lp)<2 or len(hp)<1: return None
    resLevel=high[hp[-1]]

    # --- 1. BUY Classique comme Pine ---
    lastDivIdx=None; p1v=p2v=0
    for idx in range(len(lp)-1,-1,-1):
        p1=lp[idx]
        if len(close)-1-p1>10: break
        if p1+RIGHT>=len(high): continue
        if low[-1] <= high[p1+RIGHT]: continue # confCandle
        # low[1] > high[i+right] approximation
        for jdx in range(idx-1,-1,-1):
            p2=lp[jdx]
            if p1-p2>30: break
            if low[p1] < low[p2] and macd[p1] > macd[p2]:
                lastDivIdx=p1; p1v=p1; p2v=p2; break
        if lastDivIdx is not None: break

    if lastDivIdx is not None:
        # Breakout 2 bougies
        breakout=False
        if CONF_BARS==1: breakout=close[-1]>resLevel and close[-2]<=resLevel
        else:
            allAbove=all(close[-1-k]>resLevel for k in range(CONF_BARS))
            crossed=close[-1-CONF_BARS]<=resLevel
            breakout=allAbove and crossed
        if breakout and (len(close)-1-lastDivIdx<=MAX_DIV) and isAbove:
            return f"🔵 BUY Classique {tf.upper()} {sym} Div {low[p2v]:.4f}->{low[p1v]:.4f} Break {resLevel:.4f}"

    # --- 2. RT Temps Reel comme Pine ---
    is_partial=all(low[-1] < low[-1-k] for k in range(1,RT_LEFT+1))
    if is_partial and isAbove:
        for p2 in lp[-15:]:
            # secret Pine: p2 = j sans rightBars
            if low[-1] < low[p2] and macd[-1] > macd[p2]:
                return f"⚡🔵 DIV BLUE RT {tf.upper()} {sym} {low[p2]:.4f}->{low[-1]:.4f} ⚡"
    return None

def loop():
    send("✅ SwingPro RT ON - 57 coins 4H+1D")
    while True:
        for tf in ["4h","1d"]:
            for coin in COINS:
                try:
                    sig=check_coin(coin,tf)
                    if sig: send(sig)
                except: pass
                time.sleep(0.3)
        time.sleep(600)

@app.route("/")
def home(): return "SwingPro RT Live"
@app.route("/test")
def test(): send("🔵 TEST SwingPro RT - خدام"); return "Test sent"

threading.Thread(target=loop, daemon=True).start()
