import builtins
import shutil
from collections.abc import ItemsView, KeysView, ValuesView
from contextlib import suppress
from .colored import Color, colored

np = None

with suppress(Exception):
  import numpy as np

bracket_colors: list[Color | None] = [
  None,
  "red",
  "blue",
  "magenta",
  "cyan",
  "grey",
]

def get_terminal_width():
  return shutil.get_terminal_size((80, 0))[0]

def render(value, color, indent=0):
  indent_str = "  " * indent
  next_indent_str = indent_str + "  "
  bracket_color = color or bracket_colors[indent % len(bracket_colors)]
  match value:
    case None:
      return colored(str(value), color, attrs=["bold"])
    case builtins.Ellipsis:
      return colored("...", color, attrs=["bold"])
    case int() | float():
      return colored(str(value), color or "yellow")
    case str():
      if indent == 0:
        return colored(f"{value}", color)
      else:
        return colored(f'"{value}"', color or "green")
    case tuple() | set() | frozenset() | list() | KeysView() | ValuesView() | ItemsView():
      if isinstance(value, (frozenset, KeysView, ValuesView, ItemsView)):
        prefix, postfix = f"{type(value).__name__}(", ")"
      else:
        prefix, postfix = "", ""
      opening, closing = "()" if isinstance(value, tuple) \
        else "{}" if isinstance(value, (set, frozenset)) \
        else "[]"
      opening = colored(opening, bracket_color)
      closing = colored(closing, bracket_color)
      comma = "," if isinstance(value, tuple) and len(value) == 1 else ""
      children = [render(val, color, indent + 1) for val in value]
      child_str = ", ".join(children)
      terminal_width = get_terminal_width()
      if len(child_str) <= terminal_width and "\n" not in child_str:
        return f"{prefix}{opening}{child_str}{comma}{closing}{postfix}"
      else:
        children = [next_indent_str + child for child in children]
        child_str = ",\n".join(children)
        return f"{opening}\n{child_str}\n{indent_str}{closing}"
    case dict():
      opening = colored("{", bracket_color)
      closing = colored("}", bracket_color)
      children = [
        f"{next_indent_str}{render(key, color, indent + 1)}: {render(val, color, indent + 1)}"
        for key, val in value.items()
      ]
      child_str = ",\n".join(children)
      child_str = child_str and f"\n{child_str}\n{indent_str}"
      return f"{opening}{child_str}{closing}"
    case _ if np and isinstance(value, np.ndarray):
      array_lines = np.array2string(
        value,
        max_line_width=get_terminal_width(),
        edgeitems=5,
      ).splitlines()
      if len(array_lines) == 1:
        return array_lines[0]
      else:
        array_lines[0] = " " + array_lines[0][1:]
        array_lines[-1] = array_lines[-1][:-1]
        array_lines = [next_indent_str + line for line in array_lines]
        array_str = "\n".join(array_lines)
        return f"ndarray [\n{array_str}\n{indent_str}]"
    case _:
      return str(value)

pyprint = print

def print(*values, color=None, **kwargs):
  pyprint(*(render(value, color) for value in values), **kwargs)
