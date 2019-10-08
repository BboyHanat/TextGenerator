from core.provider.textimg.layout import layout_factory

from core import text_img_provider, background_img_provider, text_provider, conf
from PIL import Image
from utils.decorator import count_time
from utils import log

out_put_dir = conf['layout_gen_conf']['out_put_dir']


class Pipeline:

    def start(self):
        while True:
            log.info("-" * 20 + " generate new picture " + "-" * 20)
            self.gen_pic()

    def gen_pic(self):
        bg_img = self.load_bg_img()
        group_box_list = self.test_gen_group_box(bg_img)
        layout = layout_factory(
            bg_img=bg_img,
            group_box_list=group_box_list,
            text_provider=text_provider,
            text_img_provider=text_img_provider,
            out_put_dir=out_put_dir
        )
        layout.gen()
        layout.dump()
        layout.show(draw_rect=True)
        pass

    @staticmethod
    def test_gen_group_box(bg_img):
        from utils.random_tools import Random
        from core.provider.textimg.layout.strategy import check_two_box_is_overlap

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

    @count_time(tag="load_background_img")
    def load_bg_img(self):
        np_img = background_img_provider.gen.__next__()
        # bgr 转 rgb
        np_img = np_img[..., ::-1]
        img = Image.fromarray(np_img, mode='RGB')
        return img


pipeline = Pipeline()
pipeline.start()
