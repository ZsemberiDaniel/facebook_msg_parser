from view import choose_chat_text_input
from data import data
from view.console.console_manager import console_manager

from test.view.view_test import ViewTests


class ChooseChatTests(ViewTests):
    def setUp(self):
        super().setUp()

        # for tests just by itself (without command processing)
        self.choose_chat_console = choose_chat_text_input.ChooseChatCommandLine([])

    def test_filter(self):
        # test it by itself
        chats = [
            data.Chat(None, None, "apple"),
            data.Chat(None, None, "appleapple"),
            data.Chat(None, None, "wow"),
            data.Chat(None, None, "woww"),
            data.Chat(None, None, "123456")
        ]

        def get_names(chats: [data.Chat]) -> [str]:
            return list(map(lambda c: c.name, chats))

        self.assertEqual(["apple", "appleapple"], get_names(self.choose_chat_console.filter(chats, ["a"])["chats"]),
                         "Something went wrong while filtering for 'a'!")
        self.assertEqual(["wow", "woww"], get_names(self.choose_chat_console.filter(chats, ["wow"])["chats"]),
                         "Something went wrong while filtering for 'wow'!")
        self.assertEqual([], get_names(self.choose_chat_console.filter(chats, ["asd"])["chats"]),
                         "Something went wrong while filtering for 'asd'!")

        # test with command line
        result = console_manager._curr_console.process_command("filter dont", chats=self.chats)["chats"]
        self.assertEqual(["dontsayhisname"], get_names(result), "Something went wrong while filtering for 'dont'!")

        result = console_manager._curr_console.process_command("f a", chats=self.chats)["chats"]
        self.assertEqual(["a100910", "agroup", "dontsayhisname", "valaki"], get_names(result),
                         "Something went wrong while filtering for 'a'!")

    def test_choose(self):
        # test it by itself
        chats = [
            data.Chat(None, None, "apple"),
            data.Chat(None, None, "appleapple"),
            data.Chat(None, None, "wow"),
            data.Chat(None, None, "woww"),
            data.Chat(None, None, "123456")
        ]

        def get_names(chats: [data.Chat]) -> [str]:
            return list(map(lambda c: c.name, chats))

        self.assertEqual(None, self.choose_chat_console.choose(chats, "appl"), "Two names possible failed in choose!")
        self.assertEqual(["apple"], get_names(self.choose_chat_console.choose(chats, ["apple"])["chats"]),
                         "Exact name match failed in choose command!")
        self.assertEqual(["123456"], get_names(self.choose_chat_console.choose(chats, ["34"])["chats"]),
                         "Substring '34' match failed in choose command!")
        self.assertEqual(["appleapple"], get_names(self.choose_chat_console.choose(chats, ["applea"])["chats"]),
                         "Substring 'applea' match failed in choose command!")
        self.assertEqual(None, self.choose_chat_console.choose(chats, ""),
                         "Substring '' match failed in choose command!")

        # test with commands
        result = console_manager._curr_console.process_command("choose dont", chats=self.chats)["chats"]
        self.assertEqual(["Justsomeone Iusedtoknow"], get_names(result),
                         "Something went wrong while choosing for 'dont'!")
        console_manager._curr_console.process_command("q")

        result = console_manager._curr_console.process_command("c a", chats=self.chats)
        self.assertEqual(5, len(result["chats"]), "Something went wrong while choosing for 'a'!")

        result = console_manager._curr_console.process_command("c \"a100\"", chats=self.chats)["chats"]
        self.assertEqual(["A1009-10"], get_names(result), "Something went wrong while choosing for 'a100'!")
        console_manager._curr_console.process_command("q")
