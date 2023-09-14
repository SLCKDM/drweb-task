# pylint: disable=missing-class-docstring,multiple-statements,invalid-name,missing-function-docstring,too-few-public-methods

from abc import ABC, ABCMeta, abstractmethod
from collections import UserDict
import functools
import logging
from typing import Any

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


class AbstractDB(ABC): ...


class AbstractApp(ABC):

    @abstractmethod
    def start(self): ...

    @abstractmethod
    def _wait_for_command(self): ...


class DB(AbstractDB):

    def __init__(self, name: str):
        self._name = name
        self._data = Data()

    def __repr__(self) -> str:
        return f'<DB {self._name}>'


class AppMetadata(ABCMeta):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class App(AbstractApp, metaclass=AppMetadata):
    _commands: dict['Command', 'Command'] = {}

    def __init__(self, name: str, db: DB) -> None:
        self._name = name
        self._db = db

    @classmethod
    def register_command(cls, _class):
        cmd = _class()
        cls._commands[cmd] = cmd
        logging.debug('%s registered', cmd)
        @functools.wraps(_class)
        def wrapper(*args, **kwargs):
            return _class(*args, **kwargs)
        return wrapper


    @property
    def name(self) -> str:
        return self._name

    @property
    def db(self):
        return self._db

    def _wait_for_command(self):
        command_input = None
        try:
            command_input = input('> ') or None
            if not command_input:
                return None
            cmd, args = Command.parse_command(command_input)
            logging.debug('Received command: %s', cmd)
        except (CommandParseException, NoCommandFoundException) as exc:
            raise AppException(msg=f'Error on input: {exc.msg}') from exc
        return cmd, args

    def start(self):
        logging.debug('App %s started', self)
        while True:

            try:

                # wait for command input
                cmd_args = self._wait_for_command()
                if not cmd_args:
                    continue
                cmd, args = cmd_args
                try:
                    logging.debug('Executing command: %s', cmd)
                    # if command received - executing
                    cmd.execute(*args)
                except CommandExecutionException:
                    logging.error('Error on executing')

            except AppException as app_exc:
                print(app_exc.msg)
                logging.error(app_exc.msg)

    def execute_command(self, cmd: 'Command', *args):
        cmd.execute(*args)

    def __repr__(self):
        return f'<App: {self.name}>'


class CommandMetadata(ABCMeta):
    _instances = {}
    method: str

    def __call__(cls, *args: Any, **kwds: Any) -> Any:
        if args:
            if args[0] not in cls._instances:
                raise NoCommandFoundException(f'No such command - "{args[0]}"')
            return cls._instances[args[0]]
        if cls.method not in cls._instances:
            cls._instances[cls.method] = super().__call__(*args, **kwds)
        return cls._instances[cls.method]


class AbstractCommand(ABC):
    method: str

    @abstractmethod
    def execute(self, var: str | None, val: str | None) -> None: ...

    @classmethod
    @abstractmethod
    def parse_command(cls, command_input: str): ...


class Command(AbstractCommand, metaclass=CommandMetadata):
    __metaclass__ = CommandMetadata
    method: str

    def __init__(self, method: str | None = None) -> None:
        if method:
            self.method = method
        logging.info('getting command from registry or creating')
        super().__init__()

    def __call__(self):
        logging.info('getting command from registry')

    @classmethod
    def parse_command(cls, command_input: str) -> tuple['Command', Any]:
        try:
            method, *args = command_input.split(' ')
        except Exception as exc:
            raise CommandParseException('Error on command parse') from exc
        return cls(method), args

    def execute(self, var: str | None = None, val: str | None = None):
        logging.debug('executing command: %s with VAR=%s and VAL=%s', self, var, val)
        # raise CommandExecutionException

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


@App.register_command
class GetCommand(Command):
    ''' GET command implementation '''
    method: str = 'GET'
    var: str

    def execute(self, var: str | None = None, val: str | None = None):
        super().execute(var=var, val=val)

@App.register_command
class SetCommand(Command):
    ''' SET command implementation '''
    method: str = 'SET'
    var: str
    val: str

    def execute(self, var: str | None = None, val: str | None = None):
        super().execute(var=var, val=val)

@App.register_command
class UnsetCommand(Command):
    ''' UNSET command implementation '''
    method: str = 'UNSET'
    var: str

    def execute(self, var: str | None = None, val: str | None = None):
        super().execute(var=var, val=None)

@App.register_command
class CountsCommand(Command):
    ''' COUNTS command implementation '''
    method: str = 'COUNTS'
    var: str

    def execute(self, var: str | None = None, val: str | None = None):
        super().execute(var=var, val=None)

@App.register_command
class FindCommand(Command):
    ''' FIND command implementation '''
    method: str = 'FIND'
    var: str

    def execute(self, var: str | None = None, val: str | None = None):
        super().execute(var=var, val=None)

@App.register_command
class EndCommand(Command):
    ''' END command implementation '''
    method: str = 'END'
    var: str

@App.register_command
class BeginCommand(Command):
    ''' BEGIN command implementation '''
    method: str = 'BEGIN'
    var: str


@App.register_command
class RollbackCommand(Command):
    ''' ROLLBACK command implementation '''
    method: str = 'ROLLBACK'
    var: str


@App.register_command
class CommitCommand(Command):
    ''' COMMIT command implementation '''
    method: str = 'COMMIT'
    var: str



def main():
    ''' runnner '''
    db = DB(name='1')
    app = App(name='MainApp', db=db)
    # GetCommand()
    # SetCommand()
    # UnsetCommand()
    # CountsCommand()
    # FindCommand()
    # EndCommand()
    app.start()

if __name__ == '__main__':
    main()
