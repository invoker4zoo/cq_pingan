# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: html_analysis.py
@ time: $18-8-22 下午3:52
"""

import json
import math
from bs4 import BeautifulSoup
import os
from tool.logger import logger
from tool.punct import sentence_delimiters
from tool.text_cut import TextCut
import numpy as np
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class htmlTableAnalysis(object):

    def __init__(self, file_path, saving_path):
        # self.file_name = file_name
        self.file_path = file_path
        self.saving_path = saving_path
        # self.soup = BeautifulSoup(self._read_file(), 'html5lib')
        # 初始化相似度计算资源
        # self._init_nlp_source()

    def get_file_name(self, file_name):
        """
        读入文件名
        函数独立，为循环读入文件夹下所有文件
        :param file_name:
        :return:
        """
        self.file_name = file_name
        self.soup = BeautifulSoup(self._read_file(), 'html5lib')

    def _read_file(self):
        """
        读取html文件
        :return:
        """
        try:
            with open(os.path.join(self.file_path, self.file_name),'r') as f:
                string = f.read()
            return string.decode('utf-8')
        except Exception,e:
            logger.error('reading html file failed for %s'%str(e))

    def _init_nlp_source(self):
        """


        """
        self._init_nlp_model()
        self._init_key_sentence_list()

    def _init_nlp_model(self):
        """
        初始化分词模型

        """
        logger.info('初始化分词模型...')
        self.nlp_model = TextCut()

    def _init_key_sentence_list(self):
        """
        初始化相似度计算的短语列表

        """
        self.key_sentence_list = [
            u'股权投资支出责任',
            u'运营补贴支出责任',
            u'风险承担责任',
            u'配套投入支出责任',
            u'一般公共预算支出数额',
            u'政府基金预算支出数额'
        ]
        self.key_sentence_seg_list = [self.nlp_model.cut_text(key_sentence) \
                                      for key_sentence in self.key_sentence_list]

    def cal_similarity_dic(self, table_info):
        """

        :param table_info:
        :return:
        """
        self.similarity_dict = dict()
        for key_sentence in self.key_sentence_list:
            self.similarity_dict[key_sentence] = list()
        for info_dict in table_info:
            table_index = info_dict.get('tableIndex')
            for key in info_dict.get('tableInfo', [{}])[0].keys():
                for key_sentence,key_sentence_seg in zip(self.key_sentence_list, self.key_sentence_seg_list):
                    similarity = self.two_sentences_similarity(self.nlp_model.cut_text(key), key_sentence_seg)
                    if similarity > 0:
                        similarity_dict = {
                            'tableIndex': table_index,
                            'key': key,
                            'similarity': similarity
                        }
                        self.similarity_dict[key_sentence].append(similarity_dict)
                    else:
                        pass
        for key_sentence in self.key_sentence_list:
            self.similarity_dict[key_sentence] = sorted(self.similarity_dict[key_sentence], \
                                                        key=lambda info:info['similarity'], reverse=True)
        return self.similarity_dict


    def two_sentences_similarity(self, seg_list_1, seg_list_2):
        '''
        计算两个分词列表的相似性
        :param seg_list_1:
        :param seg_list_2:
        :return:
        '''
        counter = 0
        for seg in seg_list_1:
            if seg in seg_list_2:
                counter += 1
        return counter / (math.log(len(seg_list_1) + len(seg_list_2)))

    def _analysis_table_tag(self, table_tag):
        """

        :param table_tag:
        :return:
        """
        pass

    def _get_tag_string(self, tag):
        """
        读取一个tag中的所有字符串
        :param tag:
        :return:
        """
        des = ''
        if tag.string:
            return tag.string
        else:
            for str in tag.strings:
                des += str
        return des

    def _check_sentence(self, str):
        """
        判断是否为完整句子
        :param str:
        :return:
        """
        for seg in str[::-1]:
            try:
                if seg.encode('utf-8') in sentence_delimiters:
                    return True
            except:
                continue
        return False

    def _check_list_repeat(self, key_list):
        """
        判断列表中是否存在重复的子列表,如果有，提出子列表的index 和key
        :param key_list:
        :return:is_repeat bool
                repeat index list [[index1, index2, index3,...],...]
                new_key_list list
        """
        key_list = key_list.tolist()
        is_repeat = False
        key_set = set(key_list)
        key_list_length = len(key_list)
        if len(key_set) == len(key_list):
            return False, None, key_list
        new_key_list = key_list
        for seg in key_list:
            seg_index = [index for index, key in enumerate(key_list) if seg == key]
            if len(seg_index) > 1:
                cache_list = list()
                for index, _ in enumerate(seg_index[:-1]):
                    cache_list.append(seg_index[index + 1] - seg_index[index])
                cache_list.append(key_list_length - seg_index[-1])
                repeat_length = min(cache_list)
                if repeat_length < 2:
                    continue
                for shift in range(1, repeat_length):
                    cache_list = list()
                    for index in seg_index:
                        cache_list.append(key_list[index:index + shift + 1])
                    # set unhashable list
                    # if len(set(cache_list)) == 1:
                    #     continue
                    for index in range(0, len(cache_list) - 1):
                        if cache_list[index] == cache_list[index + 1]:
                            continue
                        else:
                            index -= 1
                            break
                    if index == len(cache_list) - 2:
                        if shift == repeat_length - 1:
                            is_repeat = True
                            shift_length = shift
                            continue
                        else:
                            continue
                    else:
                        if shift == 1:
                            break
                        else:
                            is_repeat = True
                            shift_length = shift - 1
                            break
                if is_repeat:
                    new_key_list = key_list[seg_index[0]:seg_index[0] + shift_length + 1]
                    cache_list = list()
                    for index in seg_index:
                        cache_list.append(range(index, index + shift_length + 1))
                    return is_repeat, cache_list, new_key_list
                else:
                    return False, None, new_key_list
            else:
                continue
        return False, None, new_key_list

    def _search_table_describe(self, table_tag):
        """
        搜索表格标签的描述；
        搜索策略: 搜索text_align属性，有text_align属性搜索到非text_align为止；
                如果为段落，进行分句，取最后一个句子;需要判断tag是否有效
        :param table_tag:
        :return: table describe string
        """
        try:
            des = ''
            for element in table_tag.previous_siblings:
                is_center = False
                if element.name:
                    # element.name
                    if element.name == 'table':
                        des = u'连续表'
                        break
                    if element.get('align', '') == 'center':
                        is_center = True
                        try:
                            int(self._get_tag_string(element).strip())
                            is_center = False
                            continue
                        except:
                            # if is_center:
                            #     continue
                            # else:
                            #     break
                            des = self._get_tag_string(element) + des
                            continue
                    else:
                        if is_center:
                            break

                    des = self._get_tag_string(element) + des
                    if self._check_sentence(des):
                        break
                else:
                    continue
            if self._check_sentence(des):
                if des[-1].encode('utf-8') in sentence_delimiters:
                    des = des[:-1]
                for index, seg in enumerate(des[::-1]):
                    if seg.encode('utf-8') in sentence_delimiters:
                        return des.split(seg)[-1]
                return des
            else:
                return des
        except Exception,e:
            logger.error('search table describe failed for %s'%str(e))

    def _search_table_base_info(self,table_tag):
        """
        计算表格基础信息
        :param table_tag:
        :return:
        """
        table_col = 0
        table_row = len(table_tag.find_all('tr'))
        tr_head = table_tag.find('tr')
        num_head = 0
        year_head = 0
        row_head = 1
        empty_head = 0
        type_list = list()
        for td in tr_head.find_all('td'):
            td_str = self._get_tag_string(td)
            td_str.strip()
            td_str.replace(',', '')
            try:
                float(str)
                num_head += 1
            except:
                try:
                    float(str[:-1])
                    num_head += 1
                except:
                    pass
            if td_str == '':
                empty_head += 1
            if td_str.endswith(u'年'):
                year_head += 1
            if td.attrs.get('rowspan'):
                row_head = max(row_head, int(td.attrs.get('rowspan')))
            if td.attrs.get('colspan'):
                table_col += int(td.attrs.get('colspan'))
            else:
                table_col += 1
            #
            if td.attrs.get('rowspan'):
                type_list.append(1)
            elif td.attrs.get('colspan'):
                type_list.append(2)
            else:
                type_list.append(0)
        # 计算左上表头大小，同一类型才能被默认为一个表头
        if type_list[0] == 0:
            col_head = 1
        else:
            for index in range(1, len(type_list)):
                if len(set(type_list[0:index + 1])) == 1:
                    continue
                else:
                    col_head = index
                    break
        # 判断横向表和竖向表
        # is_horizontal = True if float(year_head)/table_col > 0.6 or float(year_head)/table_col > 0.6 else False
        # 有效性检查
        invaild = True if float(empty_head) / table_col > 0.8 or table_col < 1 or table_row < 2 else False
        return table_col, table_row, row_head, col_head, invaild

    def save_info_list(self, info_list):
        """

        :param info:row_head - 1][col_head:
        :return:
        """
        try:
            string = json.dumps(info_list, ensure_ascii=False, indent=1)
            file_name_origin = self.file_name.split('.')[0]
            with open(os.path.join(self.saving_path, file_name_origin + '.json'),'w') as f:
                f.write(string)
        except Exception,e:
            logger.error('dump info list failed for %s'%str(e))

    def save_new_soup(self):
        """

        :return:
        """
        try:
            file_name = self.file_name
            origin_name = file_name.split('.')[0]
            new_name = origin_name + '_trans'
            new_file_name = new_name + '.' + file_name.split('.')[-1]
            with open(os.path.join(self.saving_path, new_file_name), 'w') as f:
                f.write(str(self.soup.contents[0]))
        except Exception, e:
            logger.error('save new soup failed for %s'%str(e))

    def generate_table_matrix(self, table_tag, table_col, table_row):
        """

        :param table_tag:
        :param table_col:
        :param table_row:
        :return:
        """
        try:
            str_matrix = [[None for _ in range(table_col)] for _ in range(table_row)]
            for row_index, tr in enumerate(table_tag.find_all('tr')):
                for col_index, td in enumerate(tr.find_all('td')):
                    wide = 0
                    height = 0
                    des = self._get_tag_string(td)
                    des = des.strip()
                    des = des.replace('\n', '')
                    des = des.replace(' ', '')
                    for i in range(0, table_col - col_index):
                        if str_matrix[row_index][col_index + i] == None:
                            str_matrix[row_index][col_index + i] = des
                            # 横向重定位
                            col_index = col_index + i
                            break
                        else:
                            continue
                    if td.attrs.get('rowspan'):
                        height = int(td.attrs.get('rowspan'))
                    if td.attrs.get('colspan'):
                        wide = int(td.attrs.get('colspan'))
                    if wide and height:
                        for i in range(0, height):
                            for j in range(0, wide):
                                str_matrix[row_index + i][col_index + j] = des
                        continue
                    elif wide or height:
                        if wide:
                            for i in range(1, wide):
                                str_matrix[row_index][col_index + i] = des
                        if height:
                            for i in range(1, height):
                                str_matrix[row_index + i][col_index] = des
                    else:
                        pass
            # self.matrix = str_matrix
            return str_matrix
        except Exception, e:
            logger.error('get table matrix failed')
            return None

    def generate_table_json(self, matrix, row_head, _col_head):
        """
        表格数据json化
        :param table_tag:
        :param matrix:
        :param row_head:
        :return:
        """
        try:
            table_info= []
            matrix = np.array(matrix)
            table_col = len(matrix[0, :])
            table_row = len(matrix[:, 0])
            # 在函数内部对_col_head进行了操作，需要用函数内的变量代替_col_head
            # global _col_head
            row_list = matrix[row_head:, _col_head - 1]
            col_list = matrix[row_head - 1, _col_head:]
            head_str = matrix[row_head - 1, _col_head - 1]
            year_head = 0
            num_head = 0
            year_head_row = 0
            num_head_row = 0
            for seg in col_list:
                if seg.endswith(u'年'):
                    year_head += 1
                try:
                    int(seg.strip())
                    num_head += 1
                except:
                    pass
            for seg in row_list:
                if seg.endswith(u'年'):
                    year_head_row += 1
                try:
                    float(seg.strip())
                    num_head_row += 1
                except:
                    pass
            # clean head_str
            head_str = head_str.strip().replace('\n', '').replace(' ', '')
            if head_str == u'序号':
                head_str_index = True
            else:
                head_str_index = False


            is_horizontal = True if float(year_head) / table_col > 0.6 or float(num_head) / table_col > 0.6 else False
            # 去除序号列
            is_row_num = True if float(year_head_row) / table_col < 0.4 or float(num_head_row) / table_col > 0.6 else False
            if head_str_index and is_row_num:
                _col_head += 1
                row_list = matrix[row_head:, _col_head - 1]
                col_list = matrix[row_head - 1, _col_head:]
            if is_horizontal:
                key_list = row_list
                inner_key_list = col_list
            else:
                key_list = col_list
                inner_key_list = row_list
            is_repeat, repeat_index, new_key_list = self._check_list_repeat(key_list)
            if not is_repeat:
                info_dic = dict()
                for i, key in enumerate(key_list):
                    key = key.strip().replace('\n', '').replace(' ', '')
                    if key not in info_dic.keys():
                        info_dic[key] = dict()
                    else:
                        continue
                    for j, inner_key in enumerate(inner_key_list):
                        inner_key = inner_key.strip().replace('\n', '').replace(' ', '')
                        if inner_key not in info_dic[key].keys():
                            if is_horizontal:
                                info_dic[key][inner_key] = matrix[i + row_head,j + _col_head]
                            else:
                                info_dic[key][inner_key] = matrix[j + row_head, i + _col_head]
                table_info.append(info_dic)
                # return table_json
            else:
                # 是否一开始就出现重复key
                # 如果重复key是以第一个key开始，则重新提取inner_key
                if repeat_index[0][0]!=0:
                    begin_repeat = False
                else:
                    begin_repeat = True
                for index_list in repeat_index:
                    if begin_repeat:
                        if is_horizontal:
                            inner_key_list = matrix[row_head + index_list[0] - 1, _col_head:]
                        else:
                            inner_key_list = matrix[row_head:, _col_head + index_list[0] - 1]
                    info_dic = dict()
                    for i, key in zip(index_list, new_key_list):
                        key = key.strip().replace('\n', '').replace(' ', '')
                        if key not in info_dic.keys():
                            info_dic[key] = dict()

                        for j, inner_key in enumerate(inner_key_list):
                            inner_key = inner_key.strip().replace('\n', '').replace(' ', '')
                            if inner_key not in info_dic[key].keys():
                                if is_horizontal:
                                    info_dic[key][inner_key] = matrix[i + row_head][j + _col_head]
                                else:
                                    info_dic[key][inner_key] = matrix[j + row_head][i + _col_head]
                    table_info.append(info_dic)
            return table_info
        except Exception, e:
            logger.error('get table info failed for %s'%str(e))
            return []

    def generate_table_info(self):
        """

        :return: table info list
        """
        self.table_info = list()
        try:
            for index, table in enumerate(self.soup.find_all('table')):
                info = dict()
                info['describe'] = self._search_table_describe(table)
                table_col, table_row, row_head, col_head, invaild = self._search_table_base_info(table)
                if invaild:
                    logger.info('find a invaild table tag, continue...')
                    continue
                else:
                    info['matrix'] = self.generate_table_matrix(table, table_col, table_row)
                    info['tableIndex'] = index
                    info['tableInfo'] = self.generate_table_json(info['matrix'], row_head, col_head)
                self.table_info.append(info)
        except Exception,e:
            logger.error('get table info failed for %s'%str(e))

        return self.table_info

    def generate_result_dict(self, table_info, similarity_dict):
        """
        将填报结果的内容抽取出来
        :param table_info:table information list
        :param similarity_dict: key sentence similarity dict
        :return:result dict
        """
        try:
            result_dict = dict()
            for key, similarity_info in similarity_dict.items():
                if key not in result_dict.keys():
                    result_dict[key] = dict()
                if len(similarity_info) > 0:
                    # 暂时只取第一个排序最高的info，不考虑相同的情况
                    table_index = similarity_info[0].get('tableIndex')
                    search_key = similarity_info[0].get('key')
                else:
                    continue
                for seg_info in table_info:
                    if seg_info['tableIndex'] != table_index:
                        continue
                    else:
                        for inner_key in seg_info['tableInfo'][0].keys():
                            if inner_key != search_key:
                                continue
                            else:
                                result_dict[key] = sorted(seg_info['tableInfo'][0][inner_key].iteritems(), \
                                                          key=lambda key:key[0], reverse=False)
            return result_dict

        except Exception, e:
            logger.error('generate result dict failed for %s'%str(e))
            return None

    def update_html(self, similarity_dict):
        """
        通过找到的表格位置修改html，添加链接和表格的锚点
        :param similarity_dict:
        :return:
        """
        try:
            append_tag = self.soup.body.find_all('div')[-1]
            for index, (key_sentence, similarity_info) in enumerate(similarity_dict.items()):
                br_tag = self.soup.new_tag('br')
                table_index = similarity_info[0]['tableIndex']
                table_tag = self.soup.find_all('table')[table_index]
                if table_tag.attrs.get('id'):
                    new_tag = self.soup.new_tag('a')
                    new_tag.attrs = {'href': '#%s' % table_tag.attrs.get('id')}
                else:
                    table_tag.attrs['id'] = 'link_%d' % index
                    new_tag = self.soup.new_tag('a')
                    new_tag.attrs = {'href': '#link_%d' % index}
                new_tag.string = key_sentence
                append_tag.insert_after(new_tag)
                append_tag.insert_after(br_tag)
        except Exception, e:
            logger.error('update html failed for %s'%str(e))

if __name__ == '__main__':
    # file_path = '/home/showlove/cc/gov/ppp/html'
    # file_name = '高青县东部城区和南部新区集中供热工程项目财政承受能力论证报告（含附表）.htm'
    # file_name = '河北省承德市宽城满族自治县中医院迁址新建一期财政承受能力报告.htm'
    # file_name = '陕西省铜川市汽车客运综合总站PPP项目财政可承受能力论证报告.htm'
    # file_name = '陕西省铜川市耀州区“美丽乡村”气化工程财政承受能力论证报告.htm'
    # file_name = '宜昌市妇幼保健院（市儿童医院）PPP项目财政承受能力报告.htm'
    # file_name = 'test.htm'
    # file_path = '/home/showlove/cc/gov/ppp/test/html'
    # saving_path = '/home/showlove/cc/gov/ppp/test/table_info'
    # model = htmlTableAnalysis(file_path, saving_path)
    # model.get_file_name(file_name)
    # table_info_list = model.generate_table_info()
    # saving_path = '/home/showlove/cc/gov/ppp/table_info'
    # model = htmlTableAnalysis(file_path, saving_path, file_name)
    # table_info_list = model.generate_table_info()
    # similarity_dict = model.cal_similarity_dic(table_info_list)
    # result_dict = model.generate_result_dict(table_info_list, similarity_dict)
    # model.update_html(similarity_dict)
    # # print result_dict
    # ####################################################
    # for key, info in result_dict.items():
    #     print key.encode('utf-8')
    #     for seg in info:
    #         print seg[0].encode('utf-8') + ':' + seg[1]
    # ####################################################
    # table_json = {
    #     'result': result_dict,
    #     'data': table_info_list,
    #     'similarity': similarity_dict
    # }
    # model.save_new_soup()
    # model.save_info_list(table_json)
    file_path = '/home/showlove/cc/gov/ppp/test/html'
    saving_path = '/home/showlove/cc/gov/ppp/test/table_info'
    model = htmlTableAnalysis(file_path, saving_path)
    files = os.listdir(file_path)
    for file_name in files:
        if file_name.endswith('htm'):
            logger.info('begin file %s'%file_name)
            model.get_file_name(file_name)
            table_info_list = model.generate_table_info()
            similarity_dict = model.cal_similarity_dic(table_info_list)
            result_dict = model.generate_result_dict(table_info_list, similarity_dict)
            table_json = {
                'result': result_dict,
                'data': table_info_list,
                'similarity': similarity_dict
            }
            model.save_info_list(table_json)
        else:
            continue


