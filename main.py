from flask import Flask, request
import requests, os, time, threading
import pandas as pd

app = Flask(__name__)
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

COINS = ["DEXEUSDT","BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","ADAUSDT","DOGEUSDT","AVAXUSDT","DOTUSDT","LINKUSDT","RENDERUSDT","TNSRUSDT","CHZUSDT","KERNELUSDT","APTUSDT","ARUSDT","ENSOUSDT","KSMUSDT","PHAUSDT","DCRUSDT","ALLOUSDT","METISUSDT","PROMUSDT","NILUSDT","ICPUSDT","SPKUSDT","MOVRUSDT","VETUSDT","NEARUSDT","EPICUSDT","WLDUSDT","FILUSDT","SKLUSDT","SFPUSDT","MASKUSDT","TRBUSDT","LDOUSDT","GLMUSDT","BIOUSDT","ORDIUSDT","BEAMXUSDT","PEPEUSDT","BATUSDT","BLURUSDT","REQUSDT","LTCUSDT","SOMIUSDT","HEMIUSDT","SUIUSDT","ARBUSDT","OPUSDT","ENSUSDT","TAOUSDT","UNIUSDT"]

def send_tg(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":CHAT_ID,"text":msg},timeout=10)
    except: pass

def check_div(symbol,interval):
    try:
        url=f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
        r=requests.get(url,timeout=10).json()
        closes=[float(x[4]) for x in r]
        lows=[float(x[3]) for x in r]
        ema12=pd.Series(closes).ewm(span=12).mean()
        ema26=pd.Series(closes).ewm(span=26).mean()
        macd=ema12-ema26
        if lows[-1]<min(lows[-20:-5]) and macd.iloc[-1]>macd.iloc[-20] and macd.iloc[-1]<0:
            send_tg(f"🔵 DIV BLUE - {symbol} - {interval}\nPrice: {closes[-1]}")
    except: pass

def scanner():
    time.sleep(10)
    send_tg(f"🚀 Scanner ON\n{len(COINS)} coins incl DEXE\n4H & 1D")
    while True:
        for c in COINS:
            check_div(c,"4h")
            check_div(c,"1d")
        time.sleep(1800)

@app.route('/')
def home(): return "Bot ON - DEXE OK"

@app.route('/webhook',methods=['GET','POST'])
def webhook():
    if request.method=='GET': return "OK"
    data=request.get_json(force=True)
    if "message" in data:
        cid=data["message"]["chat"]["id"]
        txt=data["message"].get("text","")
        if txt=="/start":
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":cid,"text":f"Bot 24/24 ON ✓\n{len(COINS)} coins\nDEXE added ✅"})
    return "ok"

threading.Thread(target=scanner,daemon=True).start()
if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
