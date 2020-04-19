'''
CAPP 30122 W'20: Markov models and hash tables

Tstsuo Fujino
Takayuki Kitamura
'''

import sys
import math
import hash_table

HASH_CELLS = 57


class Markov:
    '''
    Class for representing markov model.
    '''
    def __init__(self, k, s):
        '''
        Construct a new k-order Markov model using the statistics of string "s"
        '''
        self.k_value = k
        self.string = s
        self.defval = None
        self.hash_table = hash_table.HashTable(HASH_CELLS, self.defval)
        word_dic = self.make_dic()
        for i in word_dic:
            self.hash_table.update(i, word_dic[i])

    def log_probability(self, s):
        '''
        Get the log probability of string "s", given the statistics of
        character sequences modeled by this particular Markov model
        This probability is *not* normalized by the length of the string.
        '''
        sum_log_pro = 0
        num_unique_letter = len(set(self.string))
        for i in range(len(s)):
            prev_words = self.get_prev_words(s, i)
            if self.hash_table.lookup(prev_words) == self.defval:
                M = 0
                N = 0
            else:
                if s[i] in self.hash_table.lookup(prev_words):
                    M = self.hash_table.lookup(prev_words)[s[i]]
                else:
                    M = 0
                N = sum(x for x in self.hash_table.lookup(prev_words).values())
            numerator = M + 1
            denominator = N + num_unique_letter
            log_pro = math.log(numerator / denominator)
            sum_log_pro += log_pro
        return sum_log_pro

    def get_prev_words(self, string, i):
        '''
        Get previous words, i.e., k preceding characters followed by the current character

        Inputs
            string (str): it represents total due of each property
            i (int): the index of the letter

        Output:
            previous words(str): k preceding characters followed by the character
        '''
        if i >= self.k_value:
            return string[i-self.k_value:i]
        s = string + string[0:i]
        return s[-self.k_value:]

    def make_dic(self):
        '''
        Make a dictionary, whose key is previous words and value is a dictionary
        whose key is a character and value is frequency of characters in the string.

        Output:
            word_dic(dictionary): a dictionary to manage frequency of characters
        '''
        word_dic = {}
        for i in range(len(self.string)):
            prev_words = self.get_prev_words(self.string, i)
            if prev_words in word_dic:
                if self.string[i] in word_dic[prev_words]:
                    word_dic[prev_words][self.string[i]] += 1
                else:
                    word_dic[prev_words][self.string[i]] = 1
            else:
                word_dic[prev_words] = {self.string[i]:1}
        return word_dic


def identify_speaker(speaker_a, speaker_b, unknown_speech, k):
    '''
    Given sample text from two speakers, and text from an unidentified speaker,
    return a tuple with the *normalized* log probabilities of each of the
    speakers uttering that text under a "k" order character-based Markov model,
    and a conclusion of which speaker uttered the unidentified text
    based on the two probabilities.
    '''
    a_markov = Markov(k, speaker_a)
    b_markov = Markov(k, speaker_b)
    log_pro_a = a_markov.log_probability(unknown_speech) / len(unknown_speech)
    log_pro_b = b_markov.log_probability(unknown_speech) / len(unknown_speech)
    if log_pro_a > log_pro_b:
        most_likely_speaker = 'A'
    else:
        most_likely_speaker = 'B'
    return (log_pro_a, log_pro_b, most_likely_speaker)


def print_results(res_tuple):
    '''
    Given a tuple from identify_speaker, print formatted results to the screen
    '''
    (likelihood1, likelihood2, conclusion) = res_tuple

    print("Speaker A: " + str(likelihood1))
    print("Speaker B: " + str(likelihood2))

    print("")

    print("Conclusion: Speaker " + conclusion + " is most likely")


def go():
    '''
    Interprets command line arguments and runs the Markov analysis.
    Useful for hand testing.
    '''
    num_args = len(sys.argv)

    if num_args != 5:
        print("usage: python3 " + sys.argv[0] + " <file name for speaker A> " +
              "<file name for speaker B>\n  <file name of text to identify> " +
              "<order>")
        sys.exit(0)

    with open(sys.argv[1], "rU") as file1:
        speech1 = file1.read()

    with open(sys.argv[2], "rU") as file2:
        speech2 = file2.read()

    with open(sys.argv[3], "rU") as file3:
        speech3 = file3.read()

    res_tuple = identify_speaker(speech1, speech2, speech3, int(sys.argv[4]))

    print_results(res_tuple)

if __name__ == "__main__":
    go()
