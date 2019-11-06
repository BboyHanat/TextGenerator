"""
Name : SmoothAreaProvider.py
Author  : Hanat
Contect : hanati@tezign.com
Time    : 2019-09-20 17:41
Desc:
"""
import cv2
import numpy as np
from ctypes import *


def c_array(ctype, values):
    arr = (ctype * len(values))()
    arr[:] = values
    return arr


def array_to_image(arr):
    c = arr.shape[2]
    h = arr.shape[0]
    w = arr.shape[1]
    arr = np.reshape(arr, (c*h*w))
    arr = list(arr)
    data = c_array(c_uint8, arr)
    im = IMAGE(w, h, c, data)
    return im


class Rect_C(Structure):
    _fields_ = [("left", c_int),
                ("top", c_int),
                ("right", c_int),
                ("bottom", c_int)]


class InOut_Rect(Structure):
    _fields_ = [("num", c_int),
                ("rect", POINTER(Rect_C))]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_uint8))]


class SmoothAreaProvider(object):
    def __init__(self, lib_path):
        lib = CDLL(lib_path)
        segment = lib.SegmentImage
        segment.argtypes = [POINTER(IMAGE), POINTER(IMAGE)]

        self.segment = lib.SegmentImage
        self.segment.argtypes = [POINTER(IMAGE), POINTER(IMAGE)]

        self.segment_and_getrect = lib.SegmentImageAndgetRect
        self.segment_and_getrect.argtypes = [POINTER(IMAGE)]
        self.segment_and_getrect.restype = POINTER(InOut_Rect)

        self.free_io_rect = lib.freeRectPtr
        self.free_io_rect.argtypes = [POINTER(InOut_Rect)]

    def get_image_rects(self, image):
        """

        :param image:
        :return:
        """
        assert type(image) == np.ndarray
        shape = image.shape
        if len(shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        elif shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        img = array_to_image(image)
        rects_ptr = self.segment_and_getrect(img)
        print(rects_ptr[0].num)
        num = int(rects_ptr[0].num)
        rects = list()
        for i in range(num):
            rect = rects_ptr[0].rect[i]
            rects.append([rect.left, rect.top, rect.right, rect.bottom])
        self.free_io_rect(rects_ptr)
        return rects


if __name__=='__main__':
    smooth = SmoothAreaProvider('../../libs/libImgSegmentation.dylib')
    image = cv2.imread("../../5.jpg")
    rects = smooth.get_image_rects(image)
    print(rects)
