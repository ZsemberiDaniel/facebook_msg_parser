from data import data
import datetime


def avg_character_count(chat: data.Chat) -> {str, float}:
    """
    This function returns how many characters each participant uses on average in each message
    It also omits the special messages which contain media
    """

    output: {str, float} = {}
    msg_count = message_count(chat)

    # count characters
    for msg in chat.messages:
        output[msg.sender] += msg.character_count()

    # average them
    for participant in chat.participants:
        output[participant.name] /= msg_count[participant.name]

    return output


def character_count(chat: data.Chat) -> {str, int}:

    output: {str, int} = {}

    # default char count
    for participant in chat.participants:
        output[participant.name] = 0


def response_count(chat: data.Chat) -> {str, int}:
    """
    This function returns how many times each participant responded
    """
    response_times = _response_times(chat)
    output: {str, int} = {}

    # count starts at 0
    for participant in chat.participants:
        output[participant.name] = 0

    for response in response_times:
        output[response[0]] += 1

    return output


def avg_response_time(chat: data.Chat) -> {str, float}:
    """
    This function calculates the average response times with the overnight responses taken into consideration
    """
    # it will collect the sum in output and the count of responses to response_counter
    # at the end of the function we will divide output by counter
    output: {str, float} = {}
    response_counter: {str, int} = response_count(chat)

    response_times = _response_times(chat)

    # add participants to output
    for participant in chat.participants:
        output[participant.name] = 0

    # go in order of time (oldest first)
    for response in response_times:
        # add to the counter and sum
        output[response[0]] += response[1]

    # calculate average
    for participant in chat.participants:
        if response_counter[participant.name] != 0:
            output[participant.name] /= response_counter[participant.name]
        else:
            del output[participant.name]

    return output


def _response_times(chat: data.Chat) -> [(str, float)]:
    """
    Returns the response times and who responded in order of appearance
    """
    output: [(str, float)] = []
    msgordered: [data.Message] = list(iter(chat.messages))

    # go in order of time (oldest first)
    for i in range(1, len(msgordered)):
        # check whether it is a response (aka before message is not the same person)
        if msgordered[i].sender != msgordered[i - 1].sender:
            # add the output
            output.append((msgordered[i].sender, (msgordered[i].date - msgordered[i - 1].date).total_seconds()))

    return output


def avg_response_time_day(chat: data.Chat) -> {str, float}:
    """
    This function returns average response time for each participant. It is calculated by
    separating each day and calculating response time for each one and then averaging those
    """
    # it will collect the sum in output and the count of responses to response_counter
    # at the end of the function we will divide output by counter
    output: {str, float} = {}
    response_counter: {str, int} = response_count(chat)

    # this returns for each day the sum of response times and the resposne counters
    _response_sum_by_day = _response_times_sum_by_day(chat)

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
    :return: A list of tuples of dates and data sorted in order
    """

    output: [(datetime.date, {str: float})] = []
    time_sums_by_day = _response_times_sum_by_day(chat)

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
    This function returns for each day: {responder: (sum of response times, response count)}
    """
    output: [(datetime.date, {str: (int, float)})] = []
    msgordered: [data.Message] = list(iter(chat.messages))

    # this will store what day we are currently on and the counters and response times for each participant
    data_for_day: (datetime.date, {str: (int, float)}) = (msgordered[0].date.date(), {})
    # go in order of time (oldest first)
    for i in range(1, len(msgordered)):
        # next message is still on same day
        if (msgordered[i].date.date() - data_for_day[0]).days == 0:
            # check whether it is a response (aka before message is not the same person)
            if msgordered[i].sender != msgordered[i - 1].sender:
                # the response count and time sum so far
                rspns_cs: (int, float) = data_for_day[1].get(msgordered[i].sender, (0, 0.0))

                # add to it
                new_count = rspns_cs[0] + 1
                new_sum = rspns_cs[1] + (msgordered[i].date - msgordered[i - 1].date).total_seconds()

                # put it back
                data_for_day[1][msgordered[i].sender] = (new_count, new_sum)
        else:  # we got to at least next day
            # there were responses
            if len(data_for_day[1].keys()) != 0:
                # add to output
                output.append(data_for_day)

            # the next day is coming
            data_for_day = (msgordered[i].date.date(), {})

    return output


def message_by_day(chat: data.Chat) -> [(datetime.date, {str: int})]:
    """
    This function returns day by day how many messages were exchanged from each participant
    :param chat: The chat to analyze
    :return: A list of tuples of dates and count data sotred in order
    """

    output: [(datetime.date, {str, int})] = []
    msgordered: [data.Message] = list(iter(chat.messages))

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
            counter_for_day = (msgordered[i].date.date(), {msgordered[i].sender: 1})  # make this day the current one

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
    for msg in iter(chat.messages):
        msg_counts[msg.sender] += 1

    return msg_counts
