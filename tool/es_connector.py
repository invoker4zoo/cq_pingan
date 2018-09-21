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

if __name__ == '__main__':
    es_db = esConnector(url='localhost:9200', index='test', doc_type='finace')
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
    result = es_db.check_info_exist(title)
    print result

