#!/usr/bin/python3
# -*- encoding:utf-8 -*-

import json
from urllib.parse import urlparse, urlencode, urlunparse
from urllib.request import urlopen

import pytz
import requests
import pandas as pd
from datetime import datetime
from datetime import timedelta
from decimal import Decimal


BASE = 'https://api.binance.com/'


def interval_to_ms(i: str) -> int:
    unit = i[-1]
    ts = 0
    if unit == 'd':
        ts = timedelta(days=int(i[:-1])).total_seconds() * 1000
    elif unit == 'h':
        ts = timedelta(hours=int(i[:-1])).total_seconds() * 1000
    elif unit == 'm':
        ts = timedelta(minutes=int(i[:-1])).total_seconds() * 1000
    else:
        raise NotImplementedError
    return ts


def date_to_ts(dt: str, fmt: str = '%Y-%m-%d') -> int:
    return datetime.strptime(dt, fmt).timestamp() * 1000


def date_fr_ts(ts: int, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    fmt = '{:'
    fmt += '{}'.format(fmt)
    fmt += '}'
    return fmt.format(datetime.fromtimestamp(ts / 1000))


def get_last_klines(s, i: str = '5m', q: int = 200) -> pd.DataFrame:
    URL = BASE + 'api/v1/klines'
    data = requests.get(URL, params={'symbol': s,
                                     'interval': i,
                                     'limit': q})
    if data.status_code == requests.codes.okay:
        data = json.loads(data.text)
        data = pd.DataFrame.from_records(data, columns=['open_time',
                                                        'open',
                                                        'high',
                                                        'low',
                                                        'close',
                                                        'volume',
                                                        'close_time',
                                                        'quote_volume',
                                                        'num_of_trades',
                                                        'base_asset_volume',
                                                        'quote_asset_volume',
                                                        'ignore'])
    data = data[['open_time', 'open', 'high', 'low', 'close', 'volume', 'quote_asset_volume']]
    data['open'] = data['open'].map(lambda x: Decimal(x))
    data['high'] = data['high'].map(lambda x: Decimal(x))
    data['low'] = data['low'].map(lambda x: Decimal(x))
    data['close'] = data['close'].map(lambda x: Decimal(x))
    data['volume'] = data['volume'].map(lambda x: Decimal(x))
    data['quote_asset_volume'] = data['quote_asset_volume'].map(lambda x: Decimal(x))
    return data


def get_historical_klines(s, i, start: str = None, end: str = None, sft: str = '%Y-%m-%d', eft: str = '%Y-%m-%d') -> pd.DataFrame:
    URL = BASE + 'api/v1/klines'
    if start is None:
        start = '{:%Y-%m-%d}'.format(datetime.now())
        start = date_to_ts(start)
    else:
        start = date_to_ts(start, sft)
    if end is None:
        end = '{:%Y-%m-%d %H:%M}'.format(datetime.now())
        end = date_to_ts(end, '%Y-%m-%d %H:%M')
    else:
        end = date_to_ts(end, eft)
    data = requests.get(URL, params={'symbol': s,
                                     'interval': i,
                                     'startTime': int(start),
                                     'endTime': int(end)})
    if data.status_code == requests.codes.okay:
        data = json.loads(data.text)
        data = pd.DataFrame.from_records(data, columns=['open_time',
                                                        'open',
                                                        'high',
                                                        'low',
                                                        'close',
                                                        'volume',
                                                        'close_time',
                                                        'quote_volume',
                                                        'num_of_trades',
                                                        'base_asset_volume',
                                                        'quote_asset_volume',
                                                        'ignore'])
        data = data[['open_time', 'open', 'high', 'low', 'close', 'quote_asset_volume', 'volume']]
        return data
    else:
        return


def get_symbols() -> list:
    URL = BASE + 'api/v1/ticker/24hr'
    s = list()
    data = requests.get(URL)
    data = json.loads(data.text)
    for e in data:
        s.append(e['symbol'])
    return s


def get_klines(s: str, i: str, cs: int) -> pd.DataFrame:
    url = BASE + 'api/v1/klines'
    params = {
        'symbol': s,
        'interval': i,
        'limit': cs
    }
    print(url)
    url_parts = list(urlparse(url))
    url_parts[4] = urlencode(params)
    url = urlunparse(url_parts)
    print(url)
    response = urlopen(url)
    data = json.load(response)
    data = pd.DataFrame.from_records(data, columns=['open_time',
                                                    'open',
                                                    'high',
                                                    'low',
                                                    'close',
                                                    'volume',
                                                    'close_time',
                                                    'quote_volume',
                                                    'num_of_trades',
                                                    'base_asset_volume',
                                                    'quote_asset_volume',
                                                    'ignore'])
    data = data[['open_time', 'open', 'high', 'low', 'close', 'quote_asset_volume', 'volume']]
    return data
