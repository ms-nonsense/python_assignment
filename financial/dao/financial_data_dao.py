from typing import Dict

import pymysql.cursors


class FinancialDataDao(object):
    """A class to handle operations for financial_data"""

    def __init__(self, config: Dict):
        self.__connection = pymysql.connect(
            host=config['MYSQL_HOST'],
            user=config['MYSQL_USER'],
            password=config['MYSQL_PASSWORD'],
            db=config['MYSQL_DB'],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True)
        self.__cursor = self.__connection.cursor()

    def query(self, query, params):
        """ Executes query

        :param query: query to be executed
        :param params: arguments to be used in the query
        :return: the cursor which the query executed with
        """
        self.__cursor.execute(query, params)
        return self.__cursor

    def close(self):
        """ Closes the MySQL connection"""
        self.__connection.close()

    def insert_record(self, record: dict) -> None:
        """ Inserts record

        :param record: record to be inserted
        :return: None
        """
        sql = """
            INSERT IGNORE INTO financial_data (`symbol`, `date`, `open_price`, `close_price`, `volume`)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (record['symbol'], record['date'],
                  float(record['open_price']), float(record['close_price']),
                  int(record['volume']))
        return self.query(sql, params)
