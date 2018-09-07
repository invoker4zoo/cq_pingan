# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: file_trans_script.py
@ time: $18-9-4 下午6:12
"""
from tool.db_connector import dbConnector
from tool.logger import logger
import os
import sys

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

# global params
SAVING_PATH = '/home/showlove/cc/gov/finace/center'
MONGODB_SERVER = "127.0.0.1"
MONGODB_PORT = 27017
MONGODB_DB = "gov_finace"
MONGODB_COLLECTION = "center"



def trans_file_from_db(trans_path):
    """

    :return:
    """
    try:
        mongo_db = dbConnector(MONGODB_SERVER, MONGODB_PORT, MONGODB_DB, MONGODB_COLLECTION)
        # 进入文件存储目录
        # os.system('cd %s' % SAVING_PATH)
        path_command = 'cd %s &&' % SAVING_PATH
        failed_list = list()
        for record in mongo_db.collection.find():
            file_list = record.get('attachmentFileList', [])
            for file_name in file_list:
                logger.info('begin to trans file %s' % file_name)
                # file name has space string , failed with shell command
                # remind with mongoDB attachment file list link
                if ' ' in file_name:
                    logger.info('file name has space string, trans file name')
                    os.system(path_command + "mv '%s' %s" % (file_name, file_name.replace(' ', '')))
                    file_name = file_name.replace(' ', '')
                base_name = file_name[:(len(file_name.split('.')[-1]) + 1) * -1]
                if file_name.endswith('.doc') or file_name.endswith('.docx'):
                    os.system(path_command + 'unoconv -f txt %s' % file_name)
                    os.system(path_command + 'mv %s.txt %s' % (base_name, trans_path))
                elif file_name.endswith('.xls') or file_name.endswith('.xlsx'):
                    os.system(path_command + 'unoconv -f csv %s' % file_name)
                    os.system(path_command + 'mv %s.csv %s' % (base_name, trans_path))
                elif file_name.endswith('.pdf'):
                    os.system(path_command + 'pdftotext -nopgbrk %s %s/%s.txt' % (file_name, trans_path, base_name))
                # 压缩文件类型不齐全
                # 目前包括 rar zip gz
                elif file_name.endswith('.rar') or file_name.endswith('.zip') or file_name.endswith('.gz'):
                    pass
                else:
                    logger.warn('file type is not recognized; file name is %s'%file_name)
                    # trying trans doc/docx file
                    logger.info('trying trans file with unconv txt')
                    result = os.system(path_command + 'unoconv -f txt %s' % file_name)
                    if not result:
                        os.system(path_command + 'mv %s.txt %s' % (base_name, trans_path))
                        continue
                    else:
                        logger.warn('trans file with unconv txt failed')
                    # trying trans xls/xlsx file
                    logger.info('trying trans file with unconv csv')
                    result = os.system(path_command + 'unoconv -f csv %s' % file_name)
                    if not result:
                        os.system(path_command + 'mv %s.csv %s' % (base_name, trans_path))
                        continue
                    else:
                        logger.warn('trans file with unconv csv failed')
                    # trying trans pdf file
                    logger.info('trying trans file with pdftotext')
                    result = os.system(path_command + 'pdftotext -pgnobrk %s %s/%s.txt' % (file_name, trans_path, base_name))
                    if not result:
                        continue
                    else:
                        logger.warn('trans file with pdftotext failed')
                    failed_list.append(file_name)
        # 打印无法转换的文件名称
        for file_name in failed_list:
            print file_name
    except Exception, e:
        logger.error('file trans failed for %s' % str(e))


def trans_file_from_path(trans_path, file_path):
    """

    :param trans_path:
    :param file_path:
    :return:
    """


if __name__ == '__main__':
    trans_file_from_db('/home/showlove/cc/gov/finace/center/trans')