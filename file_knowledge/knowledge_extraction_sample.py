# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: knowledge_extraction_sample.py
@ time: $18-9-21 下午3:23
"""

import thulac
import os
import sys
# from tool.db_connector import dbConnector
from tool.logger import logger
from tool.trans_dic import *
from tool.es_connector import esConnector
from tool.neo_connector import Neo4jConnector
# import elasticsearch
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# GOLBAL PARAMS
THUNLP_MODEL_PATH = "/home/showlove/cc/code/THULAC-Python/models"
THUNLP_USER_DIC_PATH = "/home/showlove/PycharmProjects/data_test/nlp/user_dic.txt"
STOP_WORD_DIC_PATH = "/home/showlove/PycharmProjects/data_test/nlp/stop_word_dic.txt"
# MONGODB_SERVER = "127.0.0.1"
# MONGODB_PORT = 27017
# MONGODB_DB = "gov_finace"
# MONGODB_COLLECTION = "center"
# neo4j config
NEO4J_URL = "bolt://localhost:7687"
NEO4J_AUTH = 'neo4j'
NEO4J_PASSWORD = 'passw0rd'
# es config
ES_URL = 'localhost:9200'
ES_INDEX = 'test'
ES_DOC_TYPE = 'finace'

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
    'parent_file': '',      # 父级文件
    'key_word': [],         # 关键词
    'abstract': [],         # 摘要
    'data_key': [],         # 抽取的数据项目
    'data': {}/[],          # 抽取的数据对象
}
"""

"""
节点类型
notice
(notice:center/shenzhen/location){id:,title:}
file
(file:center/shenzhen/location){id,title:}
entity
(entity:org/loc/name){seg:}
data
(data:center/shenzhen/location){}

关系抽取
最简版
notice attach file
file from notice
notice quote file
notice quote notice
notice explain notice
notice transmit notice
notice include entity
file include entity

"""

"""
relation rule
(source_info, target_info)
return match_rule, relation_name
"""


class buildGraph(object):
    def __init__(self):
        # init db
        self.neo4j_db = Neo4jConnector(NEO4J_URL, NEO4J_AUTH, NEO4J_PASSWORD)
        self.es_db = esConnector(ES_URL, ES_INDEX, ES_DOC_TYPE)

    def _create_doc_node(self, result_info):
        """
        建立图中的文档节点
        :result_info: es中查询结果
        :return:
        """
        try:
            for doc_info in result_info:
                doc_analysis = self._doc_info_analysis(doc_info)
                if doc_analysis:
                    if not self.neo4j_db.check_node_exist(doc_analysis):
                        self.neo4j_db.create_doc_node(doc_analysis)
                    else:
                        logger.info('node is existed, skip')
                else:
                    logger.warn('analysis doc info failed ,skip...')
        except Exception, e:
            logger.error('create doc node failed for %s' %str(e))

    def _create_entity_node(self, result_info):
        """
        建立图中的
        :param result_info:
        :return:
        """
        try:
            entity_cache_list = list()
            for doc_info in result_info:
                pass
        except Exception, e:
            logger.error('create entity node failed for %s' %str(e))

    def _doc_info_analysis(self, doc_info):
        """
        分析doc_info，提取doc的属性
        :param doc_info:
        :return:node_info
        node_type:节点的类型 notice,file
        id:es中id
        title:文件名
        """
        try:
            info = doc_info['_source']
            # 存储的doc的类型
            if len(info.get('parrent_file',[])):
                node_type = 'file'
            else:
                node_type = 'doc'
            node_id = doc_info['_id']
            title = info.get('title', '')
            location = info.get('publish_location', '')
            return {
                'node_name': 'notice',
                'node_type': node_type,
                'id': node_id,
                'title': title,
                'location': location
            }
        except Exception, e:
            logger.info('analysis doc info failed for %s' % str(e))
            return None

    def initial(self):
        """
        建立图数据库的主运行函数
        数据读取来自于es的存储数据
        :return:
        """
        try:
            result = self.es_db.search_all(size=10000)
            result_info = result['hits']['hits']
            self._create_doc_node(result_info)

        except Exception, e:
            logger.error('build graph failed for %s' % str(e))


if __name__ == '__main__':
    # neo4j_db = Neo4jConnector("bolt://localhost:7687", "neo4j", password="passw0rd")
    #
    # es_db = esConnector(url='localhost:9200', index='test', doc_type='finace')
    # result = es_db.search_all()
    # result_info = result['hits']['hits']
    # for doc_info in result_info:
    #     pass
    # pass
    process = buildGraph()
    process.initial()