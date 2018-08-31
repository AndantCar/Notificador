# -*- coding: utf-8 -*-

import time
import logging

from copy import deepcopy

from telebot import types


__author__ = 'Carlos Añorve'
__version__ = '1.0'
__all__ = []


logger = logging.getLogger(__name__)
level_debug = '1'
levels = {'1': logging.DEBUG,
          '2': logging.INFO,
          '3': logging.WARNING,
          '4': logging.ERROR,
          '5': logging.CRITICAL}

logging.basicConfig(filename=f'log_Supervisor{time.strftime("%d-%m-%Y")}.log',
                    level=levels[level_debug],
                    format='%(asctime)s - %(name)s - %(message)s')


def get_message_chat_id(message):
    """
    Obtiene el id del usuario y el mensage

    Args:
        message(telebot.types.Message):
    :return:
    """
    try:
        logger.debug('Intentando obtener el id del chat.')
        user_id = message.chat.id
    except AttributeError:
        logger.error('No fue posible obtener el id del chat con message.chat.id')
        try:
            logger.debug('Intentando obtener id del chat.')
            user_id = message.from_user.id
        except AttributeError:
            logger.warning('No es posible obtener el id del chat.')
        return None

    try:
        logger.debug('Intentando obtener el id del mensage')
        message_id = message.message_id
    except AttributeError:
        logger.error('Error al intentar obtener el id del mensage')
        try:
            logger.debug('Intentando obtener el id del mensage')
            message_id = message.message.message_id
        except AttributeError:
            logger.critical('Error al intentar obener el id del mensage')
            return None
    return user_id, message_id


def make_buttons(estructure, rows=3):
    """
    Crea un KeyBoardMarkup con la estructura pasada

    Args:
        estructure(dict): Estructura que con la que se creara el markup

    Returns:
         KeyBoardMarkup
    """
    try:
        keyboard_markup = types.InlineKeyboardMarkup()
    except Exception as details:
        logger.warning('Error al intentar crear el keryboardMarkup\n'
                       'Details: {}'.format(details))
        return None
    buttons = list()
    for button in estructure:
        try:
            keyboard_button = types.InlineKeyboardButton(button, callback_data=estructure[button])
        except Exception as details:
            logger.error('No fue posible crear el boton {}\n'
                         'Details: {}'.format(button, details))
        else:
            buttons.append(deepcopy(keyboard_button))
            del keyboard_button
            if len(buttons) == rows:
                keyboard_markup.row(*buttons)
                buttons = list()
    if len(buttons) > 0:
        keyboard_markup.row(*buttons)
    return keyboard_markup