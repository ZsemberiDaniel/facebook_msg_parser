from controller import folder_traversal
from view import choose_chat_text_input
from data import data
from view.console.console_manager import console_manager
from colorama import init as colorama_init
import sys


def main():
    colorama_init()

    # get all the chats from the folder
    chats: [data.Chat] = folder_traversal.traverse_folder(sys.argv[1])

    console_manager.start()
    console_manager.add_console(choose_chat_text_input.ChooseChatCommandLine(chats))


main()
