"""
Name : config.py
Author  : Hanat
Contect : hanati@tezign.com
Time    : 2019-09-18 11:59
Desc:
"""
from easydict import EasyDict as edict


g_conf = edict()
g_conf.path_conf = edict()
g_conf.path_conf.chinese_corpus_path = ''
g_conf.path_conf.english_corpus_path = ''
g_conf.path_conf.random_character_path = ''
g_conf.path_conf.random_latin_charater_path = ''
g_conf.path_conf.specific_scene_character_path = ''

g_conf.random_conf = edict()    # all probability sum = 1
g_conf.random_conf.chinese_corpus_probability = 0.3
g_conf.random_conf.english_corpus_probability = 0.3
g_conf.random_conf.random_character_probability = 0.1
g_conf.random_conf.random_latin_charater_probability = 0.1
g_conf.random_conf.specific_scene_character_probability = 0.2

g_conf.gen_mode_conf = edict()
g_conf.gen_mode_conf.ocr_data_gen = 1
g_conf.gen_mode_conf.detect_data_gen = 1
g_conf.gen_mode_conf.sementic_data_gen = 0









