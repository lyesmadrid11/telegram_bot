from flask import Flask
import requests, os, threading, time
import numpy as np

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# 51 عملة تاعك كاملين
COINS = [
"BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","DOGEUSDT","PEPEUSDT","LINKUSDT",
"AVAXUSDT","ADAUSDT","DOTUSDT","NEARUSDT","RENDERUSDT","FILUSDT","ARUSDT","APTUSDT",
"LTCUSDT","WLDUSDT","DEXEUSDT","TRBUSDT","MASKUSDT","ICPUSDT","KSMUSDT","BATUSDT",
"ORDIUSDT","CHZUSDT","MOVRUSDT","GLMUSDT","METISUSDT","BLURUSDT","PHAUSDT","VETUSDT",
"SFPUSDT","SKLUSDT","LDOUSDT","BEAMXUSDT","TNSRUSDT","PROMUSDT","REQUSDT","ALLOUSDT",
"DCRUSDT","SUIUSDT","NILUSDT","HEMIUSDT","SOMIUSDT","KERNELUSDT","EPICUSDT","EDENUSDT",
"ENSOUSDT","SPKUSDT","BIOUSDT"
]

LEFT=5; RIGHT=5; FAST=12; SLOW=26; SIG=9; SMA_LEN=200; MAX_DIV=30
FIRST_LOOK=10; SECOND_LOOK=30

# يحفظ آخر Div لي تبعت - باش ما يسباميش نفسها، بصح يبعث الجديدة
last_sent_4h = {}
last_sent_1d = {}

def send(t):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":t,"parse_mode":"Markdown"}, timeout=10)
    except: pass

def get_ohlc(s,tf):
    try:
        url=f"https://data-api.binance.vision/api/v3/klines?symbol={s}&interval={tf}&limit=500"
        r=requests.get(url,timeout=15).json()
        if not isinstance(r,list): return None
        h=np.array([float(x[2]) for x in r]); l=np.array([float(x[3]) for x in r]); c=np.array([float(x[4]) for x in r])
        return h,l,c
    except: return None

def calc_ema(data, period):
    alpha = 2/(period+1)
    ema = np.zeros(len(data)); ema[0]=data[0]
    for i in range(1,len(data)): ema[i]=alpha*data[i]+(1-alpha)*ema[i-1]
    return ema

def macd(close):
    ef=calc_ema(close, FAST); es=calc_ema(close, SLOW)
    return ef-es, calc_ema(ef-es, SIG)

def sma(a,n):
    ret=np.cumsum(a, dtype=float); ret[n:]=ret[n:]-ret[:-n]
    return ret/n

def pivot_low(low, idx):
    if idx < LEFT or idx >= len(low)-RIGHT: return False
    return low[idx] == np.min(low[idx-LEFT:idx+RIGHT+1])

def check_blue_div_exact(coin, tf):
    data=get_ohlc(coin,tf)
    if data is None: return None, None
    high,low,close=data
    if len(close)<250: return None, None
    macd_line,_ = macd(close)
    ma200=sma(close,SMA_LEN)

    for i in range(1, FIRST_LOOK+RIGHT+1):
        p1_idx = len(close)-1 - i - RIGHT
        if p1_idx < 0: continue
        if not pivot_low(low, p1_idx): continue
        p1_bar = p1_idx + RIGHT
        if p1_bar >= len(high): continue
        if not (low[-1] > high[p1_bar] and low[-2] <= high[p1_bar]): continue
        if close[p1_idx] < ma200[p1_idx]: continue

        for j in range(i+1, i+SECOND_LOOK+1):
            p2_idx = len(close)-1 - j - RIGHT
            if p2_idx < 0: continue
            if not pivot_low(low, p2_idx): continue
            if low[p1_idx] >= low[p2_idx]: continue
            if macd_line[p1_idx] <= macd_line[p2_idx]: continue
            if abs(p1_idx-p2_idx) > MAX_DIV: continue
            cross=False
            for x in range(p2_idx, p1_idx+1):
                y = ((low[p1_idx]-low[p2_idx])/(p1_idx-p2_idx))*(x-p2_idx)+low[p2_idx]
                if low[x] < y - 0.0001: cross=True; break
            if cross: continue

            msg = f"🟦 *DIV BLUE - {coin} {tf}*\nPrice: {close[-1]:.5f}\nLow: {low[p1_idx]:.5f} < {low[p2_idx]:.5f}"
            return msg, p1_idx
    return None, None

def scanner():
    time.sleep(5)
    send(f"✅ Bot ON - DIV BLUE ONLY - 51 coins - 4H & 1D - New Div Only")
    while True:
        try:
            for coin in COINS:
                sig, idx = check_blue_div_exact(coin,"4h")
                if sig and last_sent_4h.get(coin)!= idx:
                    send(sig)
                    last_sent_4h[coin]=idx

                sig, idx = check_blue_div_exact(coin,"1d")
                if sig and last_sent_1d.get(coin)!= idx:
                    send(sig)
                    last_sent_1d[coin]=idx

                time.sleep(0.8)
            print(f"Scan done - 4H:{len(last_sent_4h)} 1D:{len(last_sent_1d)}")
            time.sleep(180)
        except Exception as e:
            print(e); time.sleep(10)

@app.route('/')
def home(): return f"DIV BLUE - {len(COINS)} coins - New Div Logic"
@app.route('/test')
def test(): send("✅ TEST - New Div Logic"); return "OK"
threading.Thread(target=scanner, daemon=True).start()
