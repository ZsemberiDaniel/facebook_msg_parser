from test.view.view_test import ViewTests

from data import data
from view.console.console_manager import console_manager


class EmojiTests(ViewTests):

    def test_top(self):
        for chat in self.chats:
            self.enter_current_console(chat)

            # top
            # should result at least in 5 emojis per participant
            result = console_manager._curr_console.process_command("top")["emojis_per_participant"]
            for participant in result:
                self.assertGreaterEqual(5, len(result[participant]),
                                        "Simple top command should return at least 5 emojis even for " + participant)

            # top -c 10
            result = console_manager._curr_console.process_command("top")["emojis_per_participant"]
            for participant in result:
                self.assertGreaterEqual(10, len(result[participant]),
                                        "top -c 10 command should return at least 10 emojis even for " + participant)

            # top -t
            result = console_manager._curr_console.process_command("top -t")["emotions_per_participant"]
            for participant in result:
                self.assertGreaterEqual(5, len(result[participant]),
                                        "Simple top -t command should return at least 5 emotions even for " + participant)

            # top -t -c 10
            result = console_manager._curr_console.process_command("top -t -c 10")["emotions_per_participant"]
            for participant in result:
                self.assertGreaterEqual(10, len(result[participant]),
                                        "Simple top -t command should return at least 10 emotions even for " + participant)

            self.quit_current_console(chat)

    def test_overtime(self):
        for chat in self.chats:
            self.enter_current_console(chat)

            # we can't really test these because they are returned as strings, so we can only check that they really do
            # run, and don't throw errors
            # overtime -m
            result = console_manager._process_command("overtime -m")["output_string"]
            self.assertIsNotNone(result, "Overtime command failed!")

            # overtime -t -m
            result = console_manager._process_command("overtime -t -m")["output_string"]
            self.assertIsNotNone(result, "Overtime command failed!")

            self.quit_current_console(chat)

    def enter_current_console(self, chat: data.Chat):
        console_manager._curr_console.process_command("c " + chat.name)
        console_manager._curr_console.process_command("emoji -a")

    def quit_current_console(self, chat: data.Chat):
        console_manager._curr_console.process_command("q")
        console_manager._curr_console.process_command("q")
