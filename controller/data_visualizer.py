import matplotlib.pyplot as plotlib
import random
from controller import chat_analyzer
from data import data
import datetime


def plot_activity_msg(chat: data.Chat):
    # get the start and end dates
    date_between = chat_analyzer.date_between(chat)
    # for how many days the conversation went on
    day_count = (date_between[1] - date_between[0]).days

    # this stores for each day how many messages were sent by each participant
    msg_counts = chat_analyzer.message_by_day(chat)

    # get all dates between start and end
    dates: [datetime.date] = [(date_between[0] + datetime.timedelta(days=x)).date() for x in range(day_count)]

    # this stores for each participant how many messages they sent for each day
    counts_each_participant = {}
    # add default values
    for participant in chat.participants:
        counts_each_participant[participant.name] = []

    msg_index = 0
    for date in dates:
        # we are on the date when there were messages
        if (date - msg_counts[msg_index][0]).days == 0:
            # for each participant we add the current day
            for participant in chat.participants:
                msg_c = msg_counts[msg_index][1].get(participant.name, 0)

                counts_each_participant[participant.name].append(msg_c)

            msg_index += 1
        else:  # there is no data for this day -> add 0s
            for participant in chat.participants:
                counts_each_participant[participant.name].append(0)

    with plotlib.style.context("fivethirtyeight"):
        # create plotlib classes
        figure: plotlib.Figure = plotlib.figure(figsize=(30, 15))
        axes: plotlib.Axes = plotlib.axes()

        # plot all participant
        for participant in chat.participants:
            color = random_color()
            axes.plot(dates, counts_each_participant[participant.name], label=participant.name,
                      color=color)

        axes.legend(loc="upper left", fancybox=True, framealpha=1, shadow=True, borderpad=0.5)

        plotlib.show()


colors = ["#B71C1C", "#4527A0", "#1565C0", "#2E7D32", "#EF6C00", "#4E342E", "#212121"]


def random_color() -> str:
    return colors[random.randint(0, len(colors) - 1)] + "5D"
