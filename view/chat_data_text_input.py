from data import data
from view import markov_text_input
from view import console_input as con_inp
from controller import chat_analyzer
from controller import data_visualizer
import texttable as tt
import datetime
from copy import deepcopy


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
    # TODO
    command_emojis = con_inp.ConsoleCommand(
        ["emoji", "e"],
        None
    )
    commands_filter = con_inp.ConsoleCommand(
        ["filter", "f"],
        lambda cmd_line, switches, kwargs: cmd_line.filter_chat(kwargs["chat"], switches),
        lambda: ChatCommandLine.help_filter()
    )
    command_markov = con_inp.ConsoleCommand(
        ["markov", "m"],
        lambda cmd_line, switches, kwargs: cmd_line.markov_commnad_line(kwargs["chat"], switches),
        lambda: ChatCommandLine.help_markov()
    )
    command_search = con_inp.ConsoleCommand(
        ["search", "s"],
        lambda cmd_line, switches, kwargs: cmd_line.search(kwargs["chat"], switches[:-1], switches[-1]),
        lambda: ChatCommandLine.help_search()
    )
    command_write = con_inp.ConsoleCommand(
        ["write", "w"],
        lambda cmd_line, switches, kwargs: cmd_line.print_write(kwargs["chat"], switches),
        lambda: ChatCommandLine.help_write()
    )

    def __init__(self, chat: data.Chat):
        super().__init__()
        self.chat = chat

        self.add_commands(self.command_basic_data, self.command_message_count, self.command_chart, self.commands_filter,
                          self.command_markov, self.command_search, self.command_write)

    def process_command(self, commands, **kwargs):
        super().process_command(commands, chat=deepcopy(self.chat))

    def enter_markov_command_line(self, chat: data.Chat, switches: [str]):
        layer_count = 3
        try:
            if len(switches) >= 1:
                layer_count = int(switches[1])
        except ValueError:
            pass

        print("Entering markov command line!")
        markov_text_input.start_markov_command_line(chat, layer_count)

    def chart(self, chat: data.Chat, switches: [str]):
        width = 1000
        emoji_per_row = 15

        try:
            at = switches.index("-s")

            if len(switches) > at + 1:
                width = int(switches[at + 1])
        except ValueError:  # both index and parsing can come here
            pass

        try:
            at = switches.index("-r")

            if len(switches) > at + 1:
                emoji_per_row = int(switches[at + 1])
        except ValueError:
            pass

        if len(switches) == 0 or "-m" in switches:
            data_visualizer.plot_activity_msg(chat)
        if len(switches) == 0 or "-c" in switches:
            data_visualizer.plot_activity_char(chat)
        if len(switches) == 0 or "-e" in switches:
            data_visualizer.plot_emojis_per_participant(chat, width, emoji_size=width // emoji_per_row)
        if len(switches) == 0 or "-ey" in switches:
            data_visualizer.plot_emojis_per_participant_yearly(chat, width, emoji_size=width // emoji_per_row)

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
                f_year, f_month, f_day = map(int, switches[date_in_array + 1].split("."))

                from_date = datetime.date(f_year, f_month, f_day)

            # to date
            # the to date was omitted
            if len(switches) <= date_in_array + 2 or switches[date_in_array + 2] == "_" or \
                    switches[date_in_array + 2].startswith("-"):  # another switch
                to_date = datetime.date.today()
            else:
                t_year, t_month, t_day = map(int, switches[date_in_array + 2].split("."))

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

    def print_write(self, chat: data.Chat, switches: [str]):
        # here we'll store the messages we want to write out because we may want to apply filters to them
        output_messages: data.Chat = data.Chat()
        output_messages.messages = chat.messages.copy()

        # what we want to write
        output = ""
        for msg in output_messages.messages:
            output += msg.str_for_user() + "\n"

        # write to file or write to console
        try:
            file_in_array = switches.index("-f")
            file_name = switches[file_in_array + 1]

            with open(file_name, "w+") as oFile:
                oFile.write(output)
        except ValueError:  # we should write to console
            print(output)

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
            print("Nothing found that matches " + word_or_regex)
            chat.messages = []

            return chat

        # got some results. Ask whether we want to print them or not
        print("Found " + str(msg_count) + " matching messages")

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
        emojis_count = chat_analyzer.emoji_count_per_participant(chat)
        most_used_emoji = chat_analyzer.emoji_most_used_per_participant(chat)

        table = tt.Texttable()
        header = [""]
        msg_counts_text = ["Message counts"]
        response_count_text = ["Response count"]
        avg_resp_time_day_text = ["Avg. response time (no overnight)"]
        avg_resp_time_text = ["Avg. response time (with overnight🌃)"]
        char_count_text = ["Character count"]
        avg_char_count_text = ["Avg. character count"]
        emoji_count_text = ["Emoji count"]
        most_used_emoji_text = ["Most used emoji"]

        for participant in msg_counts.keys():
            header.append(participant)
            msg_counts_text.append(msg_counts.get(participant, "-"))
            response_count_text.append(response_count.get(participant, "-"))
            avg_resp_time_day_text.append(str(avg_response_time_day.get(participant, 0) / 60) + " min")
            avg_resp_time_text.append(str(avg_response_time.get(participant, 0) / 60) + " min")
            char_count_text.append(sum_character_count.get(participant, "-"))
            avg_char_count_text.append(avg_character_count.get(participant, "-"))
            emoji_count_text.append(emojis_count.get(participant, "-"))
            most_used_emoji_text.append(most_used_emoji.get(participant, "-"))

        table.header(header)
        table.add_row(msg_counts_text)
        table.add_row(response_count_text)
        table.add_row(avg_resp_time_day_text)
        table.add_row(avg_resp_time_text)
        table.add_row(char_count_text)
        table.add_row(avg_char_count_text)
        table.add_row(emoji_count_text)
        table.add_row(most_used_emoji_text)

        print("*************************************************************")
        print("Chatting started at " + str(between_dates[0].date()) + " ended (so far) at " + str(between_dates[1].date()))
        print(table.draw())
        print("*************************************************************")

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
    def help_write():
        # write
        print("Write out messages with \t write [switches]")
        print("\t You can write to a file with \t -f [filename]")

    @staticmethod
    def help_chart():
        # chart
        print("Make charts with \t chart")
        print("\t You can omit all the switches to get every chart.")
        print("\t Chart message count with \t -m")
        print("\t Chart character count with \t -c")
        print("\t Chart emojis with \t -e")
        print("\t Chart emojis yearly with with \t -ey")
        print("\t For emoji charting:")
        print("\t\t Specify size with (height will be decided by how many emojis there are) \t -s [width]")
        print("\t\t Specify how many emojis per row with \t -r [value]")
