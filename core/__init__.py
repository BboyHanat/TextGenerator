import os
from ruamel import yaml

basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')

with open(os.path.join(basedir, "config.yml"), 'r') as f:
    conf = yaml.load(f.read(), Loader=yaml.Loader)

from core.provider.TextImgProvider import TextImgProvider

text_img_provider = TextImgProvider(seed=conf['random_conf']['seed'],
                                    font_file_dir=conf['path_conf']['font_file_dir'],
                                    text_img_output_dir=conf['path_conf']['text_img_output_dir'],
                                    text_img_info_output_dir=conf['path_conf']['text_img_info_output_dir'])
