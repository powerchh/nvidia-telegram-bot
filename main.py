import requests
import pandas as pd
from datetime import datetime, timedelta

api_key = 'BQUMH2LGY4P8OK1A'
symbol = 'TSLA'

# 使用免费接口 TIME_SERIES_DAILY
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=compact&apikey={api_key}'

try:
    response = requests.get(url, timeout=10)
    data = response.json()
    if "Time Series (Daily)" in data:
        df = pd.DataFrame(data["Time Series (Daily)"]).T
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        # 只取近90天
        start_date = datetime.now() - timedelta(days=90)
        recent_df = df[df.index >= start_date]
        print(recent_df)
    else:
        print('API返回异常:', data)
except Exception as e:
    print('请求异常:', e)