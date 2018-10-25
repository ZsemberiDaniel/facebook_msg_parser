import re
from typing import Any, Callable

from emoji import emojize


class ConsoleCommand:
    def __init__(self, names: [str], function_to_execute: Callable,
                 help_function: Callable[[], None]=None):
        """

        :param names: Aliases for the command
        :param function_to_execute: Takes in three parameters: console itself, switches used in command,
                                    other data in kwargs. Should handle the command
        :param help_function: Takes in no parameters and should handle writing out the help of the functions
        """
        self.names = names
        self.function_to_execute = function_to_execute
        self.help_function = help_function


class ConsoleInput:
    command_quit = ConsoleCommand(
        ["quit", "q"],
        lambda console, switches, kwargs: console.quit(),
        lambda: ConsoleInput._print_quit_help()
    )
    command_help = ConsoleCommand(
        ["help", "h"],
        lambda console, switches, kwargs: console.help(switches),
        lambda: ConsoleInput._print_help_help()
    )
    commands_all: [ConsoleCommand] = []
    _console_running = False

    def __init__(self):
        self._commands_dict = {}

        self.add_commands(self.command_quit, self.command_help)

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

    @staticmethod
    def get_next_command(prompt="Type command: ") -> str:
        return input(prompt)

    @staticmethod
    def split_command(cmd: str) -> [str]:
        # split by whitespaces except when the whitespace is in quotes
        # we need to map the tuple because of the word found is in quotes it will be in the snd of the tuple
        return list(map(lambda t: t[0] if len(t[1]) == 0 else t[1],
                        re.findall(r"(\"(.*)\"|\S+)", cmd.strip())))

    def start_command_line(self, **kwargs):
        """
        Starts the command line and passes the kwargs to the process command method
        """
        self._console_running = True

        while self._console_running:
            self.process_command(ConsoleInput.get_next_command(), kwargs=kwargs)

    def process_command(self, commands, **kwargs):
        """
        Processes the given command while passing the switches and the kwargs to the function of the command
        """
        pipeline = commands.split("||")

        for command in pipeline:
            split = ConsoleInput.split_command(command)
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

    def help(self, switches: [str]):
        """
        Prints the help for the given switches. If there are no switches given (None or length 0) then it prints help
        for all the commands
        """
        def _is_any_in_switches(values) -> bool:
            return any([x in switches for x in values])

        # remove - from the beginning of switches if there are any
        if switches is not None:
            switches = list(map(lambda s: s[1:] if s.startswith("-") else s, switches))

        for cmd in self.commands_all:
            if (switches is None or len(switches) <= 0 and "help" not in cmd.names) or _is_any_in_switches(cmd.names):
                cmd.help_function()

    def quit(self):
        """
        Quits from this console
        """
        self._console_running = False

    @staticmethod
    def _print_quit_help():
        print("Quit with \t quit")

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
