from typing import Dict, Tuple

import pymysql.cursors

from financial.model.query_parameters import QueryParameters


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
            INSERT IGNORE INTO financial_data
            (`symbol`, `date`, `open_price`, `close_price`, `volume`)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (record['symbol'], record['date'],
                  float(record['open_price']), float(record['close_price']),
                  int(record['volume']))
        return self.query(sql, params)

    # FIXME: If data size is large, definitely return generator
    def fetch_record(self, query_params: QueryParameters) -> dict:
        """ Fetches records from the table that meet the conditions (if
        specified) given

        :param query_params: conditional items
        :return: dict of records
        """
        # We only fetch the columns we need so we are not going to use *.
        # This is to avoid any effects when in the future, a new column is
        # added.

        sql = """
            SELECT
                symbol
                ,date_format(date, %(date_format)s) AS date
                ,open_price
                ,close_price
                ,volume
            FROM
                financial_data
        """
        # Missing %s and %Y causes ValueError unsupported format character so
        # we'll pass date_format as parameter.
        params = {'date_format': '%Y-%m-%d'}
        conditional_clause, cond_params = self.__create_conditional_clause(
            query_params)

        if conditional_clause:
            sql += f""" WHERE {conditional_clause}"""
            params.update(cond_params)

        return self.query(sql, params=params).fetchall()

    # can be used for statistics query
    @staticmethod
    def __create_conditional_clause(
            query_params: QueryParameters) -> Tuple[str, dict]:
        """
        Create list of conditions from request parameters
        :param query_params: Query parameters passed from URL
        :return: conditional clause
        """
        conds = []
        cond_params = {}
        if query_params.symbol:
            conds.append('symbol=%(symbol)s')
            cond_params['symbol'] = query_params.symbol

        if query_params.start_date and query_params.end_date:
            conds.append('date BETWEEN %(start_date)s AND %(end_date)s')
            cond_params['start_date'] = query_params.start_date
            cond_params['end_date'] = query_params.end_date

        if query_params.start_date and not query_params.end_date:
            conds.append('date >= %(start_date)s')
            cond_params['start_date'] = query_params.start_date

        if not query_params.start_date and query_params.end_date:
            conds.append('date <= %(end_date)s')
            cond_params['end_date'] = query_params.end_date

        return ' AND '.join(conds), cond_params
