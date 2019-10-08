from core.provider.TextImgProvider import TextImg
from PIL import Image, ImageDraw
from core.constant import const
from core.provider.textimg.layout.strategy import Strategy
from core.provider.TextProvider import TextProvider
from core.provider.TextImgProvider import TextImgProvider
from utils.decorator import count_time
from utils import log
from utils.random_tools import Random
import numpy as np
import cv2
import os
import hashlib
import json


class Block:
    def __init__(self, img: Image.Image, inner_x=0, inner_y=0, margin=0, rotate_angle=0):
        self.inner_box = ()
        self.outer_box = ()
        self.img = img
        self.img = self.img.rotate(angle=rotate_angle, expand=True)

        self.margin = margin

        self.inner_width = self.img.width
        self.inner_height = self.img.height
        self.inner_size = (self.inner_width, self.inner_height)

        self.outer_width = self.inner_width + 2 * margin
        self.outer_height = self.inner_height + 2 * margin
        self.outer_size = (self.outer_width, self.outer_height)

        self.locate_by_inner(inner_x=inner_x, inner_y=inner_y)

    def get_data(self):
        pass

    def locate_by_inner(self, inner_x, inner_y):
        self.inner_box = (inner_x, inner_y, inner_x + self.img.width, inner_y + self.img.height)
        self.outer_box = (inner_x - self.margin,
                          inner_y - self.margin,
                          inner_x + self.img.width + self.margin,
                          inner_y + self.img.height + self.margin)

    def locate_by_outter(self, outer_x, outer_y):
        inner_x = outer_x + self.margin
        inner_y = outer_y + self.margin
        self.locate_by_inner(inner_x, inner_y)

    def get_img(self) -> Image.Image:
        return self.img

    def get_alpha_mask(self):
        r, g, b, a = self.get_img().split()
        return a

    def crop_self(self, bg_img: Image.Image):
        return bg_img.crop(self.inner_box)


class TextBlock(Block):
    def __init__(self, text_img: TextImg, inner_x=0, inner_y=0, margin=0, rotate_angle=0):
        self.img = text_img.img
        super().__init__(self.img, inner_x, inner_y, margin=margin, rotate_angle=rotate_angle)
        # todo:字符边框坐标位置的重新计算
        # for char_obj in text_img.char_obj_list:
        #     char_obj.box = # 更新为矩阵旋转变换后的位置

        self.text_img = text_img

    def get_img(self) -> Image.Image:
        return super().get_img()

    def get_data(self):
        return str(self.text_img.text)


