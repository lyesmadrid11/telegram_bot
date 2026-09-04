from flask import Flask
import threading, time, ccxt, pandas as pd, requests, os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

print(f"DEBUG TOKEN exists: {bool(TELEGRAM_TOKEN)}")
print(f"DEBUG CHAT_ID exists: {bool(CHAT_ID)}")
if TELEGRAM_TOKEN:
    print(f"DEBUG TOKEN len: {len(TELEGRAM_TOKEN)}")

@app.route('/', methods=['GET','HEAD'])
def home():
    return "Bot BLUE MM50 Running", 200

@app.route('/test')
def test():
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        r = requests.post(url, data={'chat_id': CHAT_ID, 'text': '✅ تست - البوت يخدم'}, timeout=10)
        return f"Telegram response: {r.text}", 200
    except Exception as e:
        return f"Error: {e}", 500

SYMBOLS = ['BTC/USDT','ETH/USDT','BNB/USDT','SOL/USDT','XRP/USDT','ADA/USDT','AVAX/USDT','DOT/USDT','LINK/USDT','LTC/USDT','NEAR/USDT','APT/USDT','AR/USDT','ICP/USDT','FIL/USDT','GRT/USDT','AAVE/USDT','UNI/USDT','LDO/USDT','KSM/USDT','MOVR/USDT','METIS/USDT','PROM/USDT','EPIC/USDT','DCR/USDT','BAT/USDT','DEXE/USDT','TRB/USDT','WLD/USDT','BLUR/USDT','BIO/USDT','ORDI/USDT','INJ/USDT','TAO/USDT','RENDER/USDT','FET/USDT','TIA/USDT','SEI/USDT','SUI/USDT','ARB/USDT','PENDLE/USDT','ONDO/USDT']
SENT = set()

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        r = requests.post(url, data={'chat_id': CHAT_ID, 'text': msg}, timeout=10)
        print(f"Telegram sent: {r.status_code} {r.text[:100]}")
    except Exception as e:
        print(f"Telegram FAIL: {e}")

def get_candles(symbol, tf):
    for ex_id in ['binance','okx','bybit']:
        try:
            ex = getattr(ccxt, ex_id)({'enableRateLimit': True})
            ohlcv = ex.fetch_ohlcv(symbol, timeframe=tf, limit=400)
            if len(ohlcv) > 200:
                return ohlcv
        except Exception as e:
            print(f"{symbol} {ex_id} fail: {e}")
            continue
    return []

def check_blue_only(symbol, tf):
    ohlcv = get_candles(symbol, tf)
    if len(ohlcv) < 250:
        return None
    df = pd.DataFrame(ohlcv, columns=['ts','o','h','l','c','v'])
    df['ema12'] = df['c'].ewm(span=12).mean()
    df['ema26'] = df['c'].ewm(span=26).mean()
    df['macd'] = df['ema12'] - df['ema26']
    df['mm50'] = df['c'].rolling(50).mean()
    if df['c'].iloc[-1] < df['mm50'].iloc[-1]:
        return None
    left, right = 3, 3
    pivots = []
    for i in range(left, len(df)-right-1):
        is_low = True
        for k in range(1, left+1):
            if df['l'].iloc[i] >= df['l'].iloc[i-k] or df['l'].iloc[i] >= df['l'].iloc[i+k]:
                is_low = False
                break
        if is_low:
            pivots.append(i)
    if len(pivots) < 2:
        return None
    p1, p2 = pivots[-1], pivots[-2]
    price_lower_low = df['l'].iloc[p1] < df['l'].iloc[p2]
    macd_higher_low = df['macd'].iloc[p1] > df['macd'].iloc[p2]
    last_high = df['h'].iloc[p1-5:p1+5].max()
    breakout = df['c'].iloc[-1] > last_high and df['c'].iloc[-2] > last_high
    if price_lower_low and macd_higher_low and breakout:
        key = f"{symbol}_{tf}_{p1}"
        if key in SENT:
            return None
        SENT.add(key)
        return f"🔵 BLUE CONFIRMED MM50\n{symbol} {tf}\nفوق MM50 ✅\nكسر {last_high:.4f}"
    return None

def bot_loop():
    print("BOT LOOP STARTED")
    send_telegram("✅ البوت بدا\nBLUE ONLY + فوق MM50 + 4h+1d\nBinance>OKX>Bybit")
    while True:
        try:
            found = 0
            for tf in ['4h','1d']:
                for s in SYMBOLS:
                    try:
                        msg = check_blue_only(s, tf)
                        if msg:
                            send_telegram(msg)
                            found += 1
                    except Exception as e:
                        print(f"Error {s} {tf}: {e}")
                    time.sleep(0.7)
            send_telegram(f"📊 ملخص\nفحصت 84 فريم\nإشارات BLUE: {found}")
        except Exception as e:
            print(f"BOT LOOP CRASH: {e}")
        time.sleep(14400)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
