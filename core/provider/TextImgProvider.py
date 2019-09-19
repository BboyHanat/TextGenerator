import os
import time
import random
from core import conf
from utils.decorator import singleton


def list_font_path(font_file_dir):
    """
    获取所有的字体文件路径
    :param font_file_dir: 字体文件存放路径
    :return:
    """
    assert os.path.exists(font_file_dir), "font_file_dir is not exist, please check: {font_file_dir}".format(
        font_file_dir=font_file_dir)
    path_list = []
    for item in os.listdir(font_file_dir):
        path = os.path.join(font_file_dir, item)
        path_list.append(path)
    return path_list


@singleton
class TextImgProvider:

    def __init__(self, font_file_dir, seed=time.time()):
        """
        初始化文本图片生成器
        :param font_file_dir: 字体文件路径
        :param seed:
        """
        if not seed:
            seed = time.time()

        font_file_list = list_font_path(font_file_dir)

        random.seed(seed)
        random.shuffle(font_file_list)

        print(font_file_list)


text_img_provider = TextImgProvider(seed=conf['random_conf']['seed'], **conf['text_img_conf'])

if __name__ == '__main__':
    text_img_provider
