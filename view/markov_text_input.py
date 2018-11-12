from data import data
from controller import chat_analyzer
from controller.markov import markov_chain
from view.console import console_input
from colorama import Fore


class ChatMarkovData:
    def __init__(self, chat: data.Chat, layer_count=2):
        self.chat = chat
        self.layer_count = layer_count
        self.for_participants: {str: markov_chain.MarkovChain} = {}
        self.for_all = markov_chain.MarkovChain(chat.messages, layer_count)

        for participant in chat.participants:
            msgs = chat_analyzer.get_messages_only_by(chat, [participant.name]).messages
            self.for_participants[participant.name] = markov_chain.MarkovChain(msgs, layer_count)


class MarkovCommandLine(console_input.ConsoleInput):
    def __init__(self, chat: data.Chat, layer_count: int):
        super().__init__()
        self.command_words = console_input.ConsoleCommand(
            ["word", "words", "w"],
            lambda cmd_line, switches, kwargs: cmd_line.words(switches),
            lambda: MarkovCommandLine.help_words(),
            lambda switches, word: self.auto_complete_words(switches, word)
        )
        self.command_layer = console_input.ConsoleCommand(
            ["layer", "la", "l"],
            lambda cmd_line, switches, kwargs: cmd_line.layer_change(switches),
            lambda: MarkovCommandLine.help_layer()
        )

        self.command_line_name = "markov command line"
        self.layer_count = layer_count
        self.markov_data = ChatMarkovData(chat, layer_count)

        self.add_commands(self.command_words, self.command_layer)

    def layer_change(self, switches: [str]):
        try:
            new_layer = int(switches[-1])
        except ValueError:
            print(Fore.RED + "You need to give a number as the layer count" + Fore.RESET)
            return {}

        if new_layer < 1:
            print(Fore.RED + "You need to give a positive number as the layer count!" + Fore.RESET)
            return {}

        self.layer_count = new_layer
        self.markov_data = ChatMarkovData(self.markov_data.chat, self.layer_count)
        print(Fore.GREEN + "Successfully changed layer count!" + Fore.RESET)

    def words(self, switches: [str]):
        if len(switches) > 0:
            try:
                count = int(switches[-1])
            except ValueError:
                print(Fore.RED + "The provided count for words needs to be an integer!" + Fore.RESET)
                return {}
        else:
            print(Fore.RED + "You need to provide a count for the words command!" + Fore.RESET)
            return {}

        if "-a" in switches:
            words = self.markov_data.for_all.get_words(count)

            # there is a chance that no one talked, or talked only onw word, and the dictionary could not be built
            return {"words_per_participant": {"All participants": 0 if words is None else words}}

        if "-p" in switches:
            part_at = switches.index("-p")

            # doesn't have the necessary value after -p
            if len(switches) <= part_at:
                print(Fore.RED + "You need to provide parameters for -p in the word command!" + Fore.RESET)
                return {}

            def contain_participant(name):
                """
                Returns whether the given name is in the list or is a substring of the participants of the markov_data.
                If it is in there then it returns the name. Otherwise return None
                """
                for participant in self.markov_data.chat.participants:
                    if participant.substring_in_ascii(name):
                        return participant.name

                return None

            # returns a list of all the participants' real names that are given as a parameter for this command
            for_participants = list(filter(lambda v: v is not None,
                                           map(lambda name: contain_participant(name),
                                               switches[part_at + 1].split(","))
                                           ))
        else:
            for_participants = map(lambda p: p.name, self.markov_data.chat.participants)

        out_words = {}
        for participant in for_participants:
            words = self.markov_data.for_participants[participant].get_words(count)
            if words is None:
                print(Fore.RED + "No words could be generated for " + participant + ", maybe (s)he had no messages?")
                out_words[participant] = []
            else:
                out_words[participant] = words

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

    def auto_complete_words(self, switches_before: [str], word: str) -> [str]:
        if word.startswith("-"):
            return [] if "-a" in switches_before else ["a", "p"]
        elif len(switches_before) == 0:
            return ["-p", "-a"]
        else:
            if switches_before[-1] == "-p":
                # the one the user is currently typing (they are separated by ,)
                curr_participant = word.split(",")[-1]

                # we return the lower case ascii name if the given participant matches that
                return [p.to_ascii_lowe_case().split(" ")[0] for p in self.markov_data.chat.participants
                        if p.substring_in_ascii(curr_participant)]
            elif "-a" in switches_before:
                return []
            else:
                return ["-p", "-a"]

    def _print_help_help(self):
        print("""███████████▓▓▓▓▓▓▓▓▒░░░░░▒▒░░░░░░░▓█████\n██████████▓▓▓▓▓▓▓▓▒░░░░░▒▒▒░░░░░░░░▓████\n█████████▓▓▓▓▓▓▓▓▒░░░░░░▒▒▒░░░░░░░░░▓███\n████████▓▓▓▓▓▓▓▓▒░░░░░░░▒▒▒░░░░░░░░░░███\n███████▓▓▓▓▓▓▓▓▒░░▒▓░░░░░░░░░░░░░░░░░███\n██████▓▓▓▓▓▓▓▓▒░▓████░░░░░▒▓░░░░░░░░░███\n█████▓▒▓▓▓▓▓▒░▒█████▓░░░░▓██▓░░░░░░░▒███\n████▓▒▓▒▒▒░░▒███████░░░░▒████░░░░░░░░███\n███▓▒▒▒░░▒▓████████▒░░░░▓████▒░░░░░░▒███\n██▓▒▒░░▒██████████▓░░░░░▓█████░░░░░░░███\n██▓▒░░███████████▓░░░░░░▒█████▓░░░░░░███\n██▓▒░▒██████████▓▒▒▒░░░░░██████▒░░░░░▓██\n██▓▒░░▒███████▓▒▒▒▒▒░░░░░▓██████▓░░░░▒██\n███▒░░░░▒▒▒▒▒▒▒▒▒▒▒▒░░░░░░███████▓░░░▓██\n███▓░░░░░▒▒▒▓▓▒▒▒▒░░░░░░░░░██████▓░░░███\n████▓▒▒▒▒▓▓▓▓▓▓▒▒▓██▒░░░░░░░▓███▓░░░░███\n██████████▓▓▓▓▒▒█████▓░░░░░░░░░░░░░░████\n█████████▓▓▓▓▒▒░▓█▓▓██░░░░░░░░░░░░░█████\n███████▓▓▓▓▓▒▒▒░░░░░░▒░░░░░░░░░░░░██████\n██████▓▓▓▓▓▓▒▒░░░░░░░░░░░░░░░░▒▓████████\n██████▓▓▓▓▓▒▒▒░░░░░░░░░░░░░░░▓██████████\n██████▓▓▓▓▒▒██████▒░░░░░░░░░▓███████████\n██████▓▓▓▒▒█████████▒░░░░░░▓████████████\n██████▓▓▒▒███████████░░░░░▒█████████████\n██████▓▓░████████████░░░░▒██████████████\n██████▓░░████████████░░░░███████████████\n██████▓░▓███████████▒░░░████████████████\n██████▓░███████████▓░░░█████████████████\n██████▓░███████████░░░██████████████████\n██████▓▒██████████░░░███████████████████\n██████▒▒█████████▒░▓████████████████████\n██████░▒████████▓░██████████████████████\n██████░▓████████░███████████████████████\n██████░████████░▒███████████████████████\n█████▓░███████▒░████████████████████████\n█████▒░███████░▓████████████████████████\n█████░▒██████░░█████████████████████████\n█████░▒█████▓░██████████████████████████\n█████░▓█████░▒██████████████████████████\n█████░▓████▒░███████████████████████████\n█████░▓███▓░▓███████████████████████████\n██████░▓▓▒░▓████████████████████████████\n███████▒░▒██████████████████████████████\n████████████████████████████████████████\n████████████████████████████████████████""")
