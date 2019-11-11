import numpy as np
cimport numpy as np
from libc.stdio cimport printf
# from cython.parallel import prange, parallel, threadid

cdef np.float32_t sigmoid(np.float32_t x):
    return 1.0 / (1.0 + np.exp(-x))

cdef inline np.float32_t max(np.float32_t a, np.float32_t b):
    return a if a >= b else b

cdef inline np.float32_t min(np.float32_t a, np.float32_t b):
    return a if a <= b else b

def select_by_kp(np.ndarray[np.float32_t, ndim=2] imageIntegral, np.ndarray[np.float32_t, ndim=2] anchors):
    """

    :param imageIntegral:
    :param anchors:
    :return:
    """

    anchor_preserved = []
    # score_preserved = []
    cdef int length = anchors.shape[0]
    cdef int count = 0
    cdef int x1, y1, x2, y2,
    cdef int w = imageIntegral.shape[1] - 1
    cdef int h = imageIntegral.shape[0] - 1
    cdef float image_area = float(w * h)
    cdef float area, integral = 0.0
    cdef int add = 0;
    while count < length:
        x1 = int(min(max(0, anchors[count, 0]), w))
        y1 = int(min(max(0, anchors[count, 1]), h))
        x2 = int(min(max(0, anchors[count, 2]), w))
        y2 = int(min(max(0, anchors[count, 3]), h))
        integral = imageIntegral[y2, x2] - imageIntegral[y2, x1] - imageIntegral[y1, x2] + imageIntegral[y1, x1]
        if integral < 1.0:
            area = float((y2 - y1) * (x2 - x1)) / float(image_area)
            # select_out[add, :] = [x1, y1, x2, y2, area]
            anchor_preserved.append([x1, y1, x2, y2, area])
        count += 1
        integral = 0.0
    return anchor_preserved


def nms(np.ndarray[np.float32_t, ndim=2] dets, np.float thresh):
    """

    :param dets:
    :param thresh:
    :return:
    """
    cdef np.ndarray[np.float32_t, ndim=1] x1 = dets[:, 0]
    cdef np.ndarray[np.float32_t, ndim=1] y1 = dets[:, 1]
    cdef np.ndarray[np.float32_t, ndim=1] x2 = dets[:, 2]
    cdef np.ndarray[np.float32_t, ndim=1] y2 = dets[:, 3]
    cdef np.ndarray[np.float32_t, ndim=1] scores = dets[:, 4]

    cdef np.ndarray[np.float32_t, ndim=1] areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    cdef np.ndarray[np.int_t, ndim=1] order = scores.argsort()[::-1]

    cdef int ndets = dets.shape[0]
    cdef np.ndarray[np.int_t, ndim=1] suppressed = \
        np.zeros((ndets), dtype=np.int)

    # nominal indices
    cdef int _i, _j
    # sorted indices
    cdef int i, j
    # temp variables for box i's (the box currently under consideration)
    cdef np.float32_t ix1, iy1, ix2, iy2, iarea
    # variables for computing overlap with box j (lower scoring box)
    cdef np.float32_t xx1, yy1, xx2, yy2
    cdef np.float32_t w, h
    cdef np.float32_t inter, ovr

    keep = []
    for _i in range(ndets):
        i = order[_i]
        if suppressed[i] == 1:
            continue
        keep.append(i)
        ix1 = x1[i]
        iy1 = y1[i]
        ix2 = x2[i]
        iy2 = y2[i]
        iarea = areas[i]
        for _j in range(_i + 1, ndets):
            j = order[_j]
            if suppressed[j] == 1:
                continue
            xx1 = max(ix1, x1[j])
            yy1 = max(iy1, y1[j])
            xx2 = min(ix2, x2[j])
            yy2 = min(iy2, y2[j])
            w = max(0.0, xx2 - xx1 + 1)
            h = max(0.0, yy2 - yy1 + 1)
            inter = w * h
            ovr = inter / (iarea + areas[j] - inter)
            if ovr >= thresh:
                suppressed[j] = 1

    return keep


