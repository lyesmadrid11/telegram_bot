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
    except Exception as e:
        print(f"TG Error {e}", flush=True)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Bot running")
def run_fake_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()
threading.Thread(target=run_fake_server, daemon=True).start()

exchange = ccxt.binance()

# Params كما في صورك
leftBars=2
rightBars=2
smaLen=50
fastLen,slowLen=12,26

# === القائمة ديالك 51 عملة ===
SYMBOLS = [
'BTC/USDT','ETH/USDT','BNB/USDT','SOL/USDT','XRP/USDT','DOGE/USDT',
'ADA/USDT','AVAX/USDT','SHIB/USDT','DOT/USDT','LINK/USDT','TRX/USDT',
'MATIC/USDT','LTC/USDT','BCH/USDT','NEAR/USDT','UNI/USDT','XLM/USDT',
'ETC/USDT','FIL/USDT','APT/USDT','HBAR/USDT','AR/USDT','VET/USDT',
'ICP/USDT','MKR/USDT','STX/USDT','GRT/USDT','RNDR/USDT','AAVE/USDT',
'OP/USDT','INJ/USDT','SUI/USDT','TIA/USDT','SEI/USDT','PEPE/USDT',
'FLOKI/USDT','BONK/USDT','WIF/USDT','JUP/USDT','ENA/USDT','W/USDT',
'ONDO/USDT','PENDLE/USDT','STRK/USDT','ARB/USDT','FET/USDT','AGIX/USDT',
'RENDER/USDT','TAO/USDT','STX/USDT'
]

def find_pivot_lows(lows, l, r):
    pivots=[]
    for i in range(l, len(lows)-r):
        ok=True
        for k in range(1,l+1):
            if lows[i] >= lows[i-k]: ok=False; break
        for k in range(1,r+1):
            if lows
