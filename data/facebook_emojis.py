import json
import os
import emoji

from definitions import ROOT_DIR


class Emoji:
    @staticmethod
    def decode_from_json(json_dict: {}):
        name = json_dict.get("name", "no name").replace("-", "_")  # we need this conversion for the emoji library
        aliases = map(lambda a: a.replace("-", "_"), json_dict.get("also_known"))

        return Emoji(name=name,
                     codes=json_dict.get("codes", []),
                     path=os.path.join(ROOT_DIR, "img", json_dict.get("path", "default.png")),
                     aliases=aliases,
                     emotions=json_dict.get("emotions", []))

    all_emotions = ["love", "happy", "good", "neutral", "bad", "angry", "sad", "animal", "food", "meme", "kinky"]
    # colors for the emotions in order of appearance of emotions in the list
    emotion_colors = ["#FF69B4", "#FFD700", "#9ACD32", "#BC8F8F", "#2F4F4F", "#DC143C", "#6A5ACD", "#556B2F",
                      "#D2B48C", "#8A2BE2", "#8B0000"]

    def __init__(self, name: str, codes: [str], path: str, aliases: [str], emotions: [str]):
        self.name = name
        self.codes = codes
        # absolute path
        self.path = path
        self.aliases = aliases
        # any of these: "love", "happy", "good", "neutral", "bad", "angry", "sad", "animal", "food", "meme", "kinky"
        self.emotions = emotions

    def __str__(self) -> str:
        return self.name + " with codes " + str(self.codes)


class FacebookEmojis:
    def __init__(self):
        self._all_emojis: {str: Emoji} = {}

        self._load_emojis()

    @property
    def all_emojis(self) -> [Emoji]:
        return self._all_emojis

    def _load_emojis(self):
        # path to the data file
        data_file_path = os.path.join(ROOT_DIR, "img", "data.txt")

        with open(data_file_path) as file:
            # decode json of data file
            raw_json = json.loads(file.read())

            # convert to python objects
            emoji_classes = list(map(Emoji.decode_from_json, raw_json))

            for em in emoji_classes:
                # add with default name
                self._all_emojis[em.name] = em

                # add all aliases
                for alias_name in em.aliases:
                    self._all_emojis[alias_name] = em

    def get_emoji(self, emoji_str: str):
        # for some reason, beyond me, the delimiter parameter of this function does not work for -
        # NICE 😄
        demojize_str = emoji.demojize(emoji_str).lower()
        # also for some reason there are emojis with both - and _ because why the hell not
        # so we need to replace them as well
        emoji_name = demojize_str[1:-1].replace("-", "_")  # remove the : from beginning and end
        emoji_class = self.all_emojis.get(emoji_name, None)

        if emoji_class is None:
            # fall back mechanism:
            # go through the keys and check for substrings
            for emoji_code in self.all_emojis.keys():
                if emoji_name in emoji_code or emoji_code in emoji_name:
                    emoji_class = self.all_emojis[emoji_code]
                    break

        if emoji_class is None:
            print("[ERROR] Demojized", emoji_str, "to", emoji_name, "and it is not available as picture!")

        return emoji_class

    def get_emojis_from_string(self, string: str) -> [Emoji]:
        """
        Returns all emojis from a given string
        """
        return map(lambda a: self.get_emoji(a), filter(lambda char: char in emoji.UNICODE_EMOJI.keys(), string))


facebook_emojis = FacebookEmojis()
