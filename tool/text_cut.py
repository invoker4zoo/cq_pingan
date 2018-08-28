# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: text_cut.py
@ time: $18-8-28 下午2:31
"""
import numpy as np
from tool.logger import logger
from tool.punct import punct
import thulac

# GOLBAL PARAMS
THUNLP_MODEL_PATH = "/home/showlove/cc/code/THULAC-Python/models"
THUNLP_USER_DIC_PATH = "/home/showlove/PycharmProjects/data_test/nlp/user_dic.txt"
STOP_WORD_DIC_PATH = "/home/showlove/PycharmProjects/data_test/nlp/stop_word_dic.txt"

class TextCut(object):

    def __init__(self):
        self.thunlp_model = thulac.thulac(seg_only=False, model_path=THUNLP_MODEL_PATH, \
                                          user_dict=THUNLP_USER_DIC_PATH)

    def cut_text(self, text):
        """

        :param text:
        :return:text seg list
        """
        self.text_seg = self.thunlp_model.cut(text)
        self.text_seg_clear = self._clear_seg_list(self.text_seg)
        return [seg_thulp[0] for seg_thulp in self.text_seg_clear]

    def _clear_seg_list(self, text_seg):
        """
        清洗分词结果去除停用词，去除标点符号
        暂时不清洗词性
        :param text_seg: 初始的分词结果
        :return:
        """
        # text_seg_clear = self._filter_tag(text_seg)
        text_seg = self._remove_stop_word(text_seg)
        text_seg = self._remove_punct(text_seg)
        return text_seg

    def _filter_tag(self, seg_list, tag_filter=['a', 'd', 'v', 'n', 'ns', 'ni', 'vm', 'vd'], reverse=False):
        """

        :param seg_list:
        :param tag_filter: 需要过滤的词性
        n/名词 np/人名 ns/地名 ni/机构名 nz/其它专名
        m/数词 q/量词 mq/数量词 t/时间词 f/方位词 s/处所词
        v/动词 a/形容词 d/副词 h/前接成分 k/后接成分 i/习语
        j/简称 r/代词 c/连词 p/介词 u/助词 y/语气助词
        e/叹词 o/拟声词 g/语素 w/标点 x/其它 vm/能愿动词 vd/趋向动词
        :return:
        """
        if reverse:
            return [seg_info for seg_info in seg_list if seg_info[1] not in tag_filter]
        else:
            return [seg_info for seg_info in seg_list if seg_info[1] in tag_filter]

    def _remove_stop_word(self, seg_list, stop_word_dic_path=STOP_WORD_DIC_PATH):
        """
        去除停用词
        :param seg_list:
        :param stop_word_dic_path: 停用词典文件路径
        :return:
        """
        with open(stop_word_dic_path, 'rb') as f:
            stop_word_list = f.read().split('\n')
        return [seg_info for seg_info in seg_list if seg_info[0] not in stop_word_list]

    def _remove_punct(self, seg_list, punct=punct):
        """
        去除常用标点和符号
        :param seg_list:
        :param punct:
        :return:
        """
        return [seg_info for seg_info in seg_list if seg_info[0] not in punct]