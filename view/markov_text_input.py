from data import data
from controller import chat_analyzer
from controller.markov import markov_chain
from view import console_input


class ChatMarkovData:
    def __init__(self, chat: data.Chat, layer_count=3):
        self.layer_count = layer_count
        self.for_participants: {str: markov_chain.MarkovChain} = {}
        self.for_all = markov_chain.MarkovChain(chat.messages, layer_count)

        for participant in chat.participants:
            msgs = chat_analyzer.get_messages_only_by(chat, [participant.name])
            self.for_participants[participant.name] = markov_chain.MarkovChain(msgs, layer_count)

