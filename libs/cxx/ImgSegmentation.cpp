//
// Created by 艾代哈那提 on 2019-09-25.
//
#include <opencv2/opencv.hpp>
#include "ImgSegmentation.hpp"
#include<stdio.h>
#include<stdlib.h>
#define u_char unsigned char

using namespace std;
using namespace cv;

template<typename T>
vector<int> argsort(const vector<T>& a)
{
    int Len = a.size();
    vector<int> idx(Len, 0);
    for(int i = 0; i < Len; i++){
        idx[i] = i;
    }
    std::sort(idx.begin(), idx.end(), [&a](int i1, int i2){return a[i1] > a[i2];});
    return idx;
}

template<typename T>
int argmin(const vector<T>& a)
{
    int Len = a.size();
    T first = a[0];
    int idx = 0;
    for(int i=0;i<Len;i++)
    {
        if(a[i]<first)
        {
            first = a[i];
            idx = i;
        }
    }
    return idx;
}

template<typename T>
int argmax(const vector<T>& a)
{
    int Len = a.size();
    T first = a[0];
    int idx = 0;
    for(int i=0;i<Len;i++)
    {
        if(a[i]>first)
        {
            first = a[i];
            idx = i;
        }
    }
    return idx;
}


Rect_C nextRect(Rect_C rect, Point point, vector<Point> contour)
{
    int left = rect.left;
    int top = rect.top;
    int right = rect.right;
    int bottom = rect.bottom;

    Point center_point1;
    vector<Rect> candidate_rects;
    vector<int> candidate_areas;
    Rect rect_c;
    center_point1 = Point((right + left)/2,(bottom+point.y)/2);
    if(pointPolygonTest(contour, center_point1, false)==1)
    {
        rect_c = Rect(Point(left, point.y),Point(right,bottom));//ok
        candidate_rects.push_back(rect_c);
        candidate_areas.push_back(rect_c.area());
    }
    center_point1 = Point((right + point.x)/2,(bottom+top)/2);
    if(pointPolygonTest(contour, center_point1, false)==1)
    {
        rect_c = Rect(Point(point.x, top),Point(right,bottom));//ok
        candidate_rects.push_back(rect_c);
        candidate_areas.push_back(rect_c.area());
    }
    center_point1 = Point((right + left)/2,(point.y+top)/2);
    if(pointPolygonTest(contour, center_point1, false)==1)
    {
        rect_c = Rect(Point(left, top),Point(right,point.y));//ok
        candidate_rects.push_back(rect_c);
        candidate_areas.push_back(rect_c.area());
    }
    center_point1 = Point((point.x + left)/2,(bottom+top)/2);
    if(pointPolygonTest(contour, center_point1, false)==1)
    {
        rect_c = Rect(Point(left, top),Point(point.x,bottom));//ok
        candidate_rects.push_back(rect_c);
        candidate_areas.push_back(rect_c.area());
    }

    int dist_idx = argmax(candidate_areas);

    rect = Rect_C{
            candidate_rects[dist_idx].x,
            candidate_rects[dist_idx].y,
            candidate_rects[dist_idx].x+candidate_rects[dist_idx].width,
            candidate_rects[dist_idx].y+candidate_rects[dist_idx].height
    };
    return rect;
};

