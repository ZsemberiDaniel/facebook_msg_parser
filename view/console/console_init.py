import atexit
import os
from colorama import Fore
from definitions import ROOT_DIR

try:
    import readline

    # setting up history file
    hist_file = os.path.join(ROOT_DIR, ".msg_parser_history")
    try:
        readline.read_history_file(hist_file)
        # default history is infinite
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass

    atexit.register(readline.write_history_file, hist_file)
except:
    print(Fore.RED + "Readline module not available! Command line won't be as functional!" + Fore.RESET)
