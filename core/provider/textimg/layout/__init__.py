from core.provider.TextImgProvider import TextImg, CharImg
from typing import List
from PIL import Image, ImageDraw
from core.constant import const
from core.provider.textimg.layout.strategy import Strategy
from core import text_img_provider
from core.provider.TextImgProvider import text_img_generator


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

        # print('outer box >')
        # print(self.outer_box)

    def get_img(self) -> Image.Image:
        return self.img

    def get_alpha_mask(self):
        r, g, b, a = self.get_img().split()
        return a


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


class BlockGroup:
    def __init__(self, bg_img: Image.Image, group_box):
        self.bg_img = bg_img
        self.group_box = group_box
        self.block_list = []
        self.width = group_box[2] - group_box[0]
        self.height = group_box[3] - group_box[1]

    def auto_append_block(self):
        """
        自动添加block
        :return:
        """
        from core.provider.textimg.layout.strategy import only_one_vertical_strategy as strategy
        r = True
        while r:
            # todo: next block 选择器逻辑开发
            block = self.gen_block()
            r = strategy.logic(self, block)
            if r:
                self.block_list.append(block)
                # todo: crop文本贴图的逻辑可在此处完善

    def add_block(self, block: Block, outer_x, outer_y):
        """
        添加block
        :param block:
        :param outer_x:
        :param outer_y:
        :return:
        """
        self.block_list.append(block)
        block.locate_by_outter(outer_x, outer_y)

    def gen_block(self):
        """
        生成一个block
        :return:
        """
        fp = text_img_provider.next_font_path()
        text_img = text_img_generator.gen_text_img(text_img_provider, "hello world",
                                                   font_size=28,
                                                   color=const.COLOR_BLUE,
                                                   font_path=fp)

        text_block = TextBlock(text_img=text_img, margin=10, rotate_angle=10)
        print(text_block.outer_size)
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
            draw.rectangle(xy=self.group_box, width=0, outline=const.COLOR_TRANSPARENT, fill=const.COLOR_HALF_TRANSPARENT)
        sub_img = bg_img.crop(self.group_box)
        return sub_img


class Layout:
    def __init__(self, bg_img: Image.Image, group_box_list: list = []):
        self.bg_img = bg_img
        self.group_box_list = group_box_list

        self.block_group_list = []
        for group_box in self.group_box_list:
            block_group = BlockGroup(bg_img, group_box)
            self.block_group_list.append(block_group)

    def gen(self):
        """
        开始自动生成
        :return:
        """
        for block_group in self.block_group_list:
            block_group.auto_append_block()

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


if __name__ == '__main__':
    from core import text_img_provider
    from core.provider.TextImgProvider import text_img_generator

    bg_img_path = "/Users/lijianan/Documents/workspace/github/TextGenerator/data/img/spider_man.jpeg"

    bg_img = Image.open(bg_img_path)
    layout = Layout(bg_img=bg_img, group_box_list=[(0, 0, 500, 200), (30, 300, 800, 800)])
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
