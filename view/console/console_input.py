import re

try:
    import readline
except:
    pass
from typing import *

from emoji import emojize
import definitions


class ConsoleCommand:
    def __init__(self, names: [str], function_to_execute: Callable,
                 help_function: Callable[[], None] = None,
                 auto_complete: Callable[[List[AnyStr], AnyStr], List[AnyStr]] = None,
                 main_alias: str = None):
        """A command used in the ConsoleInput
        :param names: Aliases for the command
        :param function_to_execute: Takes in three parameters: console itself, switches used in command,
        other data in kwargs. Should handle the command
        :param help_function: Takes in no parameters and should handle writing out the help of the functions
        :param auto_complete: An autocomplete function for the word. Takes in the switches that are before current word
        and the current word being completed, and should return a list of words which are possible candidates for auto
        completion.
        :param main_alias: The alias that should be used for auto complete. If this is set to None then the first name
        will be used instead
        """
        if len(names) is 0:
            raise ValueError("There needs to be at least one name given to the command!")

        self.names = names
        self.function_to_execute = function_to_execute
        self.help_function = help_function
        self.auto_complete = auto_complete
        self._main_alias = main_alias

    def main_alias(self) -> str:
        """The full name of the command. Can be set by passing the main_alias, otherwise it's the first name.
        """
        if self._main_alias is not None:
            return self._main_alias
        else:
            return self.names[0]

    def __eq__(self, other):
        if isinstance(other, ConsoleCommand):
            return self.names == other.names
        else:
            return False


