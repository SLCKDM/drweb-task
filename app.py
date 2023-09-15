# pylint: disable=missing-class-docstring,multiple-statements,invalid-name,missing-function-docstring,too-few-public-methods,missing-module-docstring

import abc
import functools
import logging
from typing import Type
from custom_exceptions import (
    AppException,
    CommandException,
    NoCommandFoundException,
    CommandExecutionException,
    CommandParseException,
)
from db import DataBase


class AbstractApp(abc.ABC):

    @abc.abstractmethod
    def start(self) -> None: ...


class App(AbstractApp):

    def __init__(self, db: DataBase) -> None:
        self._db = db
        self._handler = Handler()
        self._handler.app = self

    def start(self) -> None:
        while True:
            try:
                cmd_input = input('>')
                if not cmd_input:
                    continue
                cmd_method, args = Command.parse(cmd_input)
                cmd = self.handler.get_command(cmd_method)
                cmd.execute(*args)
            except CommandException as exc:
                logging.error(exc.msg)
            except (KeyboardInterrupt, EOFError):
                print('Bye!')
                break

    @property
    def handler(self) -> 'Handler':
        return self._handler

    @property
    def db(self) -> DataBase:
        return self._db


class Handler:
    _commands: dict[str, 'Command'] = {}
    _app: App

    @property
    def app(self) -> App:
        return self._app

    @app.setter
    def app(self, _app: App) -> None:
        self._app = _app
        for cmd in self._commands.values():
            cmd.handler = self

    def get_command(self, key: str):
        if key not in self._commands:
            raise NoCommandFoundException(f'Not found command `{key}`')
        return self._commands[key]

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


class CommandAbstract(abc.ABC):

    @abc.abstractmethod
    def execute(self): ...


class Command:
    method: str
    handler: Handler

    def execute(self, *args) -> None:
        logging.debug('<%s> %s', self, args)

    @classmethod
    def parse(cls, _str: str, /) -> tuple[str, list[str]]:
        method, *args = _str.split(' ')
        return method, args


@Handler.register_command
class GET(Command):
    method = 'GET'

    def execute(self, *args) -> None:
        super().execute(args)
        if not args:
            raise CommandParseException('Not enough args')
        key = args[0]
        print(self.handler.app.db.data.get(key, ''))


@Handler.register_command
class SET(Command):
    method = 'SET'

    def execute(self, *args) -> None:
        super().execute(args)
        if len(args) <= 1:
            raise CommandParseException('Not enough args')
        key, val = args
        self.handler.app.db.data[key] = val


@Handler.register_command
class COUNTS(Command):
    method = 'COUNTS'

    def execute(self, *args) -> None:
        super().execute(args)
        if not args:
            raise CommandParseException('Not enough args')
        val = args[0]
        print(list(self.handler.app.db.data.values()).count(val))


@Handler.register_command
class UNSET(Command):
    method = 'UNSET'

    def execute(self, *args) -> None:
        super().execute(args)
        if not args:
            raise CommandParseException('Not enough args')
        key = args[0]
        self.handler.app.db.data.pop(key)


@Handler.register_command
class FIND(Command):
    method = 'FIND'

    def execute(self, *args) -> None:
        super().execute(args)
        if not args:
            raise CommandParseException('Not enough args')
        val = args[0]
        print(' '.join(k for k, v in self.handler.app.db.data.items() if v == val))


@Handler.register_command
class END(Command):
    method = 'END'

    def execute(self, *_) -> None:
        super().execute()
        raise KeyboardInterrupt


@Handler.register_command
class BEGIN(Command):
    method = 'BEGIN'

    def execute(self, *_):
        super().execute()
        self.handler.app.db.begin()


@Handler.register_command
class ROLLBACK(Command):
    method = 'ROLLBACK'

    def execute(self, *_):
        super().execute()
        self.handler.app.db.rollback()


@Handler.register_command
class COMMIT(Command):
    method = 'COMMIT'

    def execute(self, *_):
        super().execute()
        self.handler.app.db.commit()
