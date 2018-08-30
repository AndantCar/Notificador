# coding: utf-8

import sys
import time
import datetime

import telebot

from telebot import types


PERFILES = {}


binance_bot = telebot.TeleBot('558805340:AAEHYOza2FtWwORvAtdJMzV41r7ZCyITUHM')


@binance_bot.message_handler(command='start')
def commad_help(message):
    markup = types.InlineKeyboardMarkup()
    itembtna_1 = types.InlineKeyboardButton('',
                                            callback_data='/charge')
    itembtna_2 = types.InlineKeyboardButton('Crear el demonio de carga de archivos.',
                                            callback_data='/make')
    itembtna_3 = types.InlineKeyboardButton('Borrar de taskschedule el demonio de carga de archivos.',
                                            callback_data='/delete')
    itembtna_4 = types.InlineKeyboardButton('Deshabilitar el demonio de carga de archivos.',
                                            callback_data='/disable')
    itembtna_5 = types.InlineKeyboardButton('Habilidat el demonio de carga de archivos.',
                                            callback_data='/enable')