cdef inline np.int vertical_similarity(np.ndarray[np.float32_t, ndim=1] box1, np.ndarray[np.float32_t, ndim=1] box2, np.float iou_thresh):

    cdef float intersec_height = min(box1[3], box2[3]) - max(box1[1], box2[1])
    cdef float union_height = max(box1[3], box2[3]) - min(box1[1], box2[1])
    cdef float iou = intersec_height / union_height
    if iou > iou_thresh:
        return 1
    else:
        return 0####


def box_connect(np.ndarray[np.float32_t, ndim=2] imageIntegral, np.ndarray[np.float32_t, ndim=2] anchors_in, np.int h_gap, np.int width, np.int height):
    """

    :param imageIntegral:
    :param anchor:
    :return:
    """

    cdef int length = anchors_in.shape[0]
    cdef np.ndarray[np.float32_t, ndim=2] anchors = anchors_in[:, 0:4]
    cdef int x1, y1, x2, y2
    cdef float area, original_area, integral=0.0
    cdef int iou
    cdef float image_area = float(width * height)
    # left to right search
    for box_index1 in range(length):
        box1 = anchors[box_index1, :]
        for box_index2 in range(length):
            box2 = anchors[box_index2, :]
            iou = vertical_similarity(box1, box2, 0.6)
            if box1[2] <= box2[0] <= (box1[2] + h_gap) and iou==1:
                x1 = box1[0]
                y1 = int(min(box1[1], box2[1]))
                x2 = box2[2]
                y2 = int(max(box1[3], box2[3]))
                integral = imageIntegral[y2, x2] - imageIntegral[y2, x1] - imageIntegral[y1, x2] + imageIntegral[y1, x1]
                area = float((y2 - y1) * (x2 - x1))
                if integral<1:
                    area = area / image_area
                    anchors_in[box_index1, 0] = float(x1)
                    anchors_in[box_index1, 1] = float(y1)
                    anchors_in[box_index1, 2] = float(x2)
                    anchors_in[box_index1, 3] = float(y2)
                    anchors_in[box_index1, 4] = area
                    continue

                x1 = box1[0]
                y1 = int(min(box1[1], box2[1]))
                x2 = box2[2]
                y2 = int(min(box1[3], box2[3]))
                integral = imageIntegral[y2, x2] - imageIntegral[y2, x1] - imageIntegral[y1, x2] + imageIntegral[y1, x1]
                area = float((y2 - y1) * (x2 - x1))
                original_area = float((box1[2]-box1[0])*(box1[3]-box1[1])+ (box2[2]-box2[0])*(box2[3]-box2[1]))
                if integral<1 and area > original_area:
                    area = area / image_area
                    anchors_in[box_index1, 0] = float(x1)
                    anchors_in[box_index1, 1] = float(y1)
                    anchors_in[box_index1, 2] = float(x2)
                    anchors_in[box_index1, 3] = float(y2)
                    anchors_in[box_index1, 4] = area
                    continue

                x1 = box1[0]
                y1 = int(max(box1[1], box2[1]))
                x2 = box2[2]
                y2 = int(max(box1[3], box2[3]))
                integral = imageIntegral[y2, x2] - imageIntegral[y2, x1] - imageIntegral[y1, x2] + imageIntegral[y1, x1]
                area = float((y2 - y1) * (x2 - x1))
                original_area = float((box1[2]-box1[0])*(box1[3]-box1[1])+ (box2[2]-box2[0])*(box2[3]-box2[1]))
                if integral<1 and area > original_area:
                    area = area / image_area
                    anchors_in[box_index1, 0] = float(x1)
                    anchors_in[box_index1, 1] = float(y1)
                    anchors_in[box_index1, 2] = float(x2)
                    anchors_in[box_index1, 3] = float(y2)
                    anchors_in[box_index1, 4] = area
                    continue

    return anchors_in