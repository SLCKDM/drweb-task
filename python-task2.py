# pylint: disable=missing-class-docstring,multiple-statements,invalid-name,missing-function-docstring,too-few-public-methods

import abc
from collections import UserDict
import functools
import logging
from typing import Any, NoReturn, Type
from xml.sax import handler

logging.basicConfig(level=logging.DEBUG)

class CustomException(Exception):
    def __init__(self, msg: str, *args: object) -> None:
        super().__init__(*args)
        self.msg = msg

class AppException(CustomException):
    ''' raise when exception occurs during app layer '''

class CommandException(CustomException):
    ''' raise when exception occurs during command layer '''

class NoCommandFoundException(CommandException): ...

class CommandExecutionException(CommandException): ...

class CommandParseException(CommandException): ...


class Data(UserDict): ...

class DataBase:
    def __init__(self, source: Data):
        self._data = source

    @property
    def data(self) -> Data: return self._data

    def operation1(self): print('operation 1!')
    def operation2(self):print('operation 2!')





class App:

    def __init__(self, db: DataBase, handler: 'Handler') -> None:
        self._db = db
        self._handler = handler
        self._handler.app = self


    @property
    def handler(self):
        return self._handler

    @property
    def db(self):
        return self._db

    def execute_command(self, cmd: 'Command', *args) -> None:
        cmd.execute(*args)


    def start(self):
        while True:
            cmd_input = input('>')
            cmd_method, args = Command.parse(cmd_input)
            cmd = self.handler.commands[cmd_method]
            try:
                cmd.execute(*args)
            except KeyboardInterrupt:
                break


class Handler:
    _commands: dict[str, 'Command'] = {}
    _app: App

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, app: App) -> None:
        self._app = app
        for cmd in self._commands.values():
            cmd.handler = self

    @classmethod
    def register_command(cls, cmd: Type['Command']):
        cls._commands[cmd.method] = cmd()
        @functools.wraps(cmd)
        def wrapper(*args, **kwargs) -> Command:
            return cmd(*args, **kwargs)
        return wrapper

    @property
    def commands(self) -> dict[str, 'Command']:
        return self._commands











class Command:
    method: str
    handler: Handler

    def execute(self, var, val) -> None:
        logging.debug('executing')

    @classmethod
    def parse(cls, _str: str, /):
        method, *args = _str.split(' ')
        return method, args

@Handler.register_command
class GET(Command):
    method = 'GET'

    def execute(self, var, val = None) -> None:
        super().execute(var, val)
        app.db.operation1()

@Handler.register_command
class SET(Command):
    method = 'SET'

    def execute(self, var, val) -> None:
        super().execute(var, None)
        app.db.operation2()

@Handler.register_command
class END(Command):
    method = 'END'

    def execute(self, var=None, val=None) -> None:
        raise KeyboardInterrupt


db = DataBase(Data())

app = App(db, Handler())
app.start()