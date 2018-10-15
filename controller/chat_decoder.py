import json
import ftfy
import os.path
from data import data


async def add_all_data(chat) -> data.Chat:
    """
    Adds all data that can be read from messages file to the given chat.
    The chat needs to have the messages path defined.
    :return: The new chat object
    """

    if chat.msg_folder_path is None:
        raise ValueError("The given chat needs to have at least a message path.")

    with open(os.path.join(chat.msg_folder_path, "message.json"), "r") as message_file:
        # first fix the escaped character
        raw_input = message_file.read()  # get text from message file

    raw_json = json.loads(raw_input)

    # fix chat keys
    _fix_keys_and_values(raw_json)
    for participant in raw_json["participants"]:
        _fix_keys_and_values(participant)
    for msg in raw_json["messages"]:
        _fix_keys_and_values(msg)

    chat = decode_chat(raw_json, chat)

    return chat


def decode_chat(dct, chat=None) -> data.Chat:
    """
    Decodes to a Chat object from a JSON object
    :param dct: The dictionary returned by JSON decoder
    :param chat: If there is a Chat object to which we want to override the attributes
    :return: The new Chat object
    """
    if chat is None:
        chat = data.Chat()

    # load participants
    chat.participants = decode_participants(dct.get("participants", []))

    # load messages to sorted list
    msgs = decode_messages(dct.get("messages", []))

    for msg in msgs:
        chat.add_message(msg)

    # rename with a better name
    chat.name = dct.get("title", chat.name)

    return chat


def decode_messages(list):
    return [decode_message(dct) for dct in list]


def decode_message(dct, msg=None) -> data.Message:
    """
    Decodes to a Message object from a JSON object
    :param dct: The dictionary returned by JSON decoder
    :param msg: If there is a message object to which we want to override the attributes
    :return: The new message object
    """
    if msg is None:
        msg = data.Message()

    msg.sender = dct.get("sender_name", "unknown")
    msg.time_stamp = int(dct.get("timestamp_ms", "0"))
    msg.content = dct.get("content", "")
    msg.msg_type = dct.get("type", "unknown")

    # special types may not be available
    for photo in dct.get("photos", []):
        msg.photos_add(photo.get("uri", "Photo not found"))
    for gif in dct.get("gifs", []):
        msg.gifs_add(gif.get("uri", "GIF not found"))
    share = dct.get("share", {})
    for key in share.keys():
        msg.shares_add(key + ": " + share[key])

    # add reactions as well
    for reaction in dct.get("reactions", []):
        msg.reactions_add(decode_reaction(reaction))

    return msg


def decode_participants(list):
    return [decode_participant(dct) for dct in list]


def decode_participant(dct, participant=None) -> data.Participant:
    """
    Decodes to a Participant object from a JSON object
    :param dct: The dictionary returned by JSON decoder
    :param participant: If there is a Participant object to which we want to override the attributes
    :return: The new Participant object
    """
    if participant is None:
        participant = data.Participant()

    participant.name = dct.get("name", "unknown")

    return participant


def decode_reactions(list):
    return [decode_reaction(dct) for dct in list]


def decode_reaction(dct, reaction=None) -> data.Reaction:
    """
    Decodes to a Reaction object from a JSON object
    :param dct: The dictionary returned by JSON decoder
    :param reaction: If there is a Reaction object to which we want to override the attributes
    :return: The new Reaction object
    """
    if reaction is None:
        reaction = data.Reaction()

    reaction.actor = dct.get("actor", "unknown")
    reaction.reaction = dct.get("reaction", "unknown")

    return reaction


def _fix_keys_and_values(dict):
    # we can't just get the keys of the map by iteration because the size of the dict
    # is constantly changing. So we need to get the keys first as a list then
    # add the new entries to another dict and then copy them back to the old dict
    new_dict = {}
    old_keys = list(dict.keys())

    for key in old_keys:
        value = dict.pop(key)

        if isinstance(value, str):
            new_dict[_fix_string(key)] = _fix_string(value)
        else:
            new_dict[_fix_string(key)] = value

    for key in new_dict.keys():
        dict[key] = new_dict[key]


def _fix_string(str):
    return ftfy.fix_encoding(ftfy.fixes.decode_escapes(str))
