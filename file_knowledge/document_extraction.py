# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: document_extraction.py
@ time: $18-9-18 上午11:48
"""

import thulac
import os
from tool.logger import logger
from tool.text_rank_sentence import TextSummary4Sentence
from tool.text_rank_seg import TextSummary4Seg
from tool.trans_dic import NE_DICT, CENTER_DEPARTMENT, LOCATION_ORG_DICT
from tool.db_connector import dbConnector
from tool.es_connector import esConnector
import re

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# GOLBAL PARAMS
THUNLP_MODEL_PATH = "/home/showlove/cc/code/THULAC-Python/models"
THUNLP_USER_DIC_PATH = "/home/showlove/PycharmProjects/data_test/nlp/user_dic.txt"
STOP_WORD_DIC_PATH = "/home/showlove/PycharmProjects/data_test/nlp/stop_word_dic.txt"
FILE_PATH = '/home/showlove/cc/gov/finace/center/trans'
# 人名，地名，机构名，其他专有名词，简称，用户字典（用户字典只存放命名实体？）
SEG_TYPE_FILTER = ['np', 'ns', 'ni', 'nz', 'j', 'uw']
# mongodb config
MONGODB_SERVER = "127.0.0.1"
MONGODB_PORT = 27017
MONGODB_DB = "gov_finace"
MONGODB_COLLECTION = "center"



class documentExtraction(object):
    def __init__(self, record, nlp_model, file_name=None):
        """

        :param record: doc title location ...
        :param nlp_model:model need seg_only=False 保留词性
        """
        self.record = record
        self.model = nlp_model
        self.file_name = file_name
        self.__get_content_title()

        self.file_pattern = re.compile('《'.decode('utf-8') + u'(.*?)' + '》'.decode('utf-8'))
        self.link_pattern = re.compile('//(.*?)\.')
        self.identify_pattern = re.compile(u'.{2}〔\d+〕\d+号')

    def __get_content_title(self):
        """
        统一取出content和title，需要多次使用
        :return:
        """
        try:
            if not self.file_name:
                self.title = self.record.get('noticeTitle', '')
                self.content = self.record.get('noticeContent', '')
                self.type = 'notice'
            else:
                # 去掉文件名中的空格，文件格式转换时做了空格的消除
                self.file_name = self.__pre_deal_with_str(self.file_name)
                if len(self.file_name.split('.')) >= 2:
                    self.title = self.file_name.split('.')[-2]
                else:
                    self.title = self.file_name
                file_type = self.file_name.split('.')[-1]
                if file_type in ['xls', 'xlsx']:
                    trans_file_type = 'csv'
                else:
                    trans_file_type = 'txt'
                trans_file_name = self.file_name[: -1 * (len(file_type) + 1)] + '.' + trans_file_type
                if os.path.isfile(os.path.join(FILE_PATH, trans_file_name)):
                    logger.info('reading file %s' % trans_file_name)
                    with open(os.path.join(FILE_PATH, trans_file_name), 'r') as f:
                        self.content = f.read()
                        self.type = file_type
                else:
                    logger.warn('file %s do not have trans file' % trans_file_name)
                    self.content = ''
                    self.type = ''
        except Exception, e:
            logger.error('get content and title string failed for %s' % str(e))
            self.title = ''
            self.content = ''
            self.type = ''

    def __pre_deal_with_str(self, string):
        """
        字符串的前处理
        :param str:
        :return:
        """
        return string.replace(' ', '')

    def __find_uw_type(self, seg):
        """
        用户字典分词类型
        :param seg:
        :return:
        """
        for key, seg_list in NE_DICT.items():
            if seg in seg_list:
                return key
        return None

    def __extract_entity_from_str(self, string):
        """
        从字符串中抽取出命名实体，目前采用分词算法中的词性进行划分，后续替换为NER模型提取
        :param str:
        :return:
        """
        try:
            entity_list = list()
            string_cut = self.model.cut(string)
            for seg, seg_type in string_cut:
                if seg == '':
                    continue
                if seg_type in SEG_TYPE_FILTER:
                    if seg_type == 'uw':
                        entity_list.append((seg, self.__find_uw_type(seg)))
                    else:
                        entity_list.append((seg, seg_type))
            return entity_list

        except Exception, e:
            logger.error('extract entity failed for %s' % str(e))
            return []

    def _extract_entity_from_record(self):
        """
        从存储中提取实体
        [(seg ,seg_type),...]
        :return:
        """
        try:
            # title = self.__pre_deal_with_str(self.record.get('noticeTitle', ''))
            # content = self.__pre_deal_with_str(self.record.get('noticeContent', ''))
            title_entity = self.__extract_entity_from_str(self.__pre_deal_with_str(self.title))
            content_entity = self.__extract_entity_from_str(self.__pre_deal_with_str(self.content))
            return title_entity + content_entity
        except Exception, e:
            logger.error('extract entity from record failed for %s' % str(e))
            return []

    def _extract_filename_from_doc(self):
        """
        从中文中提取出文件名
        :return:
        """
        try:
            filename_list = list()
            # doc = self.record.get('noticeContent', '')
            for string in re.findall(self.file_pattern, self.content):
                if string not in filename_list:
                    filename_list.append(string)
            return filename_list
        except Exception, e:
            logger.error('find file name from doc failed for %s' % str(e))
            return []

    def _extract_filename_from_title(self):
        """
        从标题中提取出文件名列表
        :return:
        """
        try:
            filename_list = list()
            # doc = self.record.get('noticeTitle', '')
            for string in re.findall(self.file_pattern, self.title):
                if string not in filename_list:
                    filename_list.append(string)
            return filename_list
        except Exception, e:
            logger.error('find file name from title failed for %s' % str(e))
            return []

    def _extract_public_org_2(self):
        """
        针对中央财政部，提取二级发布部门
        位置在网址链接中http后的第一级字段
        :return:
        """
        try:
            link = self.record.get('noticeLink', '')
            link_start = re.findall(self.link_pattern, link)[0]
            second_org = CENTER_DEPARTMENT.get(link_start)
            return second_org
        except Exception, e:
            logger.error('extract public organization level 2 failed for %s' % str(e))
            return ''

    def _extract_identify_from_doc(self):
        """
        从文件正文中提取出文件标示编号，
        目前的文件编号格式为:财会〔2018〕20号
        :return:
        """
        try:
            doc = self.content
            identify_list = re.findall(self.identify_pattern, doc)
            if len(identify_list):
                return identify_list
            else:
                logger.warn('doc do not have file identify')
                return []
        except Exception, e:
            logger.error('extract file identify from doc failed for %s' % str(e))

    def _extract_keyword_from_doc(self):
        """
        提取文档关键词
        :return:
        """
        try:
            doc = self.title + self.content
            key_word_model = TextSummary4Seg(doc, 6, 0.85, 700, self.model)
            return key_word_model.top_n_seg(5)
        except Exception, e:
            logger.error('extract key word from doc failed for %s' % str(e))
            return []

    def _extract_abstract_from_doc(self, seperated = False):
        """
        提取文档摘要，目前使用抽取式，不使用生成式摘要
        :param seperated: 是否对文档内容分段进行摘要提取
        :return:
        """
        try:
            doc = self.title + self.content
            key_sentence_model = TextSummary4Sentence(doc, 700, 0.85, self.model)
            return key_sentence_model.top_n_sentence(3)
        except Exception, e:
            logger.error('extract abstract from doc failed for %s' % str(e))
            return []

    def _extract_data_from_doc(self):
        """
        抽取文章中的数据
        由于基本为文本，需要用模式匹配的方式，抽取的格式为元组
        :return:
        """
        pass

    def extract_knowledge_from_record(self):
        """
        抽取主函数
        :return:
        """
        try:
            # 数据库抽取
            entity_list = self._extract_entity_from_record()
            knowledge_body = {
                'publish_time': self.record.get('publishTime', ''),
                'publish_location': self.record.get('location', ''),
                'publish_org': LOCATION_ORG_DICT.get(self.record.get('location', ''), ''),
                'publish_org_2': self._extract_public_org_2(),
                'title': self.title,
                'category': self.record.get('category', ''),
                'classify': '',
                'content': self.content,
                'identify': self.record.get('noticeIdentify', ''),
                'content_identify': self._extract_identify_from_doc(),
                'content_attach': self.record.get('noticeAttachment', ''),
                'quote_title': self._extract_filename_from_title(),
                'quote_content': self._extract_filename_from_doc(),
                'entity_loc': [item[0] for item in entity_list if item[1] == 'ns'],
                'entity_org': [item[0] for item in entity_list if item[1] == 'ni'],
                'entity_name': [item[0] for item in entity_list if item[1] == 'np'],
                'attachment_file': self.record.get('attachmentFileList', []) if not self.file_name else [],
                'parrent_file': self.record.get('noticeTitle', '') if self.file_name else '',
                'key_word': [item[0] for item in self._extract_keyword_from_doc()] \
                    if self.type not in ['xls', 'xlsx'] else [],
                'abstract': [item[0] for item in self._extract_abstract_from_doc()] \
                    if self.type not in ['xls', 'xlsx'] else [],
                'data_key': [],
                'data': {}
            }
            return knowledge_body
        except Exception, e:
            logger.error('extract knowledge from record failed for %s' % str(e))
            return {}

if __name__ == '__main__':
    # 测试
    thunlp_model = thulac.thulac(seg_only=False, model_path=THUNLP_MODEL_PATH, \
                                 user_dict=THUNLP_USER_DIC_PATH)
    mongo = dbConnector(MONGODB_SERVER, MONGODB_PORT, MONGODB_DB, MONGODB_COLLECTION)
    es = esConnector(url='localhost:9200', index='test', doc_type='finace')
    for record in mongo.collection.find().batch_size(1):
        if not len(record.get('attachmentFileList', [])):
            document_model = documentExtraction(record, thunlp_model)
            if not es.check_info_exist(document_model.title):
                logger.info('begin extract doc %s...' % document_model.title)
                document_info = document_model.extract_knowledge_from_record()
                if len(document_info.keys()):
                    es.insert_single_info(document_info)
                else:
                    logger.warn('extract document info failed ,skip es store')
            else:
                logger.info('doc %s exist in es, skip' %document_model.title)
        else:
            document_model = documentExtraction(record, thunlp_model)
            if not es.check_info_exist(document_model.title):
                logger.info('begin extract doc %s...' % document_model.title)
                document_info = document_model.extract_knowledge_from_record()
                if len(document_info.keys()):
                    es.insert_single_info(document_info)
                else:
                    logger.warn('extract document info failed ,skip es store')
            else:
                logger.info('doc %s exist in es, skip' %document_model.title)
            for file_name in record.get('attachmentFileList', []):
                document_model = documentExtraction(record, thunlp_model, file_name=file_name)
                if not es.check_info_exist(document_model.title):
                    logger.info('begin extract doc %s...' % document_model.title)
                    document_info = document_model.extract_knowledge_from_record()
                    if len(document_info.keys()):
                        es.insert_single_info(document_info)
                    else:
                        logger.warn('extract document info failed ,skip es store')
                else:
                    logger.info('doc %s exist in es, skip' % document_model.title)