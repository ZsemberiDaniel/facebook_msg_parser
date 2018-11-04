from data import data
from view import markov_text_input
from view import emoji_analyzer_text_input
from view import console_input as con_inp
from controller import chat_analyzer
from controller import data_visualizer
from definitions import console_manager
from pyfiglet import figlet_format
from misc.texttable_misc import get_string_wrapped
import texttable as tt
import datetime
import unicodedata
from copy import deepcopy
from colorama import Fore


class ChatCommandLine(con_inp.ConsoleInput):
    def __init__(self, chat: data.Chat):
        super().__init__()

        self.command_basic_data = con_inp.ConsoleCommand(
            ["basic", "b"],
            lambda cmd_line, switches, kwargs: cmd_line.print_basic(kwargs["chat"]),
            lambda: ChatCommandLine.help_basic()
        )
        self.command_message_count = con_inp.ConsoleCommand(
            ["count"],
            lambda cmd_line, switches, kwargs: cmd_line.print_message_count(kwargs["chat"], switches),
            lambda: ChatCommandLine.help_msg_count()
        )
        self.command_chart = con_inp.ConsoleCommand(
            ["chart", "c"],
            lambda cmd_line, switches, kwargs: cmd_line.chart(kwargs["chat"], switches),
            lambda: ChatCommandLine.help_chart()
        )
        self.command_emojis = con_inp.ConsoleCommand(
            ["emoji", "e"],
            lambda cmd_line, switches, kwargs: cmd_line.only_emojis(kwargs["chat"], switches),
            lambda: ChatCommandLine.help_emoji()
        )
        self.commands_filter = con_inp.ConsoleCommand(
            ["filter", "f"],
            lambda cmd_line, switches, kwargs: cmd_line.filter_chat(kwargs["chat"], switches),
            lambda: ChatCommandLine.help_filter()
        )
        self.command_markov = con_inp.ConsoleCommand(
            ["markov", "m"],
            lambda cmd_line, switches, kwargs: cmd_line.enter_markov_command_line(kwargs["chat"], switches),
            lambda: ChatCommandLine.help_markov()
        )
        self.command_search = con_inp.ConsoleCommand(
            ["search", "s"],
            lambda cmd_line, switches, kwargs: cmd_line.search(kwargs["chat"], switches),
            lambda: ChatCommandLine.help_search()
        )

        self.chat = chat
        self.command_line_name = "chat command line"

        self.add_commands(self.command_basic_data, self.command_message_count, self.command_chart, self.commands_filter,
                          self.command_markov, self.command_search, self.command_emojis)

    def process_command(self, commands, **kwargs):
        return super().process_command(commands, chat=deepcopy(self.chat))

    def print_welcome_message(self):
        print("\n" + figlet_format(unicodedata.normalize("NFD", self.chat.name).encode("ASCII", "ignore")
                                   .decode("UTF-8"), font="mini"))

    def only_emojis(self, chat: data.Chat, switches: [str]):
        new_chat = chat

        # analyzing emoji usage
        if "-a" in switches:
            console_manager.add_console(emoji_analyzer_text_input.EmojiAnalyzerConsole(new_chat))
            return

        if "-onlyem" in switches or "-o" in switches:
            new_chat.messages = chat_analyzer.emoji_messages(chat)
        else:
            new_chat.messages = chat_analyzer.emoji_whole_messages(chat)

        return {"chat": new_chat}

    def enter_markov_command_line(self, chat: data.Chat, switches: [str]):
        layer_count = 2
        try:
            if len(switches) >= 1:
                layer_count = int(switches[-1])
        except ValueError:
            print(Fore.RED + "Layer count needs to be a number in markov command!" + Fore.RESET)

        console_manager.add_console(markov_text_input.MarkovCommandLine(chat, layer_count))

    def chart(self, chat: data.Chat, switches: [str]):
        # try out with: chart -m -c -s 2000x1000 -d -s 1000x3000 -e -ey -s 500x500 -em -s 1000x2000 -sa 1200x600
        # DATA
        width = 1000
        height = 600
        emoji_per_row = 15
        wh_defined_by_user = False

        # Recommended sizes for the charts. If no size is given by user theses will be used
        chart_data = {
            "-d": (1500, 1000),
            "-m": (1500, 1000),
            "-c": (1500, 1000),
            "-e": 1500,
            "-ey": 1500,
            "-em": (1000, 1500)
        }

        # what chart switch sizes does the user override?
        user_override_size: {str: (int, int)} = {}

        # what to execute when a switch is given
        execute_for_switch = {
            "-d": lambda width, height: data_visualizer.plot_message_distribution(chat, size=(width, height)),
            "-m": lambda width, height: data_visualizer.plot_activity_msg(chat, size=(width, height)),
            "-c": lambda width, height: data_visualizer.plot_activity_char(chat, size=(width, height)),
            "-e": lambda width, height: data_visualizer.plot_emojis_per_participant(chat, width,
                                                                                    emoji_count_per_row=emoji_per_row),
            "-ey": lambda width, height: data_visualizer.plot_emojis_per_participant_yearly(
                chat, width, emoji_count_per_row=emoji_per_row
            ),
            "-em": lambda width, height: data_visualizer.plot_emoji_emotions_monthly(chat, size=(width, height))
        }

        def split_size(size_str: str) -> (int, int):
            """
            Splits a given string to width and height by splitting at 'x'. If there is no x in the string but
            is still a number the height will be calculated. May throw ValueError
            """
            split = size_str.split("x")

            if len(split) > 1:  # [width]x[height]
                width = int(split[0])
                height = int(split[1])
            else:
                width = int(split[0])
                height = int(width * (2/3))

            return width, height

        # ALGORITHM
        # this defines the size for all charts
        if "-sa" in switches:
            at = switches.index("-sa")

            try:
                if at + 1 < len(switches):
                    width, height = split_size(switches[at + 1])

                    wh_defined_by_user = True
                else:
                    print(Fore.RED + "There is no size given after -sa switch!" + Fore.RESET)

                    return {"chat": chat}
            except ValueError:
                print(Fore.RED + "Integer values need to be provided for the -sa switch in chart!" + Fore.RESET)

                return {"chat": chat}

        # this can override a size for a chart if it is after a charting switch
        if "-s" in switches:
            # we get all the indices where -s can be found
            indices = list(filter(lambda i: switches[i] == "-s", range(len(switches))))

            for i in indices:
                # there can be no chart switch before this
                if i <= 0:
                    print(Fore.RED + "You need to apply -s to a charting switch (by adding -s after one)!" + Fore.RESET)

                    return {"chat": chat}

                before_switch = switches[i - 1]
                # the switch before the -s one is not a chart switch
                if before_switch not in execute_for_switch:
                    print(Fore.RED + "You need to apply -s to a charting switch (by adding -s after one)!" + Fore.RESET)

                    return {"chat": chat}

                # there is no size after -s switch
                if i + 1 >= len(switches):
                    print(Fore.RED + "You need to specify a size after -s!" + Fore.RESET)

                    return {"chat": chat}

                # we can safely split the size now, but we still need to check for parsing errors
                try:
                    user_override_size[before_switch] = split_size(switches[i + 1])
                except ValueError:
                    print(Fore.RED + "The size after -s is not an integer!" + Fore.RESET)

                    return {"chat": chat}

        # emoji per row count
        if "-r" in switches:
            at = switches.index("-r")

            if len(switches) > at + 1:
                try:
                    emoji_per_row = int(switches[at + 1])
                except ValueError:
                    print(Fore.RED + "The count after -r is not an integer!" + Fore.RESET)

                    return {"chat": chat}

        # if no switches were given then we need to plot everything
        do_all_plot = len(switches) == 0

        # go through all switches and check for ones that are chart switches
        for switch in switches:
            if do_all_plot or switch in execute_for_switch:
                # user may have overridden -sa for this chart
                overridden_size = user_override_size.get(switch, None)

                if overridden_size is not None:  # size was overridden
                    new_width, new_height = overridden_size
                    execute_for_switch[switch](new_width, new_height)
                    continue

                # width/height needs to be defined by the developer, of course it has to be the user doesn't know what's
                # really good for them, only I, the mighty coder, am able to know that.
                if not wh_defined_by_user:
                    size = chart_data[switch]
                    # size can either be an int or a tuple, based on that we need to pass it to the lambdas
                    execute_for_switch[switch](size if isinstance(size, int) else size[0],
                                               0 if isinstance(size, int) else size[1])
                else:  # user defined width and height
                    execute_for_switch[switch](width, height)

                # success message for saving the chart to file
                print(Fore.LIGHTGREEN_EX + "Chart(s) for " + switch + " is done..." + Fore.RESET)

        return {"chat": chat}

    def print_message_count(self, chat: data.Chat, switches: [str]):
        out = ""

        if "-p" in switches:
            for participant in chat.participants:
                participant_msg = list(filter(lambda msg: msg.sender == participant.name, chat.messages))

                out += participant.name + ": " + str(len(participant_msg)) + "\n"
        else:
            out += "Message count: " + str(len(chat.messages))

        return {"output-string": out, "chat": None}

    def filter_chat(self, chat: data.Chat, switches: [str]) -> {}:
        # FILTER DATE
        if "-d" in switches:
            date_in_array = switches.index("-d")

            # from date
            if len(switches) <= date_in_array + 1 or switches[date_in_array + 1] == "_":  # the from date was omitted
                from_date = datetime.date(1990, 1, 1)
            else:
                try:
                    f_year, f_month, f_day = map(int, switches[date_in_array + 1].split("."))
                except ValueError:
                    print(Fore.RED + "Starting month should be in format YYYY.MM.DD!" + Fore.RESET)

                    chat.messages = []
                    return {"chat": chat}

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

                    chat.messages = []
                    return {"chat": chat}

                to_date = datetime.date(t_year, t_month, t_day)

            chat.messages = chat_analyzer.get_from_to_date(chat, from_date, to_date)

        # FILTER
        if "-p" in switches:
            participant_in_array = switches.index("-p")

            # if there was no parameter given after the -p switch then there are no participants to filter ->
            # will result in []. If there were names given split them by ,
            to_filter_participants = [] if len(switches) <= participant_in_array + 1 else \
                switches[participant_in_array + 1].split(",")

            if len(to_filter_participants) > 0:
                chat = chat_analyzer.get_messages_only_by(chat, to_filter_participants)

        return {"chat": chat}

    def _get_write_string(self, kwargs, switches: [str]):
        chat: data.Chat = kwargs.get("chat", None)

        if chat is not None:
            # what we want to write
            output = ""
            for msg in chat.messages:
                output += msg.str_for_user() + "\n"

            return output
        elif "output-string" in kwargs:
            return kwargs["output-string"]
        else:
            return super()._get_write_string(kwargs, switches)

    def search(self, chat: data.Chat, switches: [str]) -> {}:
        if len(switches) > 0:
            word_or_regex = switches[-1]
        else:
            print(Fore.RED + "There needs to be a search query for the search command!" + Fore.RESET)

            return {"chat": chat}

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

            return {"chat": chat}

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

        out = ""
        if between_dates[0] is not None and between_dates[1] is not None:
            out += "Chatting started at " + str(between_dates[0].date()) + " ended (so far) at " +\
                   str(between_dates[1].date()) + "\n"
        out += get_string_wrapped(table, 150, 1)

        return {"output-string": out}

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
        print("\t\t If no to date is given (or _ is used) then today will be the to date.")
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
        print("""Make charts with \t chart
        \t You can omit all the switches to get every chart.
        \t Chart message count with \t -m
        \t Chart character count with \t -c
        \t Chart message distribution over hours with \t -d
        \t Chart emojis with \t -e
        \t Chart emojis yearly with with \t -ey
        \t Chart emoji emotions with \t -em
        \t Sizing:
        \t\t You can specify sizes for all charts with \t -sa [width](x[height])
        \t\t\t For emoji and emoji yearly charting height will be ignored. If only width is given then that will be used to calculate the height.
        \t\t You can specify size for one chart, overriding the -sa switch by adding a -s switch after the chart's switch.
        \t\t\t Example: chart -m -c -em -s 1000x2000 -sa 2000x1000
        \t\t\t Here the -m and -c will be 2000x1000 but the -em will be 1000x2000
        \t For emoji charting:
        \t\t Specify how many emojis per row with \t -r [value]""")
