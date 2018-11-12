from datetime import date

from data import data
from data.facebook_emojis import Emoji as FEmoji
from controller import chat_analyzer


""" ______________________________________________________________________________________________________________
                                             P E O P L E
    ______________________________________________________________________________________________________________
"""


def best_person_titles_for_chat(chat: data.Chat, top=5) -> [(str, str)]:
    """Returns the top titles for people for the given chat that match it the best. It returns 'top' amount.
    The format is (title, name)
    """
    # filter out the titles that are None
    all_titles = list(filter(lambda t: t[1] is not None, collect_all_person_titles(chat)))

    # sort by the comparison values
    # the lower that is the more the first and the second person differs
    all_titles = list(sorted(all_titles, key=lambda t: t[1][0]))

    # return only the first 'top' ones, and map them to the output format
    return [(t[0], t[1][1]) for t in all_titles[:min(top, len(all_titles))]]


def collect_all_person_titles(chat: data.Chat) -> [str, (float, str)]:
    """Collects all titles for people in this analyzer into one list with the comparision float included and then returns
    that list.
    """
    # tested pooling here but with pooling enabled it took about 30% slower for this to finish
    return [
        ("The shyest person", shyest_person(chat)),
        ("The most loving person", most_emotion_which_person(chat, "love")),
        ("The kinkiest person", most_emotion_which_person(chat, "kinky")),
        ("The person who loves animals the most", most_emotion_which_person(chat, "animal")),
        ("The saddest person", most_emotion_which_person(chat, "sad")),
        ("The hungriest person", most_emotion_which_person(chat, "food")),
        ("The most educated person", most_educated_person(chat)),
        ("The person who never answers in time", the_person_who_never_answers(chat)),
        ("The person with all the photos", the_person_with_the_photos(chat)),
        ("The person who uses gifs all the time", the_person_with_the_gifs(chat)),
        ("The person who keeps linking to the chat", the_person_with_the_links(chat))
    ]


def shyest_person(chat: data.Chat) -> (float, str):
    """Returns the shyest person in a chat and how shy is (s)he compared to the second shyest
    """
    # We'll use the char count to calculate who the "shyest" person is.
    char_counts = chat_analyzer.character_count_per_participant(chat)

    # map to a list so it can be sorted
    char_counts = list(map(lambda name: (name, char_counts[name]), char_counts))

    # Sort by the character count
    char_counts = sorted(char_counts, key=lambda t: t[1], reverse=True)

    # we have at least two people in the chat that have spoken
    if len(char_counts) >= 2 and char_counts[0][1] != 0:
        # we return the char count compared to the second one
        # and the name of the shyest person
        return char_counts[1][1] / char_counts[0][1], char_counts[0][0]
    elif len(char_counts) >= 1:  # someone is alone in a chat -> should be quite shy right?
        return 1, char_counts[0][0]
    else:
        return None


def most_emotion_which_person(chat: data.Chat, emotion: str) -> (float, str):
    """Returns the person who has the most of the given emotion and how that is compared to the person who has the
    second most. Returns None if there were no participants in the chat
    :exception ValueError: if the given emotion is not one from facebook_emojis.Emoji.all_emotions
    """
    if emotion not in FEmoji.all_emotions:
        raise ValueError("Given emotion is not a checked emotion!")

    # search for the person with the highest of given emotion
    emotions_per_participant = chat_analyzer.emoji_emotion_count_per_participant(chat)

    # map to only given emotion and a list so it can be sorted
    love_per_participant = list(map(lambda name: (name, emotions_per_participant[name][emotion]), emotions_per_participant))

    love_per_participant = list(sorted(love_per_participant, key=lambda t: t[1], reverse=True))

    # we have at least two people in the chat that have spoken
    if len(love_per_participant) >= 2 and love_per_participant[0][1] != 0:
        # we return the char count compared to the second one and the name
        return love_per_participant[1][1] / love_per_participant[0][1], love_per_participant[0][0]
    elif len(love_per_participant) >= 1:  # someone is alone in a chat -> should be the most ... right?
        return 1, love_per_participant[0][0]
    else:
        return None


