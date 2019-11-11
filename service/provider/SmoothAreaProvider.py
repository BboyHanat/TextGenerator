"""
Name : test.py
Author  : Hanat
Contect : hanati@tezign.com
Time    : 2019-10-16 15:33
Desc:
"""

# cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/data/User/hanat/opencv_install -D WITH_CUDA=ON -D ENABLE_FAST_MATH=1 -D CUDA_FAST_MATH=1 -D WITH_CUBLAS=1 -D WITH_OPENMP=1 ..

import cv2
import numpy as np
from libs import nms
from libs import select_by_kp
from libs import box_connect


def _whctrs(anchor):
    """
    Return width, height, x center, and y center for an anchor (window).
    """
    w = anchor[2] - anchor[0] + 1
    h = anchor[3] - anchor[1] + 1
    x_ctr = anchor[0] + 0.5 * (w - 1)
    y_ctr = anchor[1] + 0.5 * (h - 1)
    return w, h, x_ctr, y_ctr


def _ratio_enum(anchor, ratios):
    """
    Enumerate a set of anchors for each aspect ratio wrt an anchor.
    """

    w, h, x_ctr, y_ctr = _whctrs(anchor)
    size = w * h
    size_ratios = size / ratios
    ws = np.round(np.sqrt(size_ratios))
    hs = np.round(ws * ratios)
    anchors = _mkanchors(ws, hs, x_ctr, y_ctr)
    return anchors


def _scale_enum(anchor, scales):
    """
    Enumerate a set of anchors for each scale wrt an anchor.
    """
    w, h, x_ctr, y_ctr = _whctrs(anchor)
    ws = w * scales
    hs = h * scales
    anchors = _mkanchors(ws, hs, x_ctr, y_ctr)
    return anchors


def _mkanchors(ws, hs, x_ctr, y_ctr):
    """
    Given a vector of widths (ws) and heights (hs) around a center
    (x_ctr, y_ctr), output a set of anchors (windows).
    """
    ws = ws[:, np.newaxis]
    hs = hs[:, np.newaxis]
    anchors = np.hstack((x_ctr - 0.5 * (ws - 1),
                         y_ctr - 0.5 * (hs - 1),
                         x_ctr + 0.5 * (ws - 1),
                         y_ctr + 0.5 * (hs - 1),))
    return anchors


class SmoothAreaProvider(object):
    """

    """

    def __init__(self,
                 down_scale=32,
                 anchor_ratio=(0.17, 0.25, 0.5, 1.0, 2.0, 4.0, 6),
                 anchor_scale=(8, 16, 24, 32, 48, 64, 72, 90)
                 ):
        self._down_scale = down_scale
        self._anchor_ratio = eval(anchor_ratio) if type(anchor_ratio) == str else anchor_ratio
        self._anchor_scale = eval(anchor_scale) if type(anchor_scale) == str else anchor_scale
        # self._fast = cv2.FastFeatureDetector_create()
        self._fast = cv2.ORB_create(nfeatures=3000)

    def get_image_rects(self, image_in, long_side=320):
        """
        get region rects from image smoothness area
        :param image_in:
        :param long_side:
        :return:
        """
        assert type(image_in) == np.ndarray
        if len(image_in.shape) == 2:
            image_process = np.asarray(image_in)
        elif image_in.shape[2] == 3:
            image_process = cv2.cvtColor(image_in, cv2.COLOR_RGB2GRAY)
        elif image_in.shape[2] == 4:
            image_process = cv2.cvtColor(image_in, cv2.COLOR_RGBA2RGB)
        else:
            raise ValueError("wrong image format")

        src_h, src_w = image_process.shape[:2]
        if src_h > src_w:
            new_h = int(long_side)
            scale = src_h / long_side
            new_w = int(src_w / scale)
        else:
            new_w = int(long_side)
            scale = src_w / long_side
            new_h = int(src_h / scale)

        image_process = cv2.resize(image_process, (new_w, new_h))
        anchors, length = self.generate_anchors_pre(new_h, new_w)

        # key_points = self._fast.detect(image_process, None)
        kp_image = cv2.Canny(image_process, 50, 150) // 255
        sum_arr = np.zeros((new_h, new_w), np.float32)
        image_integral = cv2.integral(kp_image, sum_arr, cv2.CV_32FC1)
        anchor_preserved = select_by_kp(image_integral, anchors)
        length = len(anchor_preserved)
        anchor_preserved = np.asarray(anchor_preserved, np.float32)
        if length > 0:
            keep = nms(anchor_preserved, 0.00001)
            anchor_preserved = anchor_preserved[keep, :]
            anchor_preserved = box_connect(image_integral, anchor_preserved, 30, new_w, new_h)
            keep = nms(anchor_preserved, 0.00001)
            anchor_preserved = anchor_preserved[keep, :]

        for i in range(anchor_preserved.shape[0]):
            anchor_preserved[i, :] = anchor_preserved[i, :] * scale
        if anchor_preserved.shape[0] > 0:
            anchor_out = anchor_preserved[:, 0:4]
            score = anchor_preserved[:, 4]
            anchor_out = np.asarray(anchor_out, np.int32)
            anchor_out = list(anchor_out)
            return anchor_out
        else:
            return list()

    def generate_anchors_pre(self, height, width):
        """ A wrapper function to generate anchors given different scales
          Also return the number of anchors in variable 'length'
        """
        anchors = self.generate_anchors(ratios=np.asarray(self._anchor_ratio), scales=np.asarray(self._anchor_scale))
        A = anchors.shape[0]
        shift_x = np.arange(0, width)  # * self._down_scale
        shift_y = np.arange(0, height)  # * self._down_scale
        shift_x, shift_y = np.meshgrid(shift_x, shift_y)
        shifts = np.vstack((shift_x.ravel(), shift_y.ravel(), shift_x.ravel(), shift_y.ravel())).transpose()
        K = shifts.shape[0]
        # width changes faster, so here it is H, W, C
        anchors = anchors.reshape((1, A, 4)) + shifts.reshape((1, K, 4)).transpose((1, 0, 2))
        anchors = anchors.reshape((K * A, 4)).astype(np.float32, copy=False)
        length = np.int32(anchors.shape[0])

        return anchors, length

    @staticmethod
    def generate_anchors(base_size=3, ratios=np.asarray([0.5, 1, 2]),
                         scales=2 ** np.arange(3, 6)):
        """
        Generate anchor (reference) windows by enumerating aspect ratios X
        scales wrt a reference (0, 0, 15, 15) window.
        """

        base_anchor = np.array([1, 1, base_size, base_size], np.float32) - 1
        ratio_anchors = _ratio_enum(base_anchor, ratios)
        anchors = np.vstack([_scale_enum(ratio_anchors[i, :], scales)
                             for i in range(ratio_anchors.shape[0])])
        return anchors


if __name__ == '__main__':
    smooth = SmoothAreaProvider()
    image = cv2.imread("/Users/aidaihanati/TezignProject/TextGenerator/6.jpeg")
    rects = smooth.get_image_rects(image)
    for rect in rects:
        cv2.rectangle(image, (rect[0], rect[1]), (rect[2], rect[3]), (120, 78, 255), 2)
    cv2.imwrite('test.jpg', image)
    cv2.imshow("test", image)
    cv2.waitKey(3000)
