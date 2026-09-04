
from flask import Flask
import threading, time, ccxt, pandas as pd, requests, os
app = Flask(__name__)
@app.route('/', methods=['GET','HEAD'])
def home(): return "Bot BLUE MM50 Running", 200

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
SYMBOLS = ['BTC/USDT','ETH/USDT','BNB/USDT','SOL/USDT','XRP/USDT','ADA/USDT','AVAX/USDT','DOT/USDT','LINK/USDT','LTC/USDT','NEAR/USDT','APT/USDT','AR/USDT','ICP/USDT','FIL/USDT','GRT/USDT','AAVE/USDT','UNI/USDT','LDO/USDT','KSM/USDT','MOVR/USDT','METIS/USDT','PROM/USDT','EPIC/USDT','DCR/USDT','BAT/USDT','DEXE/USDT','TRB/USDT','WLD/USDT','BLUR/USDT','BIO/USDT','ORDI/USDT','INJ/USDT','TAO/USDT','RENDER/USDT','FET/USDT','TIA/USDT','SEI/USDT','SUI/USDT','ARB/USDT','PENDLE/USDT','ONDO/USDT']

SENT_NEW = set()
SENT_CONF = set()

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={'chat_id': CHAT_ID, 'text': msg}, timeout=10)
    except: pass

def get_candles(symbol, tf):
    for ex_id in ['binance','okx','bybit']:
        try:
            ex = getattr(ccxt, ex_id)({'enableRateLimit': True})
            ohlcv = ex.fetch_ohlcv(symbol, timeframe=tf, limit=400)
            if len(ohlcv) > 200:
                return ohlcv
        except: continue
    return []

def check_blue_only(symbol, tf):
    ohlcv = get_candles(symbol, tf)
    if len(ohlcv) < 250: return

    df = pd.DataFrame(ohlcv, columns=['ts','o','h','l','c','v'])
    df['ema12'] = df['c'].ewm(span=12).mean()
    df['ema26'] = df['c'].ewm(span=26).mean()
    df['macd'] = df['ema12'] - df['ema26']
    df['mm50'] = df['c'].rolling(50).mean()

    left, right = 3, 3
    pivots = []
    for i in range(left, len(df)-right-1):
        is_low = True
        for k in range(1, left+1):
            if df['l'].iloc[i] >= df['l'].iloc[i-k] or df['l'].iloc[i] >= df['l'].iloc[i+k]:
                is_low = False
                break
        if is_low: pivots.append(i)

    if len(pivots) < 2: return None
    p1, p2 = pivots[-1], pivots[-2]

    price_lower_low = df['l'].iloc[p1] < df['l'].iloc[p2]
    macd_higher_low = df['macd'].iloc[p1] > df['macd'].iloc[p2]

    # الشرط الأساسي تاع DIV الزرقاء
    if not (price_lower_low and macd_higher_low):
        return None

    is_above = df['c'].iloc[-1] > df['mm50'].iloc[-1]
    last_high = df['h'].iloc[p1-5:p1+5].max()
    breakout = df['c'].iloc[-1] > last_high

    key_base = f"{symbol}_{tf}_{p1}"
    key_new = f"NEW_{key_base}"
    key_conf = f"CONF_{key_base}"

    # 1- تنبيه بكري: غير تخرج زرقاء
    if key_new not in SENT_NEW:
        SENT_NEW.add(key_new)
        if is_above:
            pos = "فوق MM50 ✅"
        else:
            pos = f"تحت MM50 ⚠️ (MM50={df['mm50'].iloc[-1]:.4f})"
        send_telegram(f"🔵 BLUE جديدة\n{symbol} {tf}\n{pos}\nسعر: {df['c'].iloc[-1]:.4f}\nوجد روحك")

    # 2- تنبيه تأكيد: كي تطلع فوق MM50 + كسر
    if is_above and breakout:
        if key_conf not in SENT_CONF:
            SENT_CONF.add(key_conf)
            send_telegram(f"✅ BLUE CONFIRMED MM50\n{symbol} {tf}\nفوق MM50 ✅\nكسر {last_high:.4f}")

    return None

def bot_loop():
    send_telegram("✅ البوت بدا V2\n🔵 تنبيه أول كي تخرج زرقاء\n✅ تنبيه ثاني فوق MM50\n4h+1d")
    while True:
        for tf in ['4h','1d']:
            for s in SYMBOLS:
                try: check_blue_only(s, tf)
                except Exception as e: print(f"Error {s} {tf}: {e}")
                time.sleep(0.7)
        time.sleep(14400)

threading.Thread(target=bot_loop, daemon=True).start()
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
