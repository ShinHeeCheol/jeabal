import time
import pyupbit
import datetime
import schedule
import numpy as np

access = "kWQsa9LxVqZZI9NRLivL6H5atow3jiexWkqG8QoX"
secret = "yvhiCowHeluMuOpQHoUfaHC5DbzGbsO1Ag8e708d"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

k = 0
def best_k():
    def get_ror(k=0.5):
        df = pyupbit.get_ohlcv("KRW-ETC", count = 7)
        df['range'] = (df['high'] - df['low']) * k
        df['target'] = df['open'] + df['range'].shift(1)

        df['ror'] = np.where(df['high'] > df['target'],
                            df['close'] / df['target']  ,
                            1)

        ror = df['ror'].cumprod()[-2]
        return ror
    global k 
    a= []
    for i in np.arange(0.1, 1.0, 0.1):
        ror = get_ror(i)
        a.append([i,ror])
    b = sorted(a, key=lambda a:a[1])
    c = b[-1]
    k = c[0]
    return k

schedule.every().day.at("08:50").do(best_k)

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
best_k()

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-ETC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-ETC", k)
            current_price = get_current_price("KRW-ETC")
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-ETC", krw*0.9995)
        else:
            btc = get_balance("ETC")
            if btc > 0.00008:
                upbit.sell_market_order("KRW-ETC", btc*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)