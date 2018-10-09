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


class Reaction:
    def __init__(self, actor=None, reaction=None):
        self.actor = actor
        self.reaction = reaction

    def __str__(self):
        return self.actor + " reacted with " + self.reaction


class Message:
    def __init__(self, sender=None, time_stamp=None, content=None, msg_type=None):
        self._time_stamp = 0
        # special types which may not be available
        self._gifs = []
        self._photos = []
        self._share = []
        self._reactions = []

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

    @property
    def gifs(self):
        return self._gifs

    def gifs_add(self, value: str):
        self._gifs.append(value)
        self.content += " (gif: " + value + " )"

    @property
    def photos(self):
        return self._photos

    def photos_add(self, value: str):
        self._photos.append(value)
        self.content += " (photo: " + value + " )"

    @property
    def shares(self):
        return self._share

    def shares_add(self, value: str):
        self._share.append(value)
        self.content += " (share: " + value + " )"

    @property
    def reactions(self):
        return self._reactions

    def reactions_add(self, value: Reaction):
        self._reactions.append(value)
        self.content += " \t(reaction: " + str(value) + " )"

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

    def is_special_message(self) -> bool:
        """
        Returns whether this message contains any media
        """
        return len(self._share) != 0 or len(self._photos) != 0 or len(self._gifs) != 0


class Participant:
    def __init__(self, name=None):
        self.name = name
