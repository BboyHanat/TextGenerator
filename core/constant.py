from utils.random_tools import Random


class Const:

    def __init__(self):
        self.COLOR_TRANSPARENT = (0, 0, 0, 0)
        self.COLOR_HALF_TRANSPARENT = (0, 0, 0, 55)
        self.COLOR_RED = (255, 0, 0, 255)
        self.COLOR_GREEN = (0, 255, 0, 255)
        self.COLOR_BLUE = (0, 0, 255, 255)
        self.COLOR_BLACK = (0, 0, 0, 255)
        self.COLOR_WHITE = (255, 255, 255, 255)
        self.GET_RANDOM_COLOR = lambda: (
            Random.random_int(0, 255), Random.random_int(0, 255), Random.random_int(0, 255), 255)

    class ConstError(TypeError):
        pass

    def __setattr__(self, key, value):
        if key in self.__dict__.keys():
            # 存在性验证
            raise self.ConstError("Can't change a const variable: '%s'" % key)
        self.__dict__[key] = value


const = Const()
