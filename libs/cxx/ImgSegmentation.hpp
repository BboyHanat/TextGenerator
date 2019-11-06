//
// Created by 艾代哈那提 on 2019-09-25.
//

#ifndef LOAD_DYLIB_TEST_IMGSEGMENTATION_HPP
#define LOAD_DYLIB_TEST_IMGSEGMENTATION_HPP

#endif //LOAD_DYLIB_TEST_IMGSEGMENTATION_HPP

//#include <opencv2/opencv.hpp>

extern "C" {
typedef struct ImageBase {
    int w;
    int h;
    int c;
    unsigned char *data;
} ImageMeta;

typedef struct Rect_C
{
    int left;
    int top;
    int right;
    int bottom;
} Rect_C;

typedef struct IO_RECT{
    int num;
    Rect_C * rect;
};

void SegmentImage(ImageMeta *data, ImageMeta *level_mask);

IO_RECT* SegmentImageAndgetRect(ImageMeta *data);

void freeRectPtr(IO_RECT * rect_in);

};


