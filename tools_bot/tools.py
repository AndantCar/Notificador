# -*- coding: utf-8 -*-

import time
import json
import logging

from copy import deepcopy

from telebot import types


__author__ = 'Carlos Añorve'
__version__ = '1.0'

__all__ = ['get_message_chat_id',
           'make_buttons_of_dict',
           'make_button_of_list',
           'read_json']


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


def make_buttons_of_dict(estructure, rows=3):
    """
    Crea un KeyBoardMarkup con la estructura pasada

    Args:
        estructure(dict): Estructura que con la que se creara el markup
        rows(int): Determin la cntidade de columas para mostra botones.

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


def read_json(path):
    """
    Lee un archivo json y lo pasa a diccionario.

    Args:
        path(str): ubicacion del archivo en sistema.

    Returns:
         Devuelve un diccionario con la estructura del json leido.
    """
    try:
        with open(path, 'r') as json_file:
            json_data = json.loads(json_file.read())
    except Exception as details:
        logger.warning('Error al intentar leer el archivo json.\n'
                       'Path: {}\n'
                       'Detalles: {}'.format(path, details))
    else:
        return json_data


def make_button_of_list(names_buttons, rows=3):
    """
    Crea una estructura de botones a partir de una lista.

    Args:
        names_buttons(list): lista de nombre de botones.
        rows(int): Define la cantidad de columnas en el layout de botones

    Returns:
        KeyBoardMarkup
    """
    butons = list()
    try:
        keyboard_markup = types.InlineKeyboardMarkup()
    except Exception as details:
        logger.warning('Error al intentar crear el keyboardMarkup\n'
                       'Detalles: {}'.format(details))
        return None
    for name_button in names_buttons:
        try:
            inline_button = types.InlineKeyboardButton(name_button,
                                                       callback_data=name_button)
        except Exception as details:
            logger.warning('Error al intentar crear el boton.\n'
                           'Details: {}'.format(details))
        else:
            butons.append(deepcopy(inline_button))
            del inline_button
            if len(butons) == rows:
                keyboard_markup.row(*butons)
                butons = list()
    if len(butons) > 0:
        keyboard_markup.row(*butons)
    return keyboard_markup


def dataframe2json(data_frame):
    """
    Convierte el data frame obtenido del
    indicador y lo convierte a json.

    Nota:
    El data frame debe mantener el nombre del simbolo
    en la primera columan despues del indice

    Args:
        data_frame(): Dataframe btenido del indicador

    Returns:
        Devuelve los datos del data frame en un json.
    """
    llaves = ['SYMBOL', 'open_time_dt', 'close', 'MONEY_FLOW_INDEX', 'MACDT_HIST',
              'volume', 'VMA(10)', 'SIGNAL']
    senales = {}
    for datos in data_frame.values:
        senal = {}
        for i in range(len(llaves)):
            try:
                senal[llaves[i + 1]] = str(datos[i + 1])
            except IndexError:
                pass
        senales[datos[0]] = str(senal)
    return json.dumps(senales)
