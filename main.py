from flask import Flask
import threading, time, ccxt, pandas as pd, requests, os
app = Flask(__name__)
@app.route('/', methods=['GET','HEAD'])
def home(): return "Bot BLUE V4 - 15min", 200

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
            ohlcv = ex.fetch_ohlcv(symbol, timeframe=tf, limit=500)
            if len(ohlcv) > 200: return ohlcv
        except: continue
    return []

def tema(series, period=21):
    ema1 = series.ewm(span=period).mean()
    ema2 = ema1.ewm(span=period).mean()
    ema3 = ema2.ewm(span=period).mean()
    return 3*ema1 - 3*ema2 + ema3

def check_blue_only(symbol, tf):
    ohlcv = get_candles(symbol, tf)
    if len(ohlcv) < 250: return
    df = pd.DataFrame(ohlcv, columns=['ts','o','h','l','c','v'])
    df['ema12'] = df['c'].ewm(span=12).mean()
    df['ema26'] = df['c'].ewm(span=26).mean()
    df['macd'] = df['ema12'] - df['ema26']
    df['mm50'] = df['c'].rolling(50).mean()
    df['tema'] = tema(df['c'], 21)

    left, right = 3, 3
    piv_lows, piv_highs = [], []
    for i in range(left, len(df)-right-1):
        # قاع
        is_low = True
        for k in range(1, left+1):
            if df['l'].iloc[i] >= df['l'].iloc[i-k] or df['l'].iloc[i] >= df['l'].iloc[i+k]:
                is_low = False; break
        if is_low: piv_lows.append(i)
        # قمة للـ RT
        is_high = True
        for k in range(1, left+1):
            if df['h'].iloc[i] <= df['h'].iloc[i-k] or df['h'].iloc[i] <= df['h'].iloc[i+k]:
                is_high = False; break
        if is_high: piv_highs.append(i)

    if len(piv_lows) < 2: return
    p1, p2 = piv_lows[-1], piv_lows[-2]

    # فلتر 1: القاع جديد أقل من 15 شمعة
    if len(df) - p1 > 15: return
    # فلتر 2: المسافة بين القاعين
    if not (5 <= (p1 - p2) <= 100): return
    # فلتر 3: السعر ما بعدش بزاف
    if df['c'].iloc[-1] > df['l'].iloc[p1] * 1.35: return

    price_lower_low = df['l'].iloc[p1] < df['l'].iloc[p2]
    macd_higher_low = df['macd'].iloc[p1] > df['macd'].iloc[p2]
    macd_negative = df['macd'].iloc[p1] < 0 and df['macd'].iloc[p2] < 0
    if not (price_lower_low and macd_higher_low and macd_negative): return

    # ===== فلتر V4 الجديد - يطابق صورتك =====
    # لازم يكون كاين RT قبل الـ BLUE في 30 شمعة الأخيرة (ما نبعثوش، غير نتأكدو)
    has_rt_before = False
    if len(piv_highs) >= 2:
        for j in range(len(piv_highs)-1):
            h1, h2 = piv_highs[-1-j], piv_highs[-2-j]
            if p1 - h1 < 30 and h1 > p2: # RT قريب قبل BLUE
                if df['h'].iloc[h1] > df['h'].iloc[h2] and df['macd'].iloc[h1] < df['macd'].iloc[h2]:
                    has_rt_before = True; break
    # اذا تحب يفيق حتى بلا RT خليها True، اذا تحب كيما TradingView خلي الشرط
    # if not has_rt_before: return # <-- فعل هذا السطر اذا تحب 100% كيما الصورة

    is_above = df['c'].iloc[-1] > df['mm50'].iloc[-1]
    last_high = df['h'].iloc[p1-5:p1+5].max()
    breakout = df['c'].iloc[-1] > last_high

    key_base = f"{symbol}_{tf}_{p1}"
    key_new = f"NEW_{key_base}"
    key_conf = f"CONF_{key_base}"

    if key_new not in SENT_NEW:
        SENT_NEW.add(key_new)
        pos = f"فوق MM50 ✅" if is_above else f"تحت MM50 ⚠️ (MM50={df['mm50'].iloc[-1]:.4f})"
        send_telegram(f"🔵 BLUE جديدة - {symbol} {tf}\n{pos}\nسعر: {df['c'].iloc[-1]:.4f}\nTEMA: {df['tema'].iloc[-1]:.4f}\nوجد روحك")

    if is_above and breakout:
        if key_conf not in SENT_CONF:
            SENT_CONF.add(key_conf)
            send_telegram(f"✅ BLUE CONFIRMED - {symbol} {tf}\nفوق MM50 ✅\nكسر {last_high:.4f}")

def bot_loop():
    send_telegram("✅ البوت بدا V4 - 15 دقيقة\n🔵 يفيق تمتم كي تخرج BLUE\n✅ ما يبعثش RT")
    while True:
        for tf in ['4h','1d']:
            for s in SYMBOLS:
                try: check_blue_only(s, tf)
                except Exception as e: print(f"Error {s} {tf}: {e}")
                time.sleep(0.7)
        time.sleep(900) # 15 دقيقة

threading.Thread(target=bot_loop, daemon=True).start()
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
