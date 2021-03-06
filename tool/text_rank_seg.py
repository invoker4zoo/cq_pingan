# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: text_rank_seg.py
@ time: $18-8-14 上午11:48
"""
import numpy as np
from tool.logger import logger
from tool.punct import punct
import thulac
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# GOLBAL PARAMS
THUNLP_MODEL_PATH = "/home/showlove/cc/code/THULAC-Python/models"
THUNLP_USER_DIC_PATH = "/home/showlove/PycharmProjects/data_test/nlp/user_dic.txt"
STOP_WORD_DIC_PATH = "/home/showlove/PycharmProjects/data_test/nlp/stop_word_dic.txt"


class TextSummary4Seg(object):
    """

    """
    def __init__(self, doc, window_size, alpha, step, nlp_model, doc_seg=False, ):
        """

        :param doc:
        :param window_size:
        :param alpha:
        :param step:
        :param doc_seg: 传入文档是否为分词后的文档
        """
        self.doc = doc
        self.window_size = window_size
        self.alpha = alpha
        self.step = step
        self.net_edge = {}
        self.thunlp_model = nlp_model
        # 分词/清洗
        if not doc_seg:
            self.origin_doc_seg = self.cut_doc()
            self.doc_seg_clear = self._clear_seg_list(self.origin_doc_seg)
        else:
            self.origin_doc_seg = self.doc
            self.doc_seg_clear = self._clear_seg_list(self.doc)
        self.doc_seg_list = [seg_info[0] for seg_info in self.doc_seg_clear]
        self.origin_doc_seg_list = [seg_info[0] for seg_info in self.origin_doc_seg]


        # 计算重要度
        self.cal_text_rank()

    def cut_doc(self):
        """
        将文档进行分词处理
        :return:
        """
        logger.info(u'文档文本未分词，使用thunlp进行分词')
        # self.thunlp_model = thulac.thulac(seg_only=False, model_path=THUNLP_MODEL_PATH, \
        #                          user_dict=THUNLP_USER_DIC_PATH)
        doc_seg = self.thunlp_model.cut(self.doc)
        # 保存原始分词结果，进行关键相邻词的短语组合
        # self.origin_doc_seg = doc_seg
        # doc_seg_clear = self._clear_seg_list(doc_seg)
        return doc_seg

    def _clear_seg_list(self, doc_seg):
        """
        清洗分词结果，主要步骤为去除词性重要度不高的词，去除停用词，去除标点符号
        :param doc_seg: 初始的分词结果
        :return:
        """
        doc_seg_clear = self._filter_tag(doc_seg)
        doc_seg_clear = self._remove_stop_word(doc_seg_clear)
        doc_seg_clear = self._remove_punct(doc_seg_clear)
        return doc_seg_clear

    def _filter_tag(self, seg_list, tag_filter=['a','d','v','n', 'ns', 'ni', 'vm', 'vd', 'uw'], reverse=False):
        """

        :param seg_list:
        :param tag_filter: 需要过滤的词性
        n/名词 np/人名 ns/地名 ni/机构名 nz/其它专名
        m/数词 q/量词 mq/数量词 t/时间词 f/方位词 s/处所词
        v/动词 a/形容词 d/副词 h/前接成分 k/后接成分 i/习语
        j/简称 r/代词 c/连词 p/介词 u/助词 y/语气助词
        e/叹词 o/拟声词 g/语素 w/标点 x/其它 vm/能愿动词 vd/趋向动词
        uw/用户字典
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

    def count_relation(self):
        """
        通过滑动窗口，统计词间联系数量
        :return:
        """
        word_count_dic = {}
        doc_length = len(self.doc_seg_list)
        if doc_length > self.window_size:
            for index in range(0, doc_length):
                if index == doc_length-1:
                    word = self.doc_seg_list[index]
                    word_count_dic[word] = list()
                    continue
                word = self.doc_seg_list[index]
                if word not in word_count_dic.keys():
                    word_count_dic[word] = list()
                    if index + self.window_size< doc_length-1:
                        for seg in self.doc_seg_list[index + 1: index + self.window_size]:
                            word_count_dic[word].append(seg)
                    else:
                        for seg in self.doc_seg_list[index + 1:]:
                            word_count_dic[word].append(seg)
                else:
                    if index + self.window_size < doc_length - 1:
                        for seg in self.doc_seg_list[index+1: index + self.window_size]:
                            word_count_dic[word].append(seg)
                    else:
                        for seg in self.doc_seg_list[index + 1:]:
                            word_count_dic[word].append(seg)
        else:
            logger.warning('文档长度小于滑动窗口长度')
            pass
        return word_count_dic

    def build_graph(self):
        """

        :return:
        """
        self.word_length = len(set(self.doc_seg_list))
        matrix = np.zeros([self.word_length, self.word_length])
        word_count_dic = self.count_relation()
        word_index_dic = {}
        index_word_dic = {}
        for index, word in enumerate(set(self.doc_seg_list)):
            word_index_dic[word] = index
            index_word_dic[index] = word
        for word in word_index_dic.keys():
            for seg in word_count_dic[word]:
                matrix[word_index_dic[word]][word_index_dic[seg]] += 1
                matrix[word_index_dic[seg]][word_index_dic[word]] += 1
        # 归一化
        for j in range(matrix.shape[1]):
            sum = 0
            for i in range(matrix.shape[0]):
                sum += matrix[i][j]
            for i in range(matrix.shape[0]):
                matrix[i][j] /= sum
        # 记录词表
        self.word_index_dic = word_index_dic
        self.index_word_dic = index_word_dic
        return matrix

    def cal_text_rank(self):
        """
        计算word的pagerank重要度矩阵
        :return:
        """
        self.matrix = self.build_graph()
        imp_matrix = np.ones([self.word_length, 1])
        for _ in range(0, self.step):
            imp_matrix_hat = (1 - self.alpha) + self.alpha * np.dot(self.matrix, imp_matrix)
            # 判断终止条件
            ###########
            imp_matrix = imp_matrix_hat
        self.imp_matrix = imp_matrix

    def print_result(self):
        """
        输出重要性排序结果
        :return:
        """
        word_imp = {}
        for index in range(0, len(self.imp_matrix)):
            word_imp[self.index_word_dic[index]] = self.imp_matrix[index][0]
        result = sorted(word_imp.items(), key=lambda x:x[1], reverse=True)
        for item in result:
            print item[0] + ':' + str(item[1])

    def top_n_seg(self, top_n=5):
        """
        返回重要度最高的n个词
        :param top_n:
        :return:
        """
        word_imp = {}
        for index in range(0, len(self.imp_matrix)):
            word_imp[self.index_word_dic[index]] = self.imp_matrix[index][0]
        result = sorted(word_imp.items(), key=lambda x:x[1], reverse=True)
        return result[:top_n]

    def seg_merge(self, top_n=20):
        """
        排序靠前的seg，如果在文档中处于相邻位置则进行融合
        :return:
        """
        _top_seg = self.top_n_seg(top_n=top_n)
        top_seg = [seg[0] for seg in _top_seg]
        top_merge_seg = list()
        seg_index = list()
        doc_length = len(self.origin_doc_seg_list)
        for seg in top_seg:
            seg_index += [index for index, _ in enumerate(self.origin_doc_seg_list) if _==seg]
        seg_index = sorted(seg_index, key=lambda x:x, reverse=False)
        # merge part
        cache_list = list()
        for n in seg_index:
            if n not in cache_list:
                merge_list = list()
                merge_list.append(n)
                for addition in range(1, top_n):
                    if n + addition in seg_index:
                       merge_list.append(n + addition)
                    else:
                        break
                if len(merge_list) > 1:
                    top_merge_seg.append(merge_list)
                    cache_list += merge_list
            else:
                continue
        # get merge string
        result_list = list()
        for _merge_list in top_merge_seg:
            result_string = ''
            for index in _merge_list:
                result_string += self.origin_doc_seg_list[index]
            result_list.append(result_string)
        return result_list


