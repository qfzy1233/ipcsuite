import os
import time

from lib.data import VERSION, AUTHOR, POCS_PATHS, POCS, WORKER
from lib.requests import patch_session, _disable_warnings
from lib.cmd import set_commandline_options
from lib.loader import loader_string_to_module
from lib.threads import run_threading
from lib.color import Colors


def banner():
    logo = """{0}
       _                   _ __
      (_)__  _______ __ __(_) /____
     / / _ \/ __(_-</ // / / __/ -_)
    /_/ .__/\__/___/\_,_/_/\__/\__/
   /_/
            {1} #dev {2}

            {3}{4}{5}
    """.format(Colors.BLUE, Colors.YELLOW, VERSION, Colors.YELLOW,
               Colors.FUCHSIA, AUTHOR, Colors.FUCHSIA)
    print(logo)


def init():
    patch_session()
    _disable_warnings()

    _pocs = []

    for root, dirs, files in os.walk(POCS_PATHS):
        files = filter(lambda x: not x.startswith("__") and x.endswith(".py"),
                      files)
        _pocs.extend(map(lambda x: os.path.join(root, x), files))

    for poc in _pocs:
        with open(poc, "r") as fs:
            module = loader_string_to_module(fs.read())
            POCS.append(module)


def start():
    options, parser = set_commandline_options()

    if options.target is None:
        exit(0)

    for poc in POCS:
        WORKER.put((options.target, poc))

    run_threading(10, worker)


def worker():
    if not WORKER.empty():
        arg, poc = WORKER.get()
        try:
            ret = poc.audit(arg)
        except Exception as e:
            ret = None
        if ret:
            print(Colors.GREEN + "[*]" + Colors.GREEN, ret)


def end():
    print("{0}[*]{1} end shutdown {2}".format(Colors.GREEN, Colors.GREEN, time.strftime("%X")))


def main():
    banner()
    init()
    start()
    end()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
