from test.view.view_test import ViewTests
from test.misc import get_random_participant_cmd_str

from data import data
from definitions import console_manager


class MarkovTests(ViewTests):

    def test_words(self):
        for chat in self.chats:
            self.enter_current_console(chat)

            # get the chat that has messages and participants as well
            chat = console_manager._curr_console.markov_data.chat

            # words asd
            result = console_manager._curr_console.process_command("words asd").get("words_per_participant", None)
            self.assertIsNone(result, "Result of words asd is not None!")

            # words
            result = console_manager._curr_console.process_command("words").get("words_per_participant", None)
            self.assertIsNone(result, "Result of words is not None!")

            # words 50
            result = console_manager._curr_console.process_command("words 50")["words_per_participant"]
            self.assertEqual(sorted(map(lambda p: p.name, chat.participants)), sorted(result),
                             "The participants of the results of 'words 50' is not the same as the participants in the chat!")
            for participant in result:
                self.assertTrue(len(result[participant]) == 50 or len(result[participant]) == 0,
                                "The word count for " + participant + " was not 50 or 0 (for no msgs)!")

            # words 50000
            result = console_manager._curr_console.process_command("words 50000")["words_per_participant"]
            self.assertEqual(sorted(map(lambda p: p.name, chat.participants)), sorted(result),
                             "The participants of the results of 'words 50000' is not the same as the participants in the chat!")
            for participant in result:
                self.assertTrue(len(result[participant]) == 50000 or len(result[participant]) == 0,
                                "The word count for " + participant + " was not 50000 or 0 (for no msgs)!")

            # words -p random 50
            to_append, participant_need_to_be_in = get_random_participant_cmd_str(chat)
            result = console_manager._curr_console.process_command("words -p " + to_append + " 50")["words_per_participant"]
            self.assertEqual(sorted(participant_need_to_be_in), sorted(result),
                             "The participants of the results of 'words -p random 50' is not the same as the participants expected!")
            for participant in result:
                self.assertTrue(len(result[participant]) == 50 or len(result[participant]) == 0,
                                "The word count for " + participant + " was not 50 or 0 (for no msgs)!")

            # words -a -p alma 60
            result = console_manager._curr_console.process_command("words -a -p alma 60")["words_per_participant"]
            self.assertEqual(["All participants"], list(result.keys()), "Getting markov chain for all participants failed!")
            self.assertTrue(60 == len(result["All participants"]) or 0 == len(result["All participants"]),
                            " Markov chain for all participants does not contain the right amount of words!")

            self.quit_current_console(chat)

    def test_layer(self):
        for chat in self.chats:
            self.enter_current_console(chat)

            # change layer count then check whether it really changed in class
            console_manager._curr_console.process_command("layer 3")
            self.assertEqual(3, console_manager._curr_console.layer_count)

            console_manager._curr_console.process_command("layer 1")
            self.assertEqual(1, console_manager._curr_console.layer_count)

            console_manager._curr_console.process_command("layer 10")
            self.assertEqual(10, console_manager._curr_console.layer_count)

            console_manager._curr_console.process_command("layer a")
            self.assertEqual(10, console_manager._curr_console.layer_count)

            console_manager._curr_console.process_command("layer -3")
            self.assertEqual(10, console_manager._curr_console.layer_count)

            console_manager._curr_console.process_command("layer 0")
            self.assertEqual(10, console_manager._curr_console.layer_count)

            self.quit_current_console(chat)

    def enter_current_console(self, chat: data.Chat):
        console_manager._curr_console.process_command("c " + chat.name)
        console_manager._curr_console.process_command("m")

    def quit_current_console(self, chat: data.Chat):
        console_manager._curr_console.process_command("q")
        console_manager._curr_console.process_command("q")
