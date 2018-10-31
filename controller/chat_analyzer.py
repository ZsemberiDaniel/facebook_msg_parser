from data import data
import datetime
import re
import emoji
import unicodedata
from colorama import Fore
from data.facebook_emojis import facebook_emojis, Emoji as FEmoji

""" ___________________________________________________________________________________________
                                        Emojis
    ___________________________________________________________________________________________
    Some info for this section:
       I use emoji_messages name as data.Message objects that only contain a single emoji in it's content but
         still have other data like date and everything else
       I use whole messages as the message that contains emojis but the text is still in tact next to it
       Emoji str(s) refer to the emojis stored as unicode strings
       The mapping functions help to map these to only strings if that is what you desire
"""


def emoji_emotions_top_per_participant(chat: data.Chat, top: int = 1) -> {str: [(str, int)]}:
    """
    Returns for each participant what emotions (s)he wants to convey the most.
    {participant: [(emotion, count)]}
    """
    # output and initialization of output
    output: {str: [(str, int)]} = {}
    for participant in chat.participants:
        output[participant.name] = []

    # counts how many times the emotion is used per participant
    count_per_participant = emoji_emotion_count_per_participant(chat)
    for participant in count_per_participant:
        count = count_per_participant[participant]  # just giving it a name
        # sort it by the count
        sorted_emotions = list(sorted(count, key=lambda emotion: count[emotion], reverse=True))

        # map to output format while filtering out the emotions which are not used
        result_list = list(map(lambda emotion: (emotion, count[emotion]),
                               filter(lambda e: count[e] > 0, sorted_emotions)))

        # we return the first 'top' results, if there aren't enough in the list then we return the whole list
        output[participant] = [] if len(result_list) is 0 else result_list[:min(top, len(result_list))]

    return output


def emoji_strs_top_per_participant(chat: data.Chat, top: int = 1) -> {str: [(str, int)]}:
    """
    Returns the most used emojis for each participant. The number indicates how many emojis it
    returns.
    """
    output: {str, [str]} = {}
    emoji_grouped = emoji_strs_each_count_per_participant(chat)

    for participant in emoji_grouped.keys():
        # set default value
        output[participant] = []

        # sort the group by emoji count
        sorted_emojis = sorted(emoji_grouped[participant], key=lambda t: t[1], reverse=True)

        for i in range(min(top, len(sorted_emojis))):
            output[participant].append(sorted_emojis[i])

    return output


def emoji_emotion_count_per_participant(chat: data.Chat) -> {str: {str: int}}:
    """
    Returns for each participant how many times (s)he used the given emotions.
    {participant: {emotion: count}}
    """
    # output and initialization of output
    output: {str: {str: int}} = {}
    for participant in chat.participants:
        output[participant.name] = {}
        for emotion in FEmoji.all_emotions:
            output[participant.name][emotion] = 0

    for msg in emoji_messages(chat):
        for emotion in facebook_emojis.get_emoji(msg.content).emotions:
            output[msg.sender][emotion] += 1

    return output


def emoji_strs_each_count_per_participant(chat: data.Chat) -> {str: [(str, int)]}:
    """
    This function returns for each participant the grouped emoji count that means if the participant sent
    5 of the crying emoji the map will have {participant_name: [..., (:crying:, 5), ...]
    """
    output: {str: [(data.Message, int)]} = {}
    all_emoji: {str: [data.Message]} = emoji_messages_per_participant(chat)

    for participant in all_emoji.keys():
        # add default value
        output[participant] = []

        # first we sort the emojis then we can count how many there are of each easily
        # by counting the ones next to each other
        sorted_emojis: [data.Message] = sorted(all_emoji[participant], key=emoji_map_to_str)

        if len(sorted_emojis) <= 0:
            continue

        # in these we'll count how many there are of the currently counted
        # all of them should be next to each other
        curr_emoji = emoji_map_to_str(sorted_emojis[0])
        curr_count = 1
        for i in range(1, len(sorted_emojis)):
            # there is still more of the one currently being counter
            if emoji_map_to_str(sorted_emojis[i]) == curr_emoji:
                curr_count += 1
            else:  # a new emoji has begun appearing
                # store the old one
                output[participant].append((curr_emoji, curr_count))

                # set the new one to be the current one
                curr_emoji = emoji_map_to_str(sorted_emojis[i])
                curr_count = 1

    return output


