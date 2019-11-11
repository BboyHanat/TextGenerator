import os
import time
from typing import List
from service.constant import const
from utils.decorator import singleton
from utils.random_tools import Random
from core.element.CharImg import CharImg
from core.element.TextImg import create, gen_batch_char_obj, TYPE_ORIENTATION_HORIZONTAL, TYPE_ORIENTATION_VERTICAL, \
    TYPE_ALIGN_MODEL_C, TYPE_ALIGN_MODEL_B, TYPE_ALIGN_MODEL_T
from core.layout.strategy.HorizontalStrategy import HorizontalStrategy
from core.layout.strategy.VerticalStrategy import VerticalStrategy
from core.layout.strategy.HorizontalFlowStrategy import HorizontalFlowStrategy
from core.layout.strategy.VerticalFlowStrategy import VerticalFlowStrategy
from core.layout.strategy.CustomizationStrategy1 import CustomizationStrategy1
from utils import font_tool
import numpy as np
import cv2


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

    def __init__(self, font_file_dir, text_img_output_dir, text_img_info_output_dir, font_min_size,
                 use_char_common_color_probability,
                 char_common_color_list,
                 char_border_width, char_border_color,
                 seed=time.time()):
        """
        初始化文本图片生成器
        :param font_file_dir: 字体文件目录
        :param text_img_output_dir: 文本图片输出目录
        :param text_img_info_output_dir: 文本图片数据输出目录
        :param font_min_size: 文本字体大小的最小值
        :param use_char_common_color_probability
        :param char_common_color_list
        :param char_border_width: 字符边框的宽度
        :param char_border_color: 字符边框的颜色
        :param seed:
        """
        os.makedirs(text_img_output_dir, exist_ok=True)
        os.makedirs(text_img_info_output_dir, exist_ok=True)

        if not seed:
            seed = time.time()

        self.font_file_list = list_font_path(font_file_dir)
        self._font_index = 0
        self.text_img_output_dir = text_img_output_dir
        self.text_img_info_output_dir = text_img_info_output_dir
        self.font_min_size = font_min_size
        self.use_char_common_color_probability = use_char_common_color_probability
        self.char_common_color_list = char_common_color_list
        self.char_border_width = char_border_width
        self.char_border_color = char_border_color

        Random.shuffle(self.font_file_list, seed)

    def next_font_path(self):
        """
        获取下一个字体路径
        :return:
        """
        font_path = self.font_file_list[self._font_index]
        self._font_index += 1
        if self._font_index >= len(self.font_file_list):
            self._font_index = 0
        return font_path

    def gen_text_img(self, text: str,
                     font_path,
                     color=const.COLOR_BLACK,
                     font_size=14,
                     border_width=0,
                     border_color=const.COLOR_TRANSPARENT,
                     orientation=TYPE_ORIENTATION_HORIZONTAL,
                     align_mode=TYPE_ALIGN_MODEL_C):
        char_obj_list = gen_batch_char_obj(text=text, color=color, font_size=font_size, border_width=border_width,
                                           border_color=border_color)

        text_img = create(char_obj_list=char_obj_list,
                          orientation=orientation,
                          align_mode=align_mode,
                          font_path=font_path,
                          text_img_output_dir=self.text_img_output_dir,
                          text_img_info_output_dir=self.text_img_info_output_dir)
        return text_img

    def gen_complex_text_img(self, char_obj_list: List[CharImg],
                             font_path,
                             orientation=TYPE_ORIENTATION_HORIZONTAL,
                             align_mode=TYPE_ALIGN_MODEL_C):
        """
        生成复杂的文本图片
        :param char_obj_list:
        :param font_path:
        :param orientation:
        :param align_mode:
        :return:
        """
        text_img = create(char_obj_list=char_obj_list,
                          orientation=orientation,
                          align_mode=align_mode,
                          font_path=font_path,
                          text_img_output_dir=self.text_img_output_dir,
                          text_img_info_output_dir=self.text_img_info_output_dir)
        return text_img

    def get_fontcolor(self, bg_img):
        """
        get font color by mean
        :param bg_img:
        :return:
        """
        char_common_color_list = self.char_common_color_list

        if Random.random_float(0, 1) <= self.use_char_common_color_probability and char_common_color_list:
            return eval(Random.random_choice_list(char_common_color_list))
        else:
            image = np.asarray(bg_img)
            lab_image = cv2.cvtColor(image, cv2.COLOR_RGB2Lab)

            bg = lab_image[:, :, 0]
            l_mean = np.mean(bg)

            new_l = Random.random_int(0, 127 - 80) if l_mean > 127 else Random.random_int(127 + 80, 255)
            new_a = Random.random_int(0, 255)
            new_b = Random.random_int(0, 255)

            lab_rgb = np.asarray([[[new_l, new_a, new_b]]], np.uint8)
            rbg = cv2.cvtColor(lab_rgb, cv2.COLOR_Lab2RGB)

            r = rbg[0, 0, 0]
            g = rbg[0, 0, 1]
            b = rbg[0, 0, 2]

            return (r, g, b, 255)

    def auto_gen_next_img(self, width, height, strategy, bg_img, block_list):
        """
        自动生成下一个文本贴图
        :return:
        """
        from service import text_provider
        text = "".join(text_provider.gen.__next__())
        fp = self.next_font_path()

        if isinstance(strategy, HorizontalStrategy):
            orientation = TYPE_ORIENTATION_VERTICAL
        elif isinstance(strategy, VerticalStrategy):
            orientation = TYPE_ORIENTATION_HORIZONTAL
        elif isinstance(strategy, HorizontalFlowStrategy):
            orientation = TYPE_ORIENTATION_HORIZONTAL
        elif isinstance(strategy, VerticalFlowStrategy):
            orientation = TYPE_ORIENTATION_VERTICAL
        elif isinstance(strategy, CustomizationStrategy1):
            if block_list:
                orientation = TYPE_ORIENTATION_HORIZONTAL
            else:
                orientation = TYPE_ORIENTATION_VERTICAL
        else:
            orientation = Random.random_choice_list(
                [TYPE_ORIENTATION_VERTICAL, TYPE_ORIENTATION_HORIZONTAL, TYPE_ORIENTATION_HORIZONTAL])

        v = min(width, height)
        # 设置字体大小

        font_size = Random.random_int(v // 20, v // 10)
        font_size = self.font_min_size if font_size < self.font_min_size else font_size

        # 剔除不存在的文字
        text = "".join(filter(lambda c: font_tool.check(c, font_path=fp), text))
        if len(text) >= 2:
            # 生成文本图片
            align = Random.random_choice_list(
                [TYPE_ALIGN_MODEL_B, TYPE_ALIGN_MODEL_T, TYPE_ALIGN_MODEL_C])
            text_img = self.gen_text_img(text,
                                         font_size=font_size,
                                         border_width=self.char_border_width,
                                         border_color=self.char_border_color,
                                         color=self.get_fontcolor(bg_img),
                                         orientation=orientation,
                                         align_mode=align,
                                         font_path=fp)
            return text_img


if __name__ == '__main__':
    # 使用示例
    from service import init_config

    init_config()
    from service import text_img_provider

    # 获取一个字体文件的路径
    fp = text_img_provider.next_font_path()

    # 导出文本图片
    p = text_img_provider.gen_text_img("hello world", color=const.COLOR_BLUE, font_path=fp)
    p.export()
    # p.show()

    # 构造文本图片
    l = []
    l.extend(gen_batch_char_obj("你好啊", const.COLOR_BLUE, font_size=24))
    l.extend(gen_batch_char_obj("李佳楠", const.COLOR_GREEN, font_size=28))
    r = text_img_provider.gen_complex_text_img(l, font_path=fp)
    r.show()

    # 获取文字区域尺寸信息
    bg_w, bg_h = text_img_provider.calc_bg_size(fp, orientation=TYPE_ORIENTATION_HORIZONTAL, char_obj_list=l,
                                                spacing_rate=0.1)

    print(bg_w)
    print(bg_h)
