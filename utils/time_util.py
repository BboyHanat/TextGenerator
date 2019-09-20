from datetime import datetime


def today():
    time = datetime.now()
    return time.strftime("%Y%m%d")


def timestamp():
    time = datetime.now()
    return time.strftime("%Y%m%d%H%M%S%f")
