from data import data
from controller import chat_analyzer
import texttable as tt
import datetime


command_help = ["help", "h"]
command_basic_data = ["basic", "b"]
command_find = ["find", "f"]
command_write = ["write", "w"]
command_quit = ["quit", "q"]


def start_command_line(chat: data.Chat):
    while _process_command(_get_next_command(), chat):
        pass


def _get_next_command() -> str:
    return input("Type command: ")


def _process_command(cmd_str: str, chat: data.Chat) -> bool:
    # only one whitespace in between -> split by that
    commands = cmd_str.strip().split(" ")

    if commands[0] in command_help:
        print_help()
    elif commands[0] in command_quit:
        return False
    elif commands[0] in command_find:
        print_search(chat, commands[1:-1], commands[-1])
    elif commands[0] in command_write:
        print_write(chat, commands[1:])
    elif commands[0] in command_basic_data:
        print_basic(chat)

    return True


def print_write(chat: data.Chat, switches: [str]):
    # here we'll store the messages we want to write out because we may want to apply filters to them
    output_messages: data.Chat = data.Chat()
    output_messages.messages = chat.messages.copy()

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
        if len(switches) <= date_in_array + 2 or switches[date_in_array + 2] == "_" or\
                switches[date_in_array + 2].startswith("-"):  # another switch
            to_date = datetime.date.today()
        else:
            t_year, t_month, t_day = map(int, switches[date_in_array + 2].split("."))

            to_date = datetime.date(t_year, t_month, t_day)

        output_messages.messages = chat_analyzer.get_from_to_date(output_messages, from_date, to_date)
    except ValueError:
        pass

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


def print_search(chat: data.Chat, switches: [str], word_or_regex: str):
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

        return

    # got some results. Ask whether we want to print them or not
    print("Found " + str(msg_count) + " matching messages")

    response = input("Print them? (y/n)").lower()
    if response == "y" or response == "yes":
        for participant in found_messages:
            print(participant + ":")

            for msg in found_messages[participant]:
                print("\t" + msg.str_for_user())


def print_help():
    print("Get basic information about your chat with \t basic")

    print("Search in messages with \t find [switches] [what to find]")
    print("\t add a keyword with (default behaviour) \t -w")
    print("\t match whole world in -w mode \t\t -h")
    print("\t add a regex with \t\t -r")
    print("\t ignore cases with \t\t -i")

    print("Write out messages with \t write [switches]")
    print("\t You can define a from and to date with \t -d [year.month.day] [year.month.day]")
    print("\t\t If no to date is given then today will be the to date.")
    print("\t\t You can omit the from date with '_'. If no from date is given then it will be written out from" +
          "the start of conversation.")
    print("\t You can write to a file with \t -f [filename]")

    print("Quit with \t quit")


def print_basic(chat: data.Chat):
    msg_counts = chat_analyzer.message_count(chat)
    response_count = chat_analyzer.response_count(chat)
    avg_response_time_day = chat_analyzer.avg_response_time_no_overnight(chat)
    avg_response_time = chat_analyzer.avg_response_time(chat)
    sum_character_count = chat_analyzer.character_count(chat)
    avg_character_count = chat_analyzer.avg_character_count(chat)

    table = tt.Texttable()
    header = [""]
    msg_counts_text = ["Message counts"]
    response_count_text = ["Response count"]
    avg_resp_time_day_text = ["Avg. response time (no overnight)"]
    avg_resp_time_text = ["Avg. response time (with overnight🌃)"]
    char_count_text = ["Character count"]
    avg_char_count_text = ["Avg. character count"]

    for participant in msg_counts.keys():
        header.append(participant)
        msg_counts_text.append(msg_counts[participant])
        response_count_text.append(response_count[participant])
        avg_resp_time_day_text.append(str(avg_response_time_day[participant] / 60) + " min")
        avg_resp_time_text.append(str(avg_response_time[participant] / 60) + " min")
        char_count_text.append(sum_character_count[participant])
        avg_char_count_text.append(avg_character_count[participant])

    table.header(header)
    table.add_row(msg_counts_text)
    table.add_row(response_count_text)
    table.add_row(avg_resp_time_day_text)
    table.add_row(avg_resp_time_text)
    table.add_row(char_count_text)
    table.add_row(avg_char_count_text)

    print(table.draw())
