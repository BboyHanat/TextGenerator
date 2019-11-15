# TextGenerator

- This is a tools for ocr dataset, text detection, fonts classification dataset generate.
- 这是一个用来生成ocr数据，文字检测数据，字体识别的最方便的工具

## 实现的功能：

- 生成基于不同语料的，不同字体、字号、颜色、旋转角度的文字贴图
- 支持多进程快速生成
- 文字贴图按照指定的布局模式填充到布局块中
- 在图像中寻找平滑区域当作布局块
- 支持文字区域的图块抠取导出（导出json文件，txt文件和图片文件，可生成voc数据，coco格式coming soon!）
- 支持用户自己配置各项生成配(图像读取，生成路径，各种概率)

## 效果预览

### 生成图片示例:

![](img/pic_7f6cb78368edaf8347a8f0ce7e5a46c2df4f3ddd.jpg)

### 文字贴图示例:

![](img/fragment_6fc1b6ac180755dea3dfe711550251708b5e2ce519.jpg)

![](img/fragment_178b7da018e0d84c80b1455be4cc099bc68a07271.jpg)

![](img/fragment_ca71322eec0332fb3f6bb2a213c22f4a183c69da7.jpg)

![](img/fragment_f712bd7187d446b5fd5daf0ee0c6cb33ad26f98710.jpg)
