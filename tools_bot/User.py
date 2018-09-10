#!/usr/bin/python3
# -*- encoding:utf-8 -*-

import telebot

from tools_bot import tools


class User(object):
    def __init__(self, group=None, name=None, id=None):
        self.__name = name
        self.__id = id
        self.__group = group

    @property
    def name(self):
        if self.__name is None:
            raise PropertyNotDefine('No se a definido el valor de la propiedad.')
        else:
            return self.__name

    @name.setter
    def name(self, value):
        """
        Asigna un valor a el atributo name.

        Args:
            value(telebot.types.Message, dict, str): Puede pasar el nombre de usuario
                directamente como string o en un diccionario o en un Message de la api telebot.

        Returns:
            None
        """
        if isinstance(value, telebot.types.Message):
            self.__name = tools.get_name(value)
        elif isinstance(value, dict):
            self.__name = value['name']
        elif isinstance(value, str):
            self.__name = value
        else:
            raise TypeError('El valor no cumple con ninguno de los tipos de datos esperados')
        if self.__name is None:
            raise PropertyNotDefine('Ocurrio un error al intentar asignar el valor.')

    @property
    def user_id(self):
        if self.__id is None:
            raise PropertyNotDefine('No se a definido el valor de la propiedd')
        else:
            return self.__id

    @user_id.setter
    def user_id(self, value):
        """
        Asigna un valor a el atributo id

        Args:
            value(telebot.types.Message, dict, str):Puede pasar el id de uuario directamente como string
                o en un diccionario o en un Message de la api telebot

        Returns:
             None
        """
        if isinstance(value, telebot.types.Message):
            self.__id = tools.get_message_id_and_chat_id(value)[1]
        elif isinstance(value, dict):
            self.__id = value['user_id']
        elif isinstance(value, str):
            self.__id = value
        else:
            raise TypeError('El valor no cumple con ninguno de los tipos de datos esperados')
        if self.__id is None:
            raise PropertyNotDefine('Ocurrio un error al intentar asignar el valor.')

    @property
    def group(self):
        if self.__group is None:
            raise PropertyNotDefine('No se a definido el valor a la propiedad.')
        else:
            return self.__group

    @group.setter
    def group(self, value):
        """
        Asigna un valor a el atributo group.

        Args:
            value(str): Define el gruo al que pertenece el usurio.

        Returns:
             None
        """
        if isinstance(value, str):
            self.__group = value
        else:
            raise TypeError('El valor no cumple con el tipo de dato esperado.')
        if self.__group is None:
            raise PropertyNotDefine('Ocurrio un problema al intentar asignar el valor.')


class PropertyNotDefine(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)