if __name__ == '__main__':
    doc = u'程序员(英文Programmer)是从事程序开发、维护的专业人员。一般将程序员分为程序设计人员和程序编码人员，但两者的界限并不非常清楚，特别是在中国。软件从业人员分为初级程序员、高级程序员、系统分析员和项目经理四大类。'
    doc = """
        网易体育2月11日讯：^M
    2007/2008赛季CBA联赛总决赛首回合比赛^M
    将于北京时间2月13日晚7点半正式打响^M
    ，首场较量华南虎广东宏远将坐镇主场迎接东北虎辽宁盼盼的挑战，比赛打到这个份上，总
    冠军奖杯近在咫尺，谁都不想遗憾地错过，本轮比赛，两只老虎势必会有一场殊死之战。^M
    相对于篮球场上其它位置，大前锋在队上担任的任务几乎都是以苦工为主，要抢篮板、防守
    、卡位都少不了他，但是要投篮、得分，他却经常是最后一个，从一定程度上说，大前锋是
    篮球场上最不起眼的。但是就是这个位置，却往往在比赛中扮演着至关重要的角色。下面就
    让我们来比较以下两队在这个位置上的人员配置。^M
    广东队这个位置杜锋、朱芳雨都能独挡一面，即使在国内篮坛来说，这个人员储备都称得上
    是豪华。辽宁队的刘相韬、李晓旭与谷立业就队内来说也是这个位置上的好手。但是把他们
    放到一个同等的界面上来说，却又有很大的不同。^M
    国内名气方面：^M
    广东队无疑要远远胜于辽宁，无论是杜锋还是朱芳雨都是国字号球员，在国内篮坛都是赫赫
    有名的角色，相比较而言，辽宁队的刘相韬，谷立业尽管在辽宁上有一些名气，但是在国内
    篮坛他们还远称不上“大腕”。^M
    个人技术方面：
    """
    thunlp_model = thulac.thulac(seg_only=False, model_path=THUNLP_MODEL_PATH, user_dict=THUNLP_USER_DIC_PATH)
    model = TextSummary4Seg(doc, 6, 0.85, 700, thunlp_model)
    # model.print_result()
    # for seg in model.origin_doc_seg_list:
    #     print seg
    top_n_seg = model.top_n_seg(10)
    top_n_seg_merge = model.seg_merge(20)
    pass