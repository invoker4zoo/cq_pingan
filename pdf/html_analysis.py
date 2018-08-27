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
from bs4 import BeautifulSoup
import os
from tool.logger import logger
from tool.punct import sentence_delimiters
import numpy as np
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class htmlTableAnalysis(object):

    def __init__(self, file_path, saving_path, file_name):
        self.file_name = file_name
        self.file_path = file_path
        self.saving_path = saving_path
        self.soup = BeautifulSoup(self._read_file(), 'html5lib')


    def _read_file(self):
        """
        读取html文件
        :return:
        """
        try:
            with open(os.path.join(self.file_path, self.file_name),'r') as f:
                string = f.read()
            return string
        except Exception,e:
            logger.error('reading html file failed for %s'%str(e))

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

        :param key_list:
        :return:
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
                    for index in seg_index[1:]:
                        new_key_list[index] = None
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
                for index, seg in enumerate(des[::-1]):
                    if seg.encode('utf-8') in sentence_delimiters:
                        if index == 0:
                            continue
                        else:
                            return des.split(seg)[-1]
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
            if td.attrs.get('rowspan'):
                type_list.append(1)
            elif td.attrs.get('colspan'):
                type_list.append(2)
            else:
                type_list.append(0)
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


    def generate_table_matrix(self, table_tag, table_col, table_row):
        """

        :param table_tag:
        :param table_col:
        :param table_row:
        :return:
        """

        str_matrix = [[None for _ in range(table_col)] for _ in range(table_row)]
        for row_index, tr in enumerate(table_tag.find_all('tr')):
            for col_index, td in enumerate(tr.find_all('td')):
                wide = 0
                height = 0
                des = self._get_tag_string(td)
                des = des.strip()
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

    def generate_table_json(self, matrix, row_head, col_head):
        """
        表格数据json化
        :param table_tag:
        :param matrix:
        :param row_head:
        :return:
        """
        table_info= []
        matrix = np.array(matrix)
        table_col = len(matrix[0,:])
        table_row = len(matrix[:,0])
        row_list = matrix[row_head:,col_head - 1]
        col_list = matrix[row_head - 1,col_head:]
        year_head = 0
        num_head = 0
        for seg in col_list:
            if seg.endswith(u'年'):
                year_head += 1
            try:
                int(seg.strip())
                num_head += 1
            except:
                pass
        is_horizontal = True if float(year_head) / table_col > 0.6 or float(num_head) / table_col > 0.6 else False
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
                if key not in info_dic.keys():
                    info_dic[key] = dict()
                for j, inner_key in enumerate(inner_key_list):
                    if inner_key not in info_dic[key].keys():
                        if is_horizontal:
                            info_dic[key][inner_key] = matrix[i + row_head,j + col_head]
                        else:
                            info_dic[key][inner_key] = matrix[j + row_head,i + col_head]
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
                        inner_key_list = matrix[row_head + index_list[0] - 1, col_head:]
                    else:
                        inner_key_list = matrix[row_head:, col_head + index_list[0] - 1]
                info_dic = dict()
                for i, key in zip(index_list, new_key_list):
                    if key not in info_dic.keys():
                        info_dic[key] = dict()

                    for j, inner_key in enumerate(inner_key_list):
                        if inner_key not in info_dic[key].keys():
                            if is_horizontal:
                                info_dic[key][inner_key] = matrix[i + row_head][j + col_head]
                            else:
                                info_dic[key][inner_key] = matrix[j + row_head][i + col_head]
                table_info.append(info_dic)
        return table_info







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
                # testing
                # try:
                #     json.dumps(info, ensure_ascii=False, indent=4)
                # except:
                #     logger.info('index %d table encoding failed'%index)
                self.table_info.append(info)
        except Exception,e:
            logger.error('get table info failed for %s'%str(e))

        return self.table_info

if __name__ == '__main__':
    file_path = '/home/showlove/cc/gov/ppp/html'
    # file_name = '高青县东部城区和南部新区集中供热工程项目财政承受能力论证报告（含附表）.htm'
    file_name = '河北省承德市宽城满族自治县中医院迁址新建一期财政承受能力报告.htm'
    # file_name = '陕西省铜川市汽车客运综合总站PPP项目财政可承受能力论证报告.htm'
    # file_name = '陕西省铜川市耀州区“美丽乡村”气化工程财政承受能力论证报告.htm'
    # file_name = '宜昌市妇幼保健院（市儿童医院）PPP项目财政承受能力报告.htm'
    saving_path = '/home/showlove/cc/gov/ppp/table_info'
    model = htmlTableAnalysis(file_path, saving_path, file_name)
    table_info_list = model.generate_table_info()
    model.save_info_list(table_info_list)

