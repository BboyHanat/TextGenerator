import os
from ruamel import yaml

from core.provider.TextImgProvider import TextImgProvider
from core.provider.BackgroundImgProvider import BackgroundImgProvider
from core.provider.TextProvider import TextProvider
from utils import log

basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
conf: dict
text_img_provider: TextImgProvider
background_img_provider: BackgroundImgProvider
text_provider: TextProvider


def load_from_config():
    global text_img_provider
    global background_img_provider
    global text_provider

    text_img_provider = TextImgProvider(
        seed=conf['random_conf']['seed'],
        font_file_dir=conf['path_conf']['font_file_dir'],
        text_img_output_dir=conf['path_conf']['text_img_output_dir'],
        text_img_info_output_dir=conf['path_conf']['text_img_info_output_dir']
    )

    background_img_provider = BackgroundImgProvider(
        bg_img_dir=conf['path_conf']['bgimage_dir'],
        # fixme: 需要修改为从配置文件加载
        gen_probability=[0.3, 0.3, 0.4],
        img_format=conf['text_bg_img_conf']['img_can_load_format'],
        gen_random_image=conf['text_bg_img_conf']['gen_random_image']
    )

    text_provider = TextProvider(
        chinese_corpus_path=conf['path_conf']['chinese_corpus_path'],
        english_corpus_path=conf['path_conf']['english_corpus_path'],
        random_character_path=conf['path_conf']['random_character_path'],
        specific_scene_character_path=conf['path_conf']['specific_scene_character_path'],
        characters_len_range=eval(conf['text_gen_conf']['characters_len_range']),
        gen_probability=conf['text_gen_conf']['gen_probability'],
        random_choice=conf['text_gen_conf']['random_choice']
    )


def init_config():
    log.info("load config")
    global conf
    with open(os.path.join(basedir, "config.yml"), 'r') as f:
        conf = yaml.load(f.read(), Loader=yaml.Loader)
        load_from_config()


init_config()
