#!/usr/bin/python3
# -*- encoding:utf-8 -*-

import pytz
import time
import pandas as pd
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from binance.client import Client
from binance.websockets import BinanceSocketManager

from osomatli.finance import macdmfv


signals = list()
frames = dict()
symbol = 'BTCUSDT'
df = pd.DataFrame()
global symbol

spu = {
    'm': 60,
    'h': 60 * 60,
    'd': 60 * 60 * 24,
    'w': 60 * 60 * 24 * 7
}


def date_to_ms(date: str) -> int:
    utorigin = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    utdate = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    if utdate.tzinfo is None or utdate.tzinfo.utcoffset(utdate) is None:
        utdate = utdate.replace(tzinfo=pytz.utc)
    return int((utdate - utorigin).total_seconds() * 1000)


def interval_to_ms(interval: str) -> int:
    ms = None
    unit = interval[-1:]
    if unit in spu:
        try:
            ms = int(interval[:-1]) * spu[unit] * 1000
        except ValueError:
            return
    return ms


def handler(msg: dict):
    global df
    global signals
    global symbol
    content = msg['k']
    dt = datetime.utcfromtimestamp(content['t'] / 1000)
    et = datetime.utcfromtimestamp(msg['E'] / 1000)
    ot = datetime.utcfromtimestamp(content['t'] / 1000)
    ct = datetime.utcfromtimestamp(content['T'] / 1000)
    open = content['o']
    close = content['c']
    high = content['h']
    low = content['l']
    volume = content['v']
    data = {
        'datetime': ['{:%Y-%m-%d %H:%M:%S}'.format(dt)],
        'event_time': ['{:%Y-%m-%d %H:%M:%S}'.format(et)],
        'open_time': ['{:%Y-%m-%d %H:%M:%S}'.format(ot)],
        'close_time': ['{:%Y-%m-%d %H:%M:%S}'.format(ct)],
        'open': [open],
        'close': [close],
        'high': [high],
        'low': [low],
        'volume': [volume]
    }
    # print(msg)
    # print('[{}] ONTBTC > {} | {} : {} <{}>'.format(et, high, low, close,
    #                                                volume))
    tdf = pd.DataFrame.from_dict(data)
    if 'open_time' in df.columns:
        otstr = ot.strftime('%Y-%m-%d %H:%M:%S')
        if otstr in df['open_time'].unique():
            print('Actualizando Valores')
            df.loc[df['open_time'] == ot, 'event_time'] = et
            df.loc[df['open_time'] == ot, 'high'] = high
            df.loc[df['open_time'] == ot, 'low'] = low
            df.loc[df['open_time'] == ot, 'close'] = close
            df.loc[df['open_time'] == ot, 'volume'] = volume
        else:
            print('Agregando valores al final')
            df = macdmfv(df, r=1)
            tail = df.tail(1)
            # print('Tail: {}'.format(type(tail)))
            # print('{}'.format(tail['SIGNAL'].values[0]))
            if tail['SIGNAL'].values[0]:
                signals.append(tail.to_dict())
                print(signals)
                print('SEÑAAAAAAAAAAAAAAAL')
            # else:
            #     print('NO HAY SEÑAL')
            df = df.append(tdf, sort=False)
    else:
        print('Creando nuevo DataFrame')
        df = df.append(tdf, sort=False)
    df.reset_index(drop=True, inplace=True)
    df.to_csv('data/STREAM_{}.csv'.format(symbol))


def main(symbol: str = 'BTCUSDT', interval: str = '15m'):
    global df
    client = Client('', '')
    output = list()
    timeframe = interval_to_ms(interval)
    start = datetime.combine((datetime.utcnow() - timedelta(days=2)).date(),
                             datetime.min.time())
    end = datetime.utcnow()
    start = date_to_ms('{:%Y-%m-%d %H:%M:%S}'.format(start))
    end = date_to_ms('{:%Y-%m-%d %H:%M:%S}'.format(end))
    idx = 0
    symbol_existed = False
    while start < end:
        tdata = client.get_klines(symbol=symbol,
                                  interval=interval,
                                  limit=500,
                                  startTime=start,
                                  endTime=end)
        if not symbol_existed and len(tdata):
            symbol_existed = True
        if symbol_existed:
            output += tdata
            start = tdata[-1][0] + timeframe
        else:
            start += timeframe
        idx += 1
        if len(tdata) < 500:
            break
        if idx % 3 == 0:
            time.sleep(1)
    df = pd.DataFrame.from_records(output, columns=['open_time', 'open', 'high', 'low', 'close', 'volume',
                                                    'close_time', 'quote_asset_volume', 'trades',
                                                    'base_orders_volume', 'quote_orders_volume', 'delete_this'])
    df = df[['open_time', 'close_time', 'open', 'close', 'high', 'low', 'volume']]
    df['open'] = df['open'].map(lambda x: Decimal(x))
    df['close'] = df['close'].map(lambda x: Decimal(x))
    df['high'] = df['high'].map(lambda x: Decimal(x))
    df['low'] = df['low'].map(lambda x: Decimal(x))
    df['volume'] = df['volume'].map(lambda x: Decimal(x))
    df['open_time'] = df['open_time'].map(lambda x: '{:%Y-%m-%d %H:%M:%S}'.format(datetime.utcfromtimestamp(int(x) / 1000.0)))
    df['close_time'] = df['close_time'].map(lambda x: '{:%Y-%m-%d %H:%M:%S}'.format(datetime.utcfromtimestamp(int(x) / 1000.0)))
    bsm = BinanceSocketManager(client)
    bsm.start_kline_socket(symbol, handler, interval)
    try:
        bsm.start()
        bsm.join()
    except KeyboardInterrupt:
        bsm.close()
        exit(230)


if __name__ == '__main__':
    symbol = 'BTCUSDT'
    main(symbol)
