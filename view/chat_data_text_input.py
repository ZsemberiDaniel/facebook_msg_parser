from data import data
from view import markov_text_input
from view import emoji_analyzer_text_input
from view import console_input as con_inp
from controller import chat_analyzer
from controller import data_visualizer
from pyfiglet import figlet_format
from misc.texttable_misc import get_string_wrapped
import texttable as tt
import datetime
import unicodedata
from copy import deepcopy
from colorama import Fore


class ChatCommandLine(con_inp.ConsoleInput):
    command_basic_data = con_inp.ConsoleCommand(
        ["basic", "b"],
        lambda cmd_line, switches, kwargs: cmd_line.print_basic(kwargs["chat"]),
        lambda: ChatCommandLine.help_basic()
    )
    command_message_count = con_inp.ConsoleCommand(
        ["count"],
        lambda cmd_line, switches, kwargs: cmd_line.print_message_count(kwargs["chat"], switches),
        lambda: ChatCommandLine.help_msg_count()
    )
    command_chart = con_inp.ConsoleCommand(
        ["chart", "c"],
        lambda cmd_line, switches, kwargs: cmd_line.chart(kwargs["chat"], switches),
        lambda: ChatCommandLine.help_chart()
    )
    command_emojis = con_inp.ConsoleCommand(
        ["emoji", "e"],
        lambda cmd_line, switches, kwargs: cmd_line.only_emojis(kwargs["chat"], switches),
        lambda: ChatCommandLine.help_emoji()
    )
    commands_filter = con_inp.ConsoleCommand(
        ["filter", "f"],
        lambda cmd_line, switches, kwargs: cmd_line.filter_chat(kwargs["chat"], switches),
        lambda: ChatCommandLine.help_filter()
    )
    command_markov = con_inp.ConsoleCommand(
        ["markov", "m"],
        lambda cmd_line, switches, kwargs: cmd_line.enter_markov_command_line(kwargs["chat"], switches),
        lambda: ChatCommandLine.help_markov()
    )
    command_search = con_inp.ConsoleCommand(
        ["search", "s"],
        lambda cmd_line, switches, kwargs: cmd_line.search(kwargs["chat"], switches[:-1], switches[-1]),
        lambda: ChatCommandLine.help_search()
    )

    def __init__(self, chat: data.Chat):
        super().__init__()
        self.chat = chat
        self.command_line_name = "chat command line"

        self.add_commands(self.command_basic_data, self.command_message_count, self.command_chart, self.commands_filter,
                          self.command_markov, self.command_search, self.command_write, self.command_emojis)

    def process_command(self, commands, **kwargs):
        super().process_command(commands, chat=deepcopy(self.chat))

    def print_welcome_message(self):
        print("\n" + figlet_format(unicodedata.normalize("NFD", self.chat.name).encode("ASCII", "ignore")
                                   .decode("UTF-8"), font="mini"))

    def only_emojis(self, chat: data.Chat, switches: [str]):
        new_chat = chat

        # analyzing emoji usage
        if "-a" in switches:
            emoji_console = emoji_analyzer_text_input.EmojiAnalyzerConsole(new_chat)
            emoji_console.start_command_line()
            return

        if "-onlyem" in switches or "-o" in switches:
            new_chat.messages = chat_analyzer.emoji_messages(chat)
        else:
            new_chat.messages = chat_analyzer.emoji_whole_messages(chat)

        return {"chat": new_chat}

    def enter_markov_command_line(self, chat: data.Chat, switches: [str]):
        layer_count = 3
        try:
            if len(switches) >= 1:
                layer_count = int(switches[-1])
        except ValueError:
            print(Fore.RED + "Layer count needs to be a number in markov command!" + Fore.RESET)

        markov_cmd_line = markov_text_input.MarkovCommandLine(chat, layer_count)
        markov_cmd_line.start_command_line()

    def chart(self, chat: data.Chat, switches: [str]):
        width = 1000
        height = 600
        emoji_per_row = 15

        try:
            at = switches.index("-s")

            try:
                if len(switches) > at + 1:
                    split = switches[at + 1].split("x")
                    if len(split) > 1:  # [width]x[height]
                        width = int(split[0])
                        height = int(split[1])
                    else:
                        width = int(switches[at + 1])
                        height = int(width * (2/3))
            except ValueError:
                print(Fore.RED + "Integer values need to be provided for the -s switch in chart!" + Fore.RESET)
                return
        except ValueError:
            pass

        try:
            at = switches.index("-r")

            if len(switches) > at + 1:
                emoji_per_row = int(switches[at + 1])
        except ValueError:
            pass

        do_all_plot = len(switches) == 0

        if do_all_plot or "-d" in switches:
            data_visualizer.plot_message_distribution(chat, size=(width, height))
        if do_all_plot or "-m" in switches:
            data_visualizer.plot_activity_msg(chat, size=(width, height))
        if do_all_plot or "-c" in switches:
            data_visualizer.plot_activity_char(chat, size=(width, height))
        if do_all_plot or "-e" in switches:
            data_visualizer.plot_emojis_per_participant(chat, width, emoji_size=width // emoji_per_row)
        if do_all_plot or "-ey" in switches:
            data_visualizer.plot_emojis_per_participant_yearly(chat, width, emoji_size=width // emoji_per_row)
        if do_all_plot or "-em" in switches:
            data_visualizer.plot_emoji_emotions_monthly(chat, size=(width, height))

    def print_message_count(self, chat: data.Chat, switches: [str]):
        if "-p" in switches:
            for participant in chat.participants:
                participant_msg = list(filter(lambda msg: msg.sender == participant.name, chat.messages))

                print(participant.name + ": " + str(len(participant_msg)))
        else:
            print("Message count: " + str(len(chat.messages)))

    def filter_chat(self, chat: data.Chat, switches: [str]) -> {}:
        # FILTER DATE
        try:
            date_in_array = switches.index("-d")

            # from date
            if switches[date_in_array + 1] == "_":  # the from date was omitted
                from_date = datetime.date(1990, 1, 1)
            else:
                try:
                    f_year, f_month, f_day = map(int, switches[date_in_array + 1].split("."))
                except ValueError:
                    print(Fore.RED + "Starting month should be in format YYYY.MM.DD!" + Fore.RESET)
                    return

                from_date = datetime.date(f_year, f_month, f_day)

            # to date
            # the to date was omitted
            if len(switches) <= date_in_array + 2 or switches[date_in_array + 2] == "_" or \
                    switches[date_in_array + 2].startswith("-"):  # another switch
                to_date = datetime.date.today()
            else:
                try:
                    t_year, t_month, t_day = map(int, switches[date_in_array + 2].split("."))
                except ValueError:
                    print(Fore.RED + "Ending date should be in format YYYY.MM.DD!" + Fore.RESET)
                    return

                to_date = datetime.date(t_year, t_month, t_day)

            chat.messages = chat_analyzer.get_from_to_date(chat, from_date, to_date)
        except ValueError:
            pass

        # FILTER
        try:
            participant_in_array = switches.index("-p")

            # if there was no parameter given after the -p switch then there are no participants to filter ->
            # will result in []. If there were names given split them by ,
            to_filter_participants = [] if len(switches) <= participant_in_array + 1 else \
                switches[participant_in_array + 1].split(",")

            if len(to_filter_participants) > 0:
                chat = chat_analyzer.get_messages_only_by(chat, to_filter_participants)

        except ValueError:
            pass

        return {"chat": chat}

    def _get_write_string(self, kwargs, switches: [str]):
        chat: data.Chat = kwargs.get("chat", None)

        if chat is not None:
            # what we want to write
            output = ""
            for msg in chat.messages:
                output += msg.str_for_user() + "\n"

            return output
        else:
            return super()._get_write_string(kwargs, switches)

    def search(self, chat: data.Chat, switches: [str], word_or_regex: str) -> {}:
        # based on the switches we can search in regex or
        if "-r" in switches:
            found_messages = chat_analyzer.search_in_messages(chat,
                                                              regex=word_or_regex,
                                                              ignore_case="-i" in switches)
        else:
            found_messages = chat_analyzer\
                .search_in_messages(chat,  # this matches whole word
                                    word=(" " + word_or_regex + " " if "-h" in switches else word_or_regex),
                                    ignore_case="-i" in switches)

        # how many messages were found
        msg_count = 0
        for participant in found_messages.keys():
            msg_count += len(found_messages[participant])

        # nothing found
        if msg_count == 0:
            print(Fore.YELLOW + "Nothing found that matches " + word_or_regex + Fore.RESET)
            chat.messages = []

            return chat

        # got some results
        print(Fore.GREEN + "Found " + str(msg_count) + " matching messages" + Fore.RESET)

        # collect them into one list
        all_msg = []
        for participant in found_messages:
            all_msg += found_messages[participant]

        chat.messages = all_msg

        return {"chat": chat}

    def print_basic(self, chat: data.Chat):
        between_dates = chat_analyzer.date_between(chat)
        msg_counts = chat_analyzer.message_count(chat)
        response_count = chat_analyzer.response_count(chat)
        avg_response_time_day = chat_analyzer.avg_response_time_no_overnight(chat) or {}
        avg_response_time = chat_analyzer.avg_response_time(chat) or {}
        sum_character_count = chat_analyzer.character_count(chat)
        avg_character_count = chat_analyzer.avg_character_count(chat)
        emojis_count = chat_analyzer.emoji_strs_count_per_participant(chat)
        most_used_emoji = chat_analyzer.emoji_strs_top_per_participant(chat)
        most_used_emotion = chat_analyzer.emoji_emotions_top_per_participant(chat)

        table = tt.Texttable()
        table.set_cols_width([25] + [10] * len(msg_counts.keys()))
        header = [""]
        msg_counts_text = ["Message counts"]
        response_count_text = ["Response count"]
        avg_resp_time_day_text = ["Avg. response time (no overnight)"]
        avg_resp_time_text = ["Avg. response time (with overnight🌃)"]
        char_count_text = ["Character count"]
        avg_char_count_text = ["Avg. character count"]
        emoji_count_text = ["Emoji count"]
        most_used_emoji_text = ["Most used emoji"]
        most_used_emotion_text = ["Most used emotion"]

        for participant in sorted(msg_counts.keys()):
            header.append(participant)
            msg_counts_text.append(msg_counts.get(participant, 0))
            response_count_text.append(response_count.get(participant, 0))
            avg_resp_time_day_text.append("{0:.2f} min".format(avg_response_time_day.get(participant, 0) / 60))
            avg_resp_time_text.append("{0:.2f} min".format(avg_response_time.get(participant, 0) / 60))
            char_count_text.append(sum_character_count.get(participant, 0))
            avg_char_count_text.append("{0:.2f}".format(avg_character_count.get(participant, 0)))
            emoji_count_text.append(emojis_count.get(participant, "-"))
            top_emoji = most_used_emoji.get(participant, None)
            if top_emoji is not None and len(top_emoji) > 0:
                most_used_emoji_text.append(str(top_emoji[0][0]) + ": " + str(top_emoji[0][1]))
            else:
                most_used_emoji_text.append("-")
            top_emotion = most_used_emotion.get(participant, None)
            if top_emotion is not None and len(top_emotion) > 0 and top_emotion[0][1] is not 0:
                most_used_emotion_text.append(top_emotion[0][0] + ": " + str(top_emotion[0][1]))
            else:
                most_used_emotion_text.append("-")

        table.header(header)
        table.add_row(msg_counts_text)
        table.add_row(response_count_text)
        table.add_row(avg_resp_time_day_text)
        table.add_row(avg_resp_time_text)
        table.add_row(char_count_text)
        table.add_row(avg_char_count_text)
        table.add_row(emoji_count_text)
        table.add_row(most_used_emoji_text)
        table.add_row(most_used_emotion_text)

        print("*************************************************************")
        print("Chatting started at " + str(between_dates[0].date()) + " ended (so far) at " + str(between_dates[1].date()))
        print(get_string_wrapped(table, 150, 1))
        print("*************************************************************")

    @staticmethod
    def help_emoji():
        print("""Get only the messages containing emojis \t emoji
        \t You can enter emoji analyzer console with \t -a
        \t You can remove non-emojis from messages with \t -onlyem or -o
        """)

    @staticmethod
    def help_basic():
        # basic
        print("Get basic information about your chat with \t basic")

    @staticmethod
    def help_msg_count():
        # msg count
        print("Write out how many messages there are with \t count")
        print("\t You can specify to write out separately for each participant with \t -p")

    @staticmethod
    def help_filter():
        # filter
        print("Filter with \t filter")
        print("\t You can define a from and to date with \t -d [year.month.day] [year.month.day]")
        print("\t\t If no to date is given then today will be the to date.")
        print("\t\t You can omit the from date with '_'. If no from date is given then it will be written out from" +
              "the start of conversation.")
        print("\t You can filter for participant(s) with \t -p participant1(,participant2)(,participant3)(...),")
        print("\t\t The names are checked with them being converted to lower case ASCII characters and as a\n"
              "\t\t substring of the real names of participants.")
        print("\t\t If more names are given separated by commas then the logical operator between them is or.")

    @staticmethod
    def help_search():
        # search
        print("Search in messages with \t search [switches] [what to find]")
        print("\t add a keyword with (default behaviour) \t -w")
        print("\t match whole world in -w mode \t\t -h")
        print("\t add a regex with \t\t -r")
        print("\t ignore cases with \t\t -i")

    @staticmethod
    def help_markov():
        # markov
        print("Enter the markov chain mode with \t markov [number_of_layers]")

    @staticmethod
    def help_chart():
        # chart
        print("Make charts with \t chart")
        print("\t You can omit all the switches to get every chart.")
        print("\t Chart message count with \t -m")
        print("\t Chart character count with \t -c")
        print("\t Chart message distribution over hours with \t -d")
        print("\t Chart emojis with \t -e")
        print("\t Chart emojis yearly with with \t -ey")
        print("\t Chart emoji emotions with \t -em")
        print("\t For count charting:")
        print("\t\t Specify size with \t -s [width](x[height])")
        print("\t For emoji charting:")
        print("\t\t Specify size with (height will be decided by how many emojis there are) \t -s [width]")
        print("\t\t Specify how many emojis per row with \t -r [value]")
