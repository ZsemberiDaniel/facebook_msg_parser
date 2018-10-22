import random
import re
import unicodedata
import emoji
from data import data


class MarkovState:
    def __init__(self, word):
        self.word = word
        self._transitions = []
        self._sum_of_transitions = 0

    @property
    def transitions(self):
        return self._transitions

    def add_transition(self, transition):
        self._sum_of_transitions += transition.probability
        self._transitions.append(transition)

    def get_random_state(self):
        """
        Returns a new random state from the transitions of this state.
        May return None if there are no transitions left for this state
        """
        if len(self._transitions) == 0:
            return None

        rand_int = random.randint(1, self._sum_of_transitions)

        # check which transition it is
        sum = 0
        for transition in self._transitions:
            sum += transition.probability

            # if the random number before was not in the the range [0;sum] but now it is in
            # [0;sum+probability] then it has to be in ]sum; sum+probability]
            if rand_int <= sum:
                return transition.state

        # the if should always be hit in the loop but if for some reason it has not been hit
        # then a good fallback is the last element
        return self._transitions[len(self._transitions) - 1].state

    def __hash__(self):
        return hash(self.word)


class MarkovTransition:
    def __init__(self, probability: int, state: MarkovState):
        """
        Constructs a new markov state
        :param probability: The probability is an integer because it will be compared to all the other
        probabilities in a state
        :param state: Which state to transition to
        """
        self.probability = probability
        self.state = state


class MarkovChain:
    def __init__(self, messages: [data.Message]):
        self.messages = messages
        self._all_states: {str: MarkovState} = {}

    def make_t(self, count):
        state: MarkovState = self._all_states[random.choice(list(self._all_states.keys()))]

        for i in range(count):
            print(state.word, end=" ")
            state = state.get_random_state()

            if state is None:
                state: MarkovState = self._all_states[random.choice(list(self._all_states.keys()))]

        print()

    def _build_states(self):
        # this is a dict that has the words as keys and has
        # another dict as values. That other dict has other words as keys and how many times this word followed the
        # other as keys
        chain = {}

        for msg in self.messages:
            stripped_punctuation = re.sub(r"[.,\/#!?$%\^&\*;:{}=\-_`~()\"']", "", msg.content)
            stripped_emoji = re.sub(emoji.get_emoji_regexp(), "", stripped_punctuation)
            stripped_unicode = unicodedata.normalize("NFD", stripped_emoji.lower()).encode("ASCII", "ignore")\
                .decode("UTF-8")
            words = stripped_unicode.split(" ")
            for i in range(len(words) - 1):
                state_dict = chain.get(words[i], {})
                state_dict[words[i + 1]] = state_dict.get(words[i + 1], 0) + 1
                chain[words[i]] = state_dict

        states = {}
        # first we add every word as a state
        for word in chain.keys():
            states[word] = MarkovState(word)

            for follow_word in chain[word].keys():
                states[follow_word] = MarkovState(follow_word)

        # then we make the transitions
        for word in chain.keys():
            for follow_word in chain[word].keys():
                transition = MarkovTransition(chain[word][follow_word], states[follow_word])
                states[word].add_transition(transition)

        self._all_states = states
