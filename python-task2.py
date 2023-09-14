# pylint: disable=missing-class-docstring,multiple-statements,invalid-name,missing-function-docstring,too-few-public-methods

import abc
import logging

logging.basicConfig(level=logging.DEBUG)


class Data: ...
class DataBase: ...

class App:

    def __init__(self, db: DataBase) -> None:
        self._db = db

    def execute_command(self, cmd: 'Command', *args):
        cmd.execute(args)

class CommandsMeta(type):


class Command:
    method: str

    def execute(self, *args):
        logging.debug('executing')
        args
