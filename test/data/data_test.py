from unittest import TestCase
from os.path import exists, join as join_path

from definitions import ROOT_DIR
from controller import folder_traversal, chat_decoder
from data.data import Participant, Chat, Message, Reaction
from data.facebook_emojis import facebook_emojis, Emoji as FEmoji


class DataTests(TestCase):

    def test_participant(self):
        participant1 = Participant("Vörös Géza")
        participant2 = Participant("Soós Zoltán")

        self.assertTrue(participant1.substring_in_ascii("voro"), "Lower case ASCII mathching")
        self.assertTrue(participant1.substring_in_ascii("geza"), "Lower case ASCII mathching")
        self.assertTrue(participant1.substring_in_ascii("Vörös"), "Lower case ASCII mathching")
        self.assertFalse(participant1.substring_in_ascii("   "), "Lower case ASCII mathching")
        self.assertTrue(participant2.substring_in_ascii("oo"), "Lower case ASCII mathching")
        self.assertTrue(participant2.substring_in_ascii("tan"), "Lower case ASCII mathching")

    def test_message(self):
        msg1 = Message("abcdef", 1507522952825, "Just sent some good stuff", "basic")
        msg2 = Message("another name", 1507522374819, "Here are some emojis 😂😂😂", "basic")

        msg1.gifs_add("gif")
        msg1.gifs_add("gif2")
        msg1.reactions_add(Reaction("me", "sad"))

        self.assertEqual(["gif", "gif2"], msg1.gifs, "Gif addition not working in messages not working!")
        self.assertEqual([Reaction("me", "sad")], msg1.reactions, "Reaction addition in messages not working!")

        msg2.photos_add("photo")
        msg2.photos_add("photo2")
        msg2.photos_add("photo3")
        msg2.shares_add("share")
        msg2.shares_add("share2")

        self.assertEqual(["photo", "photo2", "photo3"], msg2.photos, "Photo addition in messages not working!")
        self.assertEqual(["share", "share2"], msg2.shares, "Share addition in messages not working!")

        self.assertTrue(msg1.is_special_message() and msg2.is_special_message(), "Being a special message not working!")

    def test_chat(self):
        # go through all chats in test chats
        for ch in folder_traversal.traverse_folder(join_path(ROOT_DIR, "test", "messages")):
            chat = chat_decoder.add_all_data(ch)

            # check whether when we ask for the responses we get them in ordder of appereance (and we get all of them)
            msg_at = 0
            chat_messages = chat.messages

            # we go through the response messages while simultaneously checking chat messages
            for response in chat.get_responses():
                for msg in response.messages:
                    if msg == chat_messages[msg_at]:
                        msg_at += 1
                    else:
                        self.fail("The messages we get from get_response is not the same as the messages in chat")

    def test_facebook_emojis(self):
        for emoji_name in facebook_emojis.all_emojis:
            emoji = facebook_emojis.all_emojis[emoji_name]
            self.assertTrue(emoji is not None, "There was a problem with decoding of facebook emojis!")
            self.assertTrue(emoji.name is not None, "There was a problem with the name decoding in facebook emojis!")
            self.assertTrue(emoji.path is not None, "The path of " + emoji.name + " is None!")
            self.assertTrue(exists(emoji.path), "The path to " + emoji.name + " does not exist!")

        # emotion and it's colors are the same length
        self.assertTrue(len(FEmoji.all_emotions) == len(FEmoji.emotion_colors), "There are not equal amount of emotions"
                                                                                "and emotion colors!")
