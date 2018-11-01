import json
import ftfy
import os.path
from definitions import is_current_decoding_version, DECODING_VERSION
from unicodedata import normalize
from data import data
from colorama import Fore


def add_all_data(chat) -> data.Chat:
    """
    Adds all data that can be read from messages file to the given chat.
    The chat needs to have the messages path defined.
    :return: The new chat object
    """
    if chat is None or chat.msg_folder_path is None:
        raise ValueError("The given chat needs to have at least a message path.")

    # indicates whether we could read the decoded file or not
    read_decoded = False
    # check whether we need to decode at all, because if there is a decoded_message.json that's version is
    # the same as the one being used by the program then we can just read that
    decoded_path = os.path.join(chat.msg_folder_path, "decoded_message.json")
    if os.path.exists(decoded_path):
        print(Fore.LIGHTYELLOW_EX + "Trying to read decoded messages." + Fore.RESET)
        with open(decoded_path, "r") as message_file:
            try:
                raw_json = json.loads(message_file.read())
            except json.decoder.JSONDecodeError:
                raw_json = {}  # when there is nothing the file

            # we are on the same decoding version as the program
            if is_current_decoding_version(raw_json.get("version", "0.0")):
                raw_json = raw_json["chat"]
                read_decoded = True
                print(Fore.LIGHTYELLOW_EX + "Successfully read decoded messages." + Fore.RESET)
            else:
                print(Fore.LIGHTYELLOW_EX + "Version not correct in decoded JSON." + Fore.RESET)

    # we couldn't load the chat from decoded_messages.json
    if not read_decoded:
        print(Fore.LIGHTYELLOW_EX + "Reading undecoded messages" + Fore.RESET)
        with open(os.path.join(chat.msg_folder_path, "message.json"), "r") as message_file:
            # first fix the escaped character
            raw_input = message_file.read()  # get text from message file

        raw_json = json.loads(raw_input)
        print(Fore.LIGHTYELLOW_EX + "Read undecoded messages.\nFixing UTF errors." + Fore.RESET)

        # fix chat keys
        _fix_keys_and_values(raw_json)
        for participant in raw_json["participants"]:
            _fix_keys_and_values(participant)
        for msg in raw_json["messages"]:
            _fix_keys_and_values(msg)

        print(Fore.LIGHTYELLOW_EX + "Fixed UTF errors." + Fore.RESET)

    chat = decode_chat(raw_json, chat)
    print(Fore.LIGHTYELLOW_EX + "Decoded chat from JSON" + Fore.RESET)

    # after decoding if we could not read the decoded file -> write to that file
    if not read_decoded:
        with open(os.path.join(chat.msg_folder_path, "decoded_message.json"), "w") as message_file:
            message_file.write(json.dumps({
                "version": DECODING_VERSION,
                "chat": encode_chat(chat)
            }))
        print(Fore.LIGHTYELLOW_EX + "Written decoded chat to cache" + Fore.RESET)

    return chat


def encode_chat(chat: data.Chat) -> {}:
    """
    Encodes a chat to a dict which then later can be dumped to json
    """
    return {
        "participants": encode_participants(chat.participants),
        "messages": encode_messages(chat.messages),
        "title": chat.name
    }


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
        chat.add_message_with_check(msg)

    # rename with a better name
    chat.name = normalize("NFD", dct.get("title", chat.name).lower()).encode("ASCII", "ignore").decode("UTF-8")\
        .replace(" ", "-")

    return chat


def encode_messages(msgs: [data.Message]) -> [{}]:
    return [encode_message(m) for m in msgs]


def encode_message(msg: data.Message) -> {}:
    """
    Encodes a message to a dict which then later can be dumped to json
    """
    out = {
        "sender_name": msg.sender,
        "timestamp_ms": msg.time_stamp,
        "content": msg.content,
        "type": msg.msg_type
    }

    # photos
    if len(msg.photos) is not 0:
        out["photos"] = []
        for photo in msg.photos:
            out["photos"].append({"uri": photo})

    # gifs
    if len(msg.gifs) is not 0:
        out["gifs"] = []
        for gif in msg.gifs:
            out["gifs"].append({"uri": gif})

    # shares
    if len(msg.shares) is not 0:
        out["shares"] = {}
        for share in msg.shares:
            split = share.split(": ")
            out["shares"][split[0]] = split[1]

    # reactions
    if len(msg.reactions) is not 0:
        out["reactions"] = encode_reactions(msg.reactions)

    return out


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


def encode_participants(participants: [data.Participant]) -> [{}]:
    return [encode_participant(p) for p in participants]


def encode_participant(participant: data.Participant) -> {}:
    """
    Encodes a participant to a dict which then later can be dumped to json
    """
    return {
        "name": participant.name
    }


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


def encode_reactions(reactions: [data.Reaction]) -> [{}]:
    return [encode_reaction(r) for r in reactions]


def encode_reaction(reaction: data.Reaction) -> {}:
    """
    Encodes a reaction to a dict which then later can be dumped to json
    """
    return {
        "actor": reaction.actor,
        "reaction": reaction.reaction
    }


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
