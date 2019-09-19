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
