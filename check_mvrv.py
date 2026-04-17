import pandas as pd
import requests
import os

# 깃허브 금고(Secrets)에서 토큰 정보를 가져옵니다
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    requests.post(url, data=payload)

def run():
    # CoinMetrics API는 깃허브 서버에서 자유롭게 호출 가능합니다
    url = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=CapMrktCurUSD,CapRealUSD&limit=1&pretty=true"
    
    try:
        response = requests.get(url).json()
        
        # 데이터에서 시가총액과 실현시가총액을 뽑아 MVRV 계산
        mkt_cap = float(response['data'][0]['CapMrktCurUSD'])
        real_cap = float(response['data'][0]['CapRealUSD'])
        mvrv_value = round(mkt_cap / real_cap, 3)
        
        report = f"✅ [MVRV 데이터 확인 성공]\n\n현재 비트코인 MVRV: `{mvrv_value}`"
        send_telegram(report)
        print(f"성공: MVRV {mvrv_value}")
        
    except Exception as e:
        send_telegram(f"❌ 데이터 추출 중 에러 발생: {e}")

if __name__ == "__main__":
    run()
