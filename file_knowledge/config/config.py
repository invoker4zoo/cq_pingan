# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: config.py
@ time: $18-9-25 下午3:25
"""
THUNLP_MODEL_PATH = "/home/showlove/cc/code/THULAC-Python/models"
THUNLP_USER_DIC_PATH = "../tool/user_dic.txt"
STOP_WORD_DIC_PATH = "../tool/stop_word_dic.txt"
FILE_PATH = '/home/showlove/cc/gov/finace/center/trans'

# 人名，地名，机构名，其他专有名词，简称，用户字典（用户字典只存放命名实体？）
SEG_TYPE_FILTER = ['np', 'ns', 'ni', 'nz', 'j', 'uw']

VECTOR_MODEL = "/home/showlove/cc/nlp/vector/sgns.renmin.bigram-char"
sentence_delimiters = ['?', '!', ';', '？', '！', '。', '；', '……', '…', '：', ':']
VECTOR_SIZE = 300

# mongo
MONGODB_SERVER = "127.0.0.1"
MONGODB_PORT = 27017
MONGODB_DB = "gov_finace"
MONGODB_COLLECTION = "center"
# neo4j config
NEO4J_URL = "bolt://localhost:7687"
NEO4J_AUTH = 'neo4j'
NEO4J_PASSWORD = 'passw0rd'
# es config
ES_URL = 'localhost:9200'
ES_INDEX = 'test'
ES_DOC_TYPE = 'finace'