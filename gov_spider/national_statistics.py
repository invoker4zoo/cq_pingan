# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: national_stastics.py
@ time: $18-11-14 下午2:34
"""
import requests
import time
import json
from tool.crawler import BaseCrawler
from tool.logger import logger
from tool.db_connector import dbConnector
from config.config import *
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class nationalStatistics(BaseCrawler):

    def __init__(self, data_url, needed_data_key=['地方财政收入', '地方财政支出']):
        """
        城市数据爬取主函数
        :param base_url:
        """
        self.data_url = data_url
        self.tree_key_info = self._load_json('../data/key_code_info.json')
        self.reg_info = self._load_json('../data/reg_info.json')
        self.needed_info = [{'name': item['name'], 'id': item['id']} for item in self.tree_key_info\
                            if item['name'] in needed_data_key]
        self.post_data = {
                'm': 'QueryData',
                'dbcode': 'fsnd',
                'rowcode': 'zb',
                'colcode': 'sj',
                'wds': '',
                'dfwds':'',
                'k1': time.time()
            }

        self.mongo = dbConnector(MONGODB_SERVER, MONGODB_PORT, MONGODB_DB_STATISTIC, MONGODB_COLLECTION_PROVINCE)

    def run(self):
        """
        主函数
        :return:
        """
        try:
            wds_info = [{"wdcode":"reg","valuecode":""}]
            dfwds_info = [{"wdcode":"zb","valuecode":""},{"wdcode":"sj","valuecode":"LAST20"}]
            for needed_key in self.needed_info:
                dfwds_info[0]['valuecode'] = needed_key['id']
                zb_key = needed_key['name']
                needed_key_info_list = list()
                for _reg in self.reg_info:
                    wds_info[0]['valuecode'] = _reg['code']
                    reg_key = _reg['name']
                    logger.info('analysis %s data info' % reg_key)
                    self.post_data['wds'] = json.dumps(wds_info)
                    self.post_data['dfwds'] = json.dumps(dfwds_info)
                    response = requests.post(self.data_url, data=self.post_data)
                    result = json.loads(response.content)
                    data_list = self._analysis_table_data(result, zb_key, reg_key)
                    data_reg_info = {
                        'location': _reg['name'],
                        'key': zb_key,
                        'data': data_list
                    }
                    needed_key_info_list.append(data_reg_info)
                self._save_json(needed_key_info_list, '../data/%s.json'%zb_key)
        except Exception, e:
            logger.error('crawler main process failed for %s' % str(e))

    def _analysis_table_data(self, table_info, zb_key, reg_key):
        """
        table_info format
        {
            'datanodes':[{
                u'code': u'zb.A080101_reg.110000_sj.2017', u'data': {u'dotcount': 2, u'data': 5430.79, u'strdata': u'5430.79', u'hasdata': True}, u'wds': [{u'wdcode': u'zb', u'valuecode': u'A080101'}, {u'wdcode': u'reg', u'valuecode': u'110000'}, {u'wdcode': u'sj', u'valuecode': u'2017'}]
            },# table data
            ],
            'wdnodes':[{zb node info}, {reg node info}, {sj node info}]
        }
        :param table_info:
        :return:
        """
        try:
            # for saving json
            data_list = list()
            zb_node_dict = dict()
            for zb_node in table_info['returndata']['wdnodes'][0]['nodes']:
                zb_node_dict[zb_node['code']] = {
                    'name': zb_node['cname'],
                    'des': zb_node.get('exp', '') + zb_node.get('memo', ''),
                    'unit': zb_node.get('exp', '')
                }
            for _data_info in table_info['returndata']['datanodes']:
                data_info = {
                    'id': _data_info['wds'][0]['valuecode'],
                    'mainKey': zb_key,
                    'location': reg_key,
                    'key': zb_node_dict[_data_info['wds'][0]['valuecode']]['name'],
                    'value': _data_info['data']['data'],
                    'year': _data_info['wds'][2]['valuecode'],
                    'unit': zb_node_dict[_data_info['wds'][0]['valuecode']]['unit']
                }
                self._save_data(data_info)
                data_list.append(data_info)
            # self._save_json(json.dumps(data_list, ensure_ascii=False, indent=4), '../data/%s.json'%)
            return data_list

        except Exception, e:
            logger.error('analysis table data failed for %s' % str(e))

    def _save_json(self, content, file_path):
        """
        存储json文件
        :param file_path:
        :return:
        """
        try:
            with open(file_path, 'wb') as f:
                f.write(json.dumps(content, ensure_ascii=False, indent=4))
        except Exception, e:
            logger.error('write json file failed for %s' % str(e))

    def _load_json(self, file_path):
        """
        加载json文件
        :param file_path:
        :return:
        """
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return json.loads(content)
        except Exception, e:
            logger.error('load json file failed for %s' % str(e))
            return None

    def _save_data(self, info):
        """
        保存data info
        :param info:
        :return:
        """
        try:
            if not self._check_info_exist(info['id'], info['year'], info['location']):
                logger.info('insert notice info...')
                self.mongo.collection.insert_one(info)
            else:
                logger.info('update notice info...')
                self.mongo.collection.find_one_and_update({'id': info['id'], 'year': info['year'], 'location': info['location']},
                                                          {'$set': info}
                                                          )
        except Exception, e:
            logger.error('mongoDB save data info failed for %s' % str(e))

    def _check_info_exist(self, id, year, reg):
        """
        判断info 是否存在
        :param zb_key: 指标的名称
        :param reg_key: 地点的名称
        :return: bool
        """
        try:
            result = self.mongo.collection.find({'id': id, 'year': year, 'location':reg})
            try:
                result[0]
                return True
            except:
                return False
        except Exception, e:
            logger.error('check title failed for %s'%str(e))


def trans_json_format(file_name):
    """
    修改数据json文件的存储格式
    :return:
    """
    with open(file_name, 'rb') as f:
        data_result = json.loads(f.read())
    result = list()
    for reg_info in data_result:
        reg_data = reg_info['data']
        reg_name = reg_info['location']
        _reg_info = {
            'location': reg_name,
            'data': []
        }
        key_list = list()
        _reg_data = list()
        for data_item in reg_data:
            if data_item['key'] not in key_list:
                _reg_data.append({
                    'key': data_item['key'],
                    'data': []
                })
                key_list.append(data_item['key'])
            for index, item in enumerate(_reg_data):
                if item['key'] == data_item['key']:
                    _reg_data[index]['data'].append(data_item)
                    break
                else:
                    continue
        for index, _ in enumerate(_reg_data):
            _reg_data[index]['data'] = sorted(_reg_data[index]['data'], key=lambda x: x['year'], reverse=False)

        # _reg_data = sorted(_reg_data, key=lambda x:x['year'], reverse=False)
        _reg_info['data'] = _reg_data
        result.append(_reg_info)
    with open('../data/trans.json', 'wb') as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=4))



if __name__ == '__main__':
    # data = {
    #     'm': 'QueryData',
    #     'dbcode': 'fsnd',
    #     'rowcode': 'zb',
    #     'colcode': 'sj',
    #     'wds': '[{"wdcode":"reg","valuecode":"110000"}]',
    #     'dfwds':'[{"wdcode":"zb","valuecode":"A0801"},{"wdcode":"sj","valuecode":"LAST20"}]',
    #     'k1': time.time()
    # }
    # headers = {
    #             # 'Accept': 'application/json, text/javascript, */*; q = 0.01',
    #             # 'Accept-Encoding':'gzip, deflate',
    #             # 'Accept-Language':'zh - CN, zh;q=0.8',
    #             # 'Connection':'keep - alive',
    #             # 'Cookie':'JSESSIONID = EAA6236B50B82D0BE7EEEAF435A8E99E;_trs_uv = j99acujt_6_hhro;experience = show;u = 6',
    #             # 'Host':'data.stats.gov.cn',
    #             # 'Referer':'http://data.stats.gov.cn/easyquery.htm?cn = E0103',
    #             # 'User-Agent': 'Mozilla/5.0(X11;Linux x86_64) AppleWebKit/537.36(KHTML, like Gecko) Chrome / 60.0.3112.78 Safari / 537.36',
    #             # 'X-Requested-With': 'XMLHttpRequest'
    # }
    # response = requests.get('http://data.stats.gov.cn/easyquery.htm', params=data, headers=headers)
    # result = json.loads(response.content)
    # print result
    # crawler = nationalStatistics(data_url='http://data.stats.gov.cn/easyquery.htm')
    # crawler.run()
    # with open('../data/地方财政收入.json', 'rb') as f:
    #     content = f.read()
    #     result = json.loads(content)
    #     print result
    trans_json_format('../data/地方财政支出.json')