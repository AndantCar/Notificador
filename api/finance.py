#!/usr/bin/python3
# -*- encoding:utf-8 -*-


import pandas as pd


def ema(data: pd.DataFrame, period: int = 0, column: str = 'close'):
    data['ema' + str(period)] = data[column].ewm(ignore_na=False, min_periods=period, com=period, adjust=True).mean()
    return data


def macd(data: pd.DataFrame, long: int = 26, short: int = 12, signal: int = 9, column: str = 'close') -> pd.DataFrame:
    remove_cols = []
    if not 'ema' + str(long) in data.columns:
        data = ema(data, long, column)
        remove_cols.append('ema' + str(long))
    if not 'ema' + str(short) in data.columns:
        data = ema(data, short, column)
        remove_cols.append('ema' + str(short))
    data['macd_val'] = data['ema' + str(short)] - data['ema' + str(long)]
    data['macd_signal_line'] = data['macd_val'].ewm(ignore_na=False, min_periods=0, com=signal, adjust=True).mean()
    data = data.drop(columns=remove_cols)
    return data


def typical_price(data, high: str = 'high', low: str = 'low', close: str = 'close') -> pd.DataFrame:
    data['typical_price'] = (float(data[high]) + float(data[low]) + float(data[close])) / 3
    return data


def mfi(data: pd.DataFrame, period: int = 14, column: str = 'volume') -> pd.DataFrame:
    remove_tp_col = False
    if 'typical_price' not in data.columns:
        data = typical_price(data)
        remove_tp_col = True
    data['money_flow'] = data['typical_price'] * data[column]
    data['money_ratio'] = 0.
    data['money_flow_index'] = 0.
    data['money_flow_positive'] = 0.
    data['money_flow_negative'] = 0.

    for i, r in data.iterrows():
        if i > 0:
            if r['typical_price'] < data.at[i - 1, 'typical_price']:
                data.set_value(i, 'money_flow_positive', r['money_flow'])
            else:
                data.set_value(i, 'money_flow_negative', r['money_flow'])
        if i >= period:
            positive_sum = data['money_flow_positive'][i - period:i].sum()
            negative_sum = data['money_flow_negative'][i - period:i].sum()
            if negative_sum == 0:
                negative_sum = 1e-10
            m_r = positive_sum / negative_sum
            m_fi = 1 - (1 / (1 + m_r))
            data.set_value(i, 'money_ratio', m_r)
            data.set_value(i, 'money_flow_index', m_fi)
    rcols = ['money_flow', 'money_ratio', 'money_flow_positive', 'money_flow_negative']
    if remove_tp_col:
        rcols.append('typical_price')
    data = data.drop(columns=rcols)
    return data
