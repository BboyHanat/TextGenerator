"""
Name : textProvider.py
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
            seek = Random.random_int(0, self._corpus_length-1)
            yield self._character_seq[seek]

    def _get_next_batch(self):
        seek = 0
        while True:
            if seek == self._corpus_length:
                seek = 0
            yield self._character_seq[seek]
            seek += 1


class RandomCharacterGen(object):
    def __init__(self, character_seq: list, len_range=(2, 15)):
        """

        :param character_seq:
        :param batch_size:
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
            batch_size = Random.random_seek(self._len_range[0], self._len_range[1])
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
    def __init__(self,
                 chinese_corpus_path: str,
                 english_corpus_path: str,
                 random_character_path: str,
                 specific_scene_character_path: str,
                 characters_len_range: tuple,
                 gen_probability: list,
                 random_choice=False
                 ):
        """
        init TextProvider object
        :param chinese_corpus_path:
        :param english_corpus_path:
        :param random_character_path:
        :param specific_scene_character_path:
        :param characters_len_range:
        """
        self._chinese_corpus_path = chinese_corpus_path
        self._english_corpus_path = english_corpus_path
        self._random_character_path = random_character_path
        self._specific_scene_character_path = specific_scene_character_path
        self.gen_probability = gen_probability
        self._random_choice = random_choice

        self._chinese_corpus_gen, self._english_corpus_gen, self._random_character_gen, \
        self._specific_scene_character_gen = self._init_generators(characters_len_range)
        self._all_generator = [self._chinese_corpus_gen, self._english_corpus_gen, self._random_character_gen, self._specific_scene_character_gen]
        self.gen = self.get_generator()

    def _init_generators(self, characters_len_range: tuple):
        """
        init all generator
        :param characters_len_range:
        :return:
        """
        chinese_corpus_gen = None
        if self._chinese_corpus_path:
            with open(self._chinese_corpus_path, 'r') as fp:
                chinese_corpus_list = fp.readlines()
            chinese_corpus_list = self._replace_useless(chinese_corpus_list)
            if not chinese_corpus_list == []:
                chinese_corpus_gen = RandomCorpusGen(chinese_corpus_list, characters_len_range)

        english_corpus_gen = None
        if self._english_corpus_path:
            with open(self._english_corpus_path, 'r') as fp:
                english_corpus_list = fp.readlines()
            english_corpus_list = self._replace_useless(english_corpus_list)
            if not english_corpus_list == []:
                english_corpus_gen = RandomCorpusGen(english_corpus_list, characters_len_range)

        random_character_gen = None
        if self._random_character_path:
            with open(self._random_character_path, 'r') as fp:
                random_character_list = list(fp.readline())
            random_character_list = self._replace_useless(random_character_list)
            if not random_character_list == []:
                random_character_gen = RandomCharacterGen(random_character_list, characters_len_range)

        specific_scene_character_gen = None
        if self._specific_scene_character_path:
            with open(self._specific_scene_character_path, 'r') as fp:
                specific_scene_character_list = list(fp.readlines())
            specific_scene_character_list = self._replace_useless(specific_scene_character_list)
            if not specific_scene_character_list == []:
                specific_scene_character_gen = RandomCorpusGen(specific_scene_character_list, characters_len_range)

        return chinese_corpus_gen, english_corpus_gen, random_character_gen, specific_scene_character_gen

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

    def get_generator(self):
        """
        generator
        :param gen_probability_dict:
        :return:
        """
        value_list = self.gen_probability
        while True:
            index = Random.random_choice(list(value_list))
            if self._all_generator[index]:
                yield self._all_generator[index].get_next.__next__()

    def generator(self):
        return self.gen.__next__()
