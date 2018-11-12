from view.console import console_input
from view import chat_data_text_input
from controller import chat_decoder
from data import data
from view.console.console_manager import console_manager

from colorama import Fore


class ChooseChatCommandLine(console_input.ConsoleInput):
    def __init__(self, chats: [data.Chat]):
        self.command_choose = console_input.ConsoleCommand(
            ["choose", "c"],
            lambda console, switches, kwargs: console.choose(kwargs["chats"], switches),
            lambda: ChooseChatCommandLine.help_choose(),
            lambda switches, word: self.choose_auto_complete(switches, word)
        )
        self.command_filter = console_input.ConsoleCommand(
            ["filter", "f"],
            lambda console, switches, kwargs: console.filter(kwargs["chats"], switches),
            lambda: ChooseChatCommandLine.help_filter()
        )

        super().__init__()
        self.chats = chats
        self.command_line_name = "choose chat command line"

        self.add_commands(self.command_choose, self.command_filter)

    def process_command(self, commands, **kwargs):
        return super().process_command(commands, chats=self.chats)

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

    def filter(self, chats: [data.Chat], switches: [str]) -> {str: []}:
        """
        Filters the names with the given substring in switches
        """
        if len(switches) <= 0:
            print(Fore.RED + "You need to provide a substring of a name for filter!" + Fore.RESET)
            return

        substr = switches[-1]

        return {"chats": list(filter(lambda chat: substr in chat.name, chats))}

    def choose(self, chats: [data.Chat], switches: [str]):
        """
        Chooses the chat from the switches then starts a command line for that
        """
        if len(switches) <= 0:
            print(Fore.RED + "You need to provide a substring of a name for choose!" + Fore.RESET)
            return

        substr = switches[-1]

        # get all that contain this string
        found = [c for c in chats if substr in c.name]

        chosen_chat = None
        # if there was an exact match then choose that
        for chat in found:
            if chat.name == substr:
                chosen_chat = chat

        # no exact match
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
        try:
            chosen_chat = chat_decoder.add_all_data(chosen_chat)
            console_manager.add_console(chat_data_text_input.ChatCommandLine(chosen_chat))
        except ValueError:
            print(Fore.RED + "The given chat has no folder path assigned to it! Maybe restart the application?" +
                  Fore.RESET)

        return {"chats": [chosen_chat]}

    @staticmethod
    def help_choose():
        print("""You can choose a chat with \t choose [substring_of_name]""")

    def choose_auto_complete(self, switches: [str], curr_word: str) -> [str]:
        # nothing before the current
        if len(switches) == 0:
            return [chat.name for chat in self.chats if curr_word in chat.name]
        else:
            return []

    @staticmethod
    def help_filter():
        print("""You can filter the names with \t filter [substring]""")