def emoji_emotions_count(chat: data.Chat) -> {str: int}:
    """
    Returns what emotions can be found in the chat and how many times. If there is 0 of that emotion that WILL BE
    INCLUDED as well.
    """
    output: {str: int} = {}
    for emotion in FEmoji.all_emotions:
        output[emotion] = 0

    for msg in emoji_map_to_strs(emoji_messages(chat)):
        for emotion in facebook_emojis.get_emoji(msg).emotions:
            output[emotion] += 1

    return output


def emoji_strs_count_per_participant(chat: data.Chat) -> {str: int}:
    """
    Returns how many emojis each participant sent in the chat
    """
    output: {str, int} = {}
    all_emojis = emoji_messages_per_participant(chat)

    for participant in all_emojis.keys():
        output[participant] = len(all_emojis[participant])

    return output


def emoji_emotions_monthly(chat: data.Chat) -> {datetime.date: {str: {str: int}}}:
    """
    Returns for each month the chat was active, the per participant emotions conveyed by emojis.
    {month: {participant: {emotion, count}}}
    """
    months = all_months(chat)
    months.append(months[len(months) - 1] + datetime.timedelta(days=33))  # add an extra date for messages after last dt
    messages = emoji_messages(chat)

    # We go through the months and while the messages's date is smaller than the current month we add it to a dict
    # of {participant: {emotion: count}}. msg_at represents where we are in the messages lst so we don't have to start
    # over each time.
    output: {datetime.date: {str: {str: int}}} = {}
    msg_at = 0
    for month_at in range(1, len(months)):
        month = months[month_at]  # we are currently adding emojis till this month
        data: {str: {str: int}} = {}

        # add all participants
        for participant in chat.participants:
            data[participant.name] = {}

        # we go through the messages
        while msg_at < len(messages) and messages[msg_at].date.date() < month:
            msg = messages[msg_at]
            # get emoji object
            f_emoji_obj: FEmoji = facebook_emojis.get_emoji(emoji_map_to_str(msg))

            # add one to all emotions this emoji conveys
            for emotion in f_emoji_obj.emotions:
                data[msg.sender][emotion] = data[msg.sender].get(emotion, 0) + 1

            msg_at += 1

        # we reached the end of the emojis that are before the current month
        output[months[month_at - 1]] = data

    return output


def emoji_messages_per_participant(chat: data.Chat) -> {str: [data.Message]}:
    """
    Returns messages that only contain emoji(s) for each participant (the messages that contain emojis and text are
    mapped to containing only emojis)
    """
    output: {str: [data.Message]} = {}

    # set default values
    for participant in chat.participants:
        output[participant.name] = []

    # collect them
    for msg in emoji_messages(chat):
        # check whether the message contains an emoji
        output[msg.sender].append(msg)

    return output


def emoji_whole_messages_per_participant(chat: data.Chat) -> {str: [data.Message]}:
    """
    Returns messages that contain emoji(s) for each participant
    """
    output: {str: [data.Message]} = {}

    # set default values
    for participant in chat.participants:
        output[participant.name] = []

    # collect them
    for msg in chat.messages:
        # check whether the message contains an emoji
        if not msg.is_special_message() and re.search(emoji.get_emoji_regexp(), msg.content):
            output[msg.sender].append(msg)

    return output


def emoji_messages(chat: data.Chat) -> [data.Message]:
    """
    Returns all the messages that contain emojis but they no longer contain the text, only the emojis
    """
    def only_emojis(msg: data.Message) -> [data.Message]:
        msgs = []

        # we need to make new messages if there are multiple emojis in the message given
        # we append them to them msgs list
        for ch in msg.content:
            if ch in emoji.UNICODE_EMOJI:
                msgs.append(data.Message(msg.sender, msg.time_stamp, ch, msg.msg_type))

        return msgs

    # we get lists from the only_emojis function so we need to flatten the list
    return [item for sublist in list(map(only_emojis, emoji_whole_messages(chat))) for item in sublist]


def emoji_whole_messages(chat: data.Chat) -> [data.Message]:
    """
    Returns the messages that contain emojis in chronological order
    """
    return list(filter(lambda msg: not msg.is_special_message() and re.search(emoji.get_emoji_regexp(), msg.content),
                       chat.messages))


