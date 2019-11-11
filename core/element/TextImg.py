import cv2
from typing import List
from core.element.BaseImg import BaseImg
from core.element.CharImg import CharImg
from PIL import Image, ImageFont, ImageDraw
import os
import numpy as np
import json
from utils import time_util as tu
import math

TYPE_ORIENTATION_HORIZONTAL = 0
TYPE_ORIENTATION_VERTICAL = 1

TYPE_ALIGN_MODEL_B = 0  # 文本对齐模式：底部/左边 对齐
TYPE_ALIGN_MODEL_C = 1  # 文本对齐模式：居中 对齐
TYPE_ALIGN_MODEL_T = 2  # 文本对齐模式：顶部/右边 对齐


class TextImg(BaseImg):
    """
    字符串图片对象
    """

    def __init__(self,
                 char_obj_list: List[CharImg],
                 text_img_output_dir,
                 text_img_info_output_dir,
                 orientation,
                 align_mode,
                 img: Image.Image = None,
                 img_path: str = None,
                 **kwargs
                 ):
        tmp_list = []
        for item in char_obj_list:
            if isinstance(item, dict):
                tmp_list.append(CharImg(**item))
        if tmp_list:
            char_obj_list = tmp_list

        self.char_obj_list = char_obj_list
        self.text = "".join([char_obj.char for char_obj in self.char_obj_list])
        self.text_img_output_dir = text_img_output_dir
        self.text_img_info_output_dir = text_img_info_output_dir
        self.orientation = orientation
        self.align_mode = align_mode

        if img_path:
            self.img_name = img_path.split(os.sep)[-1]
            self.name = self.img_name.split('.')[0]
            self.img_path = img_path
            self.img = load_img(self.img_path)
        else:
            self.name = self._gen_name(align_mode, orientation)
            self.img_name = self.name + ".png"
            self.img_path = os.path.join(text_img_output_dir, self.img_name)
            self.img = img

    def _gen_name(self, align_mode, orientation):
        o = "v" if orientation == TYPE_ORIENTATION_VERTICAL else "h"
        a = 'b'
        if align_mode == TYPE_ALIGN_MODEL_T:
            a = 't'
        elif align_mode == TYPE_ALIGN_MODEL_C:
            a = 'c'
        return tu.timestamp() + "_" + o + "_" + a + "_" + self.text.replace(" ", "_")

    def __repr__(self):
        return json.dumps(self.__dict__, cls=CharImgEncoder)

    def export(self):
        """
        数据导出
        :return:
        """
        self.img.save(self.img_path)
        json_file_path = os.path.join(self.text_img_info_output_dir, self.name + ".json")
        with open(json_file_path, 'w') as f:
            json.dump(self.__dict__, f, cls=CharImgEncoder)

    @staticmethod
    def load_from_json(file_path):
        """
        从json文件中加载对象
        :param file_path:
        :return:
        """
        assert os.path.exists(file_path), "json file is not exist,please check: {file_path}".format(file_path=file_path)
        with open(file_path, 'r') as f:
            j = json.load(f)
            return TextImg(**j)

    def show(self, with_box=False):
        """
        展示图片
        :param with_box:
        :return:
        """
        image = self.cv_img()

        if with_box:
            for char_obj in self.char_obj_list:
                pt1 = (char_obj.box[0], char_obj.box[1])
                pt2 = (char_obj.box[2], char_obj.box[3])
                image = cv2.rectangle(image, pt1=pt1, pt2=pt2, color=(0, 0, 255), thickness=1)

        cv2.imshow(self.text, image)
        cv2.waitKey()
        cv2.destroyWindow(self.text)

    def cv_img(self):
        """
        获取opencv的image对象
        :return:
        """
        image = np.array(self.img)
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)
        return image

    def pil_img(self):
        """
        获取pillow的image对象
        :return:
        """
        return self.img


class CharImgEncoder(json.JSONEncoder):
    def default(self, o):
        if not isinstance(o, Image.Image):
            return o.__dict__


def load_img(img_path):
    """
    从磁盘上加载图片文件
    :param img_path:
    :return:
    """
    assert os.path.exists(img_path), "image is not exist, please check. {img_path}".format(img_path=img_path)
    return Image.open(img_path)