Rect_C insidePoint(Rect_C rect, vector<int> x_sets, vector<int> y_sets, vector<Point> contour, int width, int height) {
    int left = rect.left;
    int top = rect.top;
    int right = rect.right;
    int bottom = rect.bottom;

    vector<int> inside_x_sets;
    vector<int> inside_y_sets;
    vector<float> weight;

    for(int idx = 0; idx < x_sets.size(); idx++) {
        if (left < x_sets[idx] && x_sets[idx] < right && top < y_sets[idx] && y_sets[idx] < bottom) {
            inside_x_sets.push_back(x_sets[idx]);
            inside_y_sets.push_back(y_sets[idx]);
            float w = (float(x_sets[idx]) / float(width) - float(left) / float(width)) *
                      (float(y_sets[idx]) /float(height) -float(top) / float(height)) *
                      (float(right) / float(width) - float(x_sets[idx]) / float(width)) *
                      (float(bottom) / float(height) - float(y_sets[idx]) / float(height));
            weight.push_back(w);
        }
    }
    vector<int> weight_index = argsort(weight);
    if (inside_x_sets.size() != 0)
    {
        Point point(inside_x_sets[weight_index[0]],inside_y_sets[weight_index[0]]);
        rect = nextRect(rect, point, contour);
        rect = insidePoint(rect, inside_x_sets, inside_y_sets, contour, width, height);
        return rect;
    }
    else{
        return rect;
    }
}

Rect_C getInnerRect(Rect rect_p, vector<Point> points, int width, int height) {

    Rect_C rect_in = {rect_p.x, rect_p.y,rect_p.x+rect_p.width, rect_p.y+rect_p.height};
    vector<int> x_sets;
    vector<int> y_sets;
    for(int i=0; i<points.size();i++)
    {
        x_sets.push_back(points[i].x);
        y_sets.push_back(points[i].y);
    }
    Rect_C rect_out = insidePoint(rect_in,x_sets,y_sets, points, width,height);
    return rect_out;
}

vector<Rect_C> getRectByImgContour(Mat mat, Size serchRectSize = Size(5, 5)) {
    int h = mat.rows;
    int w = mat.cols;

    int rect_mat_h = h - serchRectSize.height;
    int rect_mat_w = w - serchRectSize.width;
    Mat rect_mask(rect_mat_h, rect_mat_w, CV_8UC1, Scalar(0));
#pragma omp parallel for
    for (short y = 0; y < rect_mat_h; y++) {
        unsigned char *ptr_mask = rect_mask.ptr<unsigned char>(y);
        for (short x = 0; x < rect_mat_w; x++) {
            Rect rect = Rect(x, y, serchRectSize.width, serchRectSize.height);
            Mat roi = mat(rect);
            Mat tmp_m, tmp_sd;
            cv::meanStdDev(roi, tmp_m, tmp_sd);
            if (tmp_sd.at<double>(0, 0) == 0) {
                ptr_mask[x] = 255;
            }
        }
    }
    vector<vector<Point>> contours;
    vector<Vec4i> hierarchy;
    findContours(rect_mask, contours, hierarchy, RETR_EXTERNAL, CHAIN_APPROX_NONE);
    vector<Rect_C> rects(contours.size(),Rect_C{0,0,0,0});
    float scale = 320.0/315.0;
#pragma omp parallel for
    for(int i=0; i<contours.size();i++)
    {


        Rect rect_p = boundingRect(contours[i]);
        if (rect_p.area()<5000){
            continue;
        }
        Rect_C rect = getInnerRect(rect_p,contours[i],rect_mat_w,rect_mat_h);
        if((rect.bottom-rect.top)*(rect.right-rect.left)>=1000){
            rects[i].left=int(float(rect.left)*scale);
            rects[i].top=int(float(rect.top)*scale);
            rects[i].right=int(float(rect.right)*scale);
            rects[i].bottom=int(float(rect.bottom)*scale);
        }
    }
    vector<Rect_C>::iterator iter = rects.begin();
    for(;iter!=rects.end();)
    {
        if(iter->top==iter->bottom || iter->right==iter->left) {
            iter=rects.erase(iter++);
        }
        else{
            iter++;
        }
    }
    rects.shrink_to_fit();
    return rects;
}


