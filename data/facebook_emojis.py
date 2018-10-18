import json
import os
import emoji


# location to the directory the project is in so we can read the facebook emoji data
__location__ = os.path.realpath(os.getcwd())


class Emoji:
    @staticmethod
    def decode_from_json(json_dict: {}):
        name = json_dict.get("name", "no name").replace("-", "_")  # we need this conversion for the emoji library
        aliases = map(lambda a: a.replace("-", "_"), json_dict.get("also_known"))

        return Emoji(name=name,
                     codes=json_dict.get("codes", []),
                     path=os.path.join(__location__, "img", json_dict.get("path", "default.png")),
                     aliases=aliases)

    def __init__(self, name: str, codes: [str], path: str, aliases: [str]):
        self.name = name
        self.codes = codes
        self.path = path
        self.aliases = aliases

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
        data_file_path = os.path.join(__location__, "img", "data.txt")

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
        demojize_str = emoji.demojize(emoji_str)
        # also for some reason there are emojis with both - and _ because why the hell not
        # so we need to replace them as well
        emoji_name = demojize_str[1:-1].replace("-", "_")  # remove the : from beginning and end
        emoji_class = self.all_emojis.get(emoji_name.lower(), None)

        if emoji_class is None:
            # fall back mechanism:
            # go through the keys and check for substrings
            for emoji_code in self.all_emojis.keys():
                if emoji_name in emoji_code or emoji_code in emoji_name:
                    emoji_class = self.all_emojis[emoji_code]
                    break

        if emoji_class is None:
            print("Demojized", emoji_str, "to", emoji_name, ". Is available?", emoji_class is not None)

        return emoji_class


facebook_emojis = FacebookEmojis()
