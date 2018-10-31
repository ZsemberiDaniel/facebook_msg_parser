import matplotlib.pyplot as plotlib
import matplotlib.ticker as ticker
import random
import os
from matplotlib.gridspec import GridSpec
from datetime import datetime, timedelta
from math import ceil
from PIL import Image, ImageDraw, ImageFont
from controller import chat_analyzer
from data import data
from data import facebook_emojis as fe
from definitions import ROOT_DIR


title_font = ImageFont.truetype(os.path.join(ROOT_DIR, "fonts", "Roboto-Bold.ttf"), 32)
title_color = (38, 50, 56, 255)
year_font = ImageFont.truetype(os.path.join(ROOT_DIR, "fonts", "Roboto-Regular.ttf"), 24)
year_color = (69, 90, 100, 255)


def plot_emoji_emotions_monthly(chat: data.Chat, size=(1000, 500), title="Emoji emotions monthly"):
    # theses will be used to make the bars
    x_axes = chat_analyzer.all_months(chat)
    per_participant: {str: {str: []}} = {}  # per participant per emotion
    max_per_participant: {str: int} = {}  # we need to store what is the max amount of one emotion for each participant
                                          # for plotting purposes. Later we calculate this while mapping data
    # initial values
    for participant in chat.participants:
        per_participant[participant.name] = {}
        max_per_participant[participant.name] = 0

        for emotion in fe.Emoji.all_emotions:
            per_participant[participant.name][emotion] = []

    # we need to map this data to per participants instead of per months
    per_month: {datetime.date: {str: {str: int}}} = chat_analyzer.emoji_emotions_monthly(chat)

    for month in per_month:
        for participant in per_month[month]:
            for emotion in fe.Emoji.all_emotions:
                count_from_emotion = per_month[month][participant].get(emotion, 0)
                per_participant[participant][emotion].append(count_from_emotion)

                # here we are calculating the max of the count
                if count_from_emotion > max_per_participant[participant]:
                    max_per_participant[participant] = count_from_emotion

    # PLOTTING

    # font sizes
    SMALL_FONT = size[0] / 200
    NORMAL_FONT = size[0] / 160
    BIGGER_FONT = size[0] / 100

    # formatting of x axes
    def x_major_tick_formatter(dt, pos) -> str:
        dt = datetime.fromordinal(int(dt))
        return "{:04d}-{:02d}".format(dt.year, dt.month)

    for participant in per_participant:
        figure: plotlib.Figure = plotlib.figure(figsize=(size[0] / 96, size[1] / 96))

        # we are making a grid of subplots based on all the emotions that can be conveyed so we base the row and
        # column count on the emotion count
        emotion_count = len(fe.Emoji.all_emotions)
        col_count = emotion_count // 3
        row_count = int(ceil(emotion_count / col_count)) + 2  # we add 2 for the !!! EXTREME SUBPLOT !!!
        gridspec = GridSpec(ncols=col_count, nrows=row_count, figure=figure)

        for x in range(col_count):
            for y in range(row_count - 2):
                emotion_at = x * (row_count - 2) + y
                if emotion_at >= emotion_count:  # we need to continue because there are no emotions left 😭
                    continue

                # what emotion we are currently plotting
                emotion = fe.Emoji.all_emotions[emotion_at]

                # set font sizes for plot
                plotlib.rc("xtick", labelsize=NORMAL_FONT)
                plotlib.rc("ytick", labelsize=NORMAL_FONT)
                plotlib.rc("legend", fontsize=SMALL_FONT)

                # adding to grid
                axes: plotlib.Axes = figure.add_subplot(gridspec[y, x])

                # plotting the bars
                axes.plot(x_axes, per_participant[participant][emotion], color=fe.Emoji.emotion_colors[emotion_at])

                # giving title
                axes.set_title("".join(emotion[0].upper() + emotion[1:]))

                # hide top bottom
                axes.spines["right"].set_visible(False)
                axes.spines["top"].set_visible(False)

                # axis settings
                axes.xaxis.set_major_formatter(ticker.FuncFormatter(x_major_tick_formatter))

                # the ticks for the y axis. We don't want too many, so we divide by 'n' to get exactly 'n'
                y_ticks = list(range(0, max_per_participant[participant], max_per_participant[participant] // 4))
                axes.yaxis.set_ticks(y_ticks)

        # BEWARE! DANGER!
        # H E R E   C O M E S   T H E   E X T R E M E   S U B P L O T
        extreme_axes: plotlib.Axes = figure.add_subplot(gridspec[-2:, :])

        # set font sizes for plot
        plotlib.rc("xtick", labelsize=BIGGER_FONT)
        plotlib.rc("ytick", labelsize=BIGGER_FONT)
        plotlib.rc("legend", fontsize=NORMAL_FONT)

        emotion_at = 0
        for emotion in fe.Emoji.all_emotions:
            extreme_axes.plot(x_axes, per_participant[participant][emotion], color=fe.Emoji.emotion_colors[emotion_at])

            emotion_at += 1

        # hide top bottom
        extreme_axes.spines["right"].set_visible(False)
        extreme_axes.spines["top"].set_visible(False)

        # axis settings
        extreme_axes.xaxis.set_major_formatter(ticker.FuncFormatter(x_major_tick_formatter))

        # TODO: title not inside the plot. Internet does not know how to do it
        figure.suptitle(title + " (" + participant + ")")
        plotlib.show()


def plot_message_distribution(chat: data.Chat, size=(1000, 500), title="Message distribution"):
    """
    Plots the message distribution over hours per participant
    :param chat: What to analyze
    :param size: What size the chart should be
    :param title: What title to give the chart
    """
    figure: plotlib.Figure = plotlib.figure(figsize=(size[0] / 96, size[1] / 96))
    axes: plotlib.Axes = plotlib.axes()

    axes.grid(True, axis="y", color="#546E7A", linestyle="dotted")

    # font sizes
    SMALL_FONT = size[0]/100
    NORMAL_FONT = size[0]/80
    BIGGER_FONT = size[0]/50

    # set font sizes for plot
    plotlib.rc("xtick", labelsize=NORMAL_FONT)
    plotlib.rc("ytick", labelsize=NORMAL_FONT)
    plotlib.rc("legend", fontsize=SMALL_FONT)

    # formatting for y axis
    def hour_formatter(nmb: int, pos):
        hour = int(nmb // 3600)
        nmb -= hour * 3600
        minute = int(nmb // 60)
        nmb -= minute * 60
        sec = int(nmb)

        return "{0:02d}".format(hour) + ":" + "{0:02d}".format(minute) + ":" + "{0:02d}".format(sec)

    axes.yaxis.set_major_formatter(ticker.FuncFormatter(hour_formatter))
    axes.set_yticks(range(0, 86_401, 14_400))

    # title if given
    if title is not None:
        axes.set_title(title, fontsize=BIGGER_FONT)

    # this contains for each participant: (color, [dates], [when message was sent])
    data: {str: (str, [datetime], [timedelta])} = {}
    for participant in chat.participants:
        data[participant.name] = (random_color() + "20", [], [])

    # map messages to the data format above
    for msg in chat.messages:
        data[msg.sender][1].append(msg.date)
        data[msg.sender][2].append((msg.date - datetime.combine(msg.date.date(), datetime.min.time())).seconds)

    # do the plotting
    for participant in chat.participants:
        axes.scatter(x=data[participant.name][1], y=data[participant.name][2], s=size[0]/50, color=data[participant.name][0],
                     label=participant.name)

    # legend
    axes.legend(loc="best", fancybox=True, framealpha=1, shadow=True, borderpad=0.5)

    # hide top bottom
    axes.spines["right"].set_visible(False)
    axes.spines["top"].set_visible(False)

    plotlib.show()


def plot_emojis_per_participant_yearly(chat: data.Chat, image_width=1000, emoji_size=100,
                                       output_path="out" + os.path.sep):
    """
    Saves a separate image for each participant with their emojis for each year.
    :param chat: Which chat to plot
    :param image_width: The width of the image. The height will be calculated by how many emojis there are
    :param emoji_size: How big an emoji should be on the image
    :param output_path: Where to save. This is without the name of the file bit with a separator at the end.
    :return: None
    """
    msg_emojis = chat_analyzer.emoji_messages_per_participant(chat)
    # map to fe.Emoji objects
    for participant in msg_emojis.keys():
        new_list = []
        # get emojis from each message and this is also where the conversion to fe.Emoji happens
        for msg in msg_emojis[participant]:
            new_list += map(lambda a: (a, msg.date.year), fe.facebook_emojis.get_emojis_from_string(msg.content))

        msg_emojis[participant] = new_list

    for participant in chat.participants:
        _save_emojis_yearly(msg_emojis[participant.name], image_width, emoji_size,
                            output_path=output_path + "emojis_yearly_" + participant.name.replace(" ", "_"),
                            title="Emojis yearly by " + participant.name)


def plot_emojis_per_participant(chat: data.Chat, image_width=1000, emoji_size=100, output_path="out" + os.path.sep):
    """
    Saves a separate image for each participant with all of their emojis in chronological order.
    :param chat: Which chat to plot
    :param image_width: The width of the image. The height will be calculated by how many emojis there are
    :param emoji_size: How big an emoji should be on the image
    :param output_path: Where to save. This is without the name of the file bit with a separator at the end.
    :return: None
    """
    # get the string emojis first
    str_emojis: {str: [str]} = chat_analyzer.emoji_map_to_strs_per_participant(
        chat_analyzer.emoji_messages_per_participant(chat)
    )

    for participant in chat.participants:
        # we need to convert them to Emoji classes so we know where the image file is
        emojis = list(filter(lambda a: a is not None, map(fe.facebook_emojis.get_emoji, str_emojis[participant.name])))
        _save_emojis(emojis, image_width, emoji_size,
                     output_path=output_path + "emojis_all_" + participant.name.replace(" ", "_"),
                     title="All emojis by " + participant.name)


def _plot_emojis_header(image_width: int, padding: (int, int), title: str) -> Image.Image:
    """
    Makes a header width the given arguments
    :param image_width: What width the resulting image should be
    :param padding: What padding to give the image
    :param title: What the title of the header should be
    :return: An image object
    """
    #                   padding          title height
    header_height = int(padding[1] * 2 + title_font.getsize(title)[1] * 1.5)
    #               padding
    header_width = image_width + 2 * padding[0]

    created_title = Image.new("RGBA", (header_width, header_height), color="white")

    # draw the title
    img_draw = ImageDraw.ImageDraw(created_title)
    img_draw.text((5, 5), title, font=title_font, fill=title_color)

    return created_title


def _plot_emojis(emojis: [fe.Emoji], image_width: int, emoji_size: int, padding: (int, int)) -> Image.Image:
    """
    Makes a table of the given emojis
    :param emojis: The emojis to make the table out of
    :param image_width: What the resulting image's width should be
    :param emoji_size: What to make an emoji in size
    :param padding: What padding to add around the image
    :return: An image object
    """
    # how many emojis there are for each line in the image
    emoji_count_per_line = image_width // emoji_size

    # how many lines there are in the image
    line_count = int(ceil(len(emojis) / emoji_count_per_line))

    image_width += padding[0] * 2
    image_height = emoji_size * line_count + padding[1] * 2

    # create new image
    created_image: Image = Image.new("RGBA", (image_width, image_height), color="white")

    row = 0
    col = 0
    for emoji in emojis:
        # open then resize image
        emoji_image: Image = Image.open(emoji.path, "r").convert("RGBA").resize((emoji_size, emoji_size))

        # paste image to correct pos
        paste_x = padding[0] + col * emoji_size
        paste_y = row * emoji_size
        created_image.paste(emoji_image, (paste_x, paste_y, paste_x + emoji_size, paste_y + emoji_size), emoji_image)

        # increment column, if at the end go down by one row
        col += 1
        if col >= emoji_count_per_line:
            col = 0
            row += 1

    return created_image


def _save_emojis_yearly(emojis: [(fe.Emoji, int)], image_width, emoji_size, output_path, title, padding=(10, 10)):
    """
    Plots the emojis yearly from the given list which is expected to be sorted by the tuples's second variable, which
    is the year.
    """
    def _year_header(year: int) -> Image.Image:
        """
        Returns a header for the given year
        """
        y_image = Image.new("RGBA", (image_width, year_font.getsize(str(year))[1] + padding[1]), color="white")

        img_draw = ImageDraw.ImageDraw(y_image)
        img_draw.text((padding[0], padding[1] // 2), str(year), font=year_font, fill=year_color)

        return y_image

    # default stuff for each participant
    header_image = _plot_emojis_header(image_width, padding, title)
    year_images: [Image.Image] = []

    image_width += padding[0] * 2
    image_height = header_image.size[1]

    # collect each year's emojis in this list
    emojis_by_year: {int, [fe.Emoji]} = {}
    for (emoji, year) in emojis:
        l = emojis_by_year.get(year, [])
        l.append(emoji)
        emojis_by_year[year] = l

    # now go through each year
    for year in emojis_by_year.keys():
        # get header and image
        year_header = _year_header(year)
        year_image = _plot_emojis(emojis_by_year[year], image_width, emoji_size, padding)

        # add to outer list
        year_images += [year_header, year_image]

        # add to image height
        image_height += year_header.size[1] + year_image.size[1]

    # make the year image
    created_image = Image.new("RGBA", (image_width, image_height), color="white")
    created_image.paste(header_image, (padding[0], 0))

    # add all year images
    curr_y = header_image.size[1]
    for img in year_images:
        created_image.paste(img, (padding[0], curr_y))

        curr_y += img.size[1]

    _save_image(created_image, output_path)


def _save_emojis(emojis: [fe.Emoji], image_width, emoji_size, output_path, title, padding=(10, 10)):
    header_image = _plot_emojis_header(image_width, padding, title)
    emoji_image = _plot_emojis(emojis, image_width, emoji_size, padding)

    #              emoji table size      title size
    image_height = emoji_image.size[1] + header_image.size[1]
    #              padding
    image_width += 2 * padding[0]

    # create new image
    created_image: Image = Image.new("RGBA", (image_width, image_height), color="white")

    # copy header
    created_image.paste(header_image, (0, 0))
    created_image.paste(emoji_image, (0, header_image.size[1]))

    _save_image(created_image, output_path)


def _save_image(image: Image.Image, path: str):
    """
    Helper function, which saves the given image to the given path
    """
    # if we want to create the file to a non-existent directory make one
    parent_dir = os.path.abspath(os.path.join(path, os.pardir))
    if not os.path.exists(parent_dir):
        os.mkdir(parent_dir)

    # save image
    image.save(path + ".png")


def plot_activity_char(chat: data.Chat, size=(1000, 750)):
    """
    Plots the activity based on the character count with a line chart
    """
    dates = chat_analyzer.all_days(chat)
    counts_each_participant = chat_analyzer.character_count_per_participant_by_day(chat)

    _plot_for_each_participant(chat, dates, counts_each_participant, title="Character counts", size=size)


def plot_activity_msg(chat: data.Chat, size=(1000, 750)):
    """
    Plots the activity based on message counts with a line chart
    """
    dates = chat_analyzer.all_days(chat)
    counts_each_participant = chat_analyzer.message_count_per_participant_by_day(chat)

    _plot_for_each_participant(chat, dates, counts_each_participant, title="Message counts", size=size)


def _plot_for_each_participant(chat: data.Chat, x_axes: [], values: {str: []}, title=None, size=(1000, 750)):
    """
    Makes a plot that has data for all the participants.
    :param chat: The chat for which we want to make the plot
    :param x_axes: What to show for the x axes values
    :param values: What values to show {participantName: [values]}
    """
    NORMAL_FONT = size[0]/80
    BIGGER_FONT = size[0]/50

    with plotlib.style.context("fivethirtyeight"):
        # set font sizes for plot
        plotlib.rc("xtick", labelsize=NORMAL_FONT)
        plotlib.rc("ytick", labelsize=NORMAL_FONT)
        plotlib.rc("legend", fontsize=BIGGER_FONT)

        # create plotlib classes
        plotlib.figure(figsize=(size[0] / 96, size[1] / 96))
        axes: plotlib.Axes = plotlib.axes()

        # set title if one was given
        if title is not None:
            axes.set_title(title, fontsize=BIGGER_FONT)

        # plot all participant
        for participant in chat.participants:
            color = random_color() + "5D"
            axes.plot(x_axes, values.get(participant.name, []), label=participant.name, color=color)

        axes.legend(loc="upper left", fancybox=True, framealpha=1, shadow=True, borderpad=0.5)

        plotlib.show()


colors = ["#B71C1C", "#4527A0", "#1565C0", "#2E7D32", "#EF6C00", "#4E342E", "#212121"]


def random_color() -> str:
    return colors[random.randint(0, len(colors) - 1)]
