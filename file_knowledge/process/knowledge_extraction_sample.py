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
sys.path.append('..')
from tool.logger import logger
from tool.trans_dic import *
from tool.es_connector import esConnector
from tool.neo_connector import Neo4jConnector
from config.config import *
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# # GOLBAL PARAMS
# THUNLP_MODEL_PATH = "/home/showlove/cc/code/THULAC-Python/models"
# THUNLP_USER_DIC_PATH = "/home/showlove/PycharmProjects/data_test/nlp/user_dic.txt"
# STOP_WORD_DIC_PATH = "/home/showlove/PycharmProjects/data_test/nlp/stop_word_dic.txt"
# # MONGODB_SERVER = "127.0.0.1"
# # MONGODB_PORT = 27017
# # MONGODB_DB = "gov_finace"
# # MONGODB_COLLECTION = "center"
# # neo4j config
# NEO4J_URL = "bolt://localhost:7687"
# NEO4J_AUTH = 'neo4j'
# NEO4J_PASSWORD = 'passw0rd'
# # es config
# ES_URL = 'localhost:9200'
# ES_INDEX = 'test'
# ES_DOC_TYPE = 'finace'

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
(source_info, #target_info)
return match_rule:bool, relation_name:string, params:[{}]
"""




class buildGraph(object):
    def __init__(self):
        # init db
        self.neo4j_db = Neo4jConnector(NEO4J_URL, NEO4J_AUTH, NEO4J_PASSWORD)
        self.es_db = esConnector(ES_URL, ES_INDEX, ES_DOC_TYPE)
        # self.rule_list = [self.rule_notice_attach, self.rule_doc_entity, self.rule_doc_explain,\
        #                   self.rule_doc_quote, self.rule_file_from]

        self.rule_list = [self.rule_notice_attach, self.rule_doc_explain,\
                      self.rule_doc_quote, self.rule_file_from, self.rule_doc_trans()]

    # rule part
    def rule_notice_attach(self, source_info):
        """
        提取附件关系的规则
        :param source_info:
        :return: bool, string, list
        """
        try:
            link_info = list()
            info = source_info.get('_source', {})
            source_id = source_info.get('_id', '')
            if len(info.get('attachment_file', [])):
                for attachment_file in info.get('attachment_file'):
                    search_name = attachment_file[: - 1 * (len(attachment_file.split('.')[-1]) + 1)]
                    _id_list, _title_list = self.es_db.search_id_from_title(search_name)
                    for _id, _title in zip(_id_list, _title_list):
                        if _id != source_id and _title == search_name:
                            link_info.append({
                                'source': source_id,
                                'target': _id,
                                'sourceType': 'id',
                                'targetType': 'id'
                            })
                    else:
                        pass
                if len(link_info):
                    return True, 'attach', link_info
                else:
                    return False, '', []
            else:
                return False, '', []
        except Exception, e:
            logger.error('searching attach relation attach failed for %s' % str(e))
            return False, '', []

    def rule_file_from(self, source_info):
        """
        提取附件从属的规则
        :param source_info:
        :return: bool, string, list
        """
        try:
            link_info = list()
            info = source_info.get('_source', {})
            source_id = source_info.get('_id', '')
            if len(info.get('parrent_file', '')):
                search_name = info.get('parrent_file')
                _id_list, _title_list = self.es_db.search_id_from_title(search_name)
                for _id, _title in zip(_id_list, _title_list):
                    if _id != source_id and _title == search_name:
                        link_info.append({
                            'source': source_id,
                            'target': _id,
                            'sourceType': 'id',
                            'targetType': 'id'
                        })
                if len(link_info):
                    return True, 'from', link_info
                else:
                    return False, '', []
            else:
                return False, '', []
        except Exception, e:
            logger.error('searching attach relation from failed for %s' % str(e))
            return False, '', []

    def rule_doc_quote(self, source_info):
        """
        提取文档的引用关系，包括idendify和文件的引用
        :param source_info:
        :return:
        """
        try:
            link_info = list()
            info = source_info.get('_source', {})
            source_id = source_info.get('_id', '')
            source_identify = info.get('identify', '')
            source_quote = info.get('quote_title', []) + info.get('quote_content', [])
            source_file = list()
            source_quote_file = list()
            # can use counter
            for item in info.get('quote_title', []):
                if item not in source_file:
                    source_file.append(item)
            for item in info.get('quote_content', []):
                if item not in source_file:
                    source_file.append(item)
            for item in source_quote:
                if item not in source_quote_file:
                    source_quote_file.append(item)
            # seaching
            if len(source_identify):
                _id_list = self.es_db.search_id_list_from_identify(source_identify)
            else:
                _id_list = []
            for _id in _id_list:
                if _id != source_id:
                   link_info.append({
                        'source': source_id,
                        'target': _id,
                        'sourceType': 'id',
                        'targetType': 'id'
                   })
            for quote_file in source_quote_file:
                _id_list = self.es_db.search_id_list_from_filename(quote_file)
                for _id in _id_list:
                    if _id != source_id:
                        link_info.append({
                            'source': source_id,
                            'target': _id,
                            'sourceType': 'id',
                            'targetType': 'id'
                        })
            if len(link_info):
                return True, 'quote', link_info
            else:
                return False, '', []

        except Exception, e:
            logger.error('searching attach relation quote failed for %s' % str(e))
            return False, '', []

    def rule_doc_entity(self, source_info):
        """

        :param source_info:
        :return:
        """
        try:
            link_info = list()
            info = source_info.get('_source', {})
            source_id = source_info.get('_id', '')
            entity_name = info.get('entity_name', [])
            entity_org = info.get('entity_org', [])
            entity_loc = info.get('entity_loc', [])
            entity_list = entity_name + entity_org + entity_loc
            for seg in entity_list:
                link_info.append({
                    'source': source_id,
                    'target': seg,
                    'sourceType': 'id',
                    'targetType': 'seg'
                })
            if len(link_info):
                return True, 'include', link_info
            else:
                return False, '', []
        except Exception, e:
            logger.error('searching entity relation failed for %s' % str(e))
            return False, '', []

    def rule_doc_explain(self, source_info):
        """
        解读文件的关系提取
        :param source_info:
        :return:
        """
        try:
            link_info = list()
            info = source_info.get('_source', {})
            source_id = source_info.get('_id', '')
            title = info.get('title', '')
            if '解读' in title or '答记者问' in title:
                pass
            else:
                return False, '', []
            if len(info.get('quote_title', [])):
                for quote_file in info.get('quote_title'):
                    _id_list = self.es_db.search_id_list_from_filename(quote_file)
                    for _id in _id_list:
                        if _id != source_id:
                            link_info.append({
                                'source': source_id,
                                'target': _id,
                                'sourceType': 'id',
                                'targetType': 'id'
                            })
                if len(link_info):
                    return True, 'explain', link_info
                else:
                    return False, '', []
            else:
                return False, '', []

        except Exception, e:
            logger.error('searching doc explain relationship failed for %s' % str(e))
            return False, '', []

    def rule_doc_trans(self, source_info):
        """
        转发文件的关系提取
        :param source_info:
        :return:
        """
        try:
            link_info = list()
            info = source_info.get('_source', {})
            source_id = source_info.get('_id', '')
            title = info.get('title', '')
            if '转发' in title:
                pass
            else:
                return False, '', []
            if len(info.get('title', [])):
                search_title = info.get('title').replace('转发', '')
                _id_list, _ = self.es_db.search_id_from_title(search_title)
                for _id in _id_list:
                    if _id != source_id:
                        link_info.append({
                                'source': source_id,
                                'target': _id,
                                'sourceType': 'id',
                                'targetType': 'id'
                        })
                # for quote_file in info.get('quote_title'):
                #     _id_list = self.es_db.search_id_list_from_filename(quote_file)
                #     for _id in _id_list:
                #         if _id != source_id:
                #             link_info.append({
                #                 'source': _id,
                #                 'target': source_id,
                #                 'sourceType': 'id',
                #                 'targetType': 'id'
                #             })

                if len(link_info):
                    return True, 'trans', link_info
                else:
                    return False, '', []
            else:
                return False, '', []

        except Exception, e:
            logger.error('searching doc explain relationship failed for %s' % str(e))
            return False, '', []
    # rule part end
    # ########################################################

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
                        logger.info('create node...')
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
                info = doc_info['_source']
                entity_name = info.get('entity_name', [])
                entity_org = info.get('entity_org', [])
                entity_loc = info.get('entity_loc', [])
                for seg in entity_name:
                    if seg not in entity_cache_list:
                        entity_info = {
                            'entity_type': 'name',
                            'seg': seg
                        }
                        self.neo4j_db.create_entity_node(entity_info)
                        logger.info('create name entity node of %s' % seg)
                        entity_cache_list.append(seg)
                    else:
                        continue
                for seg in entity_org:
                    if seg not in entity_cache_list:
                        entity_info = {
                            'entity_type': 'org',
                            'seg': seg
                        }
                        self.neo4j_db.create_entity_node(entity_info)
                        logger.info('create organization entity node of %s' % seg)
                        entity_cache_list.append(seg)
                    else:
                        continue

                for seg in entity_loc:
                    if seg not in entity_cache_list:
                        entity_info = {
                            'entity_type': 'loc',
                            'seg': seg
                        }
                        self.neo4j_db.create_entity_node(entity_info)
                        logger.info('create location entity node of %s' % seg)
                        entity_cache_list.append(seg)
                    else:
                        continue

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

    def _create_node_relationship(self, result_info, rule_list):
        """
        根据规则建立节点间的链接关系
        :param result_info:
        :return:
        """
        try:
            for source_info in result_info:
                # begin match rules
                logger.info('extract file with id %s' % str(source_info.get('_id','')))
                for rule in rule_list:
                    is_match, relationship_type, relationship_info = rule(source_info)
                    if is_match:
                        logger.info('matching rule %s'%rule.__name__)
                        self.neo4j_db.create_relation(relationship_type, relationship_info)
                    else:
                        pass
        except Exception, e:
            logger.error('extract relationship between nodes failed for %s' % str(e))

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
            self._create_entity_node(result_info)
            # self._create_node_relationship(result_info, [self.rule_doc_explain, self.rule_doc_quote])
            self._create_node_relationship(result_info, self.rule_list)

        except Exception, e:
            logger.error('build graph failed for %s' % str(e))

    def build_graph_by_id(self, id):
        """
        建立固定文档的图连接
        :param id:
        :return:
        """
        try:
            doc_result = self.es_db.search_doc_by_id(id)
            doc_result_info = doc_result['hits']['hits']
            self._create_doc_node(doc_result_info)
            self._create_entity_node(doc_result_info)
            # result = self.es_db.search_all(size=10000)
            # result_info = result['hits']['hits']
            self._create_entity_node(doc_result_info)
        except Exception, e:
            logger.error('build graph by id failed for %s' % str(e))


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