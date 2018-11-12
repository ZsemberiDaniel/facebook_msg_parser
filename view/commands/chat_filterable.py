from datetime import date
from colorama import Fore
from data import data

from controller import chat_analyzer
from view.console.console_input import ConsoleCommand


command_filter = ConsoleCommand(
    ["filter", "f"],
    lambda cmd_line, switches, kwargs: filter_chat(kwargs["chat"], switches),
    lambda: help_filter(),
    lambda switches, word: auto_complete_filter(self.chat, switches, word)
)


def filter_chat(chat: data.Chat, switches: [str]) -> {}:
    # FILTER DATE
    if "-d" in switches:
        date_in_array = switches.index("-d")

        # from date
        if len(switches) <= date_in_array + 1 or switches[date_in_array + 1] == "_":  # the from date was omitted
            from_date = date(1990, 1, 1)
        else:
            try:
                f_year, f_month, f_day = map(int, switches[date_in_array + 1].split("."))
            except ValueError:
                print(Fore.RED + "Starting month should be in format YYYY.MM.DD!" + Fore.RESET)

                chat.messages = []
                return {"chat": chat}

            from_date = date(f_year, f_month, f_day)

        # to date
        # the to date was omitted
        if len(switches) <= date_in_array + 2 or switches[date_in_array + 2] == "_" or \
                switches[date_in_array + 2].startswith("-"):  # another switch
            to_date = date.today()
        else:
            try:
                t_year, t_month, t_day = map(int, switches[date_in_array + 2].split("."))
            except ValueError:
                print(Fore.RED + "Ending date should be in format YYYY.MM.DD!" + Fore.RESET)

                chat.messages = []
                return {"chat": chat}

            to_date = date(t_year, t_month, t_day)

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


def auto_complete_filter(chat: data.Chat, switches_before: [str], word: str) -> [str]:
    switches = ["-d", "-p"]

    if word.startswith("-"):
        # return ones that have not been before and without the '-' because that would get autocompleted
        # again
        return [switch[1:] for switch in switches if switch not in switches_before]
    elif len(switches_before) == 0:
        # return ones that have not been before
        return [switch for switch in switches if switch not in switches_before]
    elif len(switches_before) > 0:  # we can have switches before
        # from date
        if switches_before[-1] == "-d":
            # trick the system to always print this
            return ["Need a date in format:", "YYYY.MM.DD", "or '_'"]
        # till date
        elif len(switches_before) > 1 and not switches_before[-1].startswith("-") and switches_before[-2] == "-d":
            # trick the system to always print this
            return ["Need a date in format:", "YYYY.MM.DD", "or you can leave it empty and have another switch"] + \
                   [switch for switch in switches if switch not in switches_before]
        elif switches_before[-1] == "-p":
            # the one the user is currently typing (they are separated by ,)
            curr_participant = word.split(",")[-1]

            # we return the lower case ascii name if the given participant matches that
            return [p.to_ascii_lowe_case().split(" ")[0] for p in chat.participants
                    if p.substring_in_ascii(curr_participant)]
        else:  # we can have another switch here
            return [switch for switch in switches if switch not in switches_before]
    else:
        return []
