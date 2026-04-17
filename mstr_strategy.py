import yfinance as yf
import pandas as pd
import requests
import os

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# [중요] 최신 공시 기준 비트코인 보유량 (추가 매입 시 이 숫자만 수정하면 됩니다)
MSTR_BTC_QTY = 252220 

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    requests.post(url, data=payload)

def get_mvrv():
    url = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=CapMrktCurUSD,CapRealUSD&limit=1&pretty=true"
    res = requests.get(url).json()
    return float(res['data'][0]['CapMrktCurUSD']) / float(res['data'][0]['CapRealUSD'])

def get_mstr_analysis():
    # 1. MSTR 시가총액 및 BTC 가격 호출
    mstr_info = yf.Ticker("MSTR").info
    mstr_cap = mstr_info.get('marketCap')
    btc_price = yf.Ticker("BTC-USD").history(period="1d")['Close'].iloc[-1]
    
    # 2. mNAV(프리미엄) 계산
    btc_value_held = btc_price * MSTR_BTC_QTY
    mnav = mstr_cap / btc_value_held
    return btc_price, mnav

def run():
    try:
        mvrv = round(get_mvrv(), 2)
        btc_p, mnav = get_mstr_analysis()
        
        status = "🌿 [정상/관망]"
        if mvrv >= 3.0 or mnav >= 2.2: status = "🚨 [과열/분할매도 권장]"
        elif mvrv <= 1.2 and mnav <= 1.1: status = "💎 [저평가/적극매수 권장]"
            
        report = (
            f"📊 *MSTR-BTC 통합 리포트*\n\n"
            f"🔸 BTC 가격: `${round(btc_p, 2)}`\n"
            f"🔸 BTC MVRV: `{mvrv}` (고점 신호: 3.0↑)\n"
            f"🔸 MSTR mNAV: `{round(mnav, 2)}` (과열 신호: 2.2↑)\n\n"
            f"🚦 *현재 판단*: {status}"
        )
        send_telegram(report)
    except Exception as e:
        send_telegram(f"❌ MSTR 분석 에러: {e}")

if __name__ == "__main__":
    run()
