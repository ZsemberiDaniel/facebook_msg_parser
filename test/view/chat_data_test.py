from os.path import join as join_path, exists
from os import listdir
from shutil import rmtree
from datetime import datetime
from PIL import Image
from emoji import get_emoji_regexp, UNICODE_EMOJI
from colorama import Fore
from copy import deepcopy
import re
import random

from controller import data_visualizer
from data import data
from definitions import console_manager, ROOT_DIR
from test.view.view_test import ViewTests
from test.misc import get_random_participant_cmd_str


class ChatDataTests(ViewTests):
    def setUp(self):
        super().setUp()

        # we change where the charts are saved
        data_visualizer.default_save_dir = join_path("test", "out")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        # remove all charts
        if exists(join_path(ROOT_DIR, data_visualizer.default_save_dir)):
            rmtree(join_path(ROOT_DIR, data_visualizer.default_save_dir))

    def enter_current_console(self, chat: data.Chat):
        # choose the current chat
        console_manager._process_command("c " + chat.name)

    def quit_current_console(self, chat: data.Chat):
        # quit to choose chat console
        console_manager._process_command("q")

    def test_basic(self):
        for chat in self.chats:
            self.enter_current_console(chat)

            # test command
            result = console_manager._process_command("basic")["output-string"]
            print(result)
            self.assertGreater(len(result), 0, "There was no basic command output!")

            self.quit_current_console(chat)

    def test_filter(self):
        for chat in self.chats:
            self.enter_current_console(chat)

            # swap to this chat because it contains the added data as well
            chat = console_manager._curr_console.chat

            # f -d 456.1.1 567.1.1
            new_chat = console_manager._process_command("f -d 456.1.1 567.1.1")["chat"]
            self.assertEqual(0, len(new_chat.messages),
                             "First and last date are before epoch and the returned messages' list length is not 0."
                             "For chat( " + chat.name + ")")

            # f -d asd sdf
            new_chat = console_manager._process_command("f -d asd sdf")["chat"]
            self.assertEqual(0, len(new_chat.messages),
                             "First and last date are letters and the returned messages' list length is not 0."
                             " For chat( " + chat.name + ")")

            # f -d
            new_chat = console_manager._process_command("f -d")["chat"]
            self.assertEqual(len(chat.messages), len(new_chat.messages),
                             "Omitting both parameters for -d and the returned messages' list length is not equal to the"
                             " original list size. For chat( " + chat.name + ")")

            # f -p
            new_chat = console_manager._process_command("f -p")["chat"]
            self.assertEqual(len(chat.messages), len(new_chat.messages),
                             "Omitting both parameters for -p and the returned messages' list length is not equal to the"
                             " original list size. For chat( " + chat.name + ")")

            # do 10 random tests
            for i in range(5):
                # test filter
                # DATE filter

                # random data
                from_date = datetime(2018 - random.randint(0, 2), random.randint(1, 10), random.randint(1, 20))
                till_date = datetime(from_date.year + random.randint(0, 1), from_date.month + random.randint(0, 2),
                                     from_date.day + random.randint(1, 5))

                from_date_str = "{d.year}.{d.month}.{d.day}".format(d=from_date)
                till_date_str = "{d.year}.{d.month}.{d.day}".format(d=till_date)

                # f -d from till
                new_chat: data.Chat = console_manager._process_command("f -d " + from_date_str + " " + till_date_str)["chat"]
                if len(new_chat.messages) > 0:  # found with given date -> check dates are really between
                    self.assertGreaterEqual(new_chat.messages[0].date.date(), from_date.date(),
                                            "Basic filter date, first date is not greater than the one in command."
                                            "for chat( " + chat.name + ")")
                    self.assertLessEqual(new_chat.messages[len(new_chat.messages) - 1].date.date(), till_date.date(),
                                         "Basic filter date. Last date is not smaller than the date given in command. For "
                                         "chat( " + chat.name + ")")

                # f -d from _
                new_chat: data.Chat = console_manager._process_command("f -d " + from_date_str + " _")["chat"]
                if len(new_chat.messages) > 0:  # found with given date -> check dates are really between
                    self.assertGreaterEqual(new_chat.messages[0].date.date(), from_date.date(),
                                            "Till date of date filter omitted with _. First date is not grater than the one"
                                            "given in the command. For chat( " + chat.name + ")")

                # f -d from
                new_chat: data.Chat = console_manager._process_command("f -d " + from_date_str)["chat"]
                if len(new_chat.messages) > 0:  # found with given date -> check dates are really between
                    self.assertGreaterEqual(new_chat.messages[0].date.date(), from_date.date(),
                                            "Till date of date filter omitted with ' '. First date is not grater than the"
                                            " one given in the command. For chat( " + chat.name + ")")

                # f -d _ till
                new_chat: data.Chat = console_manager._process_command("f -d _ " + till_date_str)["chat"]
                if len(new_chat.messages) > 0:  # found with given date -> check dates are really between
                    self.assertLessEqual(new_chat.messages[len(new_chat.messages) - 1].date.date(), till_date.date(),
                                         "From date of date filter omitted with _. Last date is not smaller than the date "
                                         "given in command. For chat( " + chat.name + ")")

                # f -d _ _
                new_chat: data.Chat = console_manager._process_command("f -d _ _")["chat"]
                self.assertEqual(chat.messages, new_chat.messages,
                                 "Both dates omitted with _ _ and the returned messages do not equal the messages given. "
                                 "For chat( " + chat.name + ")")

                # f -d _
                new_chat: data.Chat = console_manager._process_command("f -d _")["chat"]
                self.assertEqual(chat.messages, new_chat.messages,
                                 "First date omitted with _, second with ' '  and the returned messages"
                                 " do not equal the messages given. For chat( " + chat.name + ")")

                # PARTICIPANT filter

                # get new random data
                to_append, needs_to_be_in_result = get_random_participant_cmd_str()

                # apply command
                new_chat = console_manager._process_command("f -p " + to_append)["chat"]

                # we check that all the participant are in there who need to be
                for participant_name in needs_to_be_in_result:
                    self.assertTrue(new_chat.is_participant(participant_name),
                                    "The result of -p filtering does not contain a participant that has to be in there. "
                                    "Chat " + chat.name + ", participant: " + participant_name + " filtered for "
                                    + to_append)

                # we check that only messages by the participants are in there
                for msg in new_chat.messages:
                    self.assertTrue(new_chat.is_participant(msg.sender),
                                    "The result of -p filtering has a message that's sender in not in the participants"
                                    " list. Chat: " + chat.name + ", participant: " + msg.sender + " filtered for " +
                                    to_append)

                # do more complex queries

                # f -d from_date -p to_append
                new_chat = console_manager._process_command("f -d " + from_date_str + " -p " + to_append)["chat"]

                # we check that only messages by the participants are in there
                for msg in new_chat.messages:
                    self.assertTrue(new_chat.is_participant(msg.sender),
                                    "Complex query #1 has a message that's sender in not in the participants"
                                    " list. Chat: " + chat.name + ", participant: " + msg.sender + " filtered for " +
                                    to_append)

                if len(new_chat.messages) > 0:  # found with given date -> check dates are really between
                    self.assertGreaterEqual(new_chat.messages[0].date.date(), from_date.date(),
                                            "Complex query #1. First date is not grater than the"
                                            " one given in the command. For chat( " + chat.name + ")")

                # f -p to_append -d _ till_date
                new_chat = console_manager._process_command("f " + " -p " + to_append + " -d _ " + till_date_str)["chat"]

                # we check that only messages by the participants are in there
                for msg in new_chat.messages:
                    self.assertTrue(new_chat.is_participant(msg.sender),
                                    "Complex query #2 has a message that's sender in not in the participants"
                                    " list. Chat: " + chat.name + ", participant: " + msg.sender + " filtered for " +
                                    to_append)

                if len(new_chat.messages) > 0:  # found with given date -> check dates are really between
                    self.assertLessEqual(new_chat.messages[len(new_chat.messages) - 1].date.date(), till_date.date(),
                                         "Complex query #2. Last date is not smaller than the date "
                                         "given in command. For chat( " + chat.name + ")")

            self.quit_current_console(chat)

    def test_count(self):
        # test that if we add together the participants' count we get the length of messages
        for chat in self.chats:
            self.enter_current_console(chat)

            # swap to this chat because it contains the added data as well
            chat = console_manager._curr_console.chat

            # count
            # output should be like 'Message count: count'
            all_count = int(console_manager._curr_console.process_command("count")["output-string"].split(": ")[1])

            # count -p
            # output should be like the one above, but in multiple lines
            sum_count = 0
            for line in console_manager._curr_console.process_command("count -p")["output-string"].splitlines():
                sum_count += int(line.split(": ")[1])

            self.assertEqual(len(chat.messages), all_count, "The count of messages does not equal the output of 'count'")
            self.assertEqual(all_count, sum_count, "The output of 'count -p' does not equal 'count'")

            self.quit_current_console(chat)

    def test_chart(self):
        msg_count_size = (int(600 * random.uniform(0.5, 1.5)), int(300 * random.uniform(0.5, 1.5)))
        char_count_size = (int(700 * random.uniform(0.5, 1.5)), int(400 * random.uniform(0.5, 1.5)))
        emotion_monthly_size = (int(400 * random.uniform(0.5, 1.5)), int(1000 * random.uniform(0.5, 1.5)))
        message_distribution_size = (int(500 * random.uniform(0.5, 1.5)), int(250 * random.uniform(0.5, 1.5)))
        all_emojis_size = (int(500 * random.uniform(0.5, 1.5)), None)
        emoji_yearly_size = (int(600 * random.uniform(0.5, 1.5)), None)

        for chat in self.chats:
            self.enter_current_console(chat)

            # swap to this chat because it contains the added data as well
            chat = console_manager._curr_console.chat

            # path to the output folder of the chart command
            chart_path = join_path(ROOT_DIR, data_visualizer.default_save_dir, chat.name)

            # these are all commands which are made to fail
            commands_to_try = [
                "chart -d -s",
                "chart -sa",
                "chart -s 300x435",
                "chart -d -s asdx345",
                "chart -d -em -ey -s -sa",
                "chart -d -s 200.45x2345.34"
            ]

            for cmd in commands_to_try:
                new_chat = console_manager._curr_console.process_command(cmd)["chat"]
                self.assertEqual(chat.messages, new_chat.messages, cmd + " failed! Chat: (" + chat.name + ")")
                self.assertTrue(not exists(chart_path) or len(listdir(chart_path)), cmd + " failed! Images exist. Chat: (" + chat.name + ")")

            # testing single chart
            # testing leaving out height
            # chart -m -s 400   omitting the height, leaving it to the program to calculate
            console_manager._curr_console.process_command("chart -m -s 400")
            self.assertEqual(["message_count.png"], listdir(chart_path),
                             "Leaving it to the program to calculate height failed! More images exist. Chat: (" + chat.name + ")")
            with Image.open(join_path(chart_path, "message_count.png")) as img:
                self.assertEqual(400, img.size[0],
                                 "Leaving it to the program to calculate height failed! Image's size is not correct" +
                                 "Chat: (" + chat.name + ")")

            # testing two charts at once
            # testing override
            # chart -m -s 200x300 -c
            console_manager._curr_console.process_command("chart -m -s 200x300 -c")
            self.assertEqual(["character_count.png", "message_count.png"], sorted(listdir(chart_path)),
                             "Double chart failed! Image names do not match. Chat: (" + chat.name + ")")
            with Image.open(join_path(chart_path, "message_count.png")) as img:
                self.assertEqual((200, 300), img.size,
                                 "Double chart failed! Image's size is not correct Chat: (" + chat.name + ")")

            # delete the folder in which the charts are (and the charts as well)
            rmtree(chart_path)

            # chart

            # execute the command, we provide a size for each chart, except for one, which we provide size with
            # -sa. We also provide the -r just in case there is something wrong with that
            command_str = "chart -d -s {mds[0]}x{mds[1]} -m -s {mcs[0]}x{mcs[1]} -c -s {ccs[0]}x{ccs[1]} -em -s {ems[0]}x{ems[1]} -e -s {es[0]} -ey -sa {eys[0]} -r 20"\
                .format(mcs=msg_count_size, ccs=char_count_size, ems=emotion_monthly_size, mds=message_distribution_size, es=all_emojis_size, eys=emoji_yearly_size)
            console_manager._process_command(command_str)

            # we open each image and check whether they exist at all and if they do we check their sizes

            # -m: message count
            self.assertTrue(exists(join_path(chart_path, "message_count.png")),
                            "Message count plot does not exist! Chat: (" + chat.name + ")")
            with Image.open(join_path(chart_path, "message_count.png")) as img:
                self.assertEqual(msg_count_size, img.size,
                                 "Size of message count plot does not match the one given in command. " +
                                 "Chat: (" + chat.name + ")")

            # -c: character count
            self.assertTrue(exists(join_path(chart_path, "character_count.png")),
                            "Character count plot does not exist! Chat: (" + chat.name + ")")
            with Image.open(join_path(chart_path, "character_count.png")) as img:
                self.assertEqual(char_count_size, img.size,
                                 "Size of char count plot does not match the one given in command. " +
                                 "Chat: (" + chat.name + ")")

            # -d: message distribution
            self.assertTrue(exists(join_path(chart_path, "message_distribution.png")),
                            "Message distribution plot does not exist! Chat: (" + chat.name + ")")
            with Image.open(join_path(chart_path, "message_distribution.png")) as img:
                self.assertEqual(message_distribution_size, img.size,
                                 "Size of message distribution plot does not match the one given in command! " +
                                 "Chat: (" + chat.name + ")")

            # these plots need to be checked for each participant
            for participant in chat.participants:
                em_path = join_path(chart_path, "emotion_monthly_" + participant.name.lower().replace(" ", "_") + ".png")
                e_path = join_path(chart_path, "emojis_all_" + participant.name.lower().replace(" ", "_") + ".png")
                ey_path = join_path(chart_path, "emojis_yearly_" + participant.name.lower().replace(" ", "_") + ".png")

                # -em: emotion plot
                self.assertTrue(exists(em_path), "Emotion monthly plot does not exist!")
                with Image.open(em_path) as img:
                    self.assertEqual(emotion_monthly_size, img.size, "Size of emotion monthly plot does not match the " +
                                                                     "one given in command")

                # -e: all emojis plot
                self.assertTrue(exists(e_path), "All emojis plot does not exist!")
                with Image.open(e_path) as img:
                    self.assertEqual(all_emojis_size[0], img.size[0], "Size of all emojis plot does not match the " +
                                                                      "one given in command")

                # -ey: all emojis yearly plot
                self.assertTrue(exists(ey_path), "All emojis yearly plot does not exist! Chat: (" + chat.name + ")")
                with Image.open(ey_path) as img:
                    self.assertEqual(emoji_yearly_size[0], img.size[0], "Size of all emojis yearly plot does not match " +
                                                                        "the one given in command! Chat: (" + chat.name + ")")

            # delete the folder in which the charts are (and the charts as well)
            rmtree(chart_path)

            self.quit_current_console(chat)

    def test_emoji(self):
        for chat in self.chats:
            self.enter_current_console(chat)

            # swap to this chat because it contains the added data as well
            chat = console_manager._curr_console.chat

            # emoji
            new_chat = console_manager._curr_console.process_command("emoji")["chat"]

            # check whether the message really contains emojis
            for msg in new_chat.messages:
                self.assertTrue(re.search(get_emoji_regexp(), msg.content),
                                "Emoji command: there is no emoji in " + msg.content)

            new_chat = console_manager._curr_console.process_command("emoji -o")["chat"]

            # check whether the message really only contains emojis
            for msg in new_chat.messages:
                self.assertTrue(all(map(lambda ch: ch in UNICODE_EMOJI, msg.content)),
                                "Emoji command: there are more than emojis in " + msg.content)

            self.quit_current_console(chat)

    def test_search(self):
        for chat in self.chats:
            self.enter_current_console(chat)

            # swap to this chat because it contains the added data as well
            chat = console_manager._curr_console.chat

            # we search for everything via regex then check whether it returns all the messages
            # we can only check whether the chat's real content is a substring of the result content
            # because it adds coloring
            result = console_manager._curr_console.process_command("search -i -r \".+\"")["chat"]
            messages_without_special = list(filter(lambda msg: not msg.is_special_message(), chat.messages))
            for i, msg in enumerate(result.messages):
                self.assertTrue(messages_without_special[i].content == msg.content.replace(Fore.GREEN, "").replace(Fore.RESET, ""),
                                "There was a problem when searching for '.+' via regex. \n" + messages_without_special[i].content +
                                "\nis not in\n" + msg.content)

            # we test for the ignore case option with searching for a word that has an upper case letter (but search in lowercase form)
            #  and then checking whether that message is in the results
            shuffled_messages = deepcopy(chat.messages)
            random.shuffle(shuffled_messages)
            msg_content_with_uppercase = None
            upper_case_word = None
            msg_at = 0
            while msg_at < len(shuffled_messages) and upper_case_word is None:
                msg = shuffled_messages[msg_at]

                for word in msg.content.split():
                    # there is an uppercase letter in there
                    if any(map(lambda ch: ch.isupper(), word)):
                        upper_case_word = word
                        msg_content_with_uppercase = msg.content
                        break  # found word

                msg_at += 1

            # we make the search
            result = console_manager._curr_console.process_command("search -i " + upper_case_word.lower())["chat"]

            # now we check whether the message is in the result, if not test passed
            found_msg = False
            for msg in result.messages:
                if msg_content_with_uppercase == msg.content.replace(Fore.GREEN, "").replace(Fore.RESET, ""):
                    found_msg = True

            # found a match
            self.assertTrue(found_msg,
                            "Ignore case test case, did not find the message that had the upper case word " + upper_case_word +
                            " message: " + msg_content_with_uppercase)

            # make nonsense search so nothing gets found
            result = console_manager._curr_console.process_command("search dfretlkw9304k5o3oe93keirk209394**")["chat"]
            self.assertEqual(0, len(result.messages),
                             "Searching for nonsense resulted in something. Which is not impossible but quite surprising. "
                             "dfretlkw9304k5o3oe93keirk209394** should be in " + chat.messages[0].content)

            # search query omitted
            result = console_manager._curr_console.process_command("search")["chat"]
            self.assertEqual(chat.messages, result.messages, "Omitting query in search failed!")

            self.quit_current_console(chat)

    def test_complex_commands(self):
        for chat in self.chats:
            self.enter_current_console(chat)

            # swap to this chat because it contains the added data as well
            chat = console_manager._curr_console.chat

            # just test these so they do not throw exceptions, can't really test results
            console_manager._process_command("filter -d 2018.1.1 || basic")
            console_manager._process_command("filter -d 2017.5.26 || w || search -i \"x\" || w || count -p || w")
            console_manager._process_command("filter -d 2018.1.1 || basic || search -r \"[a][bcdrp]\" || w || count || w")
            console_manager._process_command("filter -p a,b,l -d _ 2017.3.4 || search a || markov || emoji -a")
            console_manager._process_command("q")
            console_manager._process_command("q")

            self.quit_current_console(chat)
