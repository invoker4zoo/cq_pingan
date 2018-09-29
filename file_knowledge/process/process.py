# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: process.py
@ time: $18-9-25 下午4:34
"""
import sys
sys.path.append('..')
from tool.logger import logger
from config.config import *
import thulac
from document_extraction import main_process
from knowledge_extraction_sample import buildGraph

if __name__ == '__main__':
    logger.info('loading nlp model')
    # thunlp_model = thulac.thulac(seg_only=False, model_path=THUNLP_MODEL_PATH, \
    #                              user_dict=THUNLP_USER_DIC_PATH)
    # logger.info('begin document extraction...')
    # main_process(thunlp_model)
    logger.info('begin knowledge extraction...')
    process = buildGraph()
    process.initial()