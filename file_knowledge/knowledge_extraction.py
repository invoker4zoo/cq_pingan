# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: knowledge_extraction.py
@ time: $18-9-14 下午5:12
"""

import thulac
import os
import sys
from tool.db_connector import dbConnector
from tool.logger import logger
from tool.trans_dic import *
import elasticsearch

# GOLBAL PARAMS
THUNLP_MODEL_PATH = "/home/showlove/cc/code/THULAC-Python/models"
THUNLP_USER_DIC_PATH = "/home/showlove/PycharmProjects/data_test/nlp/user_dic.txt"
STOP_WORD_DIC_PATH = "/home/showlove/PycharmProjects/data_test/nlp/stop_word_dic.txt"
MONGODB_SERVER = "127.0.0.1"
MONGODB_PORT = 27017
MONGODB_DB = "gov_finace"
MONGODB_COLLECTION = "center"

"""
文本域
es file format
index   finace
type    notice/file
{
    'publish_time': '',     # 发布时间
    'publish_location':'',  # 发布地点
    'publish_org': '',      # 发布机构
    'publish_org_2': '',    # 发布的二级机构
    'title': '',            # 标题
    'category': '',         # 文档栏目划分，notice [政策发布, 财经视点, 政策解读, 财政数据] file [文本附件，数据附件， 表格附件]
    'classify': '',         # 文档类型划分[财政收入，民生支出，税收增长，债务管理，社会保障支出，涉农资金，...]
    'content': '',          # 文本内容
    'identify': '',         # 抽取到的文档标示
    'content_identify': '', # content中提到的标识，例：财会〔2018〕24号
    'content_attach': '',   # content的后缀
    'quote_title': [],      # 标题引用文件
    'quote_content':[],     # 正文引用文件
    'entity_loc': [],       # 命名实体，地点
    'entity_org': [],       # 命名实体，机构
    'entity_name': [],      # 命名实体，姓名
    'attachment_file': [],  # 附件列表
    'key_word': [],         # 关键词
    'abstract': [],         # 摘要
    'data_key': [],         # 抽取的数据项目
    'data': {}/[],          # 抽取的数据对象
}
"""

# mongo = dbConnector(MONGODB_SERVER, MONGODB_PORT, MONGODB_DB, MONGODB_COLLECTION)
# for record in mongo.collection.find():
#     content = record.get('noticeContent', '')
#     title = record.get('noticeTitle', '')
#     category = record.get('category', '')
#     if category:
#         category_trans = CATEGORY.get(category)
#     else:
#         pass


if __name__ == '__main__':
    pass