def most_educated_person(chat: data.Chat, word_count=2) -> (float, str):
    """Returns the most educated person in the chat (based on the unique word count that person have used).
    Returns None if there were no participants in the chat.
    :param chat: Chat to analyze
    :param word_count: What is the maximum number of a words for that word to be considered unique
    :return: The most educated person, and how (s)he is compared to the second most educated
    """
    # how many times each word was used by each participant
    unique_words = chat_analyzer.unique_word_count_per_participant(chat)

    # filter for the words which have maximum word_count count
    for name in unique_words:
        unique_words[name] = list(filter(lambda t: t[1] <= word_count, unique_words[name]))

    # count how many words are left
    most_educated_names = list(sorted(unique_words, key=lambda name: len(unique_words[name]), reverse=True))

    # we have at least two people in the chat that have spoken
    if len(most_educated_names) >= 2 and len(unique_words[most_educated_names[0]]) != 0:
        # we return the word count compared to the second one and the name
        return len(unique_words[most_educated_names[1]]) / len(unique_words[most_educated_names[0]]), most_educated_names[0]
    elif len(most_educated_names) >= 1:  # someone is alone in a chat -> should be the most educated right?
        return 1, most_educated_names[0]
    else:
        return None


def the_person_who_never_answers(chat: data.Chat) -> (float, str):
    """Returns the person who answers the slowest and also returns how that is compared to the second slowest.
    Returns None if there were no participants in the chat.
    """
    response_times = chat_analyzer.avg_response_time(chat)

    # there were no responses
    if response_times is None:
        return None

    # sorted so the slowest is first
    slowest_response = list(sorted(response_times, key=lambda name: response_times[name], reverse=True))

    # we have at least two people in the chat that have spoken
    if len(slowest_response) >= 2 and response_times[slowest_response[0]] != 0:
        # we return the response time compared to the second one and the name
        return response_times[slowest_response[1]] / response_times[slowest_response[0]], slowest_response[0]
    elif len(slowest_response) >= 1:  # someone is alone in a chat -> should be the slowest right?
        return 1, slowest_response[0]
    else:
        return None
    

def the_person_with_the_photos(chat: data.Chat) -> (float, str):
    """Returns who sent the most photos and how the person who sent the second most compares to that.
    May return None if there were no participants in the chat or there were no photos sent.
    """
    photo_counts = chat_analyzer.photo_count_per_participant(chat)
    not_zero_photo_count = [name for name in photo_counts if photo_counts[name] != 0]

    # sort in descending order
    descending_photos = list(sorted(not_zero_photo_count, key=lambda name: photo_counts[name], reverse=True))

    # we have at least two people in the chat that have spoken
    if len(descending_photos) >= 2:
        # we return the response time compared to the second one and the name
        return photo_counts[descending_photos[1]] / photo_counts[descending_photos[0]], descending_photos[0]
    elif len(descending_photos) >= 1:  # someone is alone in a chat -> should be the one with the most photos right?
        return 1, descending_photos[0]
    else:
        return None


def the_person_with_the_gifs(chat: data.Chat) -> (float, str):
    """Returns who sent the most gifs and how the person who sent the second most compares to that.
    May return None if there were no participants in the chat.
    """
    gif_counts = chat_analyzer.gif_count_per_participant(chat)
    not_zero_gif_count = [name for name in gif_counts if gif_counts[name] != 0]

    # sort in descending order
    descending_gifs = list(sorted(not_zero_gif_count, key=lambda name: gif_counts[name], reverse=True))

    # we have at least two people in the chat that have spoken
    if len(descending_gifs) >= 2:
        # we return the response time compared to the second one and the name
        return gif_counts[descending_gifs[1]] / gif_counts[descending_gifs[0]], descending_gifs[0]
    elif len(descending_gifs) >= 1:  # someone is alone in a chat -> should be the one with the most gifs right?
        return 1, descending_gifs[0]
    else:
        return None
    
    
