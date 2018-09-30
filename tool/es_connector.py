# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: es_connector.py
@ time: $18-9-19 下午6:03
"""
from elasticsearch import Elasticsearch
from logger import logger
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class esConnector(object):
    def __init__(self, url, index, doc_type):
        """
        暂时没有分布式， url为单个链接
        :param url:
        Elasticsearch fun
        es.index
        """
        self.es = Elasticsearch([url])
        self.index = index
        self.doc_type = doc_type
        self.re_connect = 3

    def search_all(self, size=1000):
        """

        :return:
        """
        try:
            dsl_query = {
                'query':{
                    'match_all':{}
                },
                'size':size
            }
            result = self.es.search(self.index, self.doc_type, body=dsl_query)
            return result
        except Exception, e:
            logger.error('search all doc failed for %s' % str(e))
            return None

    def search_doc_by_id(self, id):
        """
        search doc by id
        :param id:
        :return:
        """
        try:
            dsl_query = {
                'query': {
                    'match': {
                        '_id': id
                    }
                }
            }
            result = self.es.search(self.index, self.doc_type, body=dsl_query)
            if len(result.get('hits', {}).get('hits', [])):
                return result.get('hits', {}).get('hits', [])[0]
            else:
                return []
        except Exception, e:
            logger.error('search doc by id failed for %s' % str(e))
            return None

    def insert_single_info(self, info):
        """

        :param info:
        :return:
        """
        try:
            result = self.es.index(self.index, self.doc_type, body=info)
            return result
        except Exception, e:
            logger.error('insert single info failed for %s' % str(e))
            return None

    def check_info_exist(self, title):
        """
        由于为对插入操作指定id，需要使用title查询文件信息是否存在
        :param title:
        :return:
        """
        try:

            # elasticsearch中的字符串精确匹配
            # 参考 https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query.html
            dsl_query = {
                'query': {
                    'match_phrase': {
                        'title': title
                    }
                }
            }
            result = self.es.search(self.index, self.doc_type, body=dsl_query)

            if len(result.get('hits', {}).get('hits', [])):
                return True
            else:
                return False
        except Exception, e:
            logger.error('check info existed failed for %s' % str(e))
            return None

    def check_list_contain(self, seg):
        """

        :param seg:
        :return:
        """
        pass

    def search_id_from_title(self, title):
        """
        通过文件名查询es id
        用于rule from
        :param title:
        :return:
        """
        dsl_query = {
            'query': {
                'match_phrase': {
                    'title': title
                }
            }
        }
        result = self.es.search(self.index, self.doc_type, body=dsl_query)
        id_list = list()
        title_list = list()
        for item in result.get('hits', {}).get('hits', []):
            _id = item.get('_id', '')
            _title = item.get('_source', {}).get('title', '')
            if _id not in id_list and _id != '':
                id_list.append(_id)
                title_list.append(_title)
        return id_list, title_list

    def search_id_list_from_identify(self, identify):
        """
        通过文件编号搜索引用id列表
        :param identify:
        :return:
        """
        dsl_query = {
            'query': {
                'match': {
                    'content_identify':{
                        'query': identify,
                        'operator': 'and'
                    }
                }
            },
            'size': 1000
        }
        result = self.es.search(self.index, self.doc_type, body=dsl_query)
        id_list = list()
        for item in result.get('hits', {}).get('hits', []):
            _id = item.get('_id', '')
            if _id not in id_list and _id != '':
                id_list.append(_id)
        return id_list

    def search_id_list_from_filename(self, file_name):
        """
        通过文件名搜索引用id列表
        :param file_name:
        :return:
        """
        dsl_query = {
            'query': {
                'bool': {
                    'should': [
                        {
                            'match_phrase': {
                                'quote_title': file_name
                            }
                        },
                        {
                                'match_phrase': {
                                    'title': file_name
                                }
                        }
                    ]
                }
            }
        }
        result = self.es.search(self.index, self.doc_type, body=dsl_query)
        id_list = list()
        for item in result.get('hits', {}).get('hits', []):
            _id = item.get('_id', '')
            if _id not in id_list and _id != '':
                id_list.append(_id)
        return id_list

    def search_id_list_explain(self, file_name):
        """
        通过文件名搜索政策解读id列表
        :param file_name:
        :return:
        """
        dsl_query = {
            'query': {
                'match_phrase': {
                    'quote_title': file_name
                }
            }
        }
        result = self.es.search(self.index, self.doc_type, body=dsl_query)
        id_list = list()
        for item in result.get('hits', {}).get('hits', []):
            _id = item.get('_id', '')
            if _id not in id_list and _id != '':
                id_list.append(_id)
        return id_list

    def search_info_by_keyword(self, key_word):
        """
        通过关键字进行召回
        :param key_word:
        :return:
        """
        dsl_query = {
            'query': {
                'match_phrase': {
                    'quote_title': key_word
                }
            }
        }
        result = self.es.search(self.index, self.doc_type, body=dsl_query)
        return result.get('hits', {}).get('hits', [])

    def test(self, title):
        """
        通过文件名查询es id
        :param title:
        :return:
        """
        dsl_query = {
            'query': {
                'match_phrase': {
                    'title': title
                }
            }
        }
        result = self.es.search(self.index, self.doc_type, body=dsl_query)
        if len(result.get('hits', {}).get('hits', [])):
            _id = result.get('hits', {}).get('hits', [])[0].get('_id', '')
        else:
            return None
        if len(_id):
            return _id
        else:
            return None

    # query part
    # #######################################
    def saerch_by_query(self, query):
        """
        abstract, title, content
        :param query:
        :return:
        """
        try:
            response = list()
            dsl_query = {
                'query': {
                    'bool': {
                        'should': [
                            {
                                'match_phrase': {
                                    'abstract': query
                                }
                            },
                            {
                                'match_phrase': {
                                    'title': query
                                }
                            },
                            {
                                'match': {
                                    'content': query
                                }
                            }
                        ]
                    }
                },
                'size': 50
            }
            # dsl_query = {
            #         "query": {
            #             "multi_match": {
            #                 "query": query,
            #                 "fields": ["abstract^3", "title^2", "content"]
            #             }
            #         },
            #         "size": 50
            # }
            # dsl_query = {
            #     "query": {
            #         "function_score": {
            #             "query": {"match_all": {}},
            #             "boost": "1",
            #             "functions": [
            #                 {
            #                     "filter": {"match": {"content": query}},
            #                     "weight": 1
            #                 },
            #                 {
            #                     "filter": {"match": {"title": query}},
            #                     "weight": 2
            #                 },
            #                 {
            #                     "filter": {"match": {"abstract": query}},
            #                     "weight": 3
            #                 }
            #             ],
            #             "max_boost": 500,
            #             "score_mode": "max",
            #             "boost_mode": "sum",
            #             "min_score": 1,
            #         }
            #     },
            #     "size": 50
            # }
            result = self.es.search(self.index, self.doc_type, body=dsl_query)
            for info in result.get('hits', {}).get('hits', []):
                response.append(info)
            return response
        except Exception, e:
            logger.error('seaching process failed for %s' % str(e))
            return []

if __name__ == '__main__':
    es_db = esConnector(url='localhost:9200', index='test', doc_type='finace')
    id = 'dcuZ9mUB6ohSoT2PExRJ'
    result = es_db.search_doc_by_id(id)
    title = '关于印发《彩票监管咨询和评审专家管理暂行办法》的通知'
    title = '彩票监管咨询和评审专家管理暂行办法'
    title = '关于开展三大粮食作物完全成本保险和收入保险试点工作的通知'
    title = '中央国有资本经营预算支出管理暂行办法'
    query = '关于印发《彩票监管咨询和评审专家管理暂行办法》的通知'
    # query = '管理暂行办法'
    result = es_db.saerch_by_query(query)
    # result = es_db.test(title)
    # title = '解读'
    # title = '中国—中东欧国家合作索非亚纲要'
    # result = es_db.check_info_exist(title)
    result = es_db.search_id_list_from_filename(title)
    result = es_db.search_id_from_title(title)
    # print result
    # 财会〔2018〕24号
    # identify = '财会〔2017〕24号'
    # identify = '财会〔2017〕25号'
    # es_db.search_id_list_from_identify(identify)


