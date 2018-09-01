#!/usr/bin/python3
# -*- encoding:utf-8 -*-


import logging
import time
from datetime import datetime
from decimal import Decimal

from sqlalchemy.engine.url import URL

from api.binance import APIManager
from api.database import Base, Instrument, create_engine, sessionmaker


logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(levelname)8s : %(message)s')


Session = sessionmaker()


class Streamer(object):
    def __init__(self, conn: str):
        self.__engine = create_engine(conn)
        self.__session = Session(bind=self.__engine)
        Base.metadata.create_all(self.__engine)

    def update(self, msg):
        t = time.time()
        data = {
            'name': msg['k']['s'],
            'date': datetime.utcfromtimestamp(msg['E'] / 1000).date(),
            'time': datetime.utcfromtimestamp(msg['E'] / 1000).time(),
            'value': Decimal(msg['k']['c'])
        }

        divisa = self.__session.query(Instrument).filter_by(name=data['name']).first()
        if divisa:
            divisa.date = data['date']
            divisa.time = data['time']
            divisa.value = data['value']
        else:
            ud = Instrument(**data)
            self.__session.add(ud)
        t2 = time.time()
        logging.debug('Dirty: {}'.format(self.__session.dirty))
        logging.debug('New: {}'.format(self.__session.new))
        self.__session.commit()
        logging.debug('Elapsed: {}'.format(t2 - t))


def main():
    am = APIManager()
    # Si quieres usar MSSQL debes instalar PyMSSQL
    # Y reemplazar la cadena de conexión con eso
    # mssql+pymssql://user:password@hostname:port/dbname
    # erver=localhost;Database=IndicesInfosel;Uid=sa;Password=ArmiTage14
    conn = {
        'drivername': 'mssql+pyodbc',
        'username': 'sa',
        'password': 'ArmiTage14',
        'host': 'localhost',
        'port': None,
        'database': 'binance'
    }
    url = URL(**conn)
    streamer = Streamer(str(url))
    am.get_all_klines_socket(func=streamer.update)
    try:
        am.start_sockets()
        am.idle()
    except KeyboardInterrupt:
        am.stop_sockets()


if __name__ == '__main__':
    main()
