from controller import folder_traversal
from view import choose_chat_text_input
from data import data
from colorama import init as colorama_init


def main():
    colorama_init()

    # get all the chats from the folder
    chats: [data.Chat] = folder_traversal.traverse_folder("/home/zsdaniel/Downloads/messages")

    cmd_line = choose_chat_text_input.ChooseChatCommandLine(chats)
    cmd_line.start_command_line()


main()
