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

# GOLBAL PARAMS
THUNLP_MODEL_PATH = "/home/showlove/cc/code/THULAC-Python/models"
THUNLP_USER_DIC_PATH = "/home/showlove/PycharmProjects/data_test/nlp/user_dic.txt"
STOP_WORD_DIC_PATH = "/home/showlove/PycharmProjects/data_test/nlp/stop_word_dic.txt"
MONGODB_SERVER = "127.0.0.1"
MONGODB_PORT = 27017
MONGODB_DB = "gov_finace"
MONGODB_COLLECTION = "center"


mongo = dbConnector(MONGODB_SERVER, MONGODB_PORT, MONGODB_DB, MONGODB_COLLECTION)
for record in mongo.collection.find():
    content = record.get('noticeContent', '')
    title = record.get('noticeTitle', '')
    category = record.get('category', '')
    if category:
        category_trans = CATEGORY.get(category)
    else:
        pass