class BlockGroup:
    def __init__(self, bg_img: Image.Image, group_box, text_provider: TextProvider = None, text_img_provider=None):
        self.bg_img = bg_img
        self.group_box = group_box
        self.block_list = []
        self.width = group_box[2] - group_box[0]
        self.height = group_box[3] - group_box[1]
        self.bg_width = self.bg_img.width
        self.bg_height = self.bg_img.height

        self.text_provider = text_provider
        self.text_img_provider = text_img_provider

    def auto_append_block(self, target_strategy=None):
        """
        自动添加block
        :param target_strategy
        :return:
        """
        from core.provider.textimg.layout.strategy import strategy_controller as sc
        strategy = sc.pick(target_strategy)
        # 尝试生成3次 提高贴图成功率
        retry_times = 3
        while retry_times > 0:
            block = self._gen_block(strategy)
            r = False
            if block:
                r = strategy.logic(self, block)
                if r:
                    self.block_list.append(block)
                    if isinstance(block, TextBlock):
                        log.info("add text on box:[{group_box}] [{strategy}] > {text}".format(
                            group_box=self.group_box,
                            strategy=strategy.name(),
                            text=block.text_img.text))
            if not r:
                retry_times -= 1

    def _gen_block(self, strategy: Strategy):
        """
        生成一个block
        :return:
        """
        from core.provider.TextImgProvider import text_img_generator, TYPE_ORIENTATION_HORIZONTAL, \
            TYPE_ORIENTATION_VERTICAL, TYPE_ALIGN_MODEL_B, TYPE_ALIGN_MODEL_T, TYPE_ALIGN_MODEL_C
        from core.provider.textimg.layout.strategy.HorizontalStrategy import HorizontalStrategy
        from core.provider.textimg.layout.strategy.VerticalStrategy import VerticalStrategy
        from core.provider.textimg.layout.strategy.CustomizationStrategy1 import CustomizationStrategy1

        text = "".join(self.text_provider.gen.__next__())
        fp = self.text_img_provider.next_font_path()

        if isinstance(strategy, HorizontalStrategy):
            orientation = TYPE_ORIENTATION_VERTICAL
        elif isinstance(strategy, VerticalStrategy):
            orientation = TYPE_ORIENTATION_HORIZONTAL
        elif isinstance(strategy, CustomizationStrategy1):
            if self.block_list:
                orientation = TYPE_ORIENTATION_HORIZONTAL
            else:
                orientation = TYPE_ORIENTATION_VERTICAL
        else:
            orientation = Random.random_choice_list([TYPE_ORIENTATION_VERTICAL])
        align = Random.random_choice_list([TYPE_ALIGN_MODEL_B, TYPE_ALIGN_MODEL_T, TYPE_ALIGN_MODEL_C])

        v = min(self.width, self.height)
        font_size = Random.random_int(v // 30, v // 10)

        rotate_angle = Random.random_int(-8, 8)

        text_img = text_img_generator.gen_text_img(self.text_img_provider, text,
                                                   font_size=font_size,
                                                   color=self.get_fontcolor(),
                                                   orientation=orientation,
                                                   align_mode=align,
                                                   font_path=fp)

        text_block = TextBlock(text_img=text_img, margin=10, rotate_angle=rotate_angle)
        return text_block

    def preview(self, draw_rect=False):
        """
        预览
        :param draw_rect:
        :return:
        """
        bg_img = self.render(draw_rect, on_origin=False)
        bg_img.show("")

    def render(self, draw_rect=False, on_origin=True):
        """
        渲染
        :param draw_rect:
        :param on_origin: 是否在原图上渲染
        :return:
        """
        mode = "RGBA"
        if not self.bg_img:
            bg_img = Image.new(mode, size=(self.width, self.height))
        else:
            if on_origin:
                bg_img = self.bg_img
            else:
                bg_img = self.bg_img.copy()
        draw = ImageDraw.Draw(bg_img, mode)
        for block in self.block_list:
            img = block.get_img()
            mask = block.get_alpha_mask()
            bg_img.paste(img, block.inner_box, mask=mask)

            if draw_rect:
                draw.rectangle(xy=block.outer_box, width=1, outline=const.COLOR_RED)
                draw.rectangle(xy=block.inner_box, width=1, outline=const.COLOR_GREEN)

        if draw_rect:
            draw.rectangle(xy=self.group_box, width=0, outline=const.COLOR_TRANSPARENT,
                           fill=const.COLOR_HALF_TRANSPARENT)
        sub_img = bg_img.crop(self.group_box)
        return sub_img

    def get_fontcolor(self):
        """
        get font color by mean
        :param image:
        :return:
        """
        image = np.asarray(self.bg_img)
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


class Layout:
    def __init__(self,
                 bg_img: Image.Image,
                 out_put_dir: str,
                 group_box_list: list = [],
                 text_provider: TextProvider = None,
                 text_img_provider: TextImgProvider = None):
        self.bg_img = bg_img
        self.out_put_dir = out_put_dir
        self.group_box_list = group_box_list
        self.text_provider = text_provider
        self.text_img_provider = text_img_provider

        self.block_group_list = []
        for group_box in self.group_box_list:
            block_group = BlockGroup(bg_img, group_box, self.text_provider, self.text_img_provider)
            self.block_group_list.append(block_group)

    def get_all_block_list(self):
        """
        获取所有的block
        :return:
        """
        all_block_list = []
        for block_group in self.block_group_list:
            block_list = block_group.block_list
            all_block_list.extend(block_list)
        return all_block_list

    @count_time(tag="自动生成文字贴图")
    def gen(self, target_strategy=None):
        """
        开始自动生成
        :param target_strategy: 目标策略
        :return:
        """
        for index, block_group in enumerate(self.block_group_list):
            log.info("start append block ---- {index} ----".format(index=index))
            block_group.auto_append_block(target_strategy=target_strategy)
        self.render()

    @count_time(tag="区块片收集")
    def collect_block_fragment(self):
        fragment_info_list = []
        for block in self.get_all_block_list():
            fragment_img = block.crop_self(self.bg_img)
            fragment_box = block.inner_box
            fragment_data = block.get_data()
            item = {
                "img": fragment_img,
                "box": fragment_box,
                "data": fragment_data,
                "type": str(block.__class__.__name__)
            }
            fragment_info_list.append(item)
        return fragment_info_list

    @count_time("dump layout info")
    def dump(self):
        result = {}
        img_dir = os.path.join(self.out_put_dir, "img")
        data_dir = os.path.join(self.out_put_dir, "data")
        os.makedirs(img_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)

        name = hashlib.sha1(self.bg_img.tobytes()).hexdigest()

        bg_name = "background_" + name + ".jpg"
        bg_img_path = os.path.join(img_dir, bg_name)
        with open(bg_img_path, 'wb') as f:
            self.bg_img.save(f)
        result['bg_img_path'] = bg_img_path
        result['fragment'] = []

        for index, fragment in enumerate(self.collect_block_fragment()):
            fragment_img = fragment['img']
            fragment_img_name = "fragment_" + name + str(index) + ".jpg"
            fragment_img_path = os.path.join(img_dir, fragment_img_name)
            with open(fragment_img_path, 'wb') as f:
                fragment_img.save(f)
            fragment.pop("img")
            fragment['img_path'] = fragment_img_path

            result['fragment'].append(fragment)

        json_file_name = name + ".json"
        with open(os.path.join(data_dir, json_file_name), 'w', encoding='utf-8') as f:
            json.dump(result, f)

        log.info("{name} dump success! ".format(name=name))

    def show(self, draw_rect=False):
        self.render(draw_rect=draw_rect)
        self.bg_img.show("")

    def render(self, draw_rect=False):
        """
        渲染
        :param draw_rect:
        :return:
        """
        for block_group in self.block_group_list:
            block_group.render(draw_rect=draw_rect, on_origin=True)


def layout_factory(bg_img: Image.Image,
                   group_box_list: list,
                   text_provider: TextProvider,
                   text_img_provider: TextImgProvider,
                   out_put_dir,
                   ) -> Layout:
    """
    生成layout的工厂方法
    :param bg_img:
    :param group_box_list:
    :param text_provider:
    :param text_img_provider:
    :param out_put_dir:
    :return:
    """
    layout = Layout(bg_img=bg_img, out_put_dir=out_put_dir, group_box_list=group_box_list, text_provider=text_provider,
                    text_img_provider=text_img_provider)
    return layout


if __name__ == '__main__':
    # from core import text_img_provider
    # from core.provider.TextImgProvider import text_img_generator

    bg_img_path = "/Users/lijianan/Documents/workspace/github/TextGenerator/data/img/spider_man.jpeg"

    bg_img = Image.open(bg_img_path)
    layout = Layout(bg_img=bg_img, group_box_list=[
        (0, 0, 500, 200),
        (30, 300, 800, 800)
    ])
    layout.gen()
    layout.show(draw_rect=True)

    # # 获取一个字体文件的路径
    # fp = text_img_provider.next_font_path()
    #
    # # 导出文本图片
    # text_img = text_img_generator.gen_text_img(text_img_provider, "hello world", color=const.COLOR_BLUE, font_path=fp)
    #
    # text_block = TextBlock(text_img=text_img, inner_x=200, inner_y=200, margin=40, rotate_angle=15)
    # bg_img_path = "/Users/lijianan/Documents/workspace/github/TextGenerator/data/img/spider_man.jpeg"
    # bg_img = Image.open(bg_img_path)
    # layout = Layout(bg_img=bg_img, block_list=[])
    # layout.preview(draw_rect=True)
