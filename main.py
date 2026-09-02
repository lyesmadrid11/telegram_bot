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

# --- الكود الأصلي تاعك كيما هو ---
import time
import requests
import ccxt
import pandas as pd

# ── Config من Render ──
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ── قائمتك برك 48 عملة لي بعثتها في التصاور ──
COINS = [
    "NIL/USDT", "DEXE/USDT", "ENSO/USDT", "HEMI/USDT", "ICP/USDT", "PROM/USDT",
    "KERNEL/USDT", "SPK/USDT", "GLM/USDT", "MASK/USDT", "DCR/USDT", "LTC/USDT",
    "EPIC/USDT", "BLUR/USDT", "KSM/USDT", "SOMI/USDT", "AVAX/USDT", "SOL/USDT",
    "TNSR/USDT", "ORDI/USDT", "CHZ/USDT", "BNB/USDT", "BTC/USDT", "XRP/USDT",
    "DOGE/USDT", "REQ/USDT", "SFP/USDT", "SUI/USDT", "TRB/USDT", "ALLO/USDT",
    "FIL/USDT", "DOT/USDT", "AR/USDT", "BIO/USDT", "NEAR/USDT", "LINK/USDT",
    "PHA/USDT", "LDO/USDT", "ADA/USDT", "METIS/USDT", "APT/USDT", "RENDER/USDT",
    "PEPE/USDT", "EDEN/USDT", "BAT/USDT", "WLD/USDT", "BEAMX/USDT", "MOVR/USDT"
]

LEFT_BARS = 2
RIGHT_BARS = 2
MM_PERIOD = 50

def send_telegram(text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram config missing")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def is_pivot_low(lows, idx):
    if idx < LEFT_BARS or idx + RIGHT_BARS >= len(lows):
        return False
    v = lows[idx]
    for k in range(1, LEFT_BARS + 1):
        if v >= lows[idx - k]:
            return False
    for k in range(1, RIGHT_BARS + 1):
        if v >= lows[idx + k]:
            return False
    return True

def check_confirmed_div(df):
    if len(df) < 100:
        return False, None
    df['macd'] = df['close'].ewm(span=12, adjust=False).mean() - df['close'].ewm(span=26, adjust=False).mean()
    df['mm50'] = df['close'].rolling(MM_PERIOD).mean()
    if df['close'].iloc[-1] < df['mm50'].iloc[-1]:
        return False, None
    lows = df['low'].values
    highs = df['high'].values
    macds = df['macd'].values
    p1_idx = len(df) - 1 - RIGHT_BARS
    if not is_pivot_low(lows, p1_idx):
        return False, None
    if not (lows[-1] > highs[p1_idx] and lows[-2] > highs[p1_idx]):
        return False, None
    for j in range(10, 31):
        p2_idx = p1_idx - j
        if p2_idx < LEFT_BARS:
            break
        if is_pivot_low(lows, p2_idx):
            if lows[p1_idx] < lows[p2_idx] and macds[p1_idx] > macds[p2_idx]:
                return True, {
                    'price': float(df['close'].iloc[-1]),
                    'low1': float(lows[p1_idx]),
                    'low2': float(lows[p2_idx])
                }
    return False, None

def main():
    print(f"Bot started - {len(COINS)} coins - CONFIRMED ONLY 2/2 MM50")
    send_telegram(f"✅ Bot démarré\nMode: CONFIRMÉE ONLY (2/2 MM50)\nCoins: {len(COINS)} (قائمتك برك)\nTF: 4H + 1D\nبلا RT")
    exchange = ccxt.binance({'enableRateLimit': True})
    while True:
        for tf in ['4h', '1d']:
            for symbol in COINS:
                try:
                    ohlcv = exchange.fetch_ohlcv(symbol, tf, limit=200)
                    df = pd.DataFrame(ohlcv, columns=['ts','open','high','low','close','vol'])
                    ok, info = check_confirmed_div(df)
                    if ok:
                        msg = f"🟦 DIV BLUE CONFIRMÉE\n{symbol} - {tf}\nPrix: {info['price']}\nLow: {info['low2']} -> {info['low1']}\nMM50 OK"
                        print(msg)
                        send_telegram(msg)
                except Exception as e:
                    print(f"Error {symbol} {tf}: {e}")
                time.sleep(0.3)
        print("Scan done, sleep 30min...")
        time.sleep(1800)

if __name__ == "__main__":
    main()
