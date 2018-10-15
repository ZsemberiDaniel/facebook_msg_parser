import re
import string
from typing import Optional

from data import data


_choose_command = "c"
_help_command = "help"
_filter_command = "f"


def choose_chat(chats) -> data.Chat:
    for chat in chats:
        print(chat.string_for_user())

    # until the user chooses get next command
    output = _process_command(_get_next_command(), chats)
    while output is None:
        output = _process_command(_get_next_command(), chats)

    return output


def _get_next_command() -> string:
    return input("Choose a chat with c [name]! For other command type help! ")


def _write_filtered(substr, chats) -> None:
    """
    Writes out the chats which names contain the given substr
    """
    for chat in chats:
        if substr in chat.name:
            print(chat.string_for_user())


def _process_command(command, chats) -> Optional[data.Chat]:
    """
    Processes a given string command. Writes out stuff if needed
    :param command: The command as string
    :param chats: What chats we are currently working with
    :return: None if we need another command otherwise the chose chat
    """

    # only one whitespace in between -> split by that
    commands = re.sub("\s+", " ", command).strip().split(" ")

    if commands[0] == _help_command:
        print("Choose a chat with \t\t\t c [name]")
        print("Filter with \t\t\t\t f [substring]")
        print("In case you already forgot get this help with \t help")
    elif commands[0] == _filter_command:
        _write_filtered(commands[1], chats)
    elif commands[0] == _choose_command:
        # get all that contain this string
        found = [c for c in chats if commands[1] in c.name]

        # if there was an exact match then choose that
        for chat in found:
            if chat.name == commands[1]:
                return chat

        if len(found) > 1:
            print("There are more than 1 names found with " + commands[1])
        elif len(found) == 0:
            print("None found with this name!")
        else:
            return found[0]
