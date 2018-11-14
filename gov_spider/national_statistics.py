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
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class nationalStatistics(BaseCrawler):

    def __init__(self, data_url):
        """
        城市数据爬取主函数
        :param base_url:
        """


if __name__ == '__main__':
    data = {
        'm': 'QueryData',
        'dbcode': 'fsnd',
        'rowcode': 'zb',
        'colcode': 'sj',
        'wds': '[{"wdcode":"reg","valuecode":"110000"}]',
        'dfwds':'[{"wdcode":"zb","valuecode":"A0801"},{"wdcode":"sj","valuecode":"LAST20"}]',
        'k1': time.time()
    }
    headers = {
                # 'Accept': 'application/json, text/javascript, */*; q = 0.01',
                # 'Accept-Encoding':'gzip, deflate',
                # 'Accept-Language':'zh - CN, zh;q=0.8',
                # 'Connection':'keep - alive',
                # 'Cookie':'JSESSIONID = EAA6236B50B82D0BE7EEEAF435A8E99E;_trs_uv = j99acujt_6_hhro;experience = show;u = 6',
                # 'Host':'data.stats.gov.cn',
                # 'Referer':'http://data.stats.gov.cn/easyquery.htm?cn = E0103',
                # 'User-Agent': 'Mozilla/5.0(X11;Linux x86_64) AppleWebKit/537.36(KHTML, like Gecko) Chrome / 60.0.3112.78 Safari / 537.36',
                # 'X-Requested-With': 'XMLHttpRequest'
    }
    response = requests.get('http://data.stats.gov.cn/easyquery.htm', params=data, headers=headers)
    result = json.loads(response.content)
    print result
