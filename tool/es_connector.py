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
                    'match':{
                        'title': {
                                'query': title,
                                'operator': 'and'
                            }
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
        :param title:
        :return:
        """
        dsl_query = {
            'query': {
                'match': {
                    'title': {
                        'query': title,
                        'operator': 'and'
                    }
                }
            }
        }
        result = self.es.search(self.index, self.doc_type, body=dsl_query)
        _id = result.get('hits', {}).get('hits', [])[0].get('_id', '')
        if len(_id):
            return _id
        else:
            return None

    def search_id_list_from_identify(self, identify):
        """

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

if __name__ == '__main__':
    es_db = esConnector(url='localhost:9200', index='test', doc_type='finace')
    # result = es_db.search_all()
    # print result
    # search_query = '地方政府债券弹性招标发行业务规程'
    # dsl_query = {
    #     'query': {
    #         'match': {
    #             'abstract': search_query
    #         }
    #     }
    # }
    # result = es_db.es.search(es_db.index, es_db.doc_type, body=dsl_query)
    # print result
    # title = u'各省份申报资料清单'
    title = '关于印发《彩票监管咨询和评审专家管理暂行办法》的通知'
    title = '彩票监管咨询和评审专家管理暂行办法'
    # result = es_db.check_info_exist(title)
    result = es_db.search_id_from_title(title)
    # print result
    # 财会〔2018〕24号
    # identify = '财会〔2017〕24号'
    # identify = '财会〔2017〕25号'
    # es_db.search_id_list_from_identify(identify)