def emoji_map_to_strs_per_participant(data: {str: [data.Message]}) -> {str: [str]}:
    """
    After using one of the emoji methods that returns emoji messages per participant you can use this function to only
    get the emoji strings
    """
    return {name: emoji_map_to_strs(data[name]) for name in data}


def emoji_map_to_strs(messages: [data.Message]) -> [str]:
    """
    After using one of the emoji methods you can use this to get only the emoji strings back, instead of the
    message objects
    """
    return list(map(emoji_map_to_str, messages))


def emoji_map_to_str(message: data.Message) -> str:
    """
    After using one of the emoji methods you can use this to get only the emoji string back, instead of the
    message object
    """
    return message.content


""" ___________________________________________________________________________________________
                                        Search
    ___________________________________________________________________________________________
"""


def _search_in_message_word(chat: data.Chat, word: str, ignore_case=False) -> {str: [data.Message]}:
    """
    Searches a word in the not special message contents
    :param chat: In which chat we want to search
    :param word: The word which we want to match
    :param ignore_case: Ignore cases or not?
    :return: A map {participant: [Messages]}
    """
    output = {}

    # add default values
    for participant in chat.participants:
        output[participant.name] = []

    for msg in chat.messages:
        found_at = (msg.content.lower() if ignore_case else msg.content).find(word)

        if not msg.is_special_message() and found_at >= 0:
            # adding coloring to the part where the substring was found
            new_content = msg.content[:found_at] + Fore.GREEN + msg.content[found_at:found_at + len(word)] + Fore.RESET\
                          + msg.content[found_at + len(word):]

            # making a new message object so we don't modify the one given as parameter
            m = data.Message(msg.sender, msg.time_stamp, new_content, msg.msg_type)
            output[msg.sender].append(m)

    return output


def _search_in_message_regex(chat: data.Chat, regex: str, ignore_case=False) -> {str: [data.Message]}:
    """
    Searches in the not special message contents with regex enabled
    :param chat: In which chat we want to search
    :param regex: The regex
    :param ignore_case: Ignore cases or not?
    :return: A map {participant: [Messages]}
    """
    output = {}

    # add default values
    for participant in chat.participants:
        output[participant.name] = []

    for msg in chat.messages:
        # naming it something random so it does not intersect with the user's groups
        search = re.search("(?P<fyop>" + regex + ")", msg.content.lower() if ignore_case else msg.content)

        if not msg.is_special_message() and search:
            found_start = search.start("fyop")
            found_end = search.end("fyop")

            # adding coloring to the part where the substring was found
            new_content = msg.content[:found_start] + Fore.GREEN + msg.content[found_start:found_end] + Fore.RESET \
                           + msg.content[found_end:]

            # making a new message object so we don't modify the one given as parameter
            m = data.Message(msg.sender, msg.time_stamp, new_content, msg.msg_type)
            output[msg.sender].append(m)

    return output


def search_in_messages(chat: data.Chat, word: str = None, regex: str = None, ignore_case=False) ->\
        {str: [data.Message]}:
    """
    We search in the given messages either with regex or just a plain word. If the regex is given
    then that will be the preferred type.
    :param chat: The chat we want to search in
    :param word: Word we want to match
    :param regex: Regex we want to match
    :param ignore_case: Ignore cases or not?
    :return: A map {participant: [Messages]}
    """
    if regex is None and word is None:
        raise ValueError()
    elif regex is not None:
        return _search_in_message_regex(chat, regex, ignore_case)
    elif word is not None:
        return _search_in_message_word(chat, word, ignore_case)


""" ___________________________________________________________________________________________
                                    Character count
    ___________________________________________________________________________________________
"""


def character_count_per_participant_by_day(chat: data.Chat) -> {str: (datetime.date, int)}:
    """
    Returns for each participant how many characters (s)he sent on each day from the start of the conversation
    till today.
    """
    # this stores for each day how many messages were sent by each participant
    character_count = character_by_day(chat)

    return _count_per_participant_per_day(chat, character_count)


def avg_character_count(chat: data.Chat) -> {str: float}:
    """
    This function returns how many characters each participant uses on average in each message
    It also omits the special messages which contain media
    """

    output: {str, float} = {}
    msg_count = message_count(chat)
    char_count = character_count(chat)

    # average them
    for participant in chat.participants:
        output[participant.name] = char_count[participant.name] / msg_count[participant.name]

    return output


