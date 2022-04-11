from pprint import pformat
import time
import pyupbit
import schedule
import datetime
import pandas as pd
import requests

access = "kWQsa9LxVqZZI9NRLivL6H5atow3jiexWkqG8QoX"
secret = "yvhiCowHeluMuOpQHoUfaHC5DbzGbsO1Ag8e708d"

def get_current_price(ticker):
    """현재가 조회"""
    current_price = pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]
    return current_price

ma15=""
def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    global ma15
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

ma20=""
def get_ma20(ticker):
    """20일 이동 평균선 조회"""
    global ma20
    df = pyupbit.get_ohlcv(ticker, interval="day", count=20)
    ma20 = df['close'].rolling(20).mean().iloc[-1]
    return ma20

socks=""
bucks=""
cocks=""
def get_MACD(ticker):
    """MACD 조회"""
    global socks
    global bucks
    global cocks
    
    macd_short, macd_long, macd_signal=12,26,9
    
    df = pyupbit.get_ohlcv(ticker, interval="day")
    df["MACD_short"] = df["close"].ewm(span=macd_short).mean()
    df["MACD_long"] = df["close"].ewm(span=macd_long).mean()
    df["MACD"]= df.apply(lambda x: (x["MACD_short"]-x["MACD_long"]), axis=1)
    socks= df["MACD"].iloc[-1]
    df["MACD_signal"]=df["MACD"].ewm(span=macd_signal).mean()
    bucks = df["MACD_signal"].iloc[-1]
    cocks = ((socks - bucks)/socks)* 100

macd_1=""
macd_2=""
signal_1=""
def get_MACD_minutes(ticker):
    """MACD 조회"""
    global macd_1
    global macd_2
    global signal_1
    macd_short, macd_long, macd_signal=12,26,9
    
    df = pyupbit.get_ohlcv(ticker, interval="minutes1")
    df["MACD_short"] = df["close"].ewm(span=macd_short).mean()
    df["MACD_long"] = df["close"].ewm(span=macd_long).mean()
    df["MACD"]= df.apply(lambda x: (x["MACD_short"]-x["MACD_long"]), axis=1)
    macd_1= df["MACD"].iloc[-1]
    macd_2= df["MACD"].iloc[-2]
    df["MACD_signal"]=df["MACD"].ewm(span=macd_signal).mean()
    signal_1 = df["MACD_signal"].iloc[-1]
    
macd_10_1=""
macd_10_2=""
def get_MACD_minutes_10(ticker):
    """MACD 조회"""
    global macd_10_1
    global macd_10_2

    macd_short, macd_long =12, 26
    
    df = pyupbit.get_ohlcv(ticker, interval="minutes10")
    df["MACD_short"] = df["close"].ewm(span=macd_short).mean()
    df["MACD_long"] = df["close"].ewm(span=macd_long).mean()
    df["MACD"]= df.apply(lambda x: (x["MACD_short"]-x["MACD_long"]), axis=1)
    macd_10_1= df["MACD"].iloc[-1]
    macd_10_2= df["MACD"].iloc[-2]
    
def get_rsi(ticker):
    url = "https://api.upbit.com/v1/candles/days"

    querystring = {"market":ticker,"count":"500"}
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    df = pd.DataFrame(data)
    df=df.reindex(index=df.index[::-1]).reset_index()
    df['close']=df["trade_price"]

    def rsi(ohlc: pd.DataFrame, period: int = 14):
        ohlc["close"] = ohlc["close"]
        delta = ohlc["close"].diff()
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        _gain = up.ewm(com=(period - 1), min_periods=period).mean()
        _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()

        RS = _gain / _loss
        return pd.Series(100 - (100 / (1 + RS)), name="RSI")
    Rsi = rsi(df,14).iloc[-1]
    return Rsi

def get_volume(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minutes1", count = 10)
    volume = df.iloc[-1]['volume']
    return volume 
    
def get_mean(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minutes1", count = 10)
    mean = (df['volume'].rolling(10).mean().iloc[-1])*2.2
    return mean  

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

selected=[]
def get_first():
    global selected
    
    # 업비트에 있는 tickers을 받아온다. 
    tickers = pyupbit.get_tickers('KRW-')
    
    for ticker in tickers:
        try:
            current_price = get_current_price(ticker)
            Rsi = get_rsi(ticker)
            ma15 = get_ma15(ticker)
            ma20 = get_ma20(ticker)
            get_MACD(ticker)
            if current_price > ma15 > ma20:
                if socks > bucks:
                    if 23 < cocks <55:
                        if 62 < Rsi < 82:
                            selected.append(ticker)
        except:
            continue

schedule.every().day.at("09:00").do(get_first)
schedule.every().day.at("12:00").do(get_first)
schedule.every().day.at("15:00").do(get_first)
schedule.every().day.at("18:00").do(get_first)
schedule.every().day.at("21:00").do(get_first)

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
get_first()
print(selected)

while True:
    try:
        schedule.run_pending()
        print(selected, "30초마다 한번씩 감시중", upbit.get_balance("KRW"), datetime.datetime.now())

        for select in selected:
            print(select)
            mean = get_mean(select)
            print(mean)
            volume = get_volume(select)
            print(volume)
            get_MACD_minutes(select)
            krw = upbit.get_balance("KRW")
            if krw > 300000 :
                if macd_1 > signal_1:  
                    if volume > mean: 
                        upbit.buy_market_order(select, krw*0.9995)
                        print(select, "매수")
            else:
                btc = upbit.get_balance(select)
                get_MACD_minutes_10(select)            
                if btc != 0:          
                    if macd_10_2 > macd_10_1:
                        upbit.sell_market_order(select, btc)
                        print(select, "매도")
        time.sleep(60)
    except Exception as e:
        print(e)
        time.sleep(1)