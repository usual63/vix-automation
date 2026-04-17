import pandas as pd
import requests
import os

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def send_test(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'})

# CoinMetrics API 호출 (GitHub 서버는 차단이 없습니다)
url = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=CapMrktCurUSD,CapRealUSD&limit=10&pretty=true"
try:
    res = requests.get(url).json()
    df = pd.DataFrame(res['data'])
    df['mvrv'] = df['CapMrktCurUSD'].astype(float) / df['CapRealUSD'].astype(float)
    
    latest_date = df['time'].iloc[-1]
    latest_mvrv = round(df['mvrv'].iloc[-1], 3)
    
    report = f"📊 [실시간 데이터 리포트]\n\n기준 시간: `{latest_date}`\n현재 BTC MVRV: `{latest_mvrv}`"
    send_test(report)
    print("성공: 텔레그램을 확인하세요")
except Exception as e:
    send_test(f"❌ 데이터 추출 에러: {e}")
