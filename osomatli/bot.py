#!/usr/bin/python3
# -*- encoding:utf-8 -*-

"""Bot de Telegram
En este módulo será almacenada la clase TelegramBot encargada de formar la
abstracción del comportamiento y funciones de un Bot de Telegram.
"""


from telegram import Bot
from telegram import InlineQuery
from telegram import CallbackQuery
from telegram.error import NetworkError
from telegram.error import Unauthorized
from telegram.ext import Updater, CommandHandler


class FinanceBot(object):
    def __init__(self, key: str):
        self.__updater = Updater(key)
        self.__dispatcher = self.__updater.dispatcher
        self.__dispatcher.add_handler(CommandHandler('start', self.__start))
        self.__dispatcher.add_handler(CommandHandler('range', self.__set_range))
        self.__dispatcher.add_handler(CommandHandler('symbol',
                                                     self.__set_symbol))
        self.__dispatcher.add_handler(CommandHandler('signals',
                                                     self.__get_signals))
        self.__dispatcher.add_handler(CommandHandler('subscribe',
                                                     self.__subscribe))
        self.__dispatcher.add_handler(CommandHandler('drop',
                                                     self.__drop_all))
        self.__users = set()

    def __start(self, bot, update):
        text = """Hola!
        Puedes usar
        /range <format>
        para configurar un rango de tiempo para los datos (1m, 5m, 15m, 30m, 1h)
        /symbol <symbol>
        para configurar un simbolo a observar (o varios)
        /signals
        para recibir un listado de todas las señales del día
        /subscribe
        para suscribirte a la lista de simbolos que hayas definido.
        /drop
        para eliminar todas las configuraciones actuales.  
        """
        update.message.reply_text(text)
        self.__users.add(bot)

    def __get_signals(self, bot, update):
        pass

    def __set_range(self, bot, update):
        pass

    def __set_symbol(self, bot, update):
        pass

    def __subscribe(self, bot, update):
        pass

    def __drop_all(self, bot, update):
        pass


def main():
    pass


if __name__ == '__main__':
    main()
