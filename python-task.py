
from abc import ABC, abstractmethod
from collections import UserDict
from functools import wraps
import logging
from typing import Any




class Data(UserDict): ...


class AbstractDB(ABC):

    def __init__(self, name: str):
        self._name = name
        self._data = Data()

    def __repr__(self) -> str:
        return f'<DB {self._name}>'


class DB(AbstractDB):

    ...


class AbstractApp(ABC):

    def __init__(self, name: str, db: DB) -> None:
        self._name = name
        self._db = db

    @property
    def name(self) -> str:
        return self._name

    @property
    def db(self):
        return self._db

    @abstractmethod
    def start(self): ...

    @abstractmethod
    def _wait_for_command(self): ...


class App(AbstractApp):

    def _wait_for_command(self):
        command_input = None
        try:
            cmd = Command.parse_command(input('> '))
            logging.debug(f'Received command: {cmd}')
        except Exception:
            logging.exception(f'Error on executing command:\n {command_input}')
            return
        logging.debug(f'Executing command: {cmd}')
        try:
            cmd.execute()
        except Exception:
            logging.exception(f'Error on executing {cmd}')

    def start(self):
        logging.debug(f'App {self} started')
        while True:
            self._wait_for_command()

    def __repr__(self):
        return f'<App: {self.name}>'

class CommandMetadata(type):
    _commands = {}

    def __call__(cls, *args: Any, **kwds: Any) -> Any:
        cmd = super().__call__(*args, **kwds)
        cls._commands[cmd]
        return cls._commands[cmd]


class AbstractCommand(ABC):

    @abstractmethod
    def execute(self) -> None: ...

    @classmethod
    @abstractmethod
    def parse_command(cls, command_input: str): ...


class Command(AbstractCommand):
    __metaclass__ = CommandMetadata
    def __init__(self, method: str) -> None:
        self._method = method
        super().__init__()

    @classmethod
    def parse_command(cls, command_input: str) -> 'Command':
        args = command_input.split(' ')
        return cls(*args)

    # @classmethod
    # def register_command(cls, obj):
        # obj(obj.method)
        # ...

    def execute(self, var: str | None = None, val: str | None = None) -> None:
        logging.debug(f'Executing command {self._method} {f"variable: {var}" if var else ""}{ "and" if var and val else ""}{f"value: {val}" if val else ""}')
        return


class GetCommand(Command):
    method: str = 'GET'
    var: str


class SetCommand(Command):
    method: str = 'SET'
    var: str
    val: str


class UnsetCommand(Command):
    method: str = 'UNSET'
    var: str


class CountsCommand(Command):
    method: str = 'COUNTS'
    var: str


def main():
    db = DB(name='1')
    app = App(name='MainApp', db=db)
    app.start()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()