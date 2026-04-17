import yfinance as yf
import pandas as pd
import requests
import os
import logging
from datetime import datetime
import pytz

# GitHub Secrets에서 보안 정보를 불러옵니다
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

        msg = ""
        if prev_zone != curr_zone:
            is_valid = (curr_zone > prev_zone and curr_sma5 > prev_sma5) or (curr_zone < prev_zone and curr_sma5 < prev_sma5)
            header = "🚀 *[상태 변화 확정]*" if is_valid else "🤔 *[휩쏘 의심]*"
            msg = f"{header}\n\n📊 현재 VIX: `{curr_vix}`\n📍 단계: `Zone {curr_zone}`\n\n*전략 지침:*\n{curr_info}"
        elif now.weekday() == 0:
            msg = f"📅 *[주간 브리핑]*\n\n📊 현재 VIX: `{curr_vix}`\n📍 단계: `Zone {curr_zone}`"

        if msg: send_telegram_message(msg)
    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    run_vix_system()
