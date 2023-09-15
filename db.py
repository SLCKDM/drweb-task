# pylint: disable=missing-class-docstring,missing-function-docstring,missing-module-docstring,multiple-statements,too-few-public-methods,
import abc
from collections import UserDict
import copy


class Data(UserDict): ...


class AbstractDB(abc.ABC):

    def __init__(self, source: Data):
        self._data = source

    @property
    def data(self) -> Data: return self._data

    @data.setter
    def data(self, _data):
        self._data = _data


class DataBase(AbstractDB):

    def __init__(self, source: Data):
        super().__init__(source)
        self._transactions = []

    @property
    def transatinos(self):
        return self._transactions

    def clear_transactions(self):
        return self._transactions.clear()

    def begin(self):
        self._transactions.append(copy.deepcopy(self._data))

    def rollback(self):
        if self._transactions:
            self._data = self._transactions.pop()

    def commit(self):
        self.clear_transactions()