void SegmentImage(ImageMeta *data, ImageMeta *level_mask) {

    Mat img = Mat::zeros(Size(data->w,data->h),CV_8UC3);
    Mat img_cp;
    img.data=data->data;
    cv::resize(img, img_cp,Size(320,320));
    int spatialRad = 15;        //空间窗口大小
    int colorRad = 30;          //色彩窗口大小
    int maxPyrLevel = 0;        //金字塔层数
    boxFilter(img_cp,img_cp, -1,Size(3,3));
    pyrMeanShiftFiltering( img_cp, img_cp, spatialRad, colorRad, maxPyrLevel); //色彩聚类平滑滤波
    Mat mask( img_cp.rows+2, img_cp.cols+2, CV_8UC1, Scalar::all(0) );  //掩模
    for( int y = 0; y < img_cp.rows; y++ )
    {
        for( int x = 0; x < img_cp.cols; x++ )
        {
            if( mask.data[(y+1) * img_cp.cols + (x+1)] == 0 )  //非0处即为1，表示已经经过填充，不再处理
            {
                Vec3b rgb = img_cp.at<Vec3b>(y,x);
                Scalar newVal(rgb[0], rgb[1], rgb[2]);
                floodFill( img_cp, mask, Point(x,y), newVal, 0, Scalar::all(30), Scalar::all(30)); //执行漫水填充
            }
        }
    }
    Mat gray;
    cvtColor(img_cp, gray,COLOR_BGR2GRAY);
    resize(gray, gray, Size(data->w, data->h),0,0,INTER_NEAREST);
    memcpy(level_mask->data, gray.data,  data->w*data->h);
    return;
}


IO_RECT* SegmentImageAndgetRect(ImageMeta *data) {
    Mat img = Mat::zeros(Size(data->w,data->h),CV_8UC3);
    Mat img_cp;
    img.data=data->data;
    cv::resize(img, img_cp,Size(320,320));


    int spatialRad = 15;        //空间窗口大小
    int colorRad = 30;          //色彩窗口大小
    int maxPyrLevel = 0;        //金字塔层数
//    medianBlur(img_cp, img_cp, 5);
    pyrMeanShiftFiltering( img_cp, img_cp, spatialRad, colorRad, maxPyrLevel); //色彩聚类平滑滤波

    Mat color_mat;
    cvtColor(img_cp, color_mat, COLOR_BGR2HSV_FULL);
    Mat mask( img_cp.rows+2, img_cp.cols+2, CV_8UC1, Scalar::all(0) );  //掩模
    for( int y = 0; y < img_cp.rows; y++ )
    {
        for( int x = 0; x < img_cp.cols; x++ )
        {
            if( mask.data[(y+1) * (img_cp.cols+2) + (x+1)] == 0 )  //非0处即为1，表示已经经过填充，不再处理
            {
                Vec3b rgb = img_cp.at<Vec3b>(y,x);
                Scalar newVal(rgb[0], rgb[1], rgb[2]);
                floodFill(color_mat, mask, Point(x,y), newVal, 0, Scalar::all(30), Scalar::all(30)); //执行漫水填充
            }
        }
    }
    Mat gray;
    cvtColor(color_mat, gray,COLOR_BGR2GRAY);
    vector<Rect_C> rects= getRectByImgContour(gray);

    IO_RECT* rects_out = (IO_RECT*)malloc(sizeof(IO_RECT));
    if(int(rects.size())==0){
        rects_out->num = int(rects.size());
        rects_out->rect = NULL;
        return rects_out;
    }

    rects_out->num = int(rects.size());
    rects_out->rect = (Rect_C *)calloc(rects.size(),4*4);
    float wScale = float(data->w) / 320.0;
    float hScale = float(data->h) / 320.0;
#pragma omp parallel for
    for(int i=0;i<rects.size();i++)
    {
        rects_out->rect[i].left=int(float(rects[i].left)*wScale);
        rects_out->rect[i].top=int(float(rects[i].top)*hScale);
        rects_out->rect[i].right=int(float(rects[i].right)*wScale);
        rects_out->rect[i].bottom=int(float(rects[i].bottom)*hScale);
    }

    return rects_out;
}

void freeRectPtr(IO_RECT * rect_in)
{
    if( rect_in != NULL){
        if(rect_in->num > 0){
            free(rect_in->rect);
        }
        free(rect_in);
    }
}


