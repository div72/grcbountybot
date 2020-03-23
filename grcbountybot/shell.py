import inspect
import shlex
from functools import wraps

from grcbountybot.utils import DotDict


class Shell:
    commands = {'default': (lambda *args, **kwargs: None)}

    def __init__(self, trigger: str):
        self.trigger = trigger

    def command(self, name: str = None):
        def _command(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            self.commands[name or func.__qualname__] = func
            return wrapper
        return _command

    @staticmethod
    def _get_arg_types(func) -> list:
        arg_types = []
        sig = inspect.signature(func)
        for param in sig.parameters.values():
            if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
                if (_type := param.annotation) == inspect._empty:
                    arg_types.append(str)
                else:
                    arg_types.append(_type)
        return arg_types

    async def parse_command(self, cmd: str, **ctx):
        args = shlex.split(cmd)
        if args[0] == self.trigger:
            func = self.commands.get(args[1], self.commands['default'])
            args = args[2:]
            if arg_types := self._get_arg_types(func):
                _args = []
                for arg, _type in zip(args, arg_types):
                    _args.append(_type(arg))
                await func(*_args, ctx=DotDict(**ctx))
            else:
                await func(*args, ctx=DotDict(**ctx))
