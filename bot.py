# -*- coding: utf-8 -*-

import sys
import time
import json
import logging

from osomatli.binance import get_symbols
from tools_bot import tools, texts_out

import zmq
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

PORT = 5551
botones_base = tools.read_json('configuraciones/botones_base.json')
binance_bot = telebot.TeleBot(TOKEN)
registrados = []
contexto = zmq.Context()
sender = contexto.socket(zmq.PUSH)
sender.bind('tcp://127.0.0.1:{}'.format(PORT))
_Users_ = []

@binance_bot.message_handler(commands=['start', 'help'])
def get_message(message):
    global registrados
    chat_id, message_id = tools.get_message_id_and_chat_id(message)
    if not (chat_id in _Users_):
        binance_bot.send_message(chat_id=chat_id,
                                 text=texts_out.CONFIRMATION,
                                 #reply_markup=tools.make_button_of_list(get_symbols(), 4),
                                 parse_mode='HTML')
        _Users_.append(chat_id)

    sender.send_json(json.dumps({'chat_id': chat_id}))


def main():
    binance_bot.polling(none_stop=True)


if __name__ == '__main__':
    main()

a = {
    'game_short_name': None,
    'chat_instance': '-4655681606207608949',
    'id': '2352851667042991284',
    'from_user': {'id': 547815968,
                'is_bot': False,
                'first_name': 'Carlos',
                'username': None,
                'last_name': 'Añorve',
                'language_code': 'es'},
    'message': {'content_type': 'text',
              'message_id': 67,
              'from_user': "<telebot.types.User object at 0x7f1edc837470>",
              'date': 1536547457,
              'chat': "<telebot.types.Chat object at 0x7f1edc837668>",
              'forward_from_chat': None,
              'forward_from': None,
              'forward_date': None,
              'reply_to_message': None,
              'edit_date': None,
              'media_group_id': None,
              'author_signature': None,
              'text': 'Yes/no?',
              'entities': None,
              'caption_entities': None,
              'audio': None,
              'document': None,
              'photo': None,
              'sticker': None,
              'video': None,
              'video_note': None,
              'voice': None,
              'caption': None,
              'contact': None,
              'location': None,
              'venue': None,
              'new_chat_member': None,
              'new_chat_members': None,
              'left_chat_member': None,
              'new_chat_title': None,
              'new_chat_photo': None,
              'delete_chat_photo': None,
              'group_chat_created': None,
              'supergroup_chat_created': None,
              'channel_chat_created': None,
              'migrate_to_chat_id': None,
              'migrate_from_chat_id': None,
              'pinned_message': None,
              'invoice': None,
              'successful_payment': None,
              'connected_website': None,
              'json': {'message_id': 67,
                       'from': {'id': 635048049,
                                'is_bot': True,
                                'first_name': 'Cripto_test',
                                'username': 'Cripto_test_bot'},
                       'chat': {'id': 547815968,
                                'first_name': 'Carlos',
                                'last_name': 'Añorve',
                                'type': 'private'},
                       'date': 1536547457,
                       'text': 'Yes/no?'}},
    'data': 'cb_no',
    'inline_message_id': None}