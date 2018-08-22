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


class htmlTableAnalysis(object):

    def __init__(self, file_path):
        self.file_path = file_path
        self.soup = BeautifulSoup(self._read_file(), 'html5lib')


    def _read_file(self):
        """
        读取html文件
        :return:
        """
        try:
            with open(self.file_path) as f:
                return f.read()
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
                        des = '连续表'
                        break
                    if element.get('align', '') == 'center':
                        is_center = True
                        try:
                            int(self.get_tag_string(element).strip())
                            is_center = False
                            continue
                        except:
                            # if is_center:
                            #     continue
                            # else:
                            #     break
                            des = self.get_tag_string(element) + des
                            continue
                    else:
                        if is_center:
                            break

                    des = self.get_tag_string(element) + des
                    if self.check_sentence(des):
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
        # 判断横向表和竖向表
        # is_horizontal = True if float(year_head)/table_col > 0.6 or float(year_head)/table_col > 0.6 else False
        # 有效性检查
        invaild = True if float(empty_head) / table_col > 0.8 or table_col < 1 or table_row < 2 else False
        return table_col, table_row, row_head, invaild

    def generate_table_info(self):
        """

        :return: table info list
        """
        self.table_info = list()
        try:
            for table in self.soup.find_all('table'):
                info = dict()
                info['describe'] = self._search_table_describe(table)
                table_col, table_row, row_head, invaild = self._search_table_base_info(table)


        except Exception,e:
            logger.error('get table info failed for %s'%str(e))
