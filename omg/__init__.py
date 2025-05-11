from typing import Callable
from .pretty_print_exc import pretty_print_exc

__all__ = ["on_reload", "pretty_print_exc"]

reload_handlers: list[Callable] = []

def on_reload(func: Callable):
  reload_handlers.append(func)
