from controller import folder_traversal
from controller import chat_decoder
from view import choose_chat_text_input as cc_tinp
from view import chat_data_text_input as cd_tinp
from data import data
import asyncio


loop = asyncio.get_event_loop()
run = True


def main():
    # get all the chats from the folder
    chats = folder_traversal.traverse_folder("/home/zsdaniel/Downloads/messages")

    # choose one via text input
    # then we add all the data from the message.json file
    while run:
        chat_task = loop.create_task(chat_decoder.add_all_data(cc_tinp.choose_chat(chats)))
        chat_task.add_done_callback(got_chosen_chat)

        loop.run_forever()


def got_chosen_chat(future):
    chat: data.Chat = future.result()
    loop.stop()

    cmd_line = cd_tinp.ChatCommandLine(chat)
    cmd_line.start_command_line()


main()
