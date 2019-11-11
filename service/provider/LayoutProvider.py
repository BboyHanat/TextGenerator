from core.layout import Layout
import numpy as np
from PIL import Image


class LayoutProvider:
    def __init__(self, out_put_dir, rotate_angle_range):
        self.out_put_dir = out_put_dir
        self.rotate_angle_range = eval(rotate_angle_range) if type(rotate_angle_range) is str else rotate_angle_range
        pass

    def gen_next_layout(self):
        from service import background_img_provider
        bg_img = background_img_provider.gen.__next__()
        group_box_list = gen_group_box_list(bg_img)

        layout = layout_factory(
            bg_img=bg_img,
            group_box_list=group_box_list,
            out_put_dir=self.out_put_dir,
            rotate_angle_range=self.rotate_angle_range
        )
        layout.gen()
        return layout


def layout_factory(bg_img: Image.Image,
                   group_box_list: list,
                   out_put_dir,
                   rotate_angle_range
                   ) -> Layout:
    """
    生成layout的工厂方法
    :param bg_img:
    :param group_box_list:
    :param out_put_dir:
    :param rotate_angle_range:
    :return:
    """
    from service import text_img_provider
    layout = Layout(bg_img=bg_img, out_put_dir=out_put_dir, group_box_list=group_box_list,
                    text_img_provider=text_img_provider, rotate_angle_range=rotate_angle_range)
    return layout


def gen_group_box_list(bg_img):
    """
    生成候选区
    :param bg_img:
    :return:
    """
    from service import smooth_area_provider
    width = bg_img.width
    height = bg_img.height
    to_width = 320
    to_height = 320
    rw = width / to_width
    rh = height / to_height
    bg_img_copy = bg_img.resize(size=(to_width, to_height))
    calc_group_box_list = smooth_area_provider.get_image_rects(np.asarray(bg_img_copy))
    group_box_list = []
    for box in calc_group_box_list:
        group_box_list.append([int(box[0] * rw),
                               int(box[1] * rh),
                               int(box[2] * rw),
                               int(box[3] * rh)])
    # 如果智能候选区域为空，则随机生成候选区
    if not group_box_list:
        group_box_list = test_gen_group_box(bg_img)
    return group_box_list


def test_gen_group_box(bg_img):
    """
    临时用来生成候选区域的方法，等智能候选区选择算法补充之后，将此处逻辑替换掉
    :param bg_img:
    :return:
    """
    from utils.random_tools import Random
    from core.layout.strategy import check_two_box_is_overlap

    w = bg_img.width
    h = bg_img.height
    min_w = w // 4
    min_h = h // 4

    def gen_one_box():
        l = Random.random_int(0, w)
        t = Random.random_int(0, h)
        r = int(l + min_w * Random.random_float(1, 3))
        b = int(t + min_h * Random.random_float(1, 2))
        box = (l, t, r, b)
        if r > w or b > h:
            return None
        return box

    group_box_list = []
    while True:
        box = gen_one_box()
        if box:
            need_stop = len(group_box_list) >= 5
            for gb in group_box_list:
                if check_two_box_is_overlap(gb, box):
                    need_stop = True
                    break
            if need_stop:
                break
            group_box_list.append(box)
        else:
            continue
    return group_box_list
