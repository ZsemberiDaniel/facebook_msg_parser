from view import console_input
from view import chat_data_text_input
from controller import chat_decoder
from data import data

from colorama import Fore, Style


class ChooseChatCommandLine(console_input.ConsoleInput):
    command_choose = console_input.ConsoleCommand(
        ["choose", "c"],
        lambda console, switches, kwargs: console.choose(kwargs["chats"], switches),
        lambda: ChooseChatCommandLine.help_choose()
    )
    command_filter = console_input.ConsoleCommand(
        ["filter", "f"],
        lambda console, switches, kwargs: console.filter(kwargs["chats"], switches),
        lambda: ChooseChatCommandLine.help_filter()
    )

    def __init__(self, chats: [data.Chat]):
        super().__init__()
        self.chats = chats
        self.command_line_name = "choose chat command line"

        self.add_commands(self.command_choose, self.command_filter)

    def process_command(self, commands, **kwargs):
        super().process_command(commands, chats=self.chats)

    def print_welcome_message(self):
        print(Fore.BLUE + """   \  |                                                                             |                         
  |\/ |   _ \   __|   __|   _ \  __ \    _` |   _ \   __|       _` |  __ \    _` |  |  |   | _  /   _ \   __| 
  |   |   __/ \__ \ \__ \   __/  |   |  (   |   __/  |         (   |  |   |  (   |  |  |   |   /    __/  |    
 _|  _| \___| ____/ ____/ \___| _|  _| \__, | \___| _|        \__,_| _|  _| \__,_| _| \__, | ___| \___| _|    
                                       |___/                                          ____/                   """ +
              Fore.RESET)

    def _get_write_string(self, kwargs, switches: [str]):
        if "chats" in kwargs:
            out_string = "Names:\n"
            chats: [data.Chat] = kwargs["chats"]

            for chat in chats:
                out_string += chat.name + "\n"

            return out_string
        else:
            return super()._get_write_string(kwargs, switches)

    def filter(self, chats: [data.Chat], switches: [str]):
        """
        Filters the names with the given substring in switches
        """
        substr = switches[-1]

        return {"chats": filter(lambda chat: substr in chat.name, chats)}

    def choose(self, chats: [data.Chat], switches: [str]):
        """
        Chooses the chat from the switches then starts a command line for that
        """
        substr = switches[-1]

        # get all that contain this string
        found = [c for c in chats if substr in c.name]

        chosen_chat = None
        # if there was an exact match then choose that
        for chat in found:
            if chat.name == substr:
                chosen_chat = chat

        if chosen_chat is None:
            if len(found) > 1:
                print(Fore.YELLOW + "There are more than 1 names found with " + substr + " (" + str(len(found))
                      + ")" + Fore.RESET)
                return
            elif len(found) == 0:
                print(Fore.RED + "None found with this name!" + Fore.RESET)
                return
            else:
                chosen_chat = found[0]

        # start chat command line
        chosen_chat = chat_decoder.add_all_data(chosen_chat)
        chat_command_line = chat_data_text_input.ChatCommandLine(chosen_chat)
        chat_command_line.start_command_line()

    @staticmethod
    def help_choose():
        print("""You can choose a chat with \t choose [substring_of_name]""")

    @staticmethod
    def help_filter():
        print("""You can filter the names with \t filter [substring]""")
