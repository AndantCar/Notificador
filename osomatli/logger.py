#!/usr/bin/python3
# -*- encoding:utf-8 -*-

"""Logger
Este módulo posee una abstracción de un Logger, creado con la finalidad de
almacenar Logs en un directorio de aplicación, además de su respectiva salida
a consola, dependiendo del comportamiento elegido.
"""


class Logger(object):
    def __init__(self, name: str = 'Dummy'):
        self.__name = None
        self.__output = None
        self.name = name

    def debug(self, msg: str):
        pass

    def info(self, msg: str):
        pass

    def warn(self, msg: str):
        pass

    def error(self, msg: str):
        pass

    def critical(self, msg: str):
        pass

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value
