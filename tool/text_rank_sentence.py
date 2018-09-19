# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: text_rank_sentence.py
@ time: $18-8-15 下午2:26
"""
import numpy as np
from logger import logger
from punct import punct
import thulac
from gensim.models import KeyedVectors
import math

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# GOLBAL PARAMS
THUNLP_MODEL_PATH = "/home/showlove/cc/code/THULAC-Python/models"
THUNLP_USER_DIC_PATH = "/home/showlove/PycharmProjects/data_test/nlp/user_dic.txt"
STOP_WORD_DIC_PATH = "/home/showlove/PycharmProjects/data_test/nlp/stop_word_dic.txt"
VECTOR_MODEL = "/home/showlove/cc/nlp/vector/sgns.renmin.bigram-char"
sentence_delimiters = ['?', '!', ';', '？', '！', '。', '；', '……', '…', '：', ':']
VECTOR_SIZE = 300

class TextSummary4Sentence(object):

    def __init__(self, doc, step, alpha, nlp_model):
        self.doc = doc
        self.step = step
        self.alpha = alpha
        # 内存加载不足，暂时使用简单的匹配相似度计算
        # self.vector_model = KeyedVectors.load_word2vec_format(VECTOR_MODEL)
        # seg_only 是否做词性分析
        # self.thunlp_model = thulac.thulac(seg_only=False, model_path=THUNLP_MODEL_PATH, \
        #                          user_dict=THUNLP_USER_DIC_PATH)
        # model 由外部传入，整个流程只加载一次
        self.thunlp_model = nlp_model
        self.cut_sentence()
        self.cut_sentence_seg()
        self.cal_importance()

    def cut_sentence(self):
        """
        文档的分句
        :return:
        """
        self.doc_sentence = []
        sentnce = ''
        for char in self.doc:
            if char not in sentence_delimiters:
                sentnce += char
            else:
                self.doc_sentence.append(sentnce)
                sentnce = ''

    def cut_sentence_seg(self):
        """
        句子的分词，用于计算句子的向量
        :return:
        """
        self.doc_sentence_seg = []
        for sentence in self.doc_sentence:
            sentence_seg = self.thunlp_model.cut(sentence)
            sentence_seg_clear = self._clear_seg_list(sentence_seg)
            self.doc_sentence_seg.append(sentence_seg_clear)

    def cos_distance(self,vector1, vector2):
        """

        :param vector1:
        :param vector2:
        :return:
        """
        tx = np.array(vector1)
        ty = np.array(vector2)
        cos1 = np.sum(tx * ty)
        cos21 = np.sqrt(sum(tx ** 2))
        cos22 = np.sqrt(sum(ty ** 2))
        cosine_value = cos1 / float(cos21 * cos22)
        return cosine_value

    def two_sentences_similarity(self, sents_1, sents_2):
        '''
        计算两个句子的相似性
        :param sents_1:
        :param sents_2:
        :return:
        '''
        counter = 0
        for sent in sents_1:
            if sent in sents_2:
                counter += 1
        return counter / (math.log(len(sents_1) + len(sents_2)))

    def cal_sentence_similarity(self, sentence1, sentence2):
        """

        :param sentence1:
        :param sentence2:
        :return:
        """
        if len(sentence1) == 0 or len(sentence2) == 0:
            return 0.0
        for index,seg in enumerate(sentence1):
            if index == 0:
                vector1 = self.vector_model[seg]
            else:
                vector1 += self.vector_model[seg]

        for index, seg in enumerate(sentence2):
            if index == 0:
                vector2 = self.vector_model[seg]
            else:
                vector2 += self.vector_model[seg]
        similarity = self.cos_distance(vector1/len(sentence1), vector2/len(sentence2))
        return similarity

    def build_graph(self):
        """
        建立句子链表的关系图
        :return:
        """
        sentence_len = len(self.doc_sentence_seg)
        self.sentence_len = sentence_len
        matrix = np.zeros([sentence_len, sentence_len])
        for i in range(0, sentence_len):
            for j in range(i, sentence_len):
                if i==j:
                    matrix[i][j] = 1
                    continue
                # matrix[i][j] = self.cal_sentence_similarity(self.doc_sentence_seg[i],\
                #                                                            self.doc_sentence_seg[j])
                matrix[i][j] = self.two_sentences_similarity(self.doc_sentence_seg[i],\
                                                                           self.doc_sentence_seg[j])

                matrix[j][i] = matrix[i][j]
        # 归一化
        for j in range(matrix.shape[1]):
            sum = 0
            for i in range(matrix.shape[0]):
                sum += matrix[i][j]
            for i in range(matrix.shape[0]):
                matrix[i][j] /= sum
        return matrix

    def cal_importance(self):
        """

        :return:
        """
        self.matrix = self.build_graph()
        imp_matrix = np.ones([self.sentence_len, 1])
        for _ in range(0, self.step):
            imp_matrix_hat = (1 - self.alpha) + self.alpha * np.dot(self.matrix, imp_matrix)
            # 判断终止条件
            ###########
            imp_matrix = imp_matrix_hat
        self.imp_matrix = imp_matrix

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

    def print_result(self, top_n=5):
        """

        :param top_n:
        :return:
        """
        word_imp = {}
        for index in range(0, len(self.imp_matrix)):
            word_imp[self.doc_sentence[index]] = self.imp_matrix[index][0]
        result = sorted(word_imp.items(), key=lambda x:x[1], reverse=True)
        for item in result[0:top_n]:
            print item[0] + ':' + str(item[1])

    def top_n_sentence(self, top_n=5):
        """
        返回重要度最高的n个句子
        :param top_n:
        :return:
        """
        word_imp = {}
        for index in range(0, len(self.imp_matrix)):
            word_imp[self.doc_sentence[index]] = self.imp_matrix[index][0]
        result = sorted(word_imp.items(), key=lambda x:x[1], reverse=True)
        return result[: top_n]


if __name__ == '__main__':
    # doc = u'程序员(英文Programmer)是从事程序开发、维护的专业人员。一般将程序员分为程序设计人员和程序编码人员，但两者的界限并不非常清楚，特别是在中国。软件从业人员分为初级程序员、高级程序员、系统分析员和项目经理四大类。'
    doc = u"""
        网易体育2月11日讯：2007/2008赛季CBA联赛总决赛首回合比赛将于北京时间2月13日晚7点半正式打响，首场较量华南虎广东宏远将坐镇主场迎接东北虎辽宁盼盼的挑战，比赛打到这个份上，总
    冠军奖杯近在咫尺，谁都不想遗憾地错过，本轮比赛，两只老虎势必会有一场殊死之战。
    相对于篮球场上其它位置，大前锋在队上担任的任务几乎都是以苦工为主，要抢篮板、防守
    、卡位都少不了他，但是要投篮、得分，他却经常是最后一个，从一定程度上说，大前锋是
    篮球场上最不起眼的。但是就是这个位置，却往往在比赛中扮演着至关重要的角色。下面就
    让我们来比较以下两队在这个位置上的人员配置。
    广东队这个位置杜锋、朱芳雨都能独挡一面，即使在国内篮坛来说，这个人员储备都称得上
    是豪华。辽宁队的刘相韬、李晓旭与谷立业就队内来说也是这个位置上的好手。但是把他们
    放到一个同等的界面上来说，却又有很大的不同。
    国内名气方面：
    广东队无疑要远远胜于辽宁，无论是杜锋还是朱芳雨都是国字号球员，在国内篮坛都是赫赫
    有名的角色，相比较而言，辽宁队的刘相韬，谷立业尽管在辽宁上有一些名气，但是在国内
    篮坛他们还远称不上“大腕”。
    个人技术方面：
    """
    doc = u""""财会〔2018〕24号\n卫生健康委，各省、自治区、直辖市、计划单列市财政厅（局），新疆生产建设兵团财政局，有关单位：\n　　《政府会计制度——行政事业单位会计科目和报表》（财会〔2017〕25号）自2019年1月1日起施行。为了确保新制度在医院的有效贯彻实施，我部制定了《关于医院执行<政府会计制度——行政事业单位会计科目和报表>的补充规定》和《关于医院执行<政府会计制度——行政事业单位会计科目和报表>的衔接规定》，现印发给你们，请遵照执行。\n　　执行中有何问题，请及时反馈我部。\n　　附件：1.关于医院执行《政府会计制度——行政事业单位会计科目和报表》的补充规定\n　　2.关于医院执行《政府会计制度——行政事业单位会计科目和报表》的衔接规定\n　　财 政 部\n　　2018年8月27日\n"""
    doc = u"""　　7月26日，国新办举行国务院政策例行吹风会，财政部副部长刘伟、财政部税政司司长王建凡介绍财政支持实体经济发展情况，并回答了记者提问。\n　　加大减税降费力度，降低实体经济成本\n　　“今年以来，全国财政运行情况良好，财政收入保持平稳较快增长，财政支出保持较高强度，对重点领域和关键环节的投入进一步加大，各项减税降费措施正按计划推进，支持实体经济发展取得明显成效。” 刘伟表示。\n　　根据中央经济工作会议和《政府工作报告》确定的2018年经济发展目标，今年全国一般公共预算支出预算安排20.98万亿元，增长7.6%；安排财政赤字2.38万亿元，保持上年规模。另安排不列入赤字的地方政府专项债券1.35万亿元，比上年增加5500亿元。今年1—6月，全国一般公共预算支出进度已经超过了序时进度。\n　　“在保持较高财政投入力度和支出强度的同时，积极财政政策的主要着力点体现在加大减税降费力度、降低实体经济成本上。”刘伟介绍，2013—2017年，实施营改增改革已累计减税2.1万亿元，加上采取小微企业税收优惠、清理各种收费等措施，共减轻市场主体负担3万多亿元。\n　　今年以来，持续推进增值税改革，降低制造业、交通运输、建筑、基础电信服务等行业增值税税率。据税务总局统计，截至5月底，增值税税率调整共涉及增值税一般纳税人895万户，与调整前相比，改革首月即实现净减税348亿元。\n　　“《政府工作报告》提出，全年减税降费1.1万亿元，这是近年来力度最大的一次。”王建凡介绍，财政部会同税务总局等部门迅速行动，抓紧制发操作文件。目前，深化增值税改革、降低收费、进一步支持小微企业和鼓励创业创新等减税措施已基本落地，装备制造等先进制造业、研发等现代服务业和电网企业增值税期末留抵退税工作正有序开展，个人所得税改革正在履行修法程序。\n　　减税降费政策还包括出台小微企业税收优惠政策，将享受减半征收企业所得税优惠政策的小型微利企业年应纳税所得额上限，从50万元提高到100万元；将高新技术企业和科技型中小企业亏损结转年限由5年延长至10年，减轻企业创新税收负担；对载运货物的挂车减半征收车辆购置税，降低企业物流成本；进一步清理规范行政事业性收费和政府性基金等。\n　　“上述政策主要聚焦支持小微企业发展，鼓励创业创新，降低企业成本。这些政策重点突出，点面结合，对激发市场活力，降低企业负担，促进经济高质量发展发挥了重要作用。”王建凡说。\n　　优化财政支出结构，引导实体经济提质增效\n　　近年来，在减税降费的同时，财政不断优化支出结构，出台多项政策支持小微企业，服务实体经济。\n　　在支持创业创新发展方面，2015年以来，财政部会同工信部、科技部等部门，分两批支持了30个示范城市开展“小微企业创业创新基地城市示范”。初步统计，首批15个示范城市的小微企业在三年示范期内累计新增就业669万人，年均增长12.9%。\n　　在解决小微企业融资困难方面，实施创业担保贷款贴息，2013—2017年，中央财政累计安排创业担保贷款贴息及奖补资金约440亿元，支持数十万家（次）小微企业获得低成本贷款，惠及就业人员约1500万人次。\n　　同时，对重点领域和产业的扶持投入，主要通过市场化方式，设立政府投资基金，撬动民间资本投入经济社会发展的重点领域和薄弱环节。\n　　为支持引导实体经济提质增效，今年财政安排就业补助资金，支持稳定和促进就业；安排中小企业发展专项资金，集中支持小微企业创业创新基地城市示范；实施创业担保贷款贴息，降低政策门槛，取消小微企业不能同时享受担保和贴息的限制，将对小微企业新招用员工比例的要求由30%降为25%。\n　　支持实体经济发展，财政政策将更加积极\n　　国务院常务会议要求，保持宏观政策稳定，财政政策要更有效服务实体经济，更有力服务宏观大局，积极财政政策要更加积极。\n　　“财政部将坚持稳中求进工作总基调，坚持不搞‘大水漫灌’式强刺激，聚焦减税降费，支持中小企业发展，促进创业创新和稳定就业。”刘伟表示，在确保全年减轻税费负担1.1万亿元以上的基础上，下半年积极财政政策将更加积极，主要体现在以下几方面：\n　　一是进一步减税，2018年至2020年底，将企业研发费用加计扣除比例提高到75%的政策由科技型中小企业扩大至所有企业，初步测算全年减收650亿元。\n　　二是对已确定的先进制造业、现代服务业、电网企业增值税留抵退税返还的1130亿元，在9月底前基本完成，尽快释放政策红利。\n　　三是助力解决小微企业融资困难，加快组建国家融资担保基金。落实不低于600亿元基金首期出资，协同省级融资担保和再担保机构，支持融资担保行业发展壮大，扩大小微企业融资担保业务规模，努力实现每年支持15万家（次）小微企业和新增1400亿元贷款的政策目标。对地方拓展小微企业融资担保规模、降低小微企业融资担保费用取得明显成效的予以奖补。会同有关部门抓紧出台操作办法，将符合条件的小微企业和个体工商户贷款利息收入免征增值税单户授信额度由100万元提高到500万元。\n　　四是加强相关方面衔接，加快今年1.35万亿元地方政府专项债券发行和使用进度，在推动在建基础设施项目上早见成效。\n　　“保持一定的支出强度，保障重点领域、关键环节和民生的投入，是积极财政政策的重要内容。”刘伟表示，今年新增地方政府专项债券1.35万亿元，连同一般债券8300亿元，都是确定了重点支出方向的，要支持京津冀协同发展、长江经济带等重大战略以及精准扶贫、生态环保、棚户区改造等重点领域，优先用于在建项目平稳建设。\n　　“发行1.35万亿元的地方政府专项债券，这是在财政赤字外的一个制度安排。但需要强调的是，这些地方政府债券都是在全国人民代表大会批准的限额之内的，不是地方想怎么发就怎么发，必须严格控制在法定限额以内。”刘伟强调，在国家确定的重点支出方向上，债券资金要有效保障在建项目融资需求，不能超越财力水平盲目铺摊子，要避免新增隐性债务。\n记者  李丽辉\n"""
    thunlp_model = thulac.thulac(seg_only=False, model_path=THUNLP_MODEL_PATH, \
                                                                user_dict=THUNLP_USER_DIC_PATH)
    model = TextSummary4Sentence(doc, 700, 0.85, thunlp_model)
    model.print_result()