def character_by_day(chat: data.Chat) -> [(datetime.date, {str: int})]:
    """
    This function returns for each active day how many characters were exchanged by each participant
    """
    output = []
    # messages in chronological order
    msgordered: [data.Message] = chat.messages

    # on which day we currently are
    curr_date: (datetime.date, {str: int}) = (msgordered[0].date.date(),
                                              {msgordered[0].sender: msgordered[0].character_count()})
    for i in range(1, len(msgordered)):
        # we are still on same day
        if (msgordered[i].date.date() - curr_date[0]).days == 0:
            # add to character count of the person
            curr_date[1][msgordered[i].sender] = curr_date[1].get(msgordered[1].sender, 0) \
                                                 + msgordered[i].character_count()
        else:
            output.append(curr_date)

            # new date
            curr_date = (msgordered[i].date.date(), {msgordered[i].sender: msgordered[i].character_count()})

    # add last
    output.append(curr_date)

    return output


def character_count(chat: data.Chat) -> {str: int}:
    """
    Returns the sum of character counts for each participant in a chat. If the message is a special
    message (for example a photo or a gif) then that message won't be summed.
    """
    output: {str, int} = {}

    # default char count
    for participant in chat.participants:
        output[participant.name] = 0

    for msg in chat.messages:
        if not msg.is_special_message():
            output[msg.sender] += msg.character_count()

    return output


""" ___________________________________________________________________________________________
                                Response count/time
    ___________________________________________________________________________________________
"""


def response_count(chat: data.Chat) -> {str: int}:
    """
    This function returns how many times each participant responded
    """
    responses = chat.get_responses()
    output: {str, int} = {}

    # count starts at 0
    for participant in chat.participants:
        output[participant.name] = 0

    for response in responses:
        output[response.sender] += 1

    return output


def avg_response_time(chat: data.Chat) -> {str: float}:
    """
    This function calculates the average response times with the overnight responses taken into consideration.
    May return None if there were no responses
    """
    # it will collect the sum in output and the count of responses to response_counter
    # at the end of the function we will divide output by counter
    output: {str, float} = {}
    response_counter: {str, int} = response_count(chat)

    responses = chat.get_responses()

    # add participants to output
    for participant in chat.participants:
        output[participant.name] = 0

    # go in order of time (oldest first)
    last_response: data.Response = next(responses, None)
    if last_response is None:
        return None
    for response in responses:
        # add to the counter and sum
        output[response.sender] += (response.date_time - last_response.date_time).seconds

        last_response = response

    # calculate average
    for participant in chat.participants:
        if response_counter[participant.name] != 0:
            output[participant.name] /= response_counter[participant.name]
        else:
            del output[participant.name]

    return output


def avg_response_time_no_overnight(chat: data.Chat) -> {str: float}:
    """
    This function returns average response time for each participant. It is calculated by
    separating each day and calculating response time for each one and then averaging those.
    May return None if there were no responses.
    """
    # it will collect the sum in output and the count of responses to response_counter
    # at the end of the function we will divide output by counter
    output: {str, float} = {}
    response_counter: {str, int} = response_count(chat)

    # this returns for each day the sum of response times and the response counters
    _response_sum_by_day = _response_times_sum_by_day(chat)

    if _response_sum_by_day is None:
        return None

    # define default value for each
    for participant in chat.participants:
        output[participant.name] = 0

    # sum up each day
    # day_data: (date, {participant: (count, sum)})
    for day_data in _response_sum_by_day:
        for participant in day_data[1]:
            output[participant] += day_data[1][participant][1]

    # divide the sum by count to get average
    for participant in chat.participants:
        if response_counter[participant.name] != 0:
            output[participant.name] /= response_counter[participant.name]
        else:
            del output[participant.name]

    return output


def avg_response_time_by_day(chat: data.Chat) -> [(datetime.date, {str: float})]:
    """
    This function returns day by day how many seconds it took for each participant to respond on average
    :param chat: The chat to analyze
    :return: A list of tuples of dates and data sorted in order. May return none if there were no responses
    """

    output: [(datetime.date, {str: float})] = []
    time_sums_by_day = _response_times_sum_by_day(chat)

    if time_sums_by_day is None:
        return None

    # map to output data (we need to calculate average)
    output_avgs = {}
    for data in time_sums_by_day:
        for participant in data[1].keys():
            response_count_sum = data[1][participant]
            output_avgs[participant] = response_count_sum[1] / response_count_sum[0]

        # add to output
        output.append((data[0], output_avgs))

        output_avgs = {}

    return output


