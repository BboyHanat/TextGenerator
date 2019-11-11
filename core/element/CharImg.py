import json


class CharImg:
    """
    字符图片对象
    """

    def __init__(self, char, font_size, color, box=(0, 0, 0, 0), size=(0, 0), border_width=0,
                 border_color=(0, 0, 0, 0)):
        self.char = char
        self.font_size = font_size
        self.color = color
        self.box = box
        self.size = size
        self.border_width = border_width
        self.border_color = border_color

    def __repr__(self):
        return json.dumps(self.__dict__)
