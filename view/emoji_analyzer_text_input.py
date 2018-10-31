from view import console_input
from controller import chat_analyzer
from data import data
from data.facebook_emojis import facebook_emojis, Emoji as FEmoji
from misc.texttable_misc import get_string_wrapped

from typing import Union
from copy import deepcopy
from colorama import Fore
from datetime import datetime
from emoji import emojize, demojize
from texttable import Texttable


class Emoji(FEmoji):
    def __init__(self, f_emoji: Union[FEmoji, None], date_time: Union[datetime, None],
                 emoji_string: str=None, count: int=None):
        if f_emoji is not None:
            super().__init__(f_emoji.name, f_emoji.codes, f_emoji.path, f_emoji.aliases, f_emoji.emotions)

        self.date_time = date_time

        # set the emoji string
        if emoji_string is None:
            self.emoji_string = emojize(self.name)
        else:
            self.emoji_string = emoji_string

        # how many times it can be found in the chat. May be None
        self.count = count

    def printable_string(self, show_date=False) -> [str]:
        """
        Returns a string which then can be printed in a table as a row
        :param show_date: Show the date
        """
        row =[]
        # date
        if show_date:
            row.append("-" if self.date_time is None else str(self.date_time))

        # emoji
        row.append(self.emoji_string + demojize(self.emoji_string, delimiters=(" (", ")")))

        # count
        if self.count is not None:
            row.append(str(self.count))
        else:
            row.append("")

        return row

    @staticmethod
    def printable_header(show_date=False) -> [str]:
        if show_date:
            header = ["Date"]
        else:
            header = []

        header += ["Emoji", "Count"]

        return header


class EmojiAnalyzerConsole(console_input.ConsoleInput):
    command_top = console_input.ConsoleCommand(
        ["top", "t"],
        lambda console, switches, kwargs: console.top_emojis(kwargs["chat"], switches),
        lambda: EmojiAnalyzerConsole.help_top()
    )
    command_over_time = console_input.ConsoleCommand(
        ["overtime", "ot", "o"],
        lambda console, switches, kwargs: console.emojis_over_time(kwargs["chat"], switches)
    )

    def __init__(self, chat: data.Chat):
        super().__init__()
        self.chat = chat
        self.command_line_name = "emoji analyzer"

        self.add_commands(self.command_top, self.command_over_time)

    def process_command(self, commands, **kwargs):
        super().process_command(commands, chat=deepcopy(self.chat))

    def _get_write_string(self, kwargs, switches: [str]):
        show_date = "-d" in switches

        if "emojis_per_participant" in kwargs:
            output = ""
            emojis_per_participant: {str: [Emoji]} = kwargs["emojis_per_participant"]

            for participant in emojis_per_participant:
                output += participant + ":" + "\n"

                texttable = Texttable(200)
                texttable.set_deco(Texttable.HEADER)
                texttable.header(Emoji.printable_header(show_date))

                for emoji in emojis_per_participant[participant]:
                    texttable.add_row(emoji.printable_string(show_date))

                output += texttable.draw() + "\n"

            return output
        if "output_string" in kwargs:
            return kwargs["output_string"]
        else:
            return super()._get_write_string(kwargs, switches)

    def top_emojis(self, chat: data.Chat, switches: [str]):
        count = 5

        # count switch
        if "-c" in switches:
            count_switch_at = switches.index("-c")

            # no number at end
            if count_switch_at + 1 >= len(switches):
                print(Fore.RED + "You need to provide a number for -c in top!" + Fore.RESET)
                return

            try:
                count = int(switches[count_switch_at + 1])
            except ValueError:
                print(Fore.RED + "A number needs to be provided for -c in top!" + Fore.RESET)

        most_used = chat_analyzer.emoji_strs_top_per_participant(chat, count)
        # map to Emoji object here
        most_used = {part: list(map(lambda t: Emoji(None, None, t[0], t[1]), most_used[part])) for part in most_used}
        return {"emojis_per_participant": most_used}

    def emojis_over_time(self, chat: data.Chat, switches: [str]):
        # monthly
        if "-m" in switches:
            monthly: {datetime.date: {str: {str: int}}} = chat_analyzer.emoji_emotions_monthly(chat)

            table = Texttable(0)
            table.set_deco(Texttable.VLINES)
            table.header(["Name"] + list(monthly.keys()))

            # rows by participant
            rows: {str: [str]} = {}
            for participant in chat.participants:
                rows[participant.name] = [participant.name]  # first entry is the name

            # adding to rows
            for month in monthly:
                for participant in monthly[month]:
                    em_this_month = monthly[month][participant]
                    rows[participant].append(max(em_this_month, key=lambda emotion: em_this_month[emotion], default=""))

            for participant in rows:
                table.add_row(rows[participant])

            return {"output_string": get_string_wrapped(table, 120, 1)}

    @staticmethod
    def help_write():
        super().help_write()
        print("""\tYou can add date to the emojis with switch \t -d
        \t\t except of course for the ones that there is no use for, for example top""")

    @staticmethod
    def help_top():
        print("""You can get the top emojis with \t top [count]
        \t You can specify how many emojis you want returned with \t -c [count]""")
