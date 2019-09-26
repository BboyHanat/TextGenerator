import time
from utils import log


def singleton(cls):
    """
    单例模式装饰器
    使用方式：
        @Singleton
        class A(object):
            pass

    :param cls:
    :return:
    """
    _instance = {}

    def _singleton(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return _singleton


def count_time(tag=""):
    def ctime(func):
        def wrapper(*args, **kwargs):
            tic = time.time()  # 程序开始时间
            func(*args, **kwargs)
            toc = time.time()  # 程序结束时间
            cost = toc - tic
            log.info("{tag} {func_name} 耗时 > {cost}".format(tag=tag, func_name=func.__name__, cost=cost))

        return wrapper

    return ctime
