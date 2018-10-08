import os
from data import data


# Returns the Chat objects made from the given folder
def traverse_folder(folder_path):
    # get the folders from messages class
    folders = [folder.lower() for folder in os.listdir(folder_path)]
    folders.sort()

    # get the name from the folder: name_someNumber
    folders_with_data = [(folder_name.split("_")[0], folder_name) for folder_name in folders]

    # if there are two folders next to each other with the same name but in different cases (upper, lower) then
    # they belong to each other, because one contains text and the other the media
    unique_folder_with_data = []
    at = 0
    while at < len(folders_with_data):
        msg_folder = folders_with_data[at]

        path_to_msg = os.path.join(folder_path, msg_folder[1])
        path_to_media = None

        # not last folder  and  the condition described above applies
        if at != len(folders_with_data) - 1 and msg_folder[0].lower() == folders_with_data[at + 1][0].lower():
            path_to_media = os.path.join(folder_path, folders_with_data[at + 1][1])

            at += 2  # skip the media folder
        # there is no media folder
        else:
            at += 1

        # add this chat
        unique_folder_with_data.append(data.Chat(path_to_msg, path_to_media, msg_folder[0]))

    return unique_folder_with_data
