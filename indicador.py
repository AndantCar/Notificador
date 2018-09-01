#!/usr/bin/python3
# -*- encoding:utf-8 -*-

import time
import threading
import argparse
import logging
from datetime import datetime
from osomatli.finance import get_signals
from osomatli.binance import get_symbols

import zmq


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(name)s - %(message)s')

FLAG = True


def send_message():
    try:
        context = zmq.Context()
    except Exception as details:
        logger.warning('No fue posible crear el objeto context\n'
                       'Details: {}'.format(details))
        return None
    try:
        socket = context.socket(zmq.REQ)
    except Exception as details:
        logger.warning('No fue posible crear el socket\n'
                       'Details: {}'.format(details))
        del context
        return None


def calc_stats(s, interval: str = '5m'):
    now = datetime.now()
    data = get_signals(s, interval=interval)
    print('Revisión {} : {:%H:%M:%S}'.format(interval, now))
    print(data.sort_values(by='open_time_dt', ascending=False))
    while FLAG:
        now = datetime.now()
        if interval[-1] == 'm':
            c = (now.minute % int(interval[:-1]) == 0)
        elif interval[-1] == 'h':
            c = (now.hour % int(interval[:-1]) == 0) and (now.minute == 0)
        else:
            raise NotImplementedError(
                'El tipo de intervalo {} no ha sido implementado'.format(interval[-1]))
        if (c) and (now.second > 0):
            try:
                data = get_signals(s, interval=interval)
                print('Revisión {} : {:%H:%M:%S}'.format(interval, now))
                print(data.sort_values(by='open_time_dt', ascending=False))
                time.sleep(60)
            except Exception as e:
                print(e)
                time.sleep(1)


def main(intervalos=None):
    """
    Args:
        intervalos(list): Lista con los intervalos de tiempo por ejemplo:
        ['5m', '10m',...'] por default solo se toma ['5m']
    :return:
    """
    global FLAG
    if intervalos is None:
        intervalos = ['5m']
    now = datetime.now()
    s = get_symbols()
    ts = []
    defbtc = ['XVGBTC', 'XRPBTC', 'IOTABTC', 'NEOBTC', 'FUELBTC', 'EOSBTC', 'BNBBTC']
    for e in s:
        if e.endswith('USDT') or e in defbtc:
            ts.append(e)
    s = ts
    print('Simbolos: {}\n{}'.format(len(s), s))
    threads = list()
    for i in intervalos:
        threads.append(threading.Thread(target=calc_stats,
                                        args=(s, i), name='Hilo {}'.format(i)))
    try:
        for t in threads:
            print('Iniciando: {}'.format(t.getName()))
            t.start()
        while FLAG:
            pass
    except KeyboardInterrupt:
        print('\nHas presionado Ctrl + C')
        FLAG = False
        print('Deteniendo hilos de ejecución')
        for t in threads:
            t.join(timeout=1)
            t.kill_received = True
        print('Terminado por el usuario')


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 2:
        print(sys.argv[1:])
        main(sys.argv[1:])
    else:
        main()
