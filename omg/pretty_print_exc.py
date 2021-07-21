import sys
import traceback
import re
from termcolor import colored

def pretty_print_exc():
  stack_trace = traceback.format_exc().splitlines()
  _, *lines, error = stack_trace
  filtered_lines = ['frozen importlib._bootstrap' in line for line in lines]
  start_line = next((
    i + 1
    for i in range(len(filtered_lines) - 1)
    if filtered_lines[i] and not filtered_lines[i + 1]
  ), 0)
  lines = lines[start_line:]
  is_external = False
  pretty_lines = ['']

  for line in lines:
    matches = re.match('File "(.*)", line (\d+), in (.+)', line.strip())
    if matches:
      path, line_number, method = matches.groups()
      is_external = not path.startswith('.')
      color_attrs = ['dark'] * is_external
      pretty_line = (
        f"{colored(path, 'cyan', attrs=color_attrs)}"
        f"{colored(':', attrs=color_attrs)}"
        f"{colored(line_number, 'yellow', attrs=color_attrs)} "
        f"{colored(method, 'green', attrs=color_attrs)}"
        f"{colored(':', attrs=color_attrs)}"
      )
      pretty_lines.append(pretty_line)
    else:
      pretty_lines.append(colored(line, 'grey') if is_external else line)

  pretty_lines = pretty_lines + [colored(error, 'red'), '']
  print('\n'.join(pretty_lines), file=sys.stderr)
