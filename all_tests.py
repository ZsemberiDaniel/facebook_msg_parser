from unittest import TestSuite, makeSuite, TextTestRunner

from test.view.chat_data_test import ChatDataTests
from test.view.choose_chat_test import ChooseChatTests
from test.view.markov_test import MarkovTests
from test.view.emoji_test import EmojiTests
from test.data.data_test import DataTests
from test.data.read_data_test import ReadDataTests


suite = TestSuite()
suite.addTests([
    makeSuite(DataTests),
    makeSuite(ReadDataTests),
    makeSuite(ChatDataTests),
    makeSuite(ChooseChatTests),
    makeSuite(MarkovTests),
    makeSuite(EmojiTests)
])

TextTestRunner().run(suite)
