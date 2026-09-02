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
        print("TG sent", flush=True)
    except Exception as e:
        print(f"TG Error {e}", flush=True)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Bot running")
def run_fake_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()
threading.Thread(target=run_fake_server, daemon=True).start()

# نستعملو OKX بدل Binance باش ما يبلوكيش Render
exchange = ccxt.okx({'enableRateLimit': True})

leftBars=2
rightBars=2
smaLen=50
fastLen=12
slowLen=26

SYMBOLS = [
'BTC/USDT','ETH/USDT','BNB/USDT','SOL/USDT','XRP/USDT','DOGE/USDT',
'ADA/USDT','AVAX/USDT','SHIB/USDT','DOT/USDT','LINK/USDT','TRX/USDT',
'MATIC/USDT','LTC/USDT','BCH/USDT','NEAR/USDT','UNI/USDT','XLM/USDT',
'ETC/USDT','FIL/USDT','APT/USDT','HBAR/USDT','AR/USDT','VET/USDT',
'ICP/USDT','MKR/USDT','STX/USDT','GRT/USDT','RNDR/USDT','AAVE/USDT',
'OP/USDT','INJ/USDT','SUI/USDT','TIA/USDT','SEI/USDT','PEPE/USDT',
'FLOKI/USDT','BONK/USDT','WIF/USDT','JUP/USDT','ENA/USDT','W/USDT',
'ONDO/USDT','PENDLE/USDT','STRK/USDT','ARB/USDT','FET/USDT','AGIX/USDT',
'RENDER/USDT','TAO/USDT'
]

def find_pivot_lows(lows, l, r):
    pivots=[]
    for i in range(l, len(lows)-r):
        ok=True
        for k in range(1,l+1):
            if lows[i] >= lows[i-k]:
                ok=False
                break
        if not ok:
            continue
        for k in range(1,r+1):
            if lows[i] >= lows[i+k]:
                ok=False
                break
        if ok:
            pivots.append(i)
    return pivots

def check_blue(symbol, tf):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, tf, limit=300)
        df = pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])
        if len(df) < 200:
            return None
        macd = df['c'].ewm(span=fastLen).mean() - df['c'].ewm(span=slowLen).mean()
        sma = df['c'].rolling(smaLen).mean()
        lows = df['l'].values
        highs = df['h'].values
        pivots = find_pivot_lows(lows, leftBars, rightBars)
        if len(pivots) < 2:
            return None
        recent = [p for p in pivots if p >= len(df)-15]
        for p1 in reversed(recent):
            idx_res = p1 + rightBars
            if idx_res >= len(highs):
                idx_res = p1
            res = highs[idx_res]
            if not (lows[-1] > res and lows[-2] > res):
                continue
            for p2 in [p for p in pivots if p < p1][-30:]:
                if lows[p1] >= lows[p2]:
                    continue
                if macd.iloc[p1] <= macd.iloc[p2]:
                    continue
                if df['c'].iloc[p1] <= sma.iloc[p1]:
                    continue
                bad=False
                if p1!= p2:
                    for x in range(p2, p1+1):
                        y = ((lows[p1]-lows[p2])/(p1-p2))*(x-p2)+lows[p2]
                        if lows[x] < y - 0.0000001:
                            bad=True
                            break
                if bad:
                    continue
                price = df['c'].iloc[-1]
                return f"🟦 DIV BLEUE CONFIRMÉE\nCoin: {symbol}\nTF: {tf}\nPrice: {price}\nMM50 | Pivot 2/2"
        return None
    except Exception as e:
        print(f"Err {symbol} {tf}: {e}", flush=True)
        return None

print("BOT BLUE - OKX - 51 coins - 4H + 1D", flush=True)
send_telegram("✅ Bot activé - OKX\n🟦 BLEU CONFIRMÉ SEULEMENT\n51 coins | 4H + DAILY | MM50 | Pivot 2/2")

sent=set()
while True:
    for tf in ['4h','1d']:
        for s in SYMBOLS:
            msg = check_blue(s, tf)
            if msg:
                key = s+tf
                if key not in sent:
                    send_telegram(msg)
                    sent.add(key)
                    print(f"BLUE {s} {tf}", flush=True)
            time.sleep(1)
    print("Cycle done", flush=True)
    time.sleep(180)
