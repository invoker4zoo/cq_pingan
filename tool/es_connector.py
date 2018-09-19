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

class esConnector(object):
    def __init__(self, url):
        """
        暂时没有分布式， url为单个链接
        :param url:
        Elasticsearch fun
        es.index
        """
        self.es = Elasticsearch([url])

