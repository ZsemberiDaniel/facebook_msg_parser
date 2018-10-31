import random
import re
import unicodedata
import emoji
from data import data


class MarkovState:
    def __init__(self, word):
        self.word = word
        self._transitions = []
        # we keep a list of all the other markov states we can transition to
        self._other_markov_states: {str: MarkovState} = {}
        self._sum_of_transitions = 0

    @property
    def transitions(self):
        return self._transitions

    def add_transition(self, transition):
        self._sum_of_transitions += transition.probability
        self._transitions.append(transition)

        # we need to keep track of all the other markov states so we can easily traverse them
        # in a MarkovChain
        if isinstance(transition.transition_to, MarkovState):
            self._other_markov_states[transition.transition_to.word] = transition.transition_to

    def get_other_state(self, word):
        """
        This returns another markov state that we can transition to from this markov state if it exists
        here. If it does not then None is returned
        """
        return self._other_markov_states.get(word, None)

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
                return transition.transition_to

        # the if should always be hit in the loop but if for some reason it has not been hit
        # then a good fallback is the last element
        return self._transitions[len(self._transitions) - 1].state


class MarkovTransition:
    def __init__(self, probability: int, transition_to: str):
        """
        Constructs a new markov state
        :param probability: The probability is an integer because it will be compared to all the other
        probabilities in a state
        :param transition_to: Which word to transition to
        """
        self.probability = probability
        self.transition_to = transition_to


class MarkovChain:
    """
    Works with any layer count.
    """
    def __init__(self, messages: [data.Message], layer_count: int):
        if layer_count <= 0:
            raise ValueError("Layer count cannot be lower than 1!")

        self.messages = messages
        self.layer_count = layer_count
        # At the end of the dictionary tree there is a MarkovState that has only words as values
        self._all_states: MarkovState = None

    def get_words(self, count: int) -> [str]:
        self._assert_built()

        if count <= 0:
            return []
        elif count == 1:
            return [self._all_states.get_random_state()]
        else:
            # generate the first few words (we need to generate layer_count amount of words)
            curr_chain = self._all_states
            words = []
            for i in range(self.layer_count - 1):
                curr_chain = curr_chain.get_random_state()

                words.append(curr_chain.word)
            # at the end there are only words
            words.append(curr_chain.get_random_state())

            # we can exit here if we don't need more words
            if count <= self.layer_count:
                return words[:count]

            for i in range(count - len(words)):
                words.append(self._get_next_word(words[-self.layer_count + 1:]))

            return words

    def _get_next_word(self, words_before: [str]) -> str:
        def _get_next_word_state(used_word_count):
            """
            Returns the next word's state using only using_word_count amount of words form the end of words_before array
            """
            # we need to traverse down the MarkovState tree if we can
            # if we get stuck somewhere just
            curr_state = self._all_states

            # if there won't be enough words to traverse down the whole tree then just don't bother
            # this also gets rid of all the unnecessary words in words_before (the first few ones)
            for i in range(len(words_before) - used_word_count, len(words_before)):
                new_state = curr_state.get_other_state(words_before[i])

                # we can't traverse to the next word in the Markov chain
                if new_state is None:
                    curr_state = None
                    # we just break out of the loop because we can try other things
                    break
                else:
                    # otherwise we just go along like usual
                    curr_state = new_state

            return curr_state

        # first we try with the max amount of words possible
        # then we decrement that by one each time
        curr_state = None
        used_word_count = min(self.layer_count - 1, len(words_before))

        while curr_state is None and used_word_count > 0:
            curr_state = _get_next_word_state(used_word_count)

            # we found the state we were looking for
            if curr_state is not None:
                result = curr_state.get_random_state()

                # we didn't fully get down the markov tree so we can only return the state's word
                if isinstance(result, MarkovState):
                    return result.word
                # we got fully down the tree
                elif isinstance(result, str):
                    return result
                else:
                    # this should never be reached
                    return None

            used_word_count -= 1

        # we couldn't traverse with the given words down the markov chain ->
        # we need fallback methods

        # TODO: Think of fallback methods
        # for now we just get a random ste and continue with tha
        return self._all_states.get_random_state().word

    def _assert_built(self):
        """
        Asserts that the states are built and can be used to generate words
        """
        if self._all_states is None:
            self._build_states()

    def _build_states(self):
        # this is a dict that has the words as keys and has
        # another dict as values. That other dict can either be other words as keys and how many times this
        # word followed the other as keys or words as keys and a dict as values (from here it repeats itself).
        chain = {}

        for msg in self.messages:
            stripped_special = re.sub(r"[\"']", "", msg.content)
            stripped_emoji = re.sub(emoji.get_emoji_regexp(), "", stripped_special)
            stripped_unicode = unicodedata.normalize("NFD", stripped_emoji.lower()).encode("ASCII", "ignore")\
                .decode("UTF-8")
            # we match these punctuations as separate words
            words = re.findall(r"([.!?,;:-]|\w+)", stripped_unicode)

            # we need to traverse the chain by going down one each time
            for i in range(len(words) - self.layer_count):
                chain_end = chain

                for k in range(self.layer_count - 1):
                    # we add a node after the current one based on whether that should be a leaf or not
                    new_dict = chain_end.get(words[i + k], (0, {}))
                    new_dict[1][words[i + k + 1]] = 0 if k == self.layer_count - 2 else (0, {})
                    # we also store how many times a word appears after another so we need to increment that
                    new_dict = (new_dict[0] + 1, new_dict[1])
                    chain_end[words[i + k]] = new_dict
                    # traversing down
                    chain_end = new_dict[1]

                # at the end we add one to the word that's at the end of this line
                chain_end[words[i + self.layer_count - 1]] = chain_end.get(words[i + self.layer_count - 1], 0) + 1

        # so now we have a dict and we need to add MarkovStates at the end
        # we have to convert the end dictionary to a MarkovState
        def markov_state_from_dictionary(word: str, dict) -> MarkovState:
            state = MarkovState(word)

            for key in dict.keys():
                state.add_transition(MarkovTransition(dict[key], key))

            return state

        def markov_state_from_tuples(word: str, tuples) -> MarkovState:
            state = MarkovState(word)

            for tuple in tuples:
                state.add_transition(MarkovTransition(tuple[0], tuple[1]))

            return state

        # with this we reach the end of the chain and convert the end dictionary to a markov state
        # while coming back we convert each dictionary to another MarkovState
        def convert_all(chain, layer_at):
            if layer_at == self.layer_count - 1:
                for key in chain.keys():
                    chain[key] = (chain[key][0], markov_state_from_dictionary(key, chain[key][1]))
            else:
                for key in chain.keys():

                    # we convert the tuples of (how_many_after_word, dicts) to MarkovStates
                    tuples = []
                    for word in chain[key][1].keys():
                        tuples.append(chain[key][1][word])

                    # if we are at the first layer we need to keep how many times a word has been encountered
                    if layer_at == 1:
                        chain[key] = (chain[key][0], markov_state_from_tuples(key, tuples))
                    else:
                        chain[key] = markov_state_from_tuples(key, tuples)

        convert_all(chain, 1)
        tuples = []
        for word in chain.keys():
            tuples.append(chain[word])
        self._all_states = markov_state_from_tuples("", tuples)
