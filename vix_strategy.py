import yfinance as yf
import pandas as pd
import requests
import os
from datetime import datetime
import pytz

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    requests.post(url, data=payload)

def get_detailed_strategy(vix):
    if vix < 14: return 1, "💎 [Zone 1] 전량 매도 / 현금 100% 확보"
    elif 14 <= vix < 20: return 2, "🌿 [Zone 2] 관망 및 유지"
    elif 20 <= vix < 30: return 3, "⚠️ [Zone 3] 1차 분할 매수"
    elif 30 <= vix < 45: return 4, "🚨 [Zone 4] 2차 적극 매수"
    else: return 5, "🔥 [Zone 5] 역사적 바닥 최대 매수"

def run_vix_system():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    try:
        data = yf.download("^VIX", period="1mo", progress=False)
        if data.empty: return
        
        close_data = data['Close']
        sma5 = close_data.rolling(window=5).mean()
        curr_vix = round(float(close_data.iloc[-1]), 2)
        prev_vix = round(float(close_data.iloc[-2]), 2)
        curr_sma5, prev_sma5 = float(sma5.iloc[-1]), float(sma5.iloc[-2])
        
        prev_zone, _ = get_detailed_strategy(prev_vix)
        curr_zone, curr_info = get_detailed_strategy(curr_vix)

        # [테스트 및 실전 통합 로직]
        msg = ""
        
        # 1. 존 변화가 있거나 휩쏘 의심될 때 (실전용)
        if prev_zone != curr_zone:
            is_valid = (curr_zone > prev_zone and curr_sma5 > prev_sma5) or (curr_zone < prev_zone and curr_sma5 < prev_sma5)
            header = "🚀 *[상태 변화 확정]*" if is_valid else "🤔 *[휩쏘 의심]*"
            msg = f"{header}\n\n📊 현재 VIX: `{curr_vix}`\n📍 단계: `Zone {curr_zone}`\n\n*전략 지침:*\n{curr_info}"
        
        # 2. 월요일 브리핑 (정기용)
        elif now.weekday() == 0:
            msg = f"📅 *[주간 브리핑]*\n\n📊 현재 VIX: `{curr_vix}`\n📍 단계: `Zone {curr_zone}`"
            
        # 3. 수동 실행 테스트 (지금 확인용)
        # 이 조건문이 있으면 강제로 실행했을 때 메시지를 보내줍니다
        else:
            msg = f"✅ *[VIX 시스템 연결 성공]*\n\n현재 수동으로 시스템을 가동했습니다.\n📊 VIX: `{curr_vix}`\n📍 단계: `Zone {curr_zone}`\n\n현재는 안정권이므로 특이사항 발생 시에만 알림이 옵니다."

        if msg:
            send_telegram_message(msg)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_vix_system()
