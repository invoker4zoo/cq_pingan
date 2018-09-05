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
from tool.db_connector import dbConnector
import datetime
import re
import time
import os


import sys
reload(sys)
sys.setdefaultencoding("utf-8")

# global params
SAVING_PATH = '/home/showlove/cc/gov/finace/center'
MONGODB_SERVER = "127.0.0.1"
MONGODB_PORT = 27017
MONGODB_DB = "gov_finace"
MONGODB_COLLECTION = "center"


class GovFinaceCrawler(BaseCrawler):

    def __init__(self, base_url, category, location, page):
        super(GovFinaceCrawler, self).__init__()
        self.base_url = base_url
        self.category = category
        self.location = location
        self.page = page
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
        self.mongo = dbConnector(MONGODB_SERVER, MONGODB_PORT, MONGODB_DB, MONGODB_COLLECTION)

    def _get_tag_string(self, tag):
        """
        读取一个tag中的所有字符串
        :param tag:
        :return:
        """
        des = ''
        if tag.string:
            return tag.string
        else:
            for str in tag.strings:
                des += str
        return des

    def save_attachement_file(self, attachment_file_link, attachment_file_name):
        """
        保存附件文件
        :param attachment_file_link:
        :return:
        """
        try:
            response = self.get(attachment_file_link)
            with open(os.path.join(SAVING_PATH, attachment_file_name), 'wb') as f:
                logger.info('saving file %s' % attachment_file_name)
                f.write(response)
        except Exception, e:
            logger.error('saving attachment file failed for %s' % str(e))

    def save_notice_info(self, notice_info):
        """

        :param notice_info:
        :return:
        """
        try:
            logger.info('insert notice info...')
            self.mongo.collection.insert_one(notice_info)
        except Exception, e:
            logger.error('mongoDB insert notice info failed for %s'%str(e))

    def _search_time_from_title(self, title):
        """

        :param title:
        :return:
        """
        try:
            pattern = re.compile('（'.decode('utf-8') + u'(.*)' + '）'.decode('utf-8'))
            for str in re.findall(pattern, title):
                try:
                    datetime.datetime.strptime(str, '%Y-%m-%d')
                    return str
                except:
                    continue
            logger.warn('do not find time str..')
            return ''
        except Exception, e:
            logger.error('searching time string failed for %s'%str(e))
            return ''

    def _check_info_exist(self, title):
        """
        判断 title 的信息是否已经在数据库中
        :param title:
        :return:
        """
        try:
            result = self.mongo.collection.find({'noticeTitle': title})
            try:
                result[0]
                return True
            except:
                return False
        except Exception, e:
            logger.error('check title failed for %s'%str(e))

    def run(self):
        """
        """
        logger.info('begin crawler..')
        try:
            self._run()
        except Exception, e:
            logger.error('star crawler failed for %s, stop crawler'%str(e))
            sys.exit(1)

    def _run(self):
        """
        启动爬虫主函数
        :return:
        """
        self.notice_link_list = list()
        self.title_base_url = self.base_url + '/' + self.category
        for page in range(0, self.page):
            if page == 0:
                url = self.title_base_url + '/' + 'index.htm'
            else:
                url = self.title_base_url + '/' + 'index_%d.htm'%page
            logger.info('searching gov finance notice link on page %d'%(page + 1))
            response = self.get(url)
            page_soup = BeautifulSoup(response, 'html5lib')
            # debug 2018-9-5
            # 财经视点栏目的tag class名字与其他栏目的tag class不一致
            if self.category == 'caijingshidian':
                notice_tag_list = page_soup.find_all('td', attrs={'class': 'xiaxu'})
            else:
                notice_tag_list = page_soup.find_all('td', attrs={'class': 'ZITI'})
            for notice_tag in notice_tag_list:
                title = notice_tag.attrs.get('title')
                time_str = self._search_time_from_title(title)
                logger.info('notice publish time is %s'%time_str)
                if title:
                    pass
                else:
                    logger.warning('searching notice title failed')
                    continue
                notice_info_tag = notice_tag.find('a')
                link = notice_info_tag.attrs.get('href')
                if link:
                    logger.info('searching notice info for %s' % title)
                    self.notice_link_list.append(link)
                    link_info, is_exist = self.search_link_info(link)
                    if link_info and not is_exist:
                        link_info['publishTime'] = time_str
                        self.save_notice_info(link_info)
                    elif is_exist:
                        logger.info('link info is existed')
                        continue
                    else:
                        logger.warn('searching link info failed')
                else:
                    logger.warning('get notice link failed for %s' % title)
                # 间隔5秒
                logger.info('crawler sleeping for 5s...')
                time.sleep(5)
            # 间隔2秒
            logger.info('crawler sleeping for 2s...')
            time.sleep(2)

    def search_link_info(self, notice_link):
        """
        通过公告链接获取全文，下载附件
        :param notice_link:
        :return:
        """
        try:
            if notice_link.startswith('http'):
                pass
            else:
                notice_link = self.title_base_url + notice_link[1:]
            # generate for attachment file url
            notice_baseurl = notice_link[0: (len(notice_link.split('/')[-1]) + 1) * -1]

            response = self.get(notice_link)
            notice_soup = BeautifulSoup(response, 'html5lib')
            title_tag = notice_soup.find('td', attrs={'class': 'font_biao1'})
            main_tag = notice_soup.find('div', attrs={'class': 'TRS_Editor'})
            attachment_tag = notice_soup.find('span', attrs={'id': 'appendix'})
            title = self._get_tag_string(title_tag).strip()
            if self._check_info_exist(title):
                return None, True
            logger.info('notice title is %s'% title)
            # notice doc search
            doc_tag_list = main_tag.find_all('p')
            doc_content = ''
            doc_identify = ''
            doc_attachment = ''
            # 原始网站中的公告内容使用p tag进行换行，所以在存入content的时候需要加入换行符
            # 2018-9-4 cc
            for doc_tag in doc_tag_list:
                if doc_tag.attrs.get('align') == 'center':
                    doc_content += self._get_tag_string(doc_tag) + '\n'
                    doc_identify += self._get_tag_string(doc_tag).strip()
                # elif doc_tag.attrs.get('align') == 'justify':
                #     doc_content += self._get_tag_string(doc_tag)
                elif doc_tag.attrs.get('align') == 'right':
                    doc_content += self._get_tag_string(doc_tag) + '\n'
                    doc_attachment += self._get_tag_string(doc_tag).strip() + '\n'
                else:
                    doc_content += self._get_tag_string(doc_tag) + '\n'

            # attachment file search
            attachment_file_list = attachment_tag.find_all('a')
            attachment_file_name_list = list()
            attachment_file_link_list = list()
            # 部分文件的后缀名不在附件名中出现需要从链接中取出后缀名
            # 2018-9-5 未修改
            for attachment_file_tag in attachment_file_list:
                attachment_file_name = ''
                _attachment_link = attachment_file_tag.attrs.get('href')
                _attachment_file_name = self._get_tag_string(attachment_file_tag).strip()
                if ':' in _attachment_file_name:
                    attachment_file_name = _attachment_file_name.split(':')[-1]
                elif '：' in _attachment_file_name:
                    attachment_file_name = _attachment_file_name.split('：')[-1]
                else:
                    attachment_file_name = _attachment_file_name
                # _attachment_link format './P020180828399303596996.pdf'
                attachment_file_link = notice_baseurl + _attachment_link[1:]
                # saving file
                self.save_attachement_file(attachment_file_link, attachment_file_name)
                attachment_file_name_list.append(attachment_file_name)
                attachment_file_link_list.append(attachment_file_link)
            return {
                'noticeTitle': title,
                'noticeContent': doc_content,
                'noticeIdentify': doc_identify,
                'noticeAttachment': doc_attachment,
                'noticeLink': notice_link,
                'attachmentFileList': attachment_file_name_list,
                'attachmentLinkList': attachment_file_link_list,
                'category': self.category,
                'filePath': SAVING_PATH,
                'location': self.location
            }, False
        except Exception, e:
            logger.error('searching link info failed for %s'% str(e))
            return None, False


if __name__ == '__main__':
    # # 中央财政部政策发布频道
    # base_url = 'http://www.mof.gov.cn/zhengwuxinxi'
    # category = 'zhengcefabu'
    # location = 'center'
    # page = 23
    # crawler = GovFinaceCrawler(base_url, category, location, page)
    # crawler.run()
    # # 中央财政部政策解读频道
    # base_url = 'http://www.mof.gov.cn/zhengwuxinxi'
    # category = 'zhengcejiedu'
    # location = 'center'
    # page = 17
    # crawler = GovFinaceCrawler(base_url, category, location, page)
    # crawler.run()
    # # 中央财政部财政数据频道
    # base_url = 'http://www.mof.gov.cn/zhengwuxinxi'
    # category = 'caizhengshuju'
    # location = 'center'
    # page = 22
    # crawler = GovFinaceCrawler(base_url, category, location, page)
    # crawler.run()
    # 中央财政部财经视点频道
    base_url = 'http://www.mof.gov.cn/zhengwuxinxi'
    category = 'caijingshidian'
    location = 'center'
    page = 15
    crawler = GovFinaceCrawler(base_url, category, location, page)
    crawler.run()