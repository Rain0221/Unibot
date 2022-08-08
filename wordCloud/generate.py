# coding:utf-8

from os import path

import jieba

from wordCloud import chnSegment, plotWordcloud


def ciyun(qunnum):
    jieba.load_userdict(path.join(path.dirname(__file__), 'userdict//userdict.txt'))  # 导入用户自定义词典
    # 读取文件
    d = path.dirname(__file__)
    #  text = open(path.join(d, 'doc//十九大报告全文.txt')).read()
    text = open(path.join(d, f'{qunnum}.txt'), encoding='utf-8').read()
    #  text="付求爱很帅并来到付求爱了网易研行大厦很帅 很帅 很帅"
    # 若是中文文本，则先进行分词操作
    text=chnSegment.word_segment(text)
    # 生成词云
    plotWordcloud.generate_wordcloud(text, qunnum)