def the_person_with_the_links(chat: data.Chat) -> (float, str):
    """Returns who sent the most links and how the person who sent the second most compares to that.
    May return None if there were no participants in the chat.
    """
    share_counts = chat_analyzer.share_count_per_participant(chat)
    not_zero_share_count = [name for name in share_counts if share_counts[name] != 0]

    # sort in descending order
    descending_shares = list(sorted(not_zero_share_count, key=lambda name: share_counts[name], reverse=True))

    # we have at least two people in the chat that have spoken
    if len(descending_shares) >= 2:
        # we return the response time compared to the second one and the name
        return share_counts[descending_shares[1]] / share_counts[descending_shares[0]], descending_shares[0]
    elif len(descending_shares) >= 1:  # someone is alone in a chat -> should be the one with the most links right?
        return 1, descending_shares[0]
    else:
        return None


""" ______________________________________________________________________________________________________________
                                             M O N T H S
    ______________________________________________________________________________________________________________
"""


def best_month_titles_for_chat(chat: data.Chat, top=5) -> [(str, str)]:
    """Returns the top titles for months for the given chat that match it the best. It returns 'top' amount.
    The format is (title, name)
    """
    # filter out the titles that are None
    all_titles = list(filter(lambda t: t[1] is not None, collect_all_month_titles(chat)))

    # sort by the comparison values
    # the lower that is the more the first and the second person differs
    all_titles = list(sorted(all_titles, key=lambda t: t[1][0]))

    # return only the first 'top' ones, and map them to the output format
    return [(t[0], t[1][1]) for t in all_titles[:min(top, len(all_titles))]]


def collect_all_month_titles(chat: data.Chat) -> [(str, (float, str))]:
    """Collects all titles for months in this analyzer into one list with the comparision float included and then returns
    that list.
    """
    return [
        ("Most active month", most_active_month(chat)),
        ("Most loving month", most_emotion_which_month(chat, "love")),
        ("Kinkiest month", most_emotion_which_month(chat, "kinky")),
        ("Month of the zoo", most_emotion_which_month(chat, "animal")),
        ("Saddest month", most_emotion_which_month(chat, "sad"))
    ]


def most_active_month(chat: data.Chat) -> (float, str):
    """Returns the most active month in terms of message count and how the second most active month compares to that.
    """
    msg_count_monthly: {date: int} = chat_analyzer.message_count_monthly(chat)

    # there will be at least two months (we can return the comparision float)
    if len(msg_count_monthly) >= 2:
        # we look for the highest and the second highest
        first_at, second_at = None, None
        first_val, second_val = -1, -1

        for month in msg_count_monthly:
            if msg_count_monthly[month] > first_val:
                # first moved down to second
                second_val = first_val
                second_at = first_at

                # first got new value
                first_val = msg_count_monthly[month]
                first_at = month

        # for division by 0 error
        if first_val == 0:
            return 1, first_at
        else:
            return second_val / first_val, first_at
    elif len(msg_count_monthly) >= 1:
        # we return the one with the highest value
        return 1, max(msg_count_monthly, key=lambda d: msg_count_monthly[d])
    else:
        return None


def most_emotion_which_month(chat: data.Chat, emotion: str) -> (float, date):
    """Return in which month the given emotion was most used and how the second month in that list compares to that.
    :exception ValueError If the given emotion is not a checked one
    """
    if emotion not in FEmoji.all_emotions:
        raise ValueError("Given emotion is not a checked emotion!")

    emotion_count_per_month: {date: {str: int}} = chat_analyzer.emoji_emotions_monthly(chat)

    # there will be at least two months (we can return the comparision float)
    if len(emotion_count_per_month) >= 2:
        # we look for the highest and the second highest
        first_at, second_at = None, None
        first_val, second_val = -1, -1

        for month in emotion_count_per_month:
            if emotion_count_per_month[month].get(emotion, 0) > first_val:
                # first moved down to second
                second_val = first_val
                second_at = first_at

                # first got new value
                first_val = emotion_count_per_month[month].get(emotion, 0)
                first_at = month

        # for division by 0 error
        if first_val == 0:
            return 1, first_at
        else:
            return second_val / first_val, first_at
    elif len(emotion_count_per_month) >= 1:
        # we return the one with the highest value
        return 1, max(emotion_count_per_month, key=lambda d: emotion_count_per_month[d][emotion])
    else:
        return None
