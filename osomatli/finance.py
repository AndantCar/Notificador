#!/usr/bin/python3
# -*- encoding:utf-8 -*-
import time
import pandas as pd
import numpy as np

from datetime import datetime, date, timedelta
from decimal import Decimal
from osomatli.binance import get_last_klines


def datestamp(data: pd.DataFrame, col: str = 'open_time') -> pd.DataFrame:
    data['{}_dt'.format(col)] = ''
    for i, r in data.iterrows():
        data.at[i, '{}_dt'.format(col)] = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.utcfromtimestamp(r[col] / 1000))
    return data


def vma(data: pd.DataFrame, t: int = 1, col: str = 'volume') -> pd.DataFrame:
    data['VMA({})'.format(t)] = data[col].rolling(t).mean()
    return data


def sma(data: pd.DataFrame, t: int = 1, col: str = 'close') -> pd.DataFrame:
    data['SMA({})'.format(t)] = data[col].rolling(t).mean()
    return data


def ema(data: pd.DataFrame, t: int = 1, col: str = 'close') -> pd.DataFrame:
    data['EMA({})'.format(t)] = data[col].ewm(ignore_na=False, min_periods=t,
                                              com=t, adjust=True).mean()
    return data


def eman(data: pd.DataFrame, t: int = 1, col: str = 'close') -> pd.DataFrame:
    data['EMAN({})'.format(t)] = np.nan
    for i, r in data.iterrows():
        if i < t - 1:
            continue
        elif i == t - 1:
            data.at[i, 'EMAN({})'.format(t)] = float(data.iloc[0:t - 1][col].sum() / t)
        else:
            data.at[i, 'EMAN({})'.format(t)] = (float(data.at[i, col]) * (2 / (t + 1))) +\
                                                 (data.at[i - 1, 'EMAN({})'.format(t)] * (1 - (2 / (t + 1))))
    return data


def emat(df: pd.DataFrame, t: int = 1, col: str = 'close') -> pd.DataFrame:
    df['EMAT({})'.format(t)] = np.nan
    for i, r in df.iterrows():
        if i < t - 1:
            continue
        elif i == t - 1:
            avg = float(df.iloc[0:t - 1][col].sum(min_count=1) / t)
            df.at[i, 'EMAT({})'.format(t)] = avg
        else:
            a = float(df.at[i, col])
            b = (2 / (t + 1))
            c = df.at[i - 1, 'EMAT({})'.format(t)]
            d = (1 - (2 / (t + 1)))
            if pd.isna(c) and pd.isna(a):
                new_ema = np.nan
            elif pd.isna(c) and not pd.isna(a):
                new_ema = a * b
            elif not pd.isna(c) and pd.isna(a):
                new_ema = c * d
            else:
                new_ema = (a * b) + (c * d)
            df.at[i, 'EMAT({})'.format(t)] = new_ema
    return df


def macd(data: pd.DataFrame, l: int = 26, s: int = 12, r: int = 9,
         col: str = 'close') -> pd.DataFrame:
    remove_cols = []
    if not 'EMA({})'.format(l) in data.columns:
        data = ema(data, l, col)
        remove_cols.append('EMA({})'.format(l))
    if not 'EMA({})'.format(s) in data.columns:
        data = ema(data, s, col)
        remove_cols.append('EMA({})'.format(s))
    data['MACD_VAL'] = data['EMA({})'.format(s)] - data['EMA({})'.format(l)]
    data['MACD_SIG'] = ema(data, r, col='MACD_VAL')['EMA({})'.format(r)]
    data['MACD_HIST'] = data['MACD_VAL'] - data['MACD_SIG']
    data = data.drop(columns=remove_cols)
    return data


def macdt(data: pd.DataFrame, l: int = 26, s: int = 12, r: int = 9, col: str = 'close') -> pd.DataFrame:
    remove_cols = []
    if not 'EMAT({})'.format(l) in data.columns:
        data = emat(data, l, col)
        remove_cols.append('EMAT({})'.format(l))
    if not 'EMAT({})'.format(s) in data.columns:
        data = emat(data, s, col)
        remove_cols.append('EMAT({})'.format(s))
    data['MACDT_VAL'] = data['EMAT({})'.format(s)] - data['EMAT({})'.format(l)]
    data['MACDT_SIG'] = emat(data, r, col='MACDT_VAL')['EMAT({})'.format(r)]
    data['MACDT_HIST'] = data['MACDT_VAL'] - data['MACDT_SIG']
    data = data.drop(columns=remove_cols)
    return data


def utctomex(dt: str, fmt: str = '%Y-%m-%d %H:%M:%S') -> datetime:
    dt = datetime.strptime(dt, fmt)
    dt = dt - timedelta(hours=5)
    return dt


