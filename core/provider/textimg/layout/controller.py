"""
1.获取可填充的区域框
2.生成一个文本贴图
3.文本贴图旋转 生成新的贴图并更新贴图信息（抠图信息在这里获取）
4.旋转后贴图送入布局策略器 获取可放置的位置
5.如果可放置，更新布局信息，如果不可放置，（再选下一组尝试 or 终止生成）
6.如果达到终止生成条件，终止生成
7.将layout信息中的数据绘制出来

"""
from PIL import Image
from core.provider.TextImgProvider import TextImg


def paste(bg_img: Image.Image, text_img: TextImg, layout_info=None, strategy=None):
    img = text_img.pil_img()

    img = img.rotate(20, expand=True)

    bg_img = bg_img.convert("RGBA")
    x, y = 0, 0

    box = (x, y, x + img.size[0], y + img.size[1])
    r, g, b, a = img.split()
    bg_img.paste(img, box, mask=a)

    crop = bg_img.crop(box=box)
    crop.show()

    bg_img.show()

    pass


if __name__ == '__main__':
    from core.provider.TextImgProvider import text_img_generator
    from core import text_img_provider
    from core.constant import const

    # 获取一个字体文件的路径
    fp = text_img_provider.next_font_path()

    # 导出文本图片
    text_img = text_img_generator.gen_text_img(text_img_provider, "hello world", color=const.COLOR_BLUE, font_path=fp,
                                               font_size=88)

    # cv2.imshow("", cv_img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    bg_img_path = '/Users/lijianan/Documents/workspace/github/TextGenerator/data/img/spider_man.jpeg'
    bg_img = Image.open(bg_img_path)

    paste(bg_img, text_img)
