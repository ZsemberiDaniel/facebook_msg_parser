from unittest import TestCase

from controller.chat_analyzer import *


class ChatAnalyzerTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.chat_empty = data.Chat(None, None, "empty")
        cls.chat_one_msg = data.Chat(None, None, "one msg")
        cls.chat_one_msg.participants = [
            data.Participant("Part1")
        ]
        cls.chat_one_msg.messages = [
            data.Message("Part1", 1538403691516, "This is the only msg", "generic")
        ]

        cls.chat1 = data.Chat(None, None, "chat1")
        cls.chat1.participants = [
            data.Participant("PÁrt1"),
            data.Participant("Part2"),
            data.Participant("Part3")
        ]
        cls.chat1.messages = [
            data.Message("PÁrt1", 1538403691483, "Content", "generic"),
            data.Message("Part2", 1538403691485, "Content😂", "generic"),
            data.Message("PÁrt1", 1538403691487, "Content", "generic"),
            data.Message("Part2", 1538403691489, "Content😂😂", "generic"),
            data.Message("PÁrt1", 1538403691499, "Content", "generic"),
            data.Message("Part2", 1538403691500, "Content", "generic"),
            data.Message("Part2", 1538403691512, "Content", "photo"),
            data.Message("PÁrt1", 1538403691514, "Content", "generic"),
            data.Message("PÁrt1", 1538403691516, "Content", "generic"),
            data.Message("PÁrt1", 1538403691518, "Content", "generic"),
            data.Message("PÁrt1", 1538499999522, "Content", "generic"),
            data.Message("Part2", 1538499999524, "Content", "generic"),
            data.Message("Part2", 1538499999527, "Content", "generic"),
            data.Message("Part3", 1538499999535, "Con😍tent", "generic"),
            data.Message("Part3", 1538499999538, "Conte😍😍nt", "generic"),
            data.Message("Part3", 1538499999542, "Conte😍nt", "generic")
        ]

    def test_active_dates(self):
        result = active_dates(self.chat1)
        self.assertEqual([datetime.date(2018, 10, 1), datetime.date(2018, 10, 2)], result, "Active dates failed!")

        result = active_dates(self.chat_empty)
        self.assertEqual(None, result, "Active dates failed!")

        result = active_dates(self.chat_one_msg)
        self.assertEqual([datetime.date(2018, 10, 1)], result, "Active dates failed!")

    def test_date_between(self):
        from_date, till_date = date_between(self.chat1)

        self.assertEqual(1538403691483, from_date.timestamp() * 1000, "From date failed!")
        self.assertEqual(1538499999542, till_date.timestamp() * 1000, "Till date failed!")

        from_date, till_date = date_between(self.chat_empty)
        self.assertIsNone(from_date, "Empty chat from date failed!")
        self.assertIsNone(till_date, "Empty chat till date failed!")

        from_date, till_date = date_between(self.chat_one_msg)
        self.assertEqual(from_date, till_date, "One msg chat from date == till date failed!")

    def test_get_messages_only_by(self):
        new_chat = get_messages_only_by(self.chat1, ["part1"])

        for msg in new_chat.messages:
            self.assertEqual("PÁrt1", msg.sender, "Filtering for participant failed!")

        new_chat = get_messages_only_by(self.chat1, ["part1", "part2", "part3"])
        self.assertEqual(self.chat1.messages, new_chat.messages, "Filtering for whole chat failed")

        new_chat = get_messages_only_by(self.chat1, ["asd," "fds", "234234", "$%$#"])
        self.assertEqual([], new_chat.messages, "Filtering for nonsense failed")

        new_chat = get_messages_only_by(self.chat_empty, ["alma", "orte"])
        self.assertEqual([], new_chat.messages, "Filtering empty chat failed!")
