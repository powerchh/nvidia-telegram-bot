import sys
sys.path.append('.')
from simple_stock_analyzer import analyze_stock
# import os
import requests
import os

FINNHUB_API_KEY = 'd1fqoahr01qig3h3kmigd1fqoahr01qig3h3kmj0'
TELEGRAM_BOT_TOKEN = '8096117370:AAGNHZvW3HZboKbHDT5By6-S_iSErQtDOwM'
TELEGRAM_CHAT_ID = '8149043019'
# FINNHUB_API_KEY = os.environ.get('FINNHUB_API_KEY')
# TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
# TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_telegram_message(msg):
    # TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
    # CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': msg}
    requests.post(url, data=payload)

if __name__ == '__main__':
    STOCK_NAME = 'TSLA'
    stock_result = analyze_stock(STOCK_NAME, days=90, verbose=False)
    if stock_result['success']:
        msg = f"[{STOCK_NAME}分析]\n收盘价: ${stock_result['current_data']['close_price']:.2f}\nMACD: {stock_result['current_data']['macd']:.3f}\n趋势: {stock_result['status']['trend']}\n建议: {stock_result['recommendation']}"
    else:
        msg = f"[{STOCK_NAME}分析] 分析失败: {stock_result['error']}"
    print(msg)
    send_telegram_message(msg) 