#!/usr/bin/python3
# -*- encoding:utf-8 -*-


import zmq
import json
import requests

from tools_bot import tools


_USUARIOS_ = []


token = '635048049:AAHmD4MK8AgiiMEzp8ZntRl5EfbQRa7aMVg'
URL_API = 'https://api.telegram.org/bot{0}/{1}'
context = zmq.Context()
from_bot = context.socket(zmq.PULL)
from_indicadot = context.socket(zmq.PULL)
from_bot.connect('tcp://127.0.0.1:5551')
from_indicadot.connect('tcp://127.0.0.1:5550')


def send_message(message, chat_id):
    comand = 'sendMessage'
    params = {'chat_id': str(chat_id), 'text': message}
    try:
        result = requests.get(url=URL_API.format(token, comand), params=params)
    except Exception as details:
        print('Error al intentar enviar el mensaje.\n'
              'Details: {}'.format(details))
    else:
        if result.status_code == requests.codes.ok:
            print('El mensaje se envio correctamente')
        else:
            print('Error al envir mensaje\n'
                  'Code error: {}'.format(result.status_code))


poller = zmq.Poller()
poller.register(from_bot, zmq.POLLIN)
poller.register(from_indicadot, zmq.POLLIN)
while 1:
    socks = dict(poller.poll())
    if from_bot in socks and socks[from_bot] == zmq.POLLIN:
        message = json.loads(from_bot.recv_json())
        if not (message['chat_id'] in _USUARIOS_):
            _USUARIOS_.append(message['chat_id'])
        else:
            send_message('Ya estas regiistrado porfavor evita hacer spam', message['chat_id'])
        print('Se activo la asignacion')
        print(_USUARIOS_)
    if from_indicadot in socks and socks[from_indicadot] == zmq.POLLIN:
        message = from_indicadot.recv_json()
        message = json.loads(message)
        message = tools.json2str(message)
        print(message)
        print('Se activo la notiicaciion')
        for user in _USUARIOS_:
            send_message(message, user)
