# -*- coding: utf-8 -*-
from connection import Connection

__all__ = ['Client']


class Client(object):

    def __init__(self, connection=None):
        if connection:
            self._connection = connection
        else:
            self._connection = Connection()

    def get_connection(self):
        return self._connection

    def create_build(self):
        pass
