import sys
import importlib
import time
import traceback
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from termcolor import colored
import signal
import re
from io import StringIO
import os

sys.path.insert(0, '.')

cwd = Path.cwd()
module_path = Path(sys.argv[1])
module_path_str = str(module_path)[:-3].replace('/', '.')
non_local_modules = set()
changed_modules = set()

class RestartException(Exception):
  pass

def print_current_traceback():
  exception_output = StringIO()
  traceback.print_exc(file=exception_output)
  stack_trace = exception_output.getvalue().splitlines()
  stack_trace.pop(0)
  error = stack_trace.pop()

  lines = list(enumerate(stack_trace))
  filter_line = lambda line: 'frozen importlib._bootstrap' in line[1]
  start_i = next(line for line in lines if filter_line(line))[0]
  start_i = next(line for line in lines[start_i:] if not filter_line(line))[0]
  lines = [l[1].strip() for l in lines[start_i:]]

  for line in lines:
    matches = re.match('File "(.*)", line (\d+), in (.+)', line)
    if matches:
      path, line_number, method = matches.groups()
    else:
      print(
        f"{colored(path, 'cyan')}"
        f":{colored(line_number, 'yellow')} "
        f"{colored(method, 'green')}: "
        f"{line}"
      )
  print(colored(error, 'red'))
  print('')

def to_module_path(module):
  try:
    return Path(module.__file__).absolute()
  except:
    return Path('/')

def is_local_module(module):
  if module in non_local_modules:
    return False
  try:
    target = to_module_path(module)
    is_local = cwd in target.parents
  except AttributeError:
    is_local = False
  if not is_local:
    non_local_modules.add(module)
  return is_local

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
      os.kill(os.getpid(), signal.SIGUSR1)

signal.signal(signal.SIGUSR1, receive_signal)

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
