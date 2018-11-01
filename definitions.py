import os


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# used for indicating when the message.json file needs to be decoded again because
# something in decoding has changed
DECODING_VERSION: str = "1.0"


def is_current_decoding_version(version: str):
    """
    Returns whether the given version of decoding is the same as the one being used by the program
    """
    return version == DECODING_VERSION
