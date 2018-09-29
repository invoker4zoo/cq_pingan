# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: QueryHandler.py
@ time: $18-9-25 下午6:28
"""
from tool.logger import logger
import os
import sys
import tornado
from tornado.concurrent import run_on_executor
from tornado.web import HTTPError
import json
from tool.es_connector import esConnector
from tool.neo_connector import Neo4jConnector
from tool.trans_dic import *
from config.config import *
# import numpy as np
# from collections import Counter
# import datetime

reload(sys)
sys.setdefaultencoding('utf-8')


CURRENT_PATH = os.path.dirname(__file__)
if CURRENT_PATH:
    CURRENT_PATH = CURRENT_PATH + "/"

es_db = esConnector(ES_URL, ES_INDEX, ES_DOC_TYPE)
neo4j_db = Neo4jConnector(NEO4J_URL, NEO4J_AUTH, NEO4J_PASSWORD)


class DBBasedHandler(tornado.web.RequestHandler):
    def build_query_params(self, **kwargs):
        """
        构建查询数据库的参数collection和filter
        :rtype : object
        """
        pass

    def handle_item(self, item):
        """
        从每条数据库记录到返回数据的默认实现，如有需要可在子类重写此方法
        :param dict item: 每条数据库的记录
        :return dict: 实际数据
        """
        if 'updateTime' in item:
            del item['updateTime']
        return item

    def _get_page_and_size(self):
        """
        ATT：不要重写此方法！！！
        """
        try:
            page = int(self.get_argument('page', 1))
            size = int(self.get_argument('size', 20))
            if not 1 < size <= 100:
                raise HTTPError(400, 'bad request.')
        except:
            raise HTTPError(400, 'bad request.')
        return page, size

    def build_return_data(self, **kwargs):
        result = {
            'total': kwargs['total'],
            'totalPage': kwargs['total_page'],
            'currentPage': kwargs['current_page'],
            'pageSize': kwargs['page_size'],
            'data': []
        }
        if self.NEED_PARAMS:
            result[self.NEED_PARAMS[0][0]] = kwargs['params'][self.NEED_PARAMS[0][0]]
        for item in kwargs['data']:
            result['data'].append(self.handle_item(item))
        return result

    @run_on_executor
    def get(self):
        pass


class MainSearchHandler(DBBasedHandler):
    def get(self):
        """
        search all node and links
        :return:
        """
        node_list, link_list = neo4j_db.search_all()
        response = {
                'nodeList': node_list,
                'linkList': link_list
        }
        if node_list:
            # self.set_header('Content-Type', 'application/json;chartset=UTF-8')
            self.write(json.dumps(response, ensure_ascii=False, sort_keys=True, indent=4))
            # self.write(response)
        else:
            raise HTTPError(404, 'not found.')


class QuerySearchHandler(DBBasedHandler):
    def get(self):
        """
        get search list with query
        :return:
        """
        query = self.get_argument('query', '')
        result = es_db.saerch_by_query(query)
        data = list()
        for info in result:
            data.append({
                'score': info.get('_score', 0),
                'id': info.get('_id', ''),
                'content': info.get('_source', {}).get('content', ''),
                'title': info.get('_source', {}).get('title', ''),
                'identify': info.get('_source', {}).get('identify', ''),
                'publishTime': info.get('_source', {}).get('publish_time', ''),
                'publishOrg': info.get('_source', {}).get('publish_org', ''),
                'publishOrg2': info.get('_source', {}).get('publish_org_2', ''),
                'keyWord': info.get('_source', {}).get('key_word', ''),
                'abstract': info.get('_source', {}).get('abstract', ''),
                'category': CATEGORY[info.get('_source', {}).get('category', '')]
            })
        if len(data):
            # self.set_header('Content-Type', 'application/json;chartset=UTF-8')
            response = {
                'data': data
            }
            self.write(json.dumps(response, ensure_ascii=False, sort_keys=True, indent=4))
            # self.write(response)
        else:
            raise HTTPError(404, 'not found.')


class IdSearchHandler(DBBasedHandler):
    """
    search node and links by id
    :return:
    """
    def get(self):
        id = self.get_argument('id', '')
        node_list, link_list = neo4j_db.search_relation_by_id(id)
        response = {
            'data': {
                'nodeList': node_list,
                'linkList': link_list
            }
        }
        if node_list:
            # self.set_header('Content-Type', 'application/json;chartset=UTF-8')
            self.write(json.dumps(response, ensure_ascii=False, sort_keys=True, indent=4))
            # self.write(response)
        else:
            raise HTTPError(404, 'not found.')