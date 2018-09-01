#!/usr/bin/python3
# -*- encoding:utf-8 -*-
import time
from datetime import datetime

import pandas as pd
import pytz
from binance.client import Client
from binance.websockets import BinanceSocketManager
from decimal import Decimal

from api.finance import mfi, typical_price


class APIManager(object):
    secs_p_unit = {
        'm': 60,
        'h': 60 * 60,
        'd': 60 * 60 * 24,
        'w': 60 * 60 * 24 * 7
    }

    def __init__(self, key: str = '', secret: str = ''):
        self.__client = Client(key, secret)
        self.__bsm = BinanceSocketManager(self.__client)

    def start_sockets(self):
        self.__bsm.start()

    def stop_sockets(self):
        self.__bsm.close()

    def idle(self):
        self.__bsm.join()

    def get_symbols(self) -> list:
        tickers = self.__client.get_all_tickers()
        symbols = list()
        for i, s in enumerate(tickers):
            symbols.append(s['symbol'])
        return symbols

    def add_symbol_to_klines_socket(self, symbol, callback, interval: str = '1m'):
        self.__bsm.start_kline_socket(symbol, callback, interval)

    def del_symbol_to_klines_socket(self, symbol):
        raise NotImplementedError

    def get_all_klines_socket(self, interval: str = '1m', func = None):
        """
        Este método carga en el SocketManager los símbolos que se pedirán para
        el Streaming, la estructura del mensaje de retorno es un Diccionario de python
        con los siguientes elementos:
        {
            "e": "kline",
            "E": 123456789,   // Event time
            "s": "BNBBTC",    // Symbol
            "k": {
                "t": 123400000, // Kline start time
                "T": 123460000, // Kline close time
                "s": "BNBBTC",  // Symbol
                "i": "1m",      // Interval
                "f": 100,       // First trade ID
                "L": 200,       // Last trade ID
                "o": "0.0010",  // Open price
                "c": "0.0020",  // Close price
                "h": "0.0025",  // High price
                "l": "0.0015",  // Low price
                "v": "1000",    // Base asset volume
                "n": 100,       // Number of trades
                "x": false,     // Is this kline closed?
                "q": "1.0000",  // Quote asset volume
                "V": "500",     // Taker buy base asset volume
                "Q": "0.500",   // Taker buy quote asset volume
                "B": "123456"   // Ignore
            }
        }
        :param interval: Periodo de delimitación, genera una variación en los valores de
        Kline start time y Kline close time, los valores posibles son:
        '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w'
        """
        symbols = list(self.get_all_tickers()['symbol'])
        for s in symbols:
            if func:
                self.__bsm.start_kline_socket(s, func, interval)
            else:
                self.__bsm.start_kline_socket(s, self.kline_callback, interval)

    def get_all_tickers(self) -> pd.DataFrame:
        tickers = self.__client.get_all_tickers()
        df = pd.DataFrame()
        for i, s in enumerate(tickers):
            df = df.append(pd.DataFrame(s, index=[i]))
        return df

    def get_last_klines(self, symbol: str, interval: str) -> pd.DataFrame:
        output = list()
        timeframe = self.interval_to_ms(interval)
        idx = 0
        tdata = self.__client.get_klines(symbol=symbol,
                                            interval=interval,
                                            limit=200)
        df = pd.DataFrame.from_records(tdata, columns=['open_time', 'open', 'high', 'low', 'close', 'volume',
                                                       'close_time', 'quote_asset_volume', 'trades',
                                                       'base_orders_volume', 'quote_orders_volume', 'delete_this'])
        df['open'] = df['open'].map(lambda x: Decimal(x))
        df['close'] = df['close'].map(lambda x: Decimal(x))
        df['high'] = df['high'].map(lambda x: Decimal(x))
        df['low'] = df['low'].map(lambda x: Decimal(x))
        df['volume'] = df['volume'].map(lambda x: Decimal(x))
        df['quote_asset_volume'] = df['quote_asset_volume'].map(lambda x: Decimal(x))
        df['trades'] = df['trades'].map(lambda x: Decimal(x))
        df['base_orders_volume'] = df['base_orders_volume'].map(lambda x: Decimal(x))
        df['quote_orders_volume'] = df['quote_orders_volume'].map(lambda x: Decimal(x))
        df = df.drop(columns=['delete_this'])
        return df

    def get_historical_klines(self, symbol: str, interval: str, start: str, end: str = None) -> pd.DataFrame:
        """
        La estructura del histórico es un DataFrame con las siguientes columnas:
        * Open Time
        * Open
        * High
        * Low
        * Close
        * Volume
        * Close Time
        * Quote asset volume
        * Number of Trades
        * Taker buy base asset volume
        * Taker buy quote asset volume
        :param symbol: Simbolo del instrumento
        :param interval: '1m', '3m', '5m', '1h', '3h', '1d', '1w'
        :param start: Fecha de inicio de la solicitud del histórico '2018-03-21'
        :param end: Fecha de fin del histórico '2018-03-24'
        :return: pd.DataFrame
        """
        output = list()
        timeframe = self.interval_to_ms(interval)
        start = self.date_to_ms(start)
        if end:
            end = self.date_to_ms(end)
        else:
            end = self.date_to_ms(datetime.utcnow().strftime('%Y-%m-%d'))
        idx = 0
        symbol_existed = False
        while start < end:
            tdata = self.__client.get_klines(symbol=symbol,
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
        df['open'] = df['open'].map(lambda x: Decimal(x))
        df['close'] = df['close'].map(lambda x: Decimal(x))
        df['high'] = df['high'].map(lambda x: Decimal(x))
        df['low'] = df['low'].map(lambda x: Decimal(x))
        df['volume'] = df['volume'].map(lambda x: Decimal(x))
        df['quote_asset_volume'] = df['quote_asset_volume'].map(lambda x: Decimal(x))
        df['trades'] = df['trades'].map(lambda x: Decimal(x))
        df['base_orders_volume'] = df['base_orders_volume'].map(lambda x: Decimal(x))
        df['quote_orders_volume'] = df['quote_orders_volume'].map(lambda x: Decimal(x))
        df = df.drop(columns=['delete_this'])
        return df

    @staticmethod
    def date_to_ms(date: str) -> int:
        """
        Este método convierte una fecha dada en formato YYYY-MM-DD a milisegundos
        contados a partir del primero de enero de 1970.
        :param date: Fecha String en formato 'YYYY-MM-DD'
        :return: Integer Milisegundos a partir de la fecha cero.
        """
        utorigin = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
        utdate = datetime.strptime(date, '%Y-%m-%d')
        if utdate.tzinfo is None or utdate.tzinfo.utcoffset(utdate) is None:
            utdate = utdate.replace(tzinfo=pytz.utc)
        return int((utdate - utorigin).total_seconds() * 1000.0)

    @staticmethod
    def interval_to_ms(interval: str) -> int:
        """
        Este método toma un intervalo de los permitidos y lo convierte a milisegundos
        :param interval: Intervalos de tiempo para las velas.
        :return: Integer Milisegundos equivalentes al intervalo.
        """
        ms = None
        unit = interval[-1:]
        if unit in APIManager.secs_p_unit:
            try:
                ms = int(interval[:-1]) * APIManager.secs_p_unit[unit] * 1000
            except ValueError:
                pass
        return ms

    @staticmethod
    def kline_callback(msg):
        """
        El mensaje recibido a través del WebSocket es un diccionario de Python con los siguientes elementos.
            "e": "kline",
            "E": 123456789,   // Event time
            "s": "BNBBTC",    // Symbol
            "k":
                "t": 123400000, // Kline start time
                "T": 123460000, // Kline close time
                "s": "BNBBTC",  // Symbol
                "i": "1m",      // Interval
                "f": 100,       // First trade ID
                "L": 200,       // Last trade ID
                "o": "0.0010",  // Open price
                "c": "0.0020",  // Close price
                "h": "0.0025",  // High price
                "l": "0.0015",  // Low price
                "v": "1000",    // Base asset volume
                "n": 100,       // Number of trades
                "x": false,     // Is this kline closed?
                "q": "1.0000",  // Quote asset volume
                "V": "500",     // Taker buy base asset volume
                "Q": "0.500",   // Taker buy quote asset volume
                "B": "123456"   // Ignore
        """
        if msg['k']['s'] == 'XVGBTC':
            df = pd.DataFrame({
                "open_time": msg['k']['t'],
                "open": Decimal(msg['k']['o']),
                "high": Decimal(msg['k']['h']),
                "low": Decimal(msg['k']['l']),
                "close": Decimal(msg['k']['c']),
                "volume": Decimal(msg['k']['v']),
                "close_time": msg['k']['T'],
                "quote_asset_volume": Decimal(msg['k']['q']),
                "trades": Decimal(msg['k']['n']),
                "base_orders_volume": Decimal(msg['k']['V']),
                "quote_orders_volume": Decimal(msg['k']['Q'])
            }, index=[1])
            df = typical_price(df)
            row = "[{}]".format(msg['E'] / 1000)
            row += " Symbol: {}".format(msg['k']['s'])
            row += "\tOpen: {}".format(msg['k']['o'])
            row += "\tClose: {}".format(msg['k']['c'])
            row += "\tHigh: {}".format(msg['k']['h'])
            row += "\tLow: {}".format(msg['k']['l'])
            row += "\tVolume: {}".format(msg['k']['v'])
            row += "\tClosed: {}".format(msg['k']['x'])
            row += "\tTPrice: {}".format(df.iloc[0]['typical_price'])
            print(row)

    @staticmethod
    def ms_to_timestamp(value: int):
        return datetime.utcfromtimestamp(value)


def main():
    api = APIManager()
    api.get_all_klines_socket()
    try:
        api.start_sockets()
        api.idle()
    except KeyboardInterrupt:
        api.stop_sockets()


if __name__ == '__main__':
    main()
