from core.provider.textimg.layout import layout_factory
from core import text_img_provider, background_img_provider, text_provider, smooth_area_provider, conf
from PIL import Image
from lxml.etree import Element, SubElement, tostring
from utils.decorator import count_time
from utils import log
from utils import font_tool
import shutil
import os
import json
import numpy as np


def get_pic_dir(out_put_dir):
    img_dir = os.path.join(out_put_dir, "img")
    pic_dir = os.path.join(img_dir, "pic")
    return pic_dir


def get_fragment_dir(out_put_dir):
    img_dir = os.path.join(out_put_dir, "img")
    fragment_dir = os.path.join(img_dir, "fragment")
    return fragment_dir


def get_data_dir(out_put_dir):
    data_dir = os.path.join(out_put_dir, "data")
    return data_dir


def get_label_data_dir(out_put_dir):
    label_data = os.path.join(out_put_dir, "label_data")
    return label_data


def get_voc_data_dir(out_put_dir):
    voc_data = os.path.join(out_put_dir, "voc_data")
    return voc_data


def gen_all_pic():
    """
    生成全部图片
    :return:
    """
    gen_count = conf['layout_gen_conf']['gen_count']

    index = 0
    while index < gen_count:
        log.info("-" * 20 + " generate new picture {index}/{gen_count}".format(index=index,
                                                                               gen_count=gen_count) + "-" * 20)
        if gen_pic():
            index += 1


def gen_pic():
    out_put_dir = conf['layout_gen_conf']['out_put_dir']

    bg_img = load_bg_img()

    group_box_list = smooth_area_provider.get_image_rects(np.asarray(bg_img))
    # group_box_list = test_gen_group_box(bg_img)
    layout = layout_factory(
        bg_img=bg_img,
        group_box_list=group_box_list,
        text_provider=text_provider,
        text_img_provider=text_img_provider,
        out_put_dir=out_put_dir
    )
    layout.gen()
    if not layout.is_empty():
        layout.dump()
        # layout.show(draw_rect=True)
        return True
    else:
        log.info("-" * 10 + "layout is empty" + "-" * 10)
        return False


def gen_label_data():
    """
    生成标签文件
    :return:
    """
    out_put_dir = conf['layout_gen_conf']['out_put_dir']

    label_data_dir = get_label_data_dir(out_put_dir=out_put_dir)
    lable_file_path = os.path.join(label_data_dir, "label.txt")
    fragment_dir = get_fragment_dir(out_put_dir)

    # 删除原有的标签文件
    shutil.rmtree(label_data_dir, ignore_errors=True)
    # 拷贝图片
    shutil.copytree(fragment_dir, label_data_dir)
    log.info("copy fragment img success")

    # 生成标签文本
    data_dir = get_data_dir(out_put_dir)

    lines = []
    for file_name in os.listdir(data_dir):
        data_file = os.path.join(data_dir, file_name)
        with open(data_file, 'r') as f:
            data = json.load(f)
            for fragment in data['fragment']:
                txt = fragment['data']
                img_name = fragment['fragment_name']
                lines.append(img_name + "^" + txt + os.linesep)

    with open(lable_file_path, 'w') as f:
        f.writelines(lines)
    log.info("gen label data success!")


def gen_all_voc():
    """
    生成voc数据集
    :return:
    """
    out_put_dir = conf['layout_gen_conf']['out_put_dir']

    voc_data_dir = get_voc_data_dir(out_put_dir=out_put_dir)

    # 删除原有的标签文件
    shutil.rmtree(voc_data_dir, ignore_errors=True)
    os.makedirs(voc_data_dir, exist_ok=True)

    voc_img_dir = os.path.join(voc_data_dir, "voc_img")
    voc_xml_dir = os.path.join(voc_data_dir, "voc_xml")
    os.makedirs(voc_xml_dir, exist_ok=True)

    pic_dir = get_pic_dir(out_put_dir)

    # 拷贝图片
    shutil.copytree(pic_dir, voc_img_dir)
    log.info("copy img success")

    # 生成标签文本
    data_dir = get_data_dir(out_put_dir)

    for file_name in os.listdir(data_dir):
        data_file = os.path.join(data_dir, file_name)
        with open(data_file, 'r') as f:
            data = json.load(f)
            _gen_voc(voc_xml_dir, data=data)
    log.info("voc data gen success")


def _gen_voc(save_dir, data, image_format='jpg'):
    w = data['width']
    h = data['height']

    node_root = Element('annotation')
    '''folder'''
    node_folder = SubElement(node_root, 'folder')
    node_folder.text = 'JPEGImages'
    '''filename'''
    node_filename = SubElement(node_root, 'filename')
    node_filename.text = data['pic_name']
    '''source'''
    node_source = SubElement(node_root, 'source')
    node_database = SubElement(node_source, 'database')
    node_database.text = 'The VOC2007 Database'
    node_annotation = SubElement(node_source, 'annotation')
    node_annotation.text = 'PASCAL VOC2007'
    node_image = SubElement(node_source, 'image')
    node_image.text = 'flickr'
    '''size'''
    node_size = SubElement(node_root, 'size')
    node_width = SubElement(node_size, 'width')
    node_width.text = str(w)
    node_height = SubElement(node_size, 'height')
    node_height.text = str(h)
    node_depth = SubElement(node_size, 'depth')
    node_depth.text = '3'
    '''segmented'''
    node_segmented = SubElement(node_root, 'segmented')
    node_segmented.text = '0'
    '''object coord and label'''
    for i, fragment in enumerate(data['fragment']):
        node_object = SubElement(node_root, 'object')
        node_name = SubElement(node_object, 'name')
        node_name.text = fragment['orientation'][0] + "_text"
        node_truncated = SubElement(node_object, 'truncated')
        node_truncated.text = '0'
        node_difficult = SubElement(node_object, 'difficult')
        node_difficult.text = '0'
        node_bndbox = SubElement(node_object, 'bndbox')
        node_xmin = SubElement(node_bndbox, 'xmin')
        node_xmin.text = str(fragment['box'][0])
        node_ymin = SubElement(node_bndbox, 'ymin')
        node_ymin.text = str(fragment['box'][1])
        node_xmax = SubElement(node_bndbox, 'xmax')
        node_xmax.text = str(fragment['box'][2])
        node_ymax = SubElement(node_bndbox, 'ymax')
        node_ymax.text = str(fragment['box'][3])

    xml = tostring(node_root, pretty_print=True)  # 格式化显示，该换行的换行

    save_xml = os.path.join(save_dir, data['pic_name'].replace(image_format, 'xml'))
    with open(save_xml, 'wb') as f:
        f.write(xml)


def test_gen_group_box(bg_img):
    """
    临时用来生成候选区域的方法，等智能候选区选择算法补充之后，将此处逻辑替换掉
    :param bg_img:
    :return:
    """
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
def load_bg_img():
    np_img = background_img_provider.gen.__next__()
    # bgr 转 rgb
    np_img = np_img[..., ::-1]
    img = Image.fromarray(np_img, mode='RGB')
    return img
