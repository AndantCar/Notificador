# -*- coding: utf-8 -*-

import sys
import time
import logging

from tools_bot import tools, texts_out

import telebot

level_debug = '1'
levels = {'1': logging.DEBUG,
          '2': logging.INFO,
          '3': logging.WARNING,
          '4': logging.ERROR,
          '5': logging.CRITICAL}

logging.basicConfig(filename=f'log_Supervisor{time.strftime("%d-%m-%Y")}.log',
                    level=levels[level_debug],
                    format='%(asctime)s - %(name)s - %(message)s')


__author__ = 'Carlos Añorve'
__version__ = '1.0'
__all__ = []


TOKEN = '635048049:AAHmD4MK8AgiiMEzp8ZntRl5EfbQRa7aMVg'
HELP_MESSAGE = ('''
<b>Que puedes hacer con este bot?</b>
''')


binance_bot = telebot.TeleBot(TOKEN)


@binance_bot.message_handler(commands=['start', 'help'])
def get_message(message):
    chat_id, message_id = tools.get_message_chat_id(message)
    estructura = {'Boton_1': '/start', 'Boton_2': '/start','Boton_3': '/start',
                  'Boton_4': '/start', 'Boton_5': '/start','Boton_6': '/start'}
    binance_bot.send_message(chat_id=chat_id,
                             text=texts_out.HELP_MESSAGE,
                             reply_markup=tools.make_buttons(estructura),
                             parse_mode='HTML')


def main():
    binance_bot.polling(none_stop=True)
    while True:
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            break
    sys.exit(0)


if __name__ == '__main__':
    main()
