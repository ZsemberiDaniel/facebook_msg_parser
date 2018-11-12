import readline
from threading import Thread, RLock

from view.console.console_input import ConsoleInput
from typing import Union


class ConsoleManager(Thread):
    def __init__(self, quit_when_no_consoles_left=False):
        super().__init__(group=None, target=self._run_command_manager, name="ConsoleManager")
        # all the consoles
        self._consoles_lock = RLock()
        self._consoles: {int: ConsoleInput} = {}
        self._max_index = -1
        self._curr_console_index = None
        self._should_be_running = True
        self._quit_when_no_consoles_left = quit_when_no_consoles_left

    @property
    def _curr_console(self) -> Union[ConsoleInput, None]:
        """
        Returns the current console on top. If there is no console on top, returns None
        """
        with self._consoles_lock:
            if self._curr_console_index is None:
                return None
            else:
                return self._consoles[self._curr_console_index]

    @property
    def _is_there_console_on_top(self) -> bool:
        """
        Returns whether there is a console on top or not
        """
        with self._consoles_lock:
            return self._curr_console_index is not None

    def add_console(self, console: ConsoleInput):
        """
        Add a console to the top of this manager and switch to that console
        """
        with self._consoles_lock:
            def new_quit(_, __, ___):
                self.pop_console()

            # add to the quit command a notification to this manager
            console.command_quit.function_to_execute = new_quit

            self._max_index += 1
            self._consoles[self._max_index] = console

            self._switch_to_index(self._max_index)

    def pop_console(self) -> ConsoleInput:
        """
        Pops the current console then switches to the highest index one.
        Then returns the console that was popped.
        """
        with self._consoles_lock:
            # search for the newest max index if we are popping the one with the max index
            if self._curr_console_index == self._max_index:
                new_max_index = -1
                for console_id in self._consoles:
                    if new_max_index < console_id < self._max_index:
                        new_max_index = console_id

                # set the new max index
                self._max_index = new_max_index

            to_pop_index = self._curr_console_index

            # we can switch to another console (there is still 1 to pop)
            if len(self._consoles) > 1:
                self._switch_to_index(self._max_index)
            else:
                self._switch_to_none()

            # pop the current console
            popped_console = self._consoles.pop(to_pop_index)

            # if the user said to stop when there are no more consoles -> stop
            if len(self._consoles) is 0 and self._quit_when_no_consoles_left:
                self._should_be_running = False

            return popped_console

    def switch_to_console(self, console: ConsoleInput):
        """
        Switches the top console to be the one given (if it is in the manager).
        If it is not in the manager, it raises a ValueError
        :exception ValueError If the given console is not in the manager
        """
        with self._consoles_lock:
            at = None

            for c in self._consoles:
                if self._consoles[c] == console:
                    at = c
                    break

            if at is None:
                raise ValueError("The given console is not in this manager. You can switch to it via adding it!")

            self._switch_to_index(at)

    def _switch_to_index(self, at: int):
        """
        Switches to the console with the given index
        """
        with self._consoles_lock:
            # print quit message if it is possible
            if self._is_there_console_on_top:
                self._curr_console.print_quit_message()
                self._curr_console._console_running = False

            self._curr_console_index = at

            # print welcome message
            self._curr_console.print_welcome_message()
            self._curr_console._console_running = True

            # set auto completer
            readline.set_completer(self._curr_console._auto_completer)

    def _switch_to_none(self):
        """
        Switches to no console being on top
        """
        with self._consoles_lock:
            # set auto completer to nothing
            readline.set_completer(None)

            # print quit message if it is possible
            if self._is_there_console_on_top:
                self._curr_console.print_quit_message()
                self._curr_console._console_running = False

            self._curr_console_index = None

    def _get_next_command(self) -> str:
        with self._consoles_lock:
            return input("" + self._curr_console.command_line_name + " : ")

    def _process_command(self, commands, **kwargs) -> {}:
        """
        Processes the given command while passing the switches and the kwargs to the function of the command
        """
        with self._consoles_lock:
            return self._curr_console.process_command(commands, **kwargs)

    def _run_command_manager(self):
        """
        Runs this console manager
        """
        while self._should_be_running:
            with self._consoles_lock:
                if self._is_there_console_on_top:
                    next_command = self._get_next_command()

                    if next_command == "qq":
                        while len(self._consoles) > 0:
                            self.pop_console()
                    else:
                        self._process_command(next_command)


# the console manager for the whole application
console_manager = ConsoleManager(quit_when_no_consoles_left=True)
