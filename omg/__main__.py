import os
import sys
import importlib
import time
import traceback
import signal
import re
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from termcolor import colored

cwd = Path.cwd()
module_path = Path(sys.argv[1])
module_path_str = str(module_path)[:-3].replace('/', '.').replace('\\', '.')
is_local_by_module = {}
changed_modules = set()

sys.path.insert(0, '.')
sys.argv = sys.argv[1:]

class RestartException(Exception):
  pass

def print_current_traceback():
  stack_trace = traceback.format_exc().splitlines()
  _, *lines, error = stack_trace
  filter_line = lambda line: 'frozen importlib._bootstrap' in line
  start_i = next(i + 1 for i in range(len(lines)) if filter_line(lines[i]) and not filter_line(lines[i + 1]), 0)
  lines = lines[start_i:]

  for line in lines:
    matches = re.match('File "(.*)", line (\d+), in (.+)', line.strip())
    if matches:
      path, line_number, method = matches.groups()
      print(
        f"{colored(path, 'cyan')}"
        f":{colored(line_number, 'yellow')} "
        f"{colored(method, 'green')}: "
      )
    else:
      print(line)
  print(colored(error, 'red'))
  print('')

def to_module_path(module):
  try:
    return Path(module.__file__).absolute()
  except:
    return Path('/___')

def is_local_module(module):
  if module in is_local_by_module:
    return is_local_by_module[module]
  target = to_module_path(module)
  is_local = cwd in target.parents
  is_local_by_module[module] = is_local
  return is_local_module(module)

def get_local_modname_by_path():
  result = {
    to_module_path(module): mod_name
    for mod_name, module in list(sys.modules.items())
    if is_local_module(module)
  }
  result[module_path.absolute()] = module_path_str
  return result

def start():
  try:
    try:
      importlib.import_module(module_path_str)
      print(f'⚠️  {module_path} finished.')
    except OSError as err:
      if str(err) == 'could not get source code':
        start()
      else:
        raise
  except KeyboardInterrupt:
    print(f'\n⚠️  Script interrupted.')
  except (SystemExit, RestartException):
    pass
  except:
    print_current_traceback()

def restart(changed_file):
  print(f'⚠️  {changed_file.relative_to(cwd)} changed, restarting.')
  for mod_name in get_local_modname_by_path().values():
    if mod_name in sys.modules:
      del sys.modules[mod_name]
  start()

def receive_signal(signum, stack):
  raise RestartException()

class EventHandler(PatternMatchingEventHandler):
  def on_any_event(self, evt):
    src_path = Path(evt.src_path)
    dest_path = Path(evt.dest_path) if hasattr(evt, 'dest_path') else None
    local_modname_by_path = get_local_modname_by_path()
    if src_path in local_modname_by_path:
      changed_modules.add(src_path)
    if dest_path in local_modname_by_path:
      changed_modules.add(dest_path)
    if len(changed_modules):
      os.kill(os.getpid(), signal.SIGTERM)

signal.signal(signal.SIGTERM, receive_signal)

observer = Observer()
observer.schedule(EventHandler(patterns=['*.py']), str(cwd), recursive=True)
observer.start()

start()

while True:
  try:
    mod_path = next(iter(changed_modules), None)
    if mod_path:
      changed_modules = set()
      restart(mod_path)
    time.sleep(0.05)
  except RestartException:
    pass
  except KeyboardInterrupt:
    break

def main():
  pass
