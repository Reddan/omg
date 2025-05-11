import sys
import traceback
import re
from pathlib import Path
from termcolor import colored
from termcolor._types import Attribute

path_pattern = re.compile(r'File "(.*)", line (\d+), in (.+)')
error_pattern = re.compile(r"^[\w.]+: ")

def pretty_print_exc():
  cwd = str(Path.cwd())
  tracelines = traceback.format_exc().splitlines()
  is_external = False
  pretty_lines = [""]

  for line in tracelines:
    matches = path_pattern.match(line.strip())
    if line.startswith("Traceback ("):
      pretty_lines.append(colored(line, attrs=["bold"]))
    elif error_pattern.match(line):
      pretty_lines.append(colored(line, "red"))
    elif not matches:
      pretty_lines.append(colored(line, "dark_grey" if is_external else None))
    else:
      path, line_number, method = matches.groups()
      if path.startswith("<frozen importlib._bootstrap"):
        continue
      is_external = (not path.startswith(".") and not path.startswith(cwd)) or ".venv" in path
      if not is_external:
        path = path.replace(cwd, ".")
      color_attrs: list[Attribute] = ["dark"] * is_external
      pretty_line = (
        f"{colored(path, "cyan", attrs=color_attrs)}"
        f"{colored(":", attrs=color_attrs)}"
        f"{colored(line_number, "yellow", attrs=color_attrs)} "
        f"{colored(method, "green", attrs=color_attrs)}"
        f"{colored(":", attrs=color_attrs)}"
      )
      pretty_lines.append(pretty_line)

  print("\n".join(pretty_lines + [""]), file=sys.stderr)
