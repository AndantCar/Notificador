#!/usr/bin/pytyhon3
# -*- encoding:utf-8 -*-

import asyncio
import json
import logging
from decimal import Decimal

import pandas as pd
from datetime import datetime, time, timedelta
from urllib.parse import urlparse, urlencode, urlunparse
from urllib.request import urlopen
from osomatli.finance import macdmfv, datestamp

BASE_URL = 'https://api.binance.com/api/v1/'
flag = True


async def get_klines(s: str, i: str, c: int = 500) -> pd.DataFrame:
    logging.debug('Task {} de {} en {}'.format(c, s, i))
    url = BASE_URL + 'klines'
    params = {
        'symbol': s,
        'interval': i,
        'limit': c
    }
    print(url)
    url_parts = list(urlparse(url))
    url_parts[4] = urlencode(params)
    url = urlunparse(url_parts)
    logging.debug(url)
    response = urlopen(url)
    data = json.load(response)
    logging.debug('Task {} de {} en {} Finalizado'.format(c, s, i))
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
    data['open'] = data['open'].map(lambda x: Decimal(x))
    data['high'] = data['high'].map(lambda x: Decimal(x))
    data['low'] = data['low'].map(lambda x: Decimal(x))
    data['close'] = data['close'].map(lambda x: Decimal(x))
    data['volume'] = data['volume'].map(lambda x: Decimal(x))
    data['quote_asset_volume'] = data['quote_asset_volume'].map(lambda x: Decimal(x))
    return data


async def get_data(s: str, i: str):
    global flag
    ts = int(i[:-1])
    while flag:
        if datetime.now().minute % ts == 0:
            logging.debug('Requesting Data {}'.format(s))
            data = await get_klines(s, i, 400)
            data = macdmfv(data)
            data['open_time'] = data['open_time'].map(lambda x: datetime.fromtimestamp(x / 1000))
            data = data.loc[data['SIGNAL'] == True]
            for j, r in data.iterrows():
                logging.debug('Señal en {}: {}\t{}\t{}'.format(s, r['open_time'],
                                                               r['MONEY_FLOW_INDEX'],
                                                               r['MACDT_HIST']))
            logging.debug('Data {} Acquired'.format(s))
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(1)


def main():
    global flag
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] %(message)s')
    logging.debug('Obteniendo Event Loop')
    loop = asyncio.get_event_loop()
    agather = asyncio.gather()
    try:
        logging.debug('Iniciando Tasks')
        loop.run_until_complete(asyncio.gather(
            get_data('BTCUSDT', '1m'),
            get_data('XRPUSDT', '1m'),
            get_data('ETHUSDT', '1m')
        ))
    except KeyboardInterrupt:
        logging.warning('Se detuvo la operación por el usuario.')
        flag = False
    finally:
        logging.info('Cerrando Loop')
        loop.close()


if __name__ == '__main__':
    main()