def _response_times_sum_by_day(chat: data.Chat) -> [(datetime.date, {str: (int, float)})]:
    """
    This function returns for each day: {responder: (sum of response times, response count)}.
    Ensures that only the dates and participants with responses are added to the list.
    May return None if there were no responses in the chat
    """
    output: [(datetime.date, {str: (int, float)})] = []
    response_ordered = chat.get_responses()

    # this will store what day we are currently on and the counters and response times for each participant
    data_for_day: (datetime.date, {str: (int, float)}) = (datetime.date(1990, 1, 1), {})
    last_response = next(response_ordered, None)

    # there were no responses
    if last_response is None:
        return None
    # go in order of time (oldest first)
    for response in response_ordered:
        # next message is still on same day
        if (response.date_time.date() - data_for_day[0]).days == 0:
            # the response count and time sum so far
            rspns_cs: (int, float) = data_for_day[1].get(response.sender, (0, 0.0))

            # add to it
            new_count = rspns_cs[0] + 1
            new_sum = rspns_cs[1] + (response.date_time - last_response.date_time).seconds

            # put it back
            data_for_day[1][response.sender] = (new_count, new_sum)
        else:  # we got to at least next day
            # there were responses
            if len(data_for_day[1].keys()) != 0:
                # add to output
                output.append(data_for_day)

            # the next day is coming
            data_for_day = (response.date_time.date(), {})

        last_response = response

    # add last
    output.append(data_for_day)

    return output


""" ___________________________________________________________________________________________
                                Message count/time
    ___________________________________________________________________________________________
"""


def message_count_per_participant_by_day(chat: data.Chat) -> {str: (datetime.date, int)}:
    """
    Returns for each participant how many messages (s)he sent on each day from the start of the conversation
    till today.
    """
    # this stores for each day how many messages were sent by each participant
    msg_counts = message_by_day(chat)

    return _count_per_participant_per_day(chat, msg_counts)


def message_by_day(chat: data.Chat) -> [(datetime.date, {str: int})]:
    """
    This function returns day by day how many messages were exchanged from each participant
    :param chat: The chat to analyze
    :return: A list of tuples of dates and count data stored in order
    """

    output: [(datetime.date, {str, int})] = []
    msgordered: [data.Message] = chat.messages

    if len(msgordered) > 0:
        # this will store what day we are currently on and the counters for each participant
        counter_for_day = (msgordered[0].date.date(), {msgordered[0].sender: 1})
        # go in order of time (oldest first)
        for i in range(1, len(msgordered)):
            # next message is still on same day
            if (msgordered[i].date.date() - counter_for_day[0]).days == 0:
                # add one to the sender's counter (if it does not exist set it to 1)
                counter_for_day[1][msgordered[i].sender] = 1 + counter_for_day[1].get(msgordered[i].sender, 0)
            else:  # we got to at least next day
                output.append(counter_for_day)  # add the last day to output
                counter_for_day = (msgordered[i].date.date(), {msgordered[i].sender: 1})  # make this day the current

        # add last one
        output.append(counter_for_day)

    return output


def message_count(chat: data.Chat) -> {str: int}:
    """
    Returns the message count for each participant in the given chat
    :param chat: Which conversation to analyze
    :return: A dictionary of { "participant": count }
    """
    msg_counts = {}

    # add each participant
    for participant in chat.participants:
        msg_counts[participant.name] = 0

    # go through the messages and count them
    for msg in chat.messages:
        msg_counts[msg.sender] += 1

    return msg_counts


""" ___________________________________________________________________________________________
                                        Dates
    ___________________________________________________________________________________________
"""


def all_days(chat: data.Chat) -> [datetime.date]:
    """
    Returns all days in a list between the start of conversation and today.
    May return None if there were no active dates
    """
    # get the start and end dates
    date_btwn = date_between(chat)
    if date_btwn is None:
        return None
    date_btwn = (date_btwn[0], datetime.datetime.today())
    # for how many days the conversation went on
    day_count = (date_btwn[1] - date_btwn[0]).days

    return [(date_btwn[0] + datetime.timedelta(days=x)).date() for x in range(day_count)]


