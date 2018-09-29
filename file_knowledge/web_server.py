# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: web_server.py
@ time: $18-9-25 下午6:25
"""

import tornado.ioloop
import tornado.web
from handler import *
from tool.logger import logger

HandlerList = [
    (r"/main", MainSearchHandler),
    (r"/search/query", QuerySearchHandler),
    (r"/search/id", IdSearchHandler),
]

if __name__ == '__main__':
    application = tornado.web.Application(HandlerList)
    serverPort = 8080
    application.listen(serverPort)
    logger.info('server start at port %d'%serverPort
                )
    tornado.ioloop.IOLoop.instance().start()
