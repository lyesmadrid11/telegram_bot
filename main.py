from flask import Flask
import threading, time, ccxt, pandas as pd, requests, os

app = Flask(__name__)

@app.route('/', methods=['GET','HEAD'])
def home():
    return "Bot V6 FIXED - No Block", 200

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

SYMBOLS = ['BTC/USDT','ETH/USDT','BNB/USDT','SOL/USDT','XRP/USDT','ADA/USDT','AVAX/USDT','DOT/USDT','LINK/USDT','LTC/USDT','NEAR/USDT','APT/USDT','AR/USDT','ICP/USDT','FIL/USDT','GRT/USDT','AAVE/USDT','UNI/USDT','LDO/USDT','KSM/USDT','MOVR/USDT','METIS/USDT','PROM/USDT','EPIC/USDT','DCR/USDT','BAT/USDT','DEXE/USDT','TRB/USDT','WLD/USDT','BLUR/USDT','BIO/USDT','ORDI/USDT','INJ/USDT','TAO/USDT','RENDER/USDT','FET/USDT','TIA/USDT','SEI/USDT','SUI/USDT','ARB/USDT','PENDLE/USDT','ONDO/USDT']

SENT_NEW = set()
SENT_CONF = set()

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={'chat_id': CHAT_ID, 'text': msg}, timeout=10)
    except Exception as e:
        print(f"TELEGRAM FAIL: {e}", flush=True)

def get_candles(symbol, tf):
    # الحل المجاني لي ينحي البلوك
    try:
        ex = ccxt.binance({
            'enableRateLimit': True,
            'urls': {
                'api': {
                    'public': 'https://data-api.binance.vision/api',
                }
            }
        })
        ohlcv = ex.fetch_ohlcv(symbol, timeframe=tf, limit=500)
        if len(ohlcv) > 200:
            print(f"BINANCE OK {symbol}", flush=True)
            return ohlcv
    except Exception as e:
        print(f"BINANCE FAIL {symbol} -> nrouh OKX", flush=True)

    # OKX راه يخدم عندك 100% شفتو في الصورة
    try:
        ex = ccxt.okx({'enableRateLimit': True})
        ohlcv = ex.fetch_ohlcv(symbol, timeframe=tf, limit=500)
        if len(ohlcv) > 200:
            print(f"OKX OK {symbol}", flush=True)
            return ohlcv
    except Exception as e:
        print(f"OKX FAIL {symbol}: {e}", flush=True)
        return []

def tema(s, p=21):
    e1 = s.ewm(span=p).mean()
    e2 = e1.ewm(span=p).mean()
    e3 = e2.ewm(span=p).mean()
    return 3*e1 - 3*e2 + e3

def check_blue_only(symbol, tf):
    ohlcv = get_candles(symbol, tf)
    if len(ohlcv) < 250: return False
    df = pd.DataFrame(ohlcv, columns=['ts','o','h','l','c','v'])
    df['ema12'] = df['c'].ewm(span=12).mean()
    df['ema26'] = df['c'].ewm(span=26).mean()
    df['macd'] = df['ema12'] - df['ema26']
    df['mm50'] = df['c'].rolling(50).mean()
    df['tema'] = tema(df['c'], 21)
    left, right = 3, 3
    piv_lows = []
    for i in range(left, len(df)-right-1):
        ok=True
        for k in range(1, left+1):
            if df['l'].iloc[i] >= df['l'].iloc[i-k] or df['l'].iloc[i] >= df['l'].iloc[i+k]:
                ok=False; break
        if ok: piv_lows.append(i)
    if len(piv_lows) < 2: return False
    p1, p2 = piv_lows[-1], piv_lows[-2]
    if len(df) - p1 > 5: return False
    if not (5 <= (p1 - p2) <= 100): return False
    if df['c'].iloc[-1] > df['l'].iloc[p1] * 1.35: return False
    if not (df['l'].iloc[p1] < df['l'].iloc[p2] and df['macd'].iloc[p1] > df['macd'].iloc[p2] and df['macd'].iloc[p1] < 0): return False
    if df['c'].iloc[-1] < df['tema'].iloc[-1]: return False
    if df['tema'].iloc[-1] <= df['tema'].iloc[-2]: return False
    is_above = df['c'].iloc[-1] > df['mm50'].iloc[-1]
    last_high = df['h'].iloc[p1-5:p1+5].max()
    breakout = df['c'].iloc[-1] > last_high
    key_base = f"{symbol}_{tf}_{p1}"
    found=False
    if f"NEW_{key_base}" not in SENT_NEW:
        SENT_NEW.add(f"NEW_{key_base}")
        found=True
        pos = "فوق MM50 ✅" if is_above else "تحت MM50 ⚠️"
        send_telegram(f"🔵 BLUE جديدة - {symbol} {tf}\n{pos}\nسعر: {df['c'].iloc[-1]:.4f}")
    if is_above and breakout and f"CONF_{key_base}" not in SENT_CONF:
        SENT_CONF.add(f"CONF_{key_base}")
        found=True
        send_telegram(f"✅ BLUE CONFIRMED - {symbol} {tf}\nكسر {last_high:.4f}")
    return found

def bot_loop():
    print(">>> BOT V6 BDA", flush=True)
    send_telegram("✅ V6 بدا - البلوك تنحا")
    loop=0
    while True:
        loop+=1
        blue=0
        print(f">>> DAWRA {loop}", flush=True)
        for tf in ['4h','1d']:
            for s in SYMBOLS:
                try:
                    if check_blue_only(s, tf): blue+=1
                except Exception as e:
                    print(f"ERROR {s}: {e}", flush=True)
                time.sleep(1.2)
        send_telegram(f"📊 فحص {loop} خلص\nلقا {blue} إشارة 🔵")
        time.sleep(900)

threading.Thread(target=bot_loop, daemon=True).start()
print(">>> THREAD TLANSA V6", flush=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