def all_months(chat: data.Chat) -> [datetime.date]:
    """
    Returns all months in a list between the start of the conversation and today
    May return None if there were no active dates
    """
    date_btwn = date_between(chat)
    if date_btwn is None:
        return None
    curr_date = datetime.date(date_btwn[0].year, date_btwn[0].month, 1)
    last_date = datetime.date.today()
    new_date: datetime.date = curr_date

    output: [datetime.date] = []
    while new_date <= last_date:
        output.append(new_date)
        if new_date.month >= 12:
            new_date = datetime.date(new_date.year + 1, 1, 1)
        else:
            new_date = datetime.date(new_date.year, new_date.month + 1, 1)

    return output


def get_from_to_date(chat: data.Chat, from_date: datetime.date, to_date: datetime.date) -> [data.Message]:
    """
    Returns messages inside the given from and till date. Inclusive on both sides
    """
    return list(filter(lambda msg: from_date <= msg.date.date() <= to_date, chat.messages))


def active_dates(chat: data.Chat) -> [datetime.date]:
    """
    Returns on which dates the chat was active.
    May return None if there were no active dates
    """
    output: [datetime.date] = []

    # ordered by time (oldest first)
    msgordered: [data.Message] = chat.messages
    if len(msgordered) == 0:
        return None

    curr_date = msgordered[0].date.date()
    output.append(curr_date)
    for i in range(1, len(msgordered)):
        new_date = msgordered[i].date.date()

        # found a new date
        if (new_date - curr_date).days != 0:
            output.append(new_date)
            curr_date = new_date

    return output


def date_between(chat: data.Chat) -> (datetime.datetime, datetime.datetime):
    """
    Returns between what dates the conversation went on
    """
    msgordered: [data.Message] = chat.messages

    return msgordered[0].date, msgordered[len(msgordered) - 1].date


"""_____________________________________________________________________________
                                MISC
    ____________________________________________________________________________
"""


def get_messages_only_by(chat: data.Chat, participants: [str]) -> data.Chat:
    """
    Returns messages only by the participants that are given. The names are checked in lower case ascii form
    and any of the given participants is a substring of
    """
    new_chat = data.Chat(chat.msg_folder_path, chat.media_folder_path, chat.name)
    # map filter participants to correct ascii lower case
    participants = list(map(lambda n: unicodedata.normalize("NFD", n.lower()).encode("ASCII", "ignore").decode("UTF-8"),
                            participants))
    # map the participants of the chat to an ascii lower case name plus the original name
    chat_participants = list(
        map(lambda p: (unicodedata.normalize("NFD", p.name.lower()).encode("ASCII", "ignore").decode("UTF-8"), p.name),
            chat.participants)
    )

    # these are the real names of the participants that are accepted by the given list
    # first it filters them from the chat_participants list of tuples then maps them to be a single value rather than
    # a tuple
    accept_participants = list(map(lambda t: t[1],
                                   filter(lambda p: any(map(lambda participant: participant in p[0], participants)),
                                          chat_participants)))

    new_chat.participants = list(map(lambda name: data.Participant(name), accept_participants))

    if len(accept_participants) > 0:
        new_messages = list(filter(lambda msg: msg.sender in accept_participants, chat.messages))
        new_chat.messages = new_messages

    return new_chat


def _count_per_participant_per_day(chat: data.Chat, data: [(datetime.date, {str: int})]) -> {str: (datetime.date, int)}:
    """
    Returns for each participant how many of the data (s)he had on each day from the start of the conversation
    till today. It sums them together. It changes how the data is stored.
    :param data: [(on what day, {participantName, dataCount}]
    :return: {participantName: (date, count)}
    """
    if len(chat.participants) == 0:
        return {}

    # get all dates between start and end
    dates: [datetime.date] = all_days(chat)

    # this stores for each participant how many messages they sent for each day
    counts_each_participant = {}
    # add default values
    for participant in chat.participants:
        counts_each_participant[participant.name] = []

    data_index = 0
    for date in dates:
        # we are on the date when there were messages
        if data_index < len(data) and (date - data[data_index][0]).days == 0:
            # for each participant we add the current day
            for participant in chat.participants:
                data_c = data[data_index][1].get(participant.name, 0)

                counts_each_participant[participant.name].append(data_c)

            data_index += 1
        else:  # there is no data for this day -> add 0s
            for participant in chat.participants:
                counts_each_participant[participant.name].append(0)

    return counts_each_participant
