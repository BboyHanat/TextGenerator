"""
Name : TextProvider.py
Author  : Hanat
Contect : hanati@tezign.com
Time    : 2019-09-18 13:53
Desc:
"""

import random
from utils.random_tools import Random


class RandomCorpusGen(object):

    def __init__(self, character_seq: list, len_range=(2, 15)):
        """

        :param character_seq:
        :param batch_size:
        """
        self._character_seq = character_seq
        # random.shuffle(self.character_seq)
        self._len_range = len_range
        self.get_next = self._get_next_batch()
        self._corpus_length = len(self._character_seq)

    def _get_random(self):
        while True:
            seek = Random.random_int(0, self._corpus_length - 1)
            yield self._character_seq[seek]

    def _random_crop(self, char_str):
        seek = Random.random_int(0, len(char_str) - self._len_range[1])
        char_str = char_str[seek: seek+self._len_range[1]]
        return char_str

    def _random_add(self, char_str):
        while True:
            length = len(char_str)
            random_str = self._get_random().__next__()
            if self._len_range[0] <= (len(random_str) + length+1) <= self._len_range[1]:
                char_str += random_str
                break
            elif (len(random_str) + length+1) < self._len_range[0]:
                char_str += random_str
            else:
                char_str += random_str
                char_str = self._random_crop(char_str)
                break
        return char_str

    def _get_next_batch(self):
        seek = 0
        while True:
            if seek == self._corpus_length:
                seek = 0
            char_str = self._character_seq[seek]
            if len(char_str) > self._len_range[1]:
                char_str = self._random_crop(char_str)
            elif len(char_str) < self._len_range[0]:
                char_str = self._random_add(char_str)
            yield char_str
            seek += 1


class RandomCharacterGen(object):
    def __init__(self, character_seq: list, len_range=(2, 15)):
        """

        :param character_seq:
        :param len_range:
        """
        self._character_seq = character_seq
        self._len_range = len_range
        self.get_next = self._get_next_batch()

    def _get_next_batch(self):
        """

        :return:
        """
        seek = 0
        while True:
            batch_size = Random.random_int(self._len_range[0], self._len_range[1])
            if len(self._character_seq) - seek < batch_size:
                for i in range(len(self._character_seq) - seek):
                    self._character_seq.insert(0, self._character_seq[-1])
                    del self._character_seq[-1]
                random.shuffle(self._character_seq)
                seek = 0
            ret_character_seq = self._character_seq[seek:seek + batch_size]
            len_seq = len(ret_character_seq)
            if random.randint(0, 6) >= 4 and 7 < len_seq < 13:
                ret_character_seq.insert(random.randint(2, len_seq - 1), ' ')

            yield ''.join(ret_character_seq)
            seek += batch_size


class TextProvider:
    def __init__(self, corpus_list):
        self.gen = self.get_generator(corpus_list)

    @staticmethod
    def _replace_useless(character_obj):
        """
        remove useless symbol from sequences
        :param character_obj:
        :return:
        """
        if isinstance(character_obj, list):
            length_character_obj = len(character_obj)
            for index in range(length_character_obj):
                character_obj[index] = character_obj[index].replace('\n', '')
                character_obj[index] = character_obj[index].replace('\r', '')
                character_obj[index] = character_obj[index].replace('\t', '')
                character_obj[index] = character_obj[index].replace(' ', '')
        elif isinstance(character_obj, str):
            character_obj = character_obj.replace('\n', '')
            character_obj = character_obj.replace('\r', '')
            character_obj = character_obj.replace('\t', '')
            character_obj = character_obj.replace(' ', '')
        return character_obj

    def get_generator(self, corpus_list):
        _all_generator = []
        gen_probability_list = []

        for corpus in corpus_list:
            gen_probability_list.append(float(corpus['probability']))

            with open(corpus['path'], 'r') as fp:
                if corpus['type'] == 'line':
                    data = fp.readlines()
                    data = self._replace_useless(data)
                    generator = RandomCorpusGen(data, eval(corpus['len_range']))
                    _all_generator.append(generator)
                elif corpus['type'] == 'word':
                    data = fp.readline()
                    data = self._replace_useless(data)
                    generator = RandomCharacterGen(list(data), eval(corpus['len_range']))
                    _all_generator.append(generator)

        while True:
            index = Random.random_choice(gen_probability_list)
            if _all_generator[index]:
                yield _all_generator[index].get_next.__next__()

    def generator(self):
        return self.gen.__next__()
