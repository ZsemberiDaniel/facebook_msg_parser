from view.console import console_input
from controller import chat_analyzer
from data import data
from data.facebook_emojis import Emoji as FEmoji
from misc.texttable_misc import get_string_wrapped

from typing import Union
from copy import deepcopy
from colorama import Fore
from datetime import datetime
from emoji import emojize, demojize
from texttable import Texttable
from view.commands import chat_filterable


class Emoji(FEmoji):
    def __init__(self, f_emoji: Union[FEmoji, None], date_time: Union[datetime, None],
                 emoji_string: str=None, other_data: str=None):
        if f_emoji is not None:
            super().__init__(f_emoji.name, f_emoji.codes, f_emoji.path, f_emoji.aliases, f_emoji.emotions)

        self.date_time = date_time

        # set the emoji string
        if emoji_string is None:
            self.emoji_string = emojize(self.name)
        else:
            self.emoji_string = emoji_string

        # other data we may want to write out
        self.other_data = other_data

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

        # other data
        if self.other_data is not None:
            row.append(str(self.other_data))
        else:
            row.append("")

        return row

    @staticmethod
    def printable_header(show_date=False) -> [str]:
        if show_date:
            header = ["Date"]
        else:
            header = []

        header += ["Emoji", "Other data"]

        return header


class EmojiAnalyzerConsole(console_input.ConsoleInput):

    def __init__(self, chat: data.Chat):
        super().__init__()

        self.command_top = console_input.ConsoleCommand(
            ["top", "t"],
            lambda console, switches, kwargs: console.top_emojis(kwargs["chat"], switches),
            lambda: EmojiAnalyzerConsole.help_top(),
            lambda switches, word: self.auto_complete_top(switches, word)
        )
        self.command_over_time = console_input.ConsoleCommand(
            ["overtime", "ot", "o"],
            lambda console, switches, kwargs: console.emojis_over_time(kwargs["chat"], switches),
            lambda: EmojiAnalyzerConsole.help_overtime(),
            lambda switches, word: self.auto_complete_overtime(switches, word)
        )
        self.command_filter = chat_filterable.command_filter

        self.chat = chat
        self.command_line_name = "emoji analyzer"

        self.add_commands(self.command_top, self.command_over_time, self.command_filter)

    def process_command(self, commands, **kwargs):
        return super().process_command(commands, chat=deepcopy(self.chat))

    def _get_write_string(self, kwargs, switches: [str]):
        show_date = "-d" in switches

        if "output_string" in kwargs:
            out = kwargs.pop("output_string")
            return out
        elif "emotions_per_participant" in kwargs:
            output = ""
            emotions_per_participant: {str: str} = kwargs["emotions_per_participant"]

            for participant in emotions_per_participant:
                output += participant + "'s emotions:" + "\n"
                output += "==============================================\n"

                for emotion in emotions_per_participant[participant]:
                    output += str(emotion) + "\n"

                output += "\n"

            return output
        elif "emojis_per_participant" in kwargs:
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
                return {}

            try:
                count = int(switches[count_switch_at + 1])
            except ValueError:
                print(Fore.RED + "A number needs to be provided for -c in top!" + Fore.RESET)
                return {}

        # we need to write out emotions instead of emojis
        if "-t" in switches:
            most_used = chat_analyzer.emoji_emotions_top_per_participant(chat, count)
            # map to string
            most_used = {part: list(map(lambda t: str(t[0]) + ": " + str(t[1]), most_used[part])) for part in most_used}
            return {"emotions_per_participant": most_used}
        else:
            most_used = chat_analyzer.emoji_strs_top_per_participant(chat, count)
            # map to Emoji object here
            most_used = {part: list(map(lambda t: Emoji(None, None, t[0], "Count: " + str(t[1])), most_used[part]))
                         for part in most_used}
            return {"emojis_per_participant": most_used}

    def emojis_over_time(self, chat: data.Chat, switches: [str]):
        # monthly
        if "-m" in switches:
            # emotions
            if "-t" in switches:
                monthly: {datetime.date: {str: {str: int}}} = chat_analyzer.emoji_emotions_per_participant_monthly(chat)
            else:  # emojis
                monthly: {datetime.date: {str: {str: int}}} = chat_analyzer.emoji_strs_per_participant_monthly(chat)

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
        print("""You can get the top emojis with \t top
        \t You can specify how many emojis you want returned with \t -c [count]
        \t You can get the emotions instead with \t -t""")

    def auto_complete_top(self, switches_before: [str], word: str) -> [str]:
        if word.startswith("-"):
            return ["c", "t"]
        elif len(switches_before) == 0:
            return ["-c", "-t"]
        else:
            if switches_before[-1] == "-c":
                return ["Count of emojis", "[count]"]
            elif word == "":
                return ["-c", "-t"]
            else:
                return []

    @staticmethod
    def help_overtime():
        print("""You can get the top emoji/emotions over time with \t overtime
        \t If you want emotions add \t -t
        \t You can get it monthly via \t -m""")

    def auto_complete_overtime(self, switches_before: [str], word: str) -> [str]:
        if word.startswith("-"):
            return ["t", "m"]
        elif len(switches_before) == 0:
            return ["-t", "-m"]
        else:
            if word == "":
                return ["-t", "-m"]
            else:
                return []
