# [emoji2pic-python](https://github.com/SkywalkerSpace/emoji2pic-python)
Apple emoji and text to picture

## 介绍 Introduction

使用Python Pillow根据unicode将文本和emoji绘制到图片上  
可自选字体，字号，行距，页边距，颜色，图片宽度和透明度等

## 开发进度 Progress
https://emojipedia.org/apple/ios-12.1/  
目前完成匹配Apple iOS 12.1 emoji 共2776个

## 依赖库 Dependencies

Pillow

## 简单入门实例 Example
```python
from emoji2pic import Emoji2Pic

instance = Emoji2Pic(text='🌷👌🌙⭕\n花好月圆', font='SourceHanSans-Light.ttc', emoji_folder='AppleEmoji')
img = instance.make_img()
img.save('example.jpg')
```

## 使用方法 Instructions

|参数|说明|格式|是否必须|
|:---:|:---:|:---:|:---:|
|text|文本内容|char|yes|
|font|字体文件路径|char|yes|
|emoji_folder|emoji图片文件夹路径|char|yes|
|width|图片宽度|int|no|
|font_size|文字大小|int|no|
|font_color|文字颜色|RGB/RGBA|no|
|color_mode|图片底色模式|char|no|
|background_color|图片底色|RGB/RGBA|no|
|line_space|行间距|int|no|
|left|左边距|int|no|
|right|右边距|int|no|
|top|上边距|int|no|
|bottom|下边距|int|no|
|half_font|半角字符字体路径|char|no|
|half_font_width|半角字符字体宽度|int|no|
|half_font_offset|半角字符纵轴偏移量|int|no|
|emoji_offset|emoji纵轴偏移量|int|no|
|progress_bar|控制台输出进度条|boolean|no|

1. make_img() 方法，返回 PIL.Image.Image
2. 图片包在 releases
3. get_unicode_from_file_name.py 从图片文件名获取对应的 Unicode，写入 emoji_directory.py

#### 注意 Note

1. 根据像素绘制文本，只适合等宽字体。很多字体的半角字符都不等宽，比如微软雅黑  
解决方法：自定义 half_font ，支持ASCII范围的半角字符，也可使用 half_font_width 调节半角字符宽度  
2. 使用半角字符字体时，会造成半角字符纵轴偏移几像素  
解决方法：使用half_font_offset，自定义半角字符纵轴偏移
3. emoji纵轴偏移几像素  
解决方法：使用emoji_offset，自定义emoji字符纵轴偏移

# 许可 License
MIT license.