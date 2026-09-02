import threading, os
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- سيرفر وهمي باش Render يولي Live ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot CONFIRMED ONLY running")
    def log_message(self, format, *args):
        return

def run_fake():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

threading.Thread(target=run_fake, daemon=True).start()
print(f"Fake server started on {os.environ.get('PORT', 10000)}")

# --- الكود الاصلي تاعك من هنا ---
import time
import requests
import ccxt
import pandas as pd

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print(f"TOKEN exists: {bool(TELEGRAM_TOKEN)} - len {len(TELEGRAM_TOKEN) if TELEGRAM_TOKEN else 0}")
print(f"CHAT_ID exists: {bool(CHAT_ID)} - value {CHAT_ID}")

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram config missing!")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        print(f"Telegram sent: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        print(f"Telegram error: {e}")

# 48 coins تاعك
COINS = ["BTC/USDT","ETH/USDT","BNB/USDT","SOL/USDT","XRP/USDT","ADA/USDT","DOGE/USDT","AVAX/USDT","DOT/USDT","MATIC/USDT","LINK/USDT","LTC/USDT","BCH/USDT","UNI/USDT","ETC/USDT","XLM/USDT","ATOM/USDT","FIL/USDT","TRX/USDT","APT/USDT","NEAR/USDT","ARBI/USDT","OP/USDT","SUI/USDT","PEPE/USDT","SHIB/USDT","RNDR/USDT","INJ/USDT","TIA/USDT","SEI/USDT","STX/USDT","IMX/USDT","ARB/USDT","MKR/USDT","AAVE/USDT","GRT/USDT","RUNE/USDT","FET/USDT","AGIX/USDT","WLD/USDT","BONK/USDT","FLOKI/USDT","JUP/USDT","ONDO/USDT","ENA/USDT","WIF/USDT","BOME/USDT"]

exchange = ccxt.binance()

def get_signal(symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, '4h', limit=100)
        df = pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])
        df['mm50'] = df['c'].rolling(50).mean()
        # هنا المنطق تاعك CONFIRMEE ONLY 2/2
        # ... خليتلك مكان
        if df['c'].iloc[-1] > df['mm50'].iloc[-1] and df['c'].iloc[-2] > df['mm50'].iloc[-2]:
            return True
        return False
    except Exception as e:
        print(f"Error {symbol} 4h: {e}")
        return False

# رسالة البداية
send_telegram(f"✅ *Bot démarré* - {len(COINS)} coins - CONFIRMÉE ONLY\nFake server OK - Render Live")
print(f"Bot started - {len(COINS)} coins - CONFIRMED ONLY 2/2 MM50")

# Loop
while True:
    try:
        count4h = 0
        count1d = 0
        for coin in COINS:
            if get_signal(coin):
                count4h += 1
                send_telegram(f"🚀 *{coin}* Signal CONFIRMÉ 2/2 au dessus MM50 - 4H")
        print(f"Scan done - 4H:{count4h} 1D:{count1d}")
        time.sleep(60) # كل دقيقة
    except Exception as e:
        print(f"ERROR BOT LOOP: {e}")
        time.sleep(10)
