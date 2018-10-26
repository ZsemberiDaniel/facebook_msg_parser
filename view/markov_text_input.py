from data import data
from controller import chat_analyzer
from controller.markov import markov_chain
from view import console_input
from colorama import Fore


class ChatMarkovData:
    def __init__(self, chat: data.Chat, layer_count=3):
        self.chat = chat
        self.layer_count = layer_count
        self.for_participants: {str: markov_chain.MarkovChain} = {}
        self.for_all = markov_chain.MarkovChain(chat.messages, layer_count)

        for participant in chat.participants:
            msgs = chat_analyzer.get_messages_only_by(chat, [participant.name]).messages
            self.for_participants[participant.name] = markov_chain.MarkovChain(msgs, layer_count)


class MarkovCommandLine(console_input.ConsoleInput):
    command_words = console_input.ConsoleCommand(
        ["word", "words", "w"],
        lambda cmd_line, switches, kwargs: cmd_line.words(switches),
        lambda: MarkovCommandLine.help_words()
    )
    command_layer = console_input.ConsoleCommand(
        ["layer", "la", "l"],
        lambda cmd_line, switches, kwargs: cmd_line.layer_change(switches),
        lambda: MarkovCommandLine.help_layer()
    )

    def __init__(self, chat: data.Chat, layer_count: int):
        super().__init__()
        self.command_line_name = "markov command line"
        self.layer_count = layer_count
        self.markov_data = ChatMarkovData(chat, layer_count)

        self.add_commands(self.command_words, self.command_layer)

    def layer_change(self, switches: [str]):
        try:
            new_layer = int(switches[-1])
        except ValueError:
            print(Fore.RED + "You need to give a number as the layer count" + Fore.RESET)
            return

        if new_layer < 0:
            print(Fore.RED + "You need to give a positive number as the layer count!" + Fore.RESET)
            return

        self.layer_count = new_layer
        self.markov_data = ChatMarkovData(self.markov_data.chat, self.layer_count)
        print(Fore.GREEN + "Successfully changed layer count!" + Fore.RESET)

    def words(self, switches: [str]):
        try:
            count = int(switches[-1])
        except IndexError:
            print(Fore.RED + "You need to provide a count for the words command!" + Fore.RESET)
            return

        try:
            all_at = switches.index("-a")

            # doesn't have the necessary value after -a
            if len(switches) <= all_at:
                print(Fore.RED + "You need to provide parameters for -a in the word command!" + Fore.RESET)
                return

            return {"words_per_participant": {"All participants": self.markov_data.for_all.get_words(count)}}
        except ValueError:
            pass

        try:
            part_at = switches.index("-p")

            # doesn't have the necessary value after -p
            if len(switches) <= part_at:
                print(Fore.RED + "You need to provide parameters for -p in the word command!" + Fore.RESET)
                return

            def contain_participant(name):
                """
                Returns whether the given name is in the list or is a substring of the participants of the markov_data.
                If it is in there then it returns the name. Otherwise return None
                """
                for participant in self.markov_data.chat.participants:
                    if participant.name_matches_ascii(name):
                        return participant.name

                return None

            # returns a list of all the participants' real names that are given as a parameter for this command
            for_participants = list(filter(lambda v: v is not None,
                                           map(lambda name: contain_participant(name),
                                               switches[part_at + 1].split(","))
                                           ))
        except ValueError:
            # otherwise the default is generating for all participant
            for_participants = map(lambda p: p.name, self.markov_data.chat.participants)

        out_words = {}
        for participant in for_participants:
            out_words[participant] = self.markov_data.for_participants[participant].get_words(count)

        return {"words_per_participant": out_words}

    def _get_write_string(self, kwargs, switches: [str]):
        if "words_per_participant" in kwargs:
            words_per_participant = kwargs["words_per_participant"]
            out_string = ""

            for participant in words_per_participant:
                out_string += participant + "\n"

                words = words_per_participant[participant]
                for i in range(len(words)):
                    if i == 0 or words[i - 1] in ".!?":
                        words[i] = words[i][0].upper() + words[i][1:]

                    if words[i] in ".!?,;:-":
                        out_string += words[i]
                    else:
                        out_string += " " + words[i]

                out_string += "\n"

            return out_string
        else:
            return super()._get_write_string(kwargs, switches)

    @staticmethod
    def help_layer():
        print("""You can specify a new layer count with \t layer [count]""")

    @staticmethod
    def help_words():
        print("""You can generate words per participant with \t words (params) [count]
        \t You can specify for which participant(s) to generate the words with \t -p participant1(,part2)(,part3)(...)
        \t You can get words from the whole chat (involving all participants) with \t -a
        \t\t If participants are specified along with then still all participants will be included""")

    def _print_help_help(self):
        print("""███████████▓▓▓▓▓▓▓▓▒░░░░░▒▒░░░░░░░▓█████\n██████████▓▓▓▓▓▓▓▓▒░░░░░▒▒▒░░░░░░░░▓████\n█████████▓▓▓▓▓▓▓▓▒░░░░░░▒▒▒░░░░░░░░░▓███\n████████▓▓▓▓▓▓▓▓▒░░░░░░░▒▒▒░░░░░░░░░░███\n███████▓▓▓▓▓▓▓▓▒░░▒▓░░░░░░░░░░░░░░░░░███\n██████▓▓▓▓▓▓▓▓▒░▓████░░░░░▒▓░░░░░░░░░███\n█████▓▒▓▓▓▓▓▒░▒█████▓░░░░▓██▓░░░░░░░▒███\n████▓▒▓▒▒▒░░▒███████░░░░▒████░░░░░░░░███\n███▓▒▒▒░░▒▓████████▒░░░░▓████▒░░░░░░▒███\n██▓▒▒░░▒██████████▓░░░░░▓█████░░░░░░░███\n██▓▒░░███████████▓░░░░░░▒█████▓░░░░░░███\n██▓▒░▒██████████▓▒▒▒░░░░░██████▒░░░░░▓██\n██▓▒░░▒███████▓▒▒▒▒▒░░░░░▓██████▓░░░░▒██\n███▒░░░░▒▒▒▒▒▒▒▒▒▒▒▒░░░░░░███████▓░░░▓██\n███▓░░░░░▒▒▒▓▓▒▒▒▒░░░░░░░░░██████▓░░░███\n████▓▒▒▒▒▓▓▓▓▓▓▒▒▓██▒░░░░░░░▓███▓░░░░███\n██████████▓▓▓▓▒▒█████▓░░░░░░░░░░░░░░████\n█████████▓▓▓▓▒▒░▓█▓▓██░░░░░░░░░░░░░█████\n███████▓▓▓▓▓▒▒▒░░░░░░▒░░░░░░░░░░░░██████\n██████▓▓▓▓▓▓▒▒░░░░░░░░░░░░░░░░▒▓████████\n██████▓▓▓▓▓▒▒▒░░░░░░░░░░░░░░░▓██████████\n██████▓▓▓▓▒▒██████▒░░░░░░░░░▓███████████\n██████▓▓▓▒▒█████████▒░░░░░░▓████████████\n██████▓▓▒▒███████████░░░░░▒█████████████\n██████▓▓░████████████░░░░▒██████████████\n██████▓░░████████████░░░░███████████████\n██████▓░▓███████████▒░░░████████████████\n██████▓░███████████▓░░░█████████████████\n██████▓░███████████░░░██████████████████\n██████▓▒██████████░░░███████████████████\n██████▒▒█████████▒░▓████████████████████\n██████░▒████████▓░██████████████████████\n██████░▓████████░███████████████████████\n██████░████████░▒███████████████████████\n█████▓░███████▒░████████████████████████\n█████▒░███████░▓████████████████████████\n█████░▒██████░░█████████████████████████\n█████░▒█████▓░██████████████████████████\n█████░▓█████░▒██████████████████████████\n█████░▓████▒░███████████████████████████\n█████░▓███▓░▓███████████████████████████\n██████░▓▓▒░▓████████████████████████████\n███████▒░▒██████████████████████████████\n████████████████████████████████████████\n████████████████████████████████████████""")
