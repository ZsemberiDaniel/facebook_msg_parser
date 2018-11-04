from unittest import TestCase
from os.path import join as join_path, exists
from os import remove as remove_file

from data.data import Message, Participant, Reaction, Chat
from data.facebook_emojis import facebook_emojis
from definitions import ROOT_DIR
from controller import chat_decoder, folder_traversal


class ReadDataTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.messages_path = join_path(ROOT_DIR, "test", "messages")
        cls.chats = folder_traversal.traverse_folder(cls.messages_path)

    @classmethod
    def tearDownClass(cls):
        # delete decoded files (if they exist)
        for c in cls.chats:
            cache_file_path = join_path(c.msg_folder_path, "decoded_message.json")

            if exists(cache_file_path):
                remove_file(cache_file_path)

    def test_folder_traversal(self):
        chat_names = list(map(lambda chat: chat.name, self.chats))
        chat_folders = list(map(lambda chat: chat.msg_folder_path, self.chats))
        has_media_folder = list(map(lambda chat: chat.has_media(), self.chats))

        # check chat names
        self.assertEqual(chat_names, ["a100910", "agroup", "dontsayhisname", "helping", "valaki"],
                         "Chat names are not correct!")
        # check chat folders
        self.assertEqual(chat_folders, [join_path(self.messages_path, "a100910_adsasd213"),
                                        join_path(self.messages_path, "agroup_wow"),
                                        join_path(self.messages_path, "dontsayhisname"),
                                        join_path(self.messages_path, "helping_23456"),
                                        join_path(self.messages_path, "valaki_dfg345")],
                         "Chat message folder are not correct!")
        # check emdia folder detecting
        self.assertEqual(has_media_folder, [False, True, True, False, False], "Media folders not detected correctly!")

    def test_chat_decoder(self):
        participants = [
            Participant("Me myself and I"),
            Participant("John smith"),
            Participant("Gordon Ramsay")
        ]
        reactions = [
            Reaction("Another Celebrity Here", "happy"),
            Reaction("John Mulaney", "sad"),
            Reaction("Conan O'Brian", "why")
        ]
        messages = [
            Message("abcdef", 1507522952825, "Just sent some good stuff", "basic"),
            Message("another name", 1507522374819, "Here are some emojis 😂😂😂", "basic"),
            Message("another name #2", 1507522379999, "This ain't a basic message anymore", "photo")
        ]
        messages[2].photos_add("lin.to.a.photo")
        messages[1].reactions_add(reactions[0])
        messages[0].gifs_add("added.a.gif")

        # encoding then decoding should result in same stuff
        self.assertEqual(participants,
                         chat_decoder.decode_participants(chat_decoder.encode_participants(participants)),
                         "Encoding then decoding participants failed")

        self.assertEqual(reactions,
                         chat_decoder.decode_reactions(chat_decoder.encode_reactions(reactions)),
                         "Encoding then decoding reactions failed")

        self.assertEqual(messages,
                         chat_decoder.decode_messages(chat_decoder.encode_messages(messages)),
                         "Encoding then decoding messages failed")

        self.assertEqual(self.chats,
                         list(map(lambda c: chat_decoder.decode_chat(chat_decoder.encode_chat(c)), self.chats)),
                         "Encoding then decoding chats failed")

        # fill chats with other data
        new_chats = list(map(lambda c: chat_decoder.add_all_data(c), self.chats))

        for c in new_chats:
            self.assertTrue(len(c.messages) > 0, "Messages are not read correctly for " + c.name)
            self.assertTrue(len(c.participants) > 0, "Participants are not read correctly for " + c.name)

        # assert cache files exist
        for c in self.chats:
            cache_file_path = join_path(c.msg_folder_path, "decoded_message.json")
            cache_dir = exists(cache_file_path)
            self.assertTrue(cache_dir, "No cache file for " + c.name + " at " + cache_file_path)

    def test_facebook_emojis_load(self):
        self.assertEqual(True, len(facebook_emojis.all_emojis) > 0, "Reading facebook emojis failed!")
