import requests
import os

def get_nvidia_price():
    API_KEY = os.environ['FINNHUB_API_KEY']
    url = f'https://finnhub.io/api/v1/quote?symbol=NVDA&token={API_KEY}'
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        price = data['c']
        return f"NVIDIA 当前股价：${price}"
    except Exception as e:
        return f"获取股价失败：{e}"

def send_telegram_message(msg):
    TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
    CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': msg}
    requests.post(url, data=payload)

if __name__ == '__main__':
    result = get_nvidia_price()
    print(result)
    send_telegram_message(result)