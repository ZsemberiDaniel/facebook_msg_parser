from unittest import TestCase
from colorama import init as colorama_init
from os.path import join as join_path

from controller import folder_traversal
from view import choose_chat_text_input
from data import data
from definitions import console_manager, ROOT_DIR


class ViewTests(TestCase):
    def setUp(self):
        colorama_init()

        # get all the chats from the folder
        self.chats: [data.Chat] = folder_traversal.traverse_folder(join_path(ROOT_DIR, "test", "messages"))

        console_manager.add_console(choose_chat_text_input.ChooseChatCommandLine(self.chats))

    def tearDown(self):
        console_manager.pop_console()

    @classmethod
    def tearDownClass(cls):
        console_manager._should_be_running = False

    def test_help(self):
        for chat in self.chats:
            self.enter_current_console(chat)

            # just execute help, and see if it throws an error or not
            try:
                console_manager._process_command("help")
            except Exception:
                self.fail("There was a problem with the help command!")

            self.quit_current_console(chat)

    def enter_current_console(self, chat: data.Chat):
        pass

    def quit_current_console(self, chat: data.Chat):
        pass
