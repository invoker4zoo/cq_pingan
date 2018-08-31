# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: gov_finance_crawler.py
@ time: $18-8-28 下午6:12
"""
from tool.logger import logger
from tool.crawler import BaseCrawler
from bs4 import BeautifulSoup
import datetime

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class GovFinaceCrawler(BaseCrawler):

    def __init__(self):
        super(GovFinaceCrawler, self).__init__()
        self.base_url = 'http://www.mof.gov.cn/zhengwuxinxi'
        self.category = 'zhengcefabu'
        self.page = 23
        self.head = {
        'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, image / apng, * / *;q = 0.8',
        'Accept - Encoding':'gzip, deflate',
        'Accept - Language':'zh - CN, zh;q = 0.8',
        'Cache - Control':'max - age = 0',
        'Connection':'keep - alive',
        'Cookie':'_trs_uv = jkutnu3l_479_2ww8',
        'Host':'zhs.mof.gov.cn',
        # 'If - Modified - Since':'Wed, 15 Aug 2018 02:07:50 GMT',
        # 'If - None - Match':"2e19-5736fcb202980",
        'Referer':'http: // www.mof.gov.cn / index.htm',
        'Upgrade - Insecure - Requests':1,
        # 'User - Agent':'Mozilla / 5.0(X11; Linux x86_64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 60.0 .3112 .78 Safari / 537.36'
        }

    def search_title_page(self):
        """

        :return:
        """
        self.notice_link_list = list()
        self.title_base_url = self.base_url + '/' + self.category
        for page in range(0, self.page):
            if page == 0:
                url = self.title_base_url + '/' + 'index.htm'
            else:
                url = self.title_base_url + '/' + 'index_%d.htm'%page
            response = self.get(url)
            page_soup = BeautifulSoup(response, 'html5lib')
            notice_tag_list = page_soup.find_all('td', attrs={'class': 'ZITI'})
            for notice_tag in notice_tag_list:
                title = notice_tag.attrs.get('title')
                if title:
                    pass
                else:
                    logger.warning()
                notice_info_tag = notice_tag.find('a')
                link = notice_info_tag.attrs.get('href')
                if link:
                    self.notice_link_list.append(link)
                else:
                    continue
            # 间隔2秒
            time.sleep(2)


    def search_link_info(self, notice_link):
        """
        通过公告链接获取全文，下载附件
        :param notice_link:
        :return:
        """



if __name__ == '__main__':
    crawler = GovFinaceCrawler()
    crawler.search_title_page()