class ConsoleInput:
    def __init__(self):
        self.command_quit = ConsoleCommand(
            ["quit", "q"],
            lambda console, switches, kwargs: console.quit(),
            lambda: ConsoleInput._print_quit_help()
        )
        self.command_help = ConsoleCommand(
            ["help", "h"],
            lambda console, switches, kwargs: console.help(switches),
            lambda: ConsoleInput._print_help_help()
        )
        self.command_write = ConsoleCommand(
            ["write", "w"],
            lambda cmd_line, switches, kwargs: cmd_line.write(kwargs, switches),
            lambda: ConsoleInput.help_write()
        )

        self._commands_dict = {}
        self.commands_all: [ConsoleCommand] = []
        self._console_running = False
        self.command_line_name = "command line"

        self.add_commands(self.command_quit, self.command_help, self.command_write)

        try:
            readline.parse_and_bind("tab: complete")
            readline.set_completer(self._auto_completer)
        except:
            pass

    def __eq__(self, other):
        if isinstance(other, ConsoleInput):
            return self.commands_all == other.commands_all and self.command_line_name == other.command_line_name
        else:
            return False

    def add_command(self, command: ConsoleCommand):
        """
        Adds a command to this command line. You can specify what aliases to use and wht function to execute when the
        command gets called.
        """
        self.commands_all.append(command)
        for name in command.names:
            self._commands_dict[name] = command

    def add_commands(self, *args: ConsoleCommand):
        """
        Adds more command to this command line. Refer to add_command()
        """
        for cmd in args:
            self.add_command(cmd)

    def print_welcome_message(self):
        print("\nWelcome to " + self.command_line_name + "!")

    def print_quit_message(self):
        print("Quitting " + self.command_line_name + "!\n")

    def get_next_command(self) -> str:
        return input("" + self.command_line_name + " : ")

    @staticmethod
    def split_command(cmd: str) -> [str]:
        # split by whitespaces except when the whitespace is in quotes
        # we need to map the tuple because of the word found is in quotes it will be in the snd of the tuple
        return list(map(lambda t: t[0] if len(t[1]) == 0 else t[1],
                        re.findall(r"(\"(.*)\"|\S+)", cmd)))

    def start_command_line(self):
        """
        Starts the command line and passes the kwargs to the process command method
        """
        self._console_running = True
        self.print_welcome_message()

        while self._console_running:
            self.process_command(self.get_next_command())

    def process_command(self, commands, **kwargs) -> {}:
        """
        Processes the given command while passing the switches and the kwargs to the function of the command
        :returns The kwargs at the end of the pipeline
        """
        pipeline = commands.split(definitions.PIPELINE_STRING)

        for command in pipeline:
            split = ConsoleInput.split_command(command.strip())

            if len(split) <= 0:
                print("No command given!")
                return

            name = split[0]
            switches = split[1:]

            command_obj: ConsoleCommand = self._commands_dict.get(name, None)
            if command_obj is None:
                print("That command could not be found!")
            else:
                new_kwargs = command_obj.function_to_execute(self, switches, kwargs)

                if new_kwargs is not None:
                    # copy the kwargs so we can keep any that has not been modified
                    for key in new_kwargs.keys():
                        kwargs[key] = new_kwargs[key]

        return kwargs

    def _get_write_string(self, kwargs, switches: [str]) -> str:
        """
        This function is used for getting the string for the write command. So override if needed
        """
        out = ""

        for key in kwargs.keys():
            out += str(key) + " : " + str(kwargs[key]) + "\n"

        return out

    def write(self, kwargs, switches: [str]):
        """
        This function is called when the user writes in the write function
        """
        out_string = self._get_write_string(kwargs, switches)

        if "-f" in switches:
            file_in_array = switches.index("-f")
            try:
                file_name = switches[file_in_array + 1]
            except IndexError:
                print("You need to provide the name of the file for write!")
                return

            with open(file_name, "w+") as file:
                file.write(out_string)
        else:
            print(out_string)

    def help(self, switches: [str]):
        """
        Prints the help for the given switches. If there are no switches given (None or length 0) then it prints help
        for all the commands
        """

        def _is_any_in_switches(values) -> bool:
            return any([x in switches for x in values])

        self.help_welcome()

        # remove '-' from the beginning of switches if there are any
        if switches is not None:
            switches = list(map(lambda s: s[1:] if s.startswith("-") else s, switches))

        for cmd in self.commands_all:
            if (switches is None or len(switches) <= 0 and "help" not in cmd.names) or _is_any_in_switches(cmd.names):
                if cmd.help_function is not None:
                    cmd.help_function()
                else:
                    print(cmd.names[0] + " has no help function!")

    def _auto_completer(self, text, state):
        """
        The function which is used for auto completion of the commands. When needed it calls the commands' auto_complete
        functions.
        """
        line = readline.get_line_buffer().split(definitions.PIPELINE_STRING)[-1]

        # all the words, we add an empty space if the command itself ends with a space, because the split
        # will get rid of that
        words = ConsoleInput.split_command(line) + ([""] if line.endswith(" ") else [])

        if len(words) > 0:
            # the word being completed
            being_completed = words[-1]
            # if word starts with " remove that
            being_completed = being_completed[1:] if being_completed.startswith("\'") else being_completed
        else:
            being_completed = ""

        candidates = None

        # we are trying to complete for command the command's name
        if len(words) == 1 or len(words) == 0:
            candidates = [cmd.names[0] for cmd in self.commands_all if being_completed in cmd.names[0]]

        # if it is a command call the child's function to get the autocomplete
        if candidates is None:
            cmd_at = 0
            while cmd_at < len(self.commands_all) and candidates is None:
                cmd = self.commands_all[cmd_at]

                # there is an autocomplete function given and the line's first word matches a command alias
                if cmd.auto_complete is not None and words[0] in cmd.names:
                    candidates = cmd.auto_complete(words[1:-1], being_completed)

                cmd_at += 1

        # there were nothing we could match
        if candidates is None:
            return None

        if len(candidates) > state:
            return candidates[state]
        else:
            return None

    def quit(self):
        """
        Quits from this console
        """
        self._console_running = False
        self.print_quit_message()

    def help_welcome(self):
        """
        Print a welcome message for the help function
        """
        pass

    @staticmethod
    def _print_quit_help():
        print("Quit with \t quit")

    @staticmethod
    def help_write():
        # write
        print("Write out anything with \t write [switches]")
        print("\t You can write to a file with \t -f [filename]")

    @staticmethod
    def _print_help_help():
        print("""
                        /}
                 _,---~-LJ,-~-._
              ,-^  '   '   '    ^:,
             :   .    '      '     :
            :     /| .   /\   '     :
           :   . //|    // \   '     :
           :     `~` /| `^~`    '     ;
           :  '     //|         '    :
           :   \-_  `~`    ,    '    :
           ;  . \.\_,--,_;^/   ,    :
            :    ^-_!^!__/^   ,    :
             :,  ,  .        ,    :   -Spookz-
               ^--_____     .   ;`
                       `^''----`
            """)
        print(emojize(":clapping_hands:") * 10)
