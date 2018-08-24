# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: html_analysis_sample.py
@ time: $18-8-22 下午3:51
"""

from bs4 import BeautifulSoup
import os
# import sys
# import numpy as np

sentence_delimiters = ['?', '!', ';', '？', '！', '。', '；', '……', '…', ',' , '，']

def get_tag_string(tag):
    """

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

def check_sentence(str):
    """
    判断语句是否出现断句
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


def print_matrix(str_matrix):
    """
    打印表格内容
    :param str_matrix:
    :return:
    """
    for row in str_matrix:
        row_des = ''
        for seg in row:
            try:
                seg.strip()
                seg = seg.replace('\n', '')
            except:
                pass
            if seg == None:
                row_des += '  None'
            else:
                row_des += '  ' + seg
        print row_des

def describe_table(table_tag):
    """
    表头的识别要查看两个属性： rowspan 和 colspan
    :param table_tag:
    :return:
    """
    # 表头的解析
    table_col = 0
    table_row = len(table_tag.find_all('tr'))
    tr_head = table_tag.find('tr')
    num_head = 0
    year_head = 0
    row_head = 1
    empty_head = 0
    for td in tr_head.find_all('td'):
        td_str = ''
        for str in td.stripped_strings:
            td_str += str
        td_str.strip()
        td_str.replace(',', '')
        try:
            float(str)
            is_number = True
            num_head += 1
        except:
            try:
                float(str[:-1])
                is_number = True
                num_head += 1
            except:
                is_number = False
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
    invaild = True if float(empty_head)/table_col >0.8 or table_col<1 or table_row<2 else False
    return table_col, table_row, row_head, invaild


def generate_table_matrix(table_tag, table_col, table_row):
    """

    :param table_tag:
    :param table_col:
    :param table_row:
    :param row_head:
    :param is_horizontal:
    :return:
    """

    str_matrix = [[None for _ in range(table_col)] for _ in range(table_row)]
    for row_index, tr in enumerate(table_tag.find_all('tr')):
        for col_index, td in enumerate(tr.find_all('td')):
            wide = 0
            height = 0
            des = get_tag_string(td)
            des = des.strip()
            for i in range(0, table_col-col_index):
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
                    for i in range(1,height):
                        str_matrix[row_index + i][col_index] = des
            else:
                pass

    return str_matrix


####### test part
# file_path = '/home/showlove/cc/gov/ppp/html'
# test_file = os.path.join(file_path,'高青县东部城区和南部新区集中供热工程项目财政承受能力论证报告（含附表）.htm')
# # test_file = os.path.join(file_path,'河北省承德市宽城满族自治县中医院迁址新建一期财政承受能力报告.htm')
# # test_file = os.path.join(file_path,'陕西省铜川市汽车客运综合总站PPP项目财政可承受能力论证报告.htm')
# # test_file = os.path.join(file_path,'陕西省铜川市耀州区“美丽乡村”气化工程财政承受能力论证报告.htm')
#
#
# with open(test_file) as f:
#     html = f.read()
#     soup = BeautifulSoup(html, 'html5lib')
#     table_list = soup.find_all('table')
#     for table in table_list:
#         print '表格描述:'
#         des = ''
#         for element in table.previous_siblings:
#             is_center = False
#             if element.name:
#                 # element.name
#                 if element.name == 'table':
#                     des = '连续表'
#                     break
#                 if element.get('align','') == 'center':
#                     # des = get_tag_string(element) + des
#                     is_center = True
#                     try:
#                         int(get_tag_string(element).strip())
#                         is_center = False
#                         continue
#                     except:
#                         # if is_center:
#                         #     continue
#                         # else:
#                         #     break
#                         des = get_tag_string(element) + des
#                         continue
#                 else:
#                     if is_center:
#                         break
#
#                 des = get_tag_string(element) + des
#                 if check_sentence(des):
#                     break
#             else:
#                 continue
#         if check_sentence(des):
#             for index, seg in enumerate(des[::-1]):
#                 if seg.encode('utf-8') in sentence_delimiters:
#                     if index == 0:
#                         continue
#                     else:
#                         print des.split(seg)[-1]
#                         break
#         else:
#             print des
#
#         # table des
#         table_col, table_row, row_head, invaild = describe_table(table)
#         if invaild:
#             print '表格无效'
#             continue
#         else:
#             str_matrix = generate_table_matrix(table,table_col,table_row)
#             print_matrix(str_matrix)

