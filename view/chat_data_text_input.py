from data import data
from controller import chat_analyzer
import texttable as tt


command_help = "help"
command_basic_data = "basic"


def start_command_line(chat: data.Chat):
    while True:
        _process_command(_get_next_command(), chat)


def _get_next_command() -> str:
    return input("With help you can access what kind of data you can get! Type command: ")


def _process_command(cmd_str: str, chat: data.Chat):

    # only one whitespace in between -> split by that
    commands = cmd_str.replace(" ", "").strip().split(" ")

    if commands[0] == command_help:
        print("Get basic information about your chat with \t basic")
        print("\n")
    elif commands[0] == command_basic_data:
        msg_counts = chat_analyzer.message_count(chat)
        response_count = chat_analyzer.response_count(chat)
        avg_response_time_day = chat_analyzer.avg_response_time_day(chat)
        avg_response_time = chat_analyzer.avg_response_time(chat)
        avg_character_count = chat_analyzer.avg_character_count(chat)

        table = tt.Texttable()
        header = [""]
        msg_counts_text = ["Message counts"]
        response_count_text = ["Response count"]
        avg_resp_time_day_text = ["Avg. response time (🚫🌃)"]
        avg_resp_time_text = ["Avg. response time (🌃)"]
        avg_char_count_text = ["Avg. character count"]

        for participant in msg_counts.keys():
            header.append(participant)
            msg_counts_text.append(msg_counts[participant])
            response_count_text.append(response_count[participant])
            avg_resp_time_day_text.append(str(avg_response_time_day[participant] / 60) + " min")
            avg_resp_time_text.append(str(avg_response_time[participant] / 60) + " min")
            avg_char_count_text.append(avg_character_count[participant])

        table.header(header)
        table.add_row(msg_counts_text)
        table.add_row(response_count_text)
        table.add_row(avg_resp_time_day_text)
        table.add_row(avg_resp_time_text)
        table.add_row(avg_char_count_text)

        print(table.draw())
