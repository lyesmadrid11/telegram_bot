from flask import Flask
import requests, time, threading, os
import numpy as np

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

COINS = ["DEXEUSDT","BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","DOTUSDT","LINKUSDT","MATICUSDT","LTCUSDT","BCHUSDT","XLMUSDT","UNIUSDT","ETCUSDT","FILUSDT","TRXUSDT","VETUSDT","ICPUSDT","NEARUSDT","APTUSDT","ARBUSDT","OPUSDT","SUIUSDT","PEPEUSDT","SHIBUSDT","DOGEUSDT","AAVEUSDT","ATOMUSDT","GRTUSDT","INJUSDT","LDOUSDT","MKRUSDT","RNDRUSDT","STXUSDT","TIAUSDT","WIFUSDT","ARUSDT","FETUSDT","AGIXUSDT","WLDUSDT","JASMYUSDT","BONKUSDT","FLOKIUSDT","SEIUSDT","JUPUSDT","PYTHUSDT","ENAUSDT","WUSDT","TAOUSDT","RENDERUSDT","ONDOUSDT","NOTUSDT","ZKUSDT"]
TIMEFRAMES = ["4h", "1d"]

# نفس اعدادات Pine تاعك
LEFT = 5
RIGHT = 5
RT_LEFT = 3
SMA_LEN = 200
MAX_DIV = 30

def send(t):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": t, "parse_mode": "Markdown"}, timeout=15)
    except: pass

def get_ohlc(symbol, tf):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={tf}&limit=500", timeout=15).json()
        high = np.array([float(x[2]) for x in r])
        low = np.array([float(x[3]) for x in r])
        close = np.array([float(x[4]) for x in r])
        return high, low, close
    except:
        return None, None, None

def ema(a, p):
    k = 2/(p+1)
    e = np.zeros(len(a))
    e[0] = a[0]
    for i in range(1, len(a)):
        e[i] = a[i]*k + e[i-1]*(1-k)
    return e

def sma(a, p):
    return np.convolve(a, np.ones(p)/p, mode='same')

def pivots_low(low):
    res = []
    for i in range(LEFT, len(low)-RIGHT):
        is_pivot = True
        for k in range(1, LEFT+1):
            if low[i] >= low[i-k]: is_pivot=False
        for k in range(1, RIGHT+1):
            if low[i] >= low[i+k]: is_pivot=False
        if is_pivot: res.append(i)
    return res

def pivots_high(high):
    res = []
    for i in range(LEFT, len(high)-RIGHT):
        is_pivot = True
        for k in range(1, LEFT+1):
            if high[i] <= high[i-k]: is_pivot=False
        for k in range(1, RIGHT+1):
            if high[i] <= high[i+k]: is_pivot=False
        if is_pivot: res.append(i)
    return res

def check_coin(symbol, tf):
    high, low, close = get_ohlc(symbol, tf)
    if close is None or len(close) < 250: return None

    macd_line = ema(close, 12) - ema(close, 26)
    ma200 = sma(close, SMA_LEN)
    isAboveSma = close[-1] > ma200[-1]

    low_pivots = pivots_low(low)
    high_p
