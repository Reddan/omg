from typing import Callable
from .colored import colored
from .pretty_print_exc import pretty_print_exc
from .print import print

__all__ = ["colored", "on_reload", "pretty_print_exc", "print"]

reload_handlers: list[Callable] = []

def on_reload(func: Callable):
  reload_handlers.append(func)
