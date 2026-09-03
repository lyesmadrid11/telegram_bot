from flask import Flask
import threading, time, ccxt, pandas as pd, requests, os

app = Flask(__name__)
@app.route('/', methods=['GET','HEAD'])
def home():
    return "Bot BLUE MM50 Running", 200

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

SYMBOLS = ['BTC/USDT','ETH/USDT','BNB/USDT','SOL/USDT','XRP/USDT','ADA/USDT','AVAX/USDT','DOT/USDT','LINK/USDT','LTC/USDT','NEAR/USDT','APT/USDT','AR/USDT','ICP/USDT','FIL/USDT','GRT/USDT','AAVE/USDT','UNI/USDT','LDO/USDT','KSM/USDT','MOVR/USDT','METIS/USDT','PROM/USDT','EPIC/USDT','DCR/USDT','BAT/USDT','DEXE/USDT','TRB/USDT','WLD/USDT','BLUR/USDT','BIO/USDT','ORDI/USDT','INJ/USDT','TAO/USDT','RENDER/USDT','FET/USDT','TIA/USDT','SEI/USDT','SUI/USDT','ARB/USDT','PENDLE/USDT','ONDO/USDT']

SENT = set()

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={'chat_id': CHAT_ID, 'text': msg}, timeout=10)
    except:
        pass

def get_candles(symbol, tf):
    for ex_id in ['binance','okx','bybit']:
        try:
            ex = getattr(ccxt, ex_id)({'enableRateLimit': True})
            ohlcv = ex.fetch_ohlcv(symbol, timeframe=tf, limit=400)
            if len(ohlcv) > 200:
                print(f"{symbol} {tf} -> {ex_id} OK")
                return ohlcv
        except Exception as e:
            print(f"{symbol} {ex_id} fail: {e}")
            continue
    print(f"{symbol} {tf} -> FAIL 3 ex")
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

    # 1- فلتر MM50
    if df['c'].iloc[-1] < df['mm50'].iloc[-1]:
        return None

    # 2- Pivots
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

    # 3- BLUE ONLY بلا RT
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
    send_telegram("✅ البوت بدا\nBLUE ONLY + فوق MM50 + 4h+1d\nBinance>OKX>Bybit")
    while True:
        found = 0
