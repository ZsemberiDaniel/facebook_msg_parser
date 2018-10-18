import matplotlib.pyplot as plotlib
import random
import os
from math import ceil
from PIL import Image
from controller import chat_analyzer
from data import data
from data import facebook_emojis as fe


def plot_emojis_per_participant(chat: data.Chat, image_width=1000, emoji_size=100, output_path="out/"):
    # get the string emojis first
    str_emojis: {str: [str]} = chat_analyzer.emojis_per_participant(chat)

    for participant in str_emojis.keys():
        # we need to convert them to Emoji classes so we know where the image file is
        emojis = list(filter(lambda a: a is not None, map(fe.facebook_emojis.get_emoji, str_emojis[participant])))

        _plot_emojis(emojis, image_width, emoji_size, output_path + participant.replace(" ", ""))

    return


def _plot_emojis(emojis: [fe.Emoji], image_width, emoji_size, output_path):
    # how many emojis there are for each line in the image
    emoji_count_per_line = image_width // emoji_size

    # how many lines there are in the image
    line_count = int(ceil(len(emojis) / emoji_count_per_line))

    # create new image
    created_image: Image = Image.new("RGBA", (image_width, emoji_size * line_count), color="white")

    row = 0
    col = 0
    for emoji in emojis:
        # open then resize image
        emoji_image: Image = Image.open(emoji.path, "r").resize((emoji_size, emoji_size))

        # paste image to correct pos
        paste_x = col * emoji_size
        paste_y = row * emoji_size
        created_image.paste(emoji_image, (paste_x, paste_y, paste_x + emoji_size, paste_y + emoji_size))

        # increment column, if at the end go down by one row
        col += 1
        if col >= emoji_count_per_line:
            col = 0
            row += 1

    # if we want to create the file to a non-existent directory make one
    parent_dir = os.path.abspath(os.path.join(output_path, os.pardir))
    if not os.path.exists(parent_dir):
        os.mkdir(parent_dir)

    # save image
    created_image.save(output_path + ".png")


def plot_activity_char(chat: data.Chat):
    """
    Plots the activity based on the character count with a line chart
    """
    dates = chat_analyzer.all_dates(chat)
    counts_each_participant = chat_analyzer.character_count_per_participant_by_day(chat)

    _plot_for_each_participant(chat, dates, counts_each_participant, title="Character counts")


def plot_activity_msg(chat: data.Chat):
    """
    Plots the activity based on message counts with a line chart
    """
    dates = chat_analyzer.all_dates(chat)
    counts_each_participant = chat_analyzer.message_count_per_participant_by_day(chat)

    _plot_for_each_participant(chat, dates, counts_each_participant, title="Message counts")


def _plot_for_each_participant(chat: data.Chat, x_axes: [], values: {str: []}, title=None):
    """
    Makes a plot that has data for all the participants.
    :param chat: The chat for which we want to make the plot
    :param x_axes: What to show for the x axes values
    :param values: What values to show {participantName: [values]}
    """
    with plotlib.style.context("fivethirtyeight"):
        # create plotlib classes
        figure: plotlib.Figure = plotlib.figure(figsize=(10, 5))
        axes: plotlib.Axes = plotlib.axes()

        # set title if one was given
        if title is not None:
            axes.set_title(title)

        # plot all participant
        for participant in chat.participants:
            color = random_color()
            axes.plot(x_axes, values.get(participant.name, []), label=participant.name, color=color)

        axes.legend(loc="upper left", fancybox=True, framealpha=1, shadow=True, borderpad=0.5)

        plotlib.show()


colors = ["#B71C1C", "#4527A0", "#1565C0", "#2E7D32", "#EF6C00", "#4E342E", "#212121"]


def random_color() -> str:
    return colors[random.randint(0, len(colors) - 1)] + "5D"