def calc_bg_size(font_path: str,
                 orientation: int,
                 char_obj_list: List[CharImg],
                 spacing_rate: float) -> tuple:
    """
    计算背景尺寸
    :param font_path: 字体路径
    :param orientation: 朝向
    :param char_obj_list: 字符对象
    :param spacing_rate: 间距 (相对于文字大小的占比)
    :return:
    """

    max_char_bg_w = 0
    max_char_bg_h = 0

    bg_w = 0
    bg_h = 0

    for index, char_obj in enumerate(char_obj_list):
        font = ImageFont.truetype(font_path, size=char_obj.font_size)

        # 获取当前字符的背景尺寸
        char_bg_w, char_bg_h = font.getsize(char_obj.char)
        # 加上边框尺寸
        char_bg_w += char_obj.border_width * 2
        char_bg_h += char_obj.border_width * 2

        char_obj.size = (char_bg_w, char_bg_h)

        # 获取当前行文本的最大字符图片的宽高
        max_char_bg_w = char_bg_w if char_bg_w > max_char_bg_w else max_char_bg_w
        max_char_bg_h = char_bg_h if char_bg_h > max_char_bg_h else max_char_bg_h

        # 判断是否遍历到了最后一个字符的位置
        is_last = index == len(char_obj_list) - 1

        r = 0 if is_last else spacing_rate

        if orientation == TYPE_ORIENTATION_VERTICAL:
            bg_w = max_char_bg_w
            bg_h += math.ceil(char_obj.size[1] * (1 + r))
        else:
            bg_w += math.ceil(char_obj.size[0] * (1 + r))
            bg_h = max_char_bg_h

    return bg_w, bg_h


def draw_text(font_path, bg_w, bg_h, orientation, char_obj_list: List[CharImg], spacing_rate, align_mode):
    """
    在文字贴图背景上绘制文字
    :param font_path:
    :param bg_w:
    :param bg_h:
    :param orientation:
    :param char_obj_list:
    :param spacing_rate:
    :param align_mode:
    :return:
    """
    img = Image.new("RGBA", (bg_w, bg_h), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    tmp_char = None
    l, t = 0, 0
    for index, char_obj in enumerate(char_obj_list):
        font = ImageFont.truetype(font_path, size=char_obj.font_size)

        cw, ch = char_obj.size

        if orientation == TYPE_ORIENTATION_VERTICAL:
            if align_mode == TYPE_ALIGN_MODEL_B:
                l = 0
            elif align_mode == TYPE_ALIGN_MODEL_C:
                l = math.ceil((bg_w - cw) / 2)
            elif align_mode == TYPE_ALIGN_MODEL_T:
                l = bg_w - cw

            if tmp_char:
                add_t = math.ceil(tmp_char.size[1] * (1 + spacing_rate))
                t += add_t
            else:
                t = 0
            char_obj.box = [l, t, l + cw, t + ch]

        else:
            if align_mode == TYPE_ALIGN_MODEL_B:
                t = bg_h - ch
            elif align_mode == TYPE_ALIGN_MODEL_C:
                t = math.ceil((bg_h - ch) / 2)
            elif align_mode == TYPE_ALIGN_MODEL_T:
                t = 0

            if tmp_char:
                add_l = math.ceil(tmp_char.size[0] * (1 + spacing_rate))
                l += add_l
            else:
                l = 0
            char_obj.box = [l, t, l + cw, t + ch]

        draw.text((l + char_obj.border_width, t + char_obj.border_width),
                  text=char_obj.char,
                  fill=char_obj.color,
                  font=font)
        if char_obj.border_width > 0:
            draw.rectangle(xy=tuple(char_obj.box), width=char_obj.border_width, outline=char_obj.border_color)
        tmp_char = char_obj
    return img


def gen_batch_char_obj(text,
                       color,
                       font_size,
                       border_width=0,
                       border_color=(0, 0, 0, 0)) -> List[CharImg]:
    """
    生成一批CharImg对象
    :param text:
    :param color:
    :param font_size:
    :param border_width:
    :param border_color:
    :return:
    """
    char_obj_list = []
    for char in text:
        char_obj_list.append(
            CharImg(char, font_size=font_size, color=color, border_width=border_width, border_color=border_color))
    return char_obj_list


def create(char_obj_list: List[CharImg],
           orientation: int = TYPE_ORIENTATION_HORIZONTAL,
           align_mode: int = TYPE_ALIGN_MODEL_B,
           spacing_rate: float = 0.08,
           font_path="",
           text_img_output_dir="",
           text_img_info_output_dir=""
           ):
    """
    生成文本图片
    :param char_obj_list: 字符对象列表
    :param orientation: 生成的方向
    :param align_mode: 文本对齐模式
    :param spacing_rate: 间距 (相对于文字大小的占比)
    :param font_path: 字体文件路径
    :param text_img_output_dir:
    :param text_img_info_output_dir:
    :return:
    """
    # 生成文本贴图的透明背景区域
    bg_w, bg_h = calc_bg_size(font_path, orientation, char_obj_list, spacing_rate)

    # 绘制文字
    img = draw_text(font_path, bg_w, bg_h, orientation, char_obj_list, spacing_rate, align_mode)

    return TextImg(char_obj_list=char_obj_list,
                   text_img_output_dir=text_img_output_dir,
                   text_img_info_output_dir=text_img_info_output_dir,
                   orientation=orientation,
                   align_mode=align_mode,
                   img=img)
