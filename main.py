
import threading, os, time, requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import ccxt
import pandas as pd

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except: pass

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Bot running")

def run_fake_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

exchange = ccxt.okx({'enableRateLimit': True})
leftBars, rightBars, smaLen = 2, 2, 50

SYMBOLS = ['BTC/USDT','ETH/USDT','BNB/USDT','SOL/USDT','XRP/USDT','DOGE/USDT','ADA/USDT','AVAX/USDT','DOT/USDT','LINK/USDT','TRX/USDT','LTC/USDT','NEAR/USDT','UNI/USDT','XLM/USDT','ETC/USDT','FIL/USDT','APT/USDT','AR/USDT','VET/USDT','ICP/USDT','GRT/USDT','RENDER/USDT','AAVE/USDT','OP/USDT','SUI/USDT','PEPE/USDT','BONK/USDT','WIF/USDT','ARB/USDT','FET/USDT','TAO/USDT','TNSR/USDT','SFP/USDT','MOVR/USDT','DCR/USDT','BAT/USDT','MASK/USDT','BLUR/USDT','ORDI/USDT','PROM/USDT','CHZ/USDT']

def find_pivot_lows(lows, l, r):
    piv=[]
    for i in range(l, len(lows)-r):
        ok=True
        for k in range(1,l+1):
            if lows[i]>=lows[i-k]: ok=False
        for k in range(1,r+1):
            if lows[i]>=lows[i+k]: ok=False
        if ok: piv.append(i)
    return piv

# نحفظو آخر قاع بعثناه باش ما نعاودوش
last_sent_pivot = {} # key = s+tf, value = index p1

def check_blue(s, tf):
    try:
        ohlcv=exchange.fetch_ohlcv(s, tf, limit=300)
        df=pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])
        if len(df)<200: return None
        macd=df['c'].ewm(span=12).mean()-df['c'].ewm(span=26).mean()
        sma=df['c'].rolling(smaLen).mean()
        lows=df['l'].values; highs=df['h'].values
        piv=find_pivot_lows(lows, leftBars, rightBars)
        if len(piv)<2: return None
        recent=[p for p in piv if p>=len(df)-15]
        for p1 in reversed(recent):
            res=highs[p1+rightBars] if p1+rightBars<len(highs) else highs[p1]
            if not (lows[-1]>res and lows[-2]>res): continue
            for p2 in [p for p in piv if p<p1][-30:]:
                if lows[p1]>=lows[p2]: continue
                if macd.iloc[p1]<=macd.iloc[p2]: continue
                if df['c'].iloc[p1]<=sma.iloc[p1]: continue
                # === فلتر جديد: ما نعاودش نفس القاع ===
                key = s+tf
                if key in last_sent_pivot and last_sent_pivot[key] == p1:
                    return None # نفس الديفيرجنس القديمة، ما نعاودهاش
                last_sent_pivot[key] = p1
                return f"🟦 DIV BLEUE CONFIRMEE\nCoin: {s}\nTF: {tf}\nPrice: {df['c'].iloc[-1]}\nPivot: {p1}"
    except Exception as e:
        if "does not have market symbol" not in str(e):
            print(f"Err {s}: {e}")
        return None

send_telegram("✅ Bot BLUE - 4H Check - 42 coins - Anti-Doublon")
print("Bot started - check every 4H")

while True:
    for tf in ['4h','1d']:
        for s in SYMBOLS:
            m=check_blue(s,tf)
            if m:
                send_telegram(m)
            time.sleep(0.8)
    print("Cycle done - next in 4H")
    time.sleep(14400) # = 4 ساعات
