import os
from ruamel import yaml
import platform

from service.provider.TextImgProvider import TextImgProvider
from service.provider.BackgroundImgProvider import BackgroundImgProvider
from service.provider.TextProvider import TextProvider
from service.provider.SmoothAreaProvider import SmoothAreaProvider
from utils import log
from multiprocessing import Pool
import traceback
import os

basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
conf: dict
text_img_provider: TextImgProvider
background_img_provider: BackgroundImgProvider
text_provider: TextProvider
smooth_area_provider: SmoothAreaProvider


def load_from_config():
    global text_img_provider
    global background_img_provider
    global text_provider
    global smooth_area_provider

    system = platform.system()

    text_img_provider = TextImgProvider(
        seed=conf['random_conf']['seed'],
        font_file_dir=conf['path_conf']['font_file_dir'],
        text_img_output_dir=conf['path_conf']['text_img_output_dir'],
        text_img_info_output_dir=conf['path_conf']['text_img_info_output_dir']
    )

    background_img_provider = BackgroundImgProvider(
        bg_img_dir=conf['path_conf']['bgimage_dir'],
        gen_probability=[
            float(conf['random_conf']['bgimage_from_dir_probability']),
            float(conf['random_conf']['bgimage_from_gauss_probability'])],
        img_format=conf['text_bg_img_conf']['img_can_load_format'],
        gen_random_image=conf['text_bg_img_conf']['gen_random_image']
    )

    text_provider = TextProvider(
        chinese_corpus_path=conf['path_conf']['chinese_corpus_path'],
        english_corpus_path=conf['path_conf']['english_corpus_path'],
        random_character_path=conf['path_conf']['random_character_path'],
        specific_scene_character_path=conf['path_conf']['specific_scene_character_path'],
        specific_business_corpus_path=conf['path_conf']['specific_business_corpus_path'],
        characters_len_range=eval(conf['text_gen_conf']['characters_len_range']),
        gen_probability=conf['text_gen_conf']['gen_probability'],
        random_choice=conf['text_gen_conf']['random_choice']
    )

    if system == 'Linux':
        lib_path = conf['library_conf']['centos_lib_path']
    else:
        lib_path = conf['library_conf']['os_x_lib_path']
    smooth_area_provider = SmoothAreaProvider(lib_path)


def init_config():
    log.info("load config")
    global conf
    with open(os.path.join(basedir, "config_server.yml"), 'r') as f:
        conf = yaml.load(f.read(), Loader=yaml.Loader)
        load_from_config()


def init():
    init_config()


def run():
    try:
        from service.base import gen_all_pic
        gen_all_pic()
    except Exception as e:
        traceback.print_exc()


def start():
    init()
    process_count = conf['gen_mode_conf']['process_count']
    print('Parent process {pid}.'.format(pid=os.getpid()))
    print('process count : {process_count}'.format(process_count=process_count))

    p = Pool(process_count)
    for i in range(process_count):
        p.apply_async(run)
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')
