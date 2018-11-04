import random

from data import data


# PARTICIPANT filter
def get_random_participant_cmd_str(chat: data.Chat) -> (str, [str]):
    """
    Returns a new string that can be appended at the end of the -p switch for filter.
    Also returns the list of participants that have to be in the result of the filter
    """
    # we need to choose random participants for filtering
    participants_name = list(map(lambda p: p.name, chat.participants))

    # it's fifty-fifty to choose a participant
    chosen_names = list(filter(lambda _: bool(random.getrandbits(1)), participants_name))

    # we chose none with the random code above -> we still need one
    if len(chosen_names) == 0:
        chosen_names = [random.choice(participants_name)]

    # we get only the first name (or whatever is before the first space) and join them with ','
    chosen_cmd_str = ",".join(list(map(lambda name: name.split(" ")[0], chosen_names)))

    return chosen_cmd_str, chosen_names
