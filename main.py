import threading, os, time, requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import ccxt
import pandas as pd

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except:
        pass

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot BLUE only - Fixed")

def run_fake_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

exchange = ccxt.okx({'enableRateLimit': True})

leftBars, rightBars = 2, 2
fastLen, slowLen = 12, 26
firstLookbackBull = 10
lowerLowLookbackBull = 30
smaLen = 50

SYMBOLS = ['BTC/USDT','ETH/USDT','BNB/USDT','SOL/USDT','XRP/USDT','DOGE/USDT','ADA/USDT','AVAX/USDT','DOT/USDT','LINK/USDT','TRX/USDT','LTC/USDT','NEAR/USDT','UNI/USDT','XLM/USDT','ETC/USDT','FIL/USDT','APT/USDT','AR/USDT','VET/USDT','ICP/USDT','GRT/USDT','RENDER/USDT','AAVE/USDT','OP/USDT','SUI/USDT','PEPE/USDT','BONK/USDT','WIF/USDT','ARB/USDT','FET/USDT','TAO/USDT','TNSR/USDT','SFP/USDT','MOVR/USDT','DCR/USDT','BAT/USDT','MASK/USDT','BLUR/USDT','ORDI/USDT','PROM/USDT','CHZ/USDT']

def find_pivots(lows, highs, l, r):
    pls = []
    for i in range(l, len(lows)-r):
        if all(lows[i] < lows[i-k] for k in range(1,l+1)) and all(lows[i] < lows[i+k] for k in range(1,r+1)):
            pls.append(i)
    return pls

last_sent_pivot = {}

def check_blue_only(s, tf):
    try:
        ohlcv = exchange.fetch_ohlcv(s, tf, limit=400)
        df = pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])
        if len(df) < 250:
            return None
        macd = df['c'].ewm(span=fastLen).mean() - df['c'].ewm(span=slowLen).mean()
        sma = df['c'].rolling(smaLen).mean()
        lows = df['l'].values
        highs = df['h'].values
        closes = df['c'].values
        piv_lows = find_pivots(lows, highs, leftBars, rightBars)
        if len(piv_lows) < 2:
            return None
        recent_piv = [p for p in piv_lows if p >= len(df)-20]
        for p1 in reversed(recent_piv):
            if closes[p1] <= sma.iloc[p1]:
                continue
            res_level = highs[p1 + rightBars]
            is_breakout = lows[-1] > res_level and lows[-2] <= res_level
            is_breakout2 = lows[-2] > res_level and lows[-3] <= res_level
            if not (is_breakout or is_breakout2):
                continue
            for p2 in [p for p in piv_lows if p < p1][-lowerLowLookbackBull:]:
                if lows[p1] >= lows[p2]:
                    continue
                if macd.iloc[p1] <= macd.iloc[p2]:
                    continue
                cross = False
                for x in range(p2+1, p1):
                    y = ((lows[p1]-lows[p2])/(p1-p2))*(x-p2)+lows[p2]
                    if lows[x] < y:
                        cross = True
                        break
                if cross:
                    continue
                key = s + tf
                if key in last_sent_pivot and last_sent_pivot[key] == p1:
                    return None
                last_sent_pivot[key] = p1
                return f"🟦 DIV BLEUE CONFIRMEE\nCoin: {s}\nTF: {tf}\nPrice: {closes[-1]:.4f}"
    except Exception as e:
        print(f"Err {s}: {e}")
        return None

send_telegram("✅ Bot BLUE ONLY ON - Fixed\n42 coins | 4H+DAILY | NO RT")

while True:
    for tf in ['4h', '1d']:
        for s in SYMBOLS:
            m = check_blue_only(s, tf)
            if m:
                send_telegram(m)
            time.sleep(0.7)
    time.sleep(14400)