def get_signals(symbols: list, interval: str = '15m', start: str = None, end: str = None, sfmt = '%Y-%m-%d', efmt = '%Y-%m-%d') -> pd.DataFrame:
    data = pd.DataFrame()
    if start is None:
        start = '{:%Y-%m-%d}'.format(datetime.now().date() - timedelta(days=1))
    if end is None:
        end = '{:%Y-%m-%d}'.format(datetime.now().date() + timedelta(days=1))
    symbols = set(symbols)
    for s in symbols:
        df = get_last_klines(s, interval)
        df = macdmfv(df)
        df = datestamp(df)
        df['SYMBOL'] = s
        min = df[['SYMBOL', 'open_time_dt', 'close', 'MONEY_FLOW_INDEX', 'MACDT_HIST', 'volume', 'VMA(10)', 'SIGNAL']]
        min = min.loc[min['SIGNAL'] == True]
        data = data.append(min)
        data.reset_index(drop=True, inplace=True)
        time.sleep(0.1)
    data['open_time_dt'] = data['open_time_dt'].map(utctomex)
    return data


def tp(data, hc: str = 'high', lc: str = 'low',
       cc: str = 'close') -> pd.DataFrame:
    data['TYP_PRICE'] = (pd.to_numeric(data[hc])
                         + pd.to_numeric(data[lc])
                         + pd.to_numeric(data[cc])) / 3
    return data


def mfi(data: pd.DataFrame, t: int = 14, col: str = 'volume') -> pd.DataFrame:
    remove_tp_col = False
    if 'TYP_PRICE' not in data.columns:
        data = tp(data)
        remove_tp_col = True
    data['MONEY_FLOW'] = data['TYP_PRICE'] * pd.to_numeric(data[col])
    data['MONEY_FLOW_POSITIVE'] = 0.
    data['MONEY_FLOW_NEGATIVE'] = 0.
    for i, r in data.iterrows():
        if i > 0:
            if r['TYP_PRICE'] < data.at[i - 1, 'TYP_PRICE']:
                data.at[i, 'MONEY_FLOW_NEGATIVE'] = r['MONEY_FLOW']
            else:
                data.at[i, 'MONEY_FLOW_POSITIVE'] = r['MONEY_FLOW']
    data['MPS'] = data['MONEY_FLOW_POSITIVE'].rolling(t).sum()
    data['MNS'] = data['MONEY_FLOW_NEGATIVE'].rolling(t).sum()
    data['MONEY_RATIO'] = data['MPS'] / data['MNS']
    data['MONEY_FLOW_INDEX'] = (100 - (100 / (1 + data['MONEY_RATIO'])))
    if remove_tp_col:
        data = data.drop(columns=['TYP_PRICE'])
    return data


def macdmfv(data: pd.DataFrame, t: int = 14, v: int = 10,
            l: int = 26, s: int = 12, r: int = 9, c: str = 'close',
            vc: str = 'volume') -> pd.DataFrame:
    data = macdt(data, l, s, r, c)
    data = mfi(data, t, vc)
    data = vma(data, v, vc)
    data['SIGNAL'] = False
    for i, r in data.iterrows():
        if i > 0:
            MACD_P = r['MACDT_HIST'] >= 0
            MACD_C = (data.at[i - 1, 'MACDT_HIST'] < 0)
            MACD = MACD_P and MACD_C
            VMA = data.at[i - 1, 'VMA({})'.format(v)]
            VOL = float(r[vc]) >= (0.5 * VMA)
            MFI = r['MONEY_FLOW_INDEX'] <= 35
            if MACD and VOL and MFI:
                data.at[i, 'SIGNAL'] = True
    return data


if __name__ == '__main__':
    from api.binance import APIManager
    am = APIManager()
    df = am.get_historical_klines('VETUSDT', '15m', '2018-07-28', '2018-08-01')
    df = emat(df, 26)
    df = emat(df, 12)
    df['MACDT_VAL'] = df['EMAT(12)'] - df['EMAT(26)']
    df['MACDT_SIG'] = emat(df, 9, col='MACDT_VAL')['EMAT(9)']
    df['MACDT_HIST'] = df['MACDT_VAL'] - df['MACDT_SIG']
    df = macd(df)
    min = df[['open_time', 'MACDT_VAL', 'MACD_VAL', 'MACDT_SIG', 'MACD_SIG', 'MACDT_HIST', 'MACD_HIST']]
    min = datestamp(min)
    min = min[['open_time_dt', 'MACDT_VAL', 'MACD_VAL', 'MACDT_SIG', 'MACD_SIG', 'MACDT_HIST', 'MACD_HIST']]
    print(min)

