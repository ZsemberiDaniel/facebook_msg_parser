from sortedcontainers import SortedList
from unicodedata import normalize
import datetime


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
        self._with_special = ""

        self.date: datetime.datetime = None
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
        self._with_special += " (gif: " + value + " )"

    @property
    def photos(self):
        return self._photos

    def photos_add(self, value: str):
        self._photos.append(value)
        self._with_special += " (photo: " + value + " )"

    @property
    def shares(self):
        return self._share

    def shares_add(self, value: str):
        self._share.append(value)
        self._with_special += " (share: " + value + " )"

    @property
    def reactions(self):
        return self._reactions

    def reactions_add(self, value: Reaction):
        self._reactions.append(value)

    @property
    def content_with_special(self) -> str:
        return self.content + self._with_special

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

    def str_for_user(self) -> str:
        return str(self.date.year) + ". " + str(self.date.month) + ". " + str(self.date.day) + ". " +\
               str(self.sender) + ": " + str(self.content_with_special)

    def character_count(self) -> int:
        return len(self.content)

    def is_special_message(self) -> bool:
        """
        Returns whether this message contains any media
        """
        return self.msg_type.lower() == "generic" and\
               (len(self._share) != 0 or len(self._photos) != 0 or len(self._gifs) != 0)


class Participant:
    def __init__(self, name=None):
        self.name = name

    def name_matches_ascii(self, to_match: str):
        """
        Checks whether the given string matches the name in lower case ASCII form.
        On to_match ASCII conversion and lower case conversion happens as well
        """
        return normalize("NFD", to_match.lower()).encode("ASCII", "ignore").decode("UTF-8") in \
                    normalize("NFD", self.name.lower()).encode("ASCII", "ignore").decode("UTF-8")

    def __eq__(self, other):
        if isinstance(other, Participant):
            return other.name == self.name
        else:
            return False

    def __hash__(self):
        return hash(self.name)


class Response:
    def __init__(self, messages: [Message]):
        self._messages = []

        self.messages = messages

    @property
    def messages(self) -> [Message]:
        return self._messages

    @messages.setter
    def messages(self, value: [Message]):
        self._messages = sorted(value)

    @property
    def sender(self) -> str:
        return self.messages[0].sender

    @property
    def date_time(self) -> datetime.datetime:
        return self.messages[0].date

    @property
    def time_span(self) -> datetime.timedelta:
        return self.messages[len(self.messages) - 1].date - self.messages[0].datechat


class Chat:
    def __init__(self, msg_folder_path=None, media_folder_path=None, name=None):
        """
        :param msg_folder_path: The absolute path
        :param media_folder_path: The absolute path
        :param name: Name of the chat
        """
        self._messages = SortedList()

        self.msg_folder_path = msg_folder_path
        self.media_folder_path = media_folder_path
        self.name = name
        self._participants = set()

    @property
    def participants(self):
        return list(self._participants)

    @participants.setter
    def participants(self, participants: [Participant]):
        self._participants = set(participants)

    def add_participant(self, participant: Participant):
        self._participants.add(participant)

    def is_participant(self, name: str):
        return Participant(name) in self._participants

    @property
    def messages(self) -> [Message]:
        return list(iter(self._messages))

    @messages.setter
    def messages(self, new_messages: [Message]):
        self._messages = SortedList()

        for msg in new_messages:
            self.add_message(msg)

    def add_message(self, message: Message):
        self._messages.add(message)

    def add_message_with_check(self, message: Message):
        """
        Adds a message while checking that there is a participant with hte given name. If there isn't
        then that is added as well.
        """
        self._messages.add(message)

        if not self.is_participant(message.sender):
            self.add_participant(Participant(message.sender))

    def __str__(self):
        return "Name: " + self.name + "\t Has media folder? " + str(self.has_media())

    def has_media(self):
        return self.media_folder_path is not None

    def get_responses(self):
        """
        Returns the responses in chronological order. A response is a chunk of message which are not broken
        by the other respondents.
        """
        msg_ordered: [Message] = self.messages

        curr_participant = msg_ordered[0].sender
        curr_chunk: [Message] = [msg_ordered[0]]

        for i in range(1, len(msg_ordered)):
            # still the same participant
            if msg_ordered[i].sender == curr_participant:
                curr_chunk.append(msg_ordered[i])
            else:  # another participant started talking
                yield Response(curr_chunk)

                curr_participant = msg_ordered[i].sender
                curr_chunk = [msg_ordered[i]]
