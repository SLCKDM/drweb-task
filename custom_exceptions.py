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
