import builtins
import importlib
import os
import signal
import sys
import time
import omg
from pathlib import Path
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

cwd = Path.cwd().resolve()
module_path = Path(sys.argv[1])
module_path_str = str(module_path.with_suffix("")).replace("/", ".").replace("\\", ".")
is_local_by_module = {}
changed_modules = set()
start_time = 0
historic_local_modname_by_path: dict[Path, str] = {}

omg.IS_OMG = True
builtins.__dict__["print"] = omg.print
sys.path.insert(0, ".")
sys.argv = sys.argv[1:]

def stopwatch():
  global start_time
  duration = round(time.time() - start_time) if start_time else 0
  minutes = duration // 60
  seconds = duration % 60
  minutes_str = f"{minutes}m" if minutes else ""
  duration_str = f"({minutes_str}{seconds}s)" if duration >= 1 else ""
  start_time = 0
  return duration_str

class RestartException(Exception):
  pass

def to_module_path(module):
  file = getattr(module, "__file__", None)
  if not file:
    ns_path = getattr(getattr(module, "__path__", None), "_path", ())
    file = next(iter(ns_path), None)
  return Path(file or "/__").resolve()

def is_local_module(module):
  modname = module.__name__
  if modname in is_local_by_module:
    return is_local_by_module[modname]
  target = to_module_path(module)
  is_local = ".venv" not in target.parts and cwd in target.parents
  is_local_by_module[modname] = is_local
  return is_local_module(module)

def get_local_modname_by_path() -> dict[Path, str]:
  result = {
    to_module_path(module): mod_name
    for mod_name, module in list(sys.modules.items())
    if is_local_module(module)
  }
  result[module_path.resolve()] = module_path_str
  return result

def start():
  global start_time
  start_time = time.time()
  try:
    try:
      importlib.import_module(module_path_str)
      historic_local_modname_by_path.clear()
      print(f"⚠️  {module_path} finished. {stopwatch()}")
    except OSError as err:
      if str(err) == "could not get source code":
        start()
      else:
        raise
  except KeyboardInterrupt:
    print(f"\n⚠️  Script interrupted. {stopwatch()}")
  except SystemExit:
    print(f"\n⚠️  Script exited. {stopwatch()}")
  except RestartException:
    pass
  except:
    omg.pretty_print_exc()

def restart(changed_file):
  os.system("cls" if os.name == "nt" else "clear")
  print(f"⚠️  {changed_file.relative_to(cwd)} changed, restarting. {stopwatch()}")
  local_modname_by_path = get_local_modname_by_path()
  historic_local_modname_by_path.update(local_modname_by_path)
  for handler in omg.reload_handlers:
    handler()
  omg.reload_handlers.clear()
  for mod_name in local_modname_by_path.values():
    sys.modules.pop(mod_name, None)
  start()

def receive_signal(signum, stack):
  raise RestartException()

class EventHandler(PatternMatchingEventHandler):
  def on_modified(self, evt):
    src_path = Path(evt.src_path).resolve()
    dest_path = Path(evt.dest_path).resolve() if hasattr(evt, "dest_path") else None
    local_modname_by_path = {**historic_local_modname_by_path, **get_local_modname_by_path()}
    if src_path in local_modname_by_path:
      changed_modules.add(src_path)
    if dest_path in local_modname_by_path:
      changed_modules.add(dest_path)
    if len(changed_modules) and os.name != "nt":
      os.kill(os.getpid(), signal.SIGTERM)

signal.signal(signal.SIGTERM, receive_signal)

observer = Observer()
observer.schedule(EventHandler(patterns=["*.py"]), str(cwd), recursive=True)
observer.start()

def main():
  start()
  while True:
    try:
      mod_path = next(iter(changed_modules), None)
      if mod_path:
        changed_modules.clear()
        restart(mod_path)
      time.sleep(0.05)
    except RestartException:
      pass
    except KeyboardInterrupt:
      break
