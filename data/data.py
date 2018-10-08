from sortedcontainers import SortedList
import datetime


class Chat:
    def __init__(self, msg_folder_path=None, media_folder_path=None, name=None):
        self.msg_folder_path = msg_folder_path
        self.media_folder_path = media_folder_path
        self.name = name
        self.participants = []
        self.messages = SortedList()

    def __str__(self):
        return "Name: " + self.name + "\t Has media folder? " + str(self.has_media())

    def string_for_user(self):
        return "Name: " + self.name

    def has_media(self):
        return self.media_folder_path is not None


class Message:
    def __init__(self, sender=None, time_stamp=None, content=None, msg_type=None):
        self._time_stamp = 0

        self.sender = sender
        self.time_stamp = time_stamp
        self.content = content
        self.msg_type = msg_type

    @property
    def time_stamp(self):
        return self._time_stamp

    @time_stamp.setter
    def time_stamp(self, value):
        self._time_stamp = value
        if value is not None:
            self.date = datetime.datetime.fromtimestamp(self._time_stamp / 1000.0)
        else:
            self.date = None

    def __eq__(self, other):
        if self is other:
            return True
        elif isinstance(self, Message) and isinstance(other, Message):
            return self.sender == other.sender and self.time_stamp == other.time_stamp and self.content == other.content
        else:
            return False

    def __lt__(self, other):
        return self.time_stamp < other.time_stamp

    def __str__(self):
        return self.sender + "(" + str(self.time_stamp) + "):\n\t" + self.content

    def character_count(self) -> int:
        return len(self.content)


class Participant:
    def __init__(self, name=None):
        self.name = name
