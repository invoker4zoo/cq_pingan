# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: neo_connector.py
@ time: $18-9-19 下午5:13
"""
from neo4j.v1 import GraphDatabase
from logger import logger


class Neo4jHandler:
    """
    Handler of graph database Neo4j reading and writing.
    """
    def __init__(self, driver):
        """
        Get Neo4j server driver.
        :param driver: driver object
            A driver object holds the detail of a Neo4j database including server URIs, credentials and other configuration, see
            " http://neo4j.com/docs/api/python-driver/current/driver.html ".
        """
        self.driver = driver

    def __repr__(self):
        printer = 'o(>﹏<)o ......Neo4j old driver "{0}" carry me fly...... o(^o^)o'.format(self.driver)
        return printer

    def listreader(self, cypher, keys):
        """
        Read data from Neo4j in specified cypher.
        Read and parse data straightly from cypher field result.
        :param cypher: string
            Valid query cypher statement.
        :param keys: list
            Cypher query columns to return.
        :return: list
            Each returned record constructs a list and stored in a big list, [[...], [...], ...].
        """
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                data = []
                result = tx.run(cypher)
                for record in result:
                    rows = []
                    for key in keys:
                        rows.append(record[key])
                    data.append(rows)
                return data

    def dictreader(self, cypher):
        """
        Read data from Neo4j in specified cypher.
        The function depends on constructing dict method of dict(key = value) and any error may occur if the "key" is invalid to Python.
        you can choose function dictreaderopted() below to read data by hand(via the args "keys").
        :param cypher: string
            Valid query cypher statement.
        :return: list
            Each returned record constructs a dict in "key : value" pairs and stored in a big list, [{...}, {...}, ...].
        """
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                data = []
                for record in tx.run(cypher).records():
                    item = {}
                    for args in str(record).split('>')[0].split()[1:]:
                        exec "item.update(dict({0}))".format(args)
                    data.append(item)
                return data

    def dictreaderopted(self, cypher, keys=None):
        """
        Optimized function of dictreader().
        Read and parse data straightly from cypher field result.
        :param cypher: string
            Valid query cypher statement.
        :param keys: list, default : none(call dictreader())
            Cypher query columns to return.
        :return: list.
            Each returned record constructs an dict in "key : value" pairs and stored in a list, [{...}, {...}, ...].
        """
        if not keys:
            return self.dictreader(cypher)
        else:
            with self.driver.session() as session:
                with session.begin_transaction() as tx:
                    data = []
                    result = tx.run(cypher)
                    for record in result:
                        item = {}
                        for key in keys:
                            item.update({key : record[key]})
                        data.append(item)
                    return data

    def cypherexecuter(self, cypher):
        """
        Execute manipulation into Neo4j in specified cypher.
        :param cypher: string
            Valid handle cypher statement.
        :return: none.
        """
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                tx.run(cypher)
        session.close()


class Neo4jConnector(object):

    def __init__(self, url, author, password):
        super(Neo4jConnector, self).__init__()
        self.url = url
        self.author = author
        self.password = password
        self.driver = GraphDatabase(self.url, auth=(self.author, self.password))
        self.neo4j_db = Neo4jHandler(self.driver)