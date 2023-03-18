"""
This python script do the following:
1. Retrieve the financial data of two given stocks (IBM, Apple Inc.) from
AlphaVantage for the most recently two weeks.
2. Process the raw API data response
3. Insert the processed data into a local database. See schema.sql for the
table's DDL
"""
import logging
from logging import config

from pathlib import Path
from typing import Dict, List
from datetime import datetime, date

import pymysql.cursors
from pymysql import Connection
import requests
from requests.exceptions import Timeout, JSONDecodeError
from dotenv import dotenv_values

from dateutil import parser
from dateutil.relativedelta import relativedelta

from financial.utilities import get_config

script_location = Path(__file__).absolute().parent
log_conf_loc = script_location / 'financial/conf/logging.conf'
config.fileConfig(log_conf_loc)

LOGGER = logging.getLogger()


# TODO: the contents of this file is getting too long. db-related file should be
#  in another file
def __create_db_conn(db_config: Dict) -> Connection:
    connection = pymysql.connect(
        host=db_config['MYSQL_HOST'],
        port=int(db_config['MYSQL_PORT']),
        user=db_config['MYSQL_USER'],
        password=db_config['MYSQL_PASSWORD'],
        db=db_config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True)
    return connection


def __close_db_conn(db_conn: Connection):
    """ Closes the MySQL connection"""
    db_conn.close()


def __insert_record(db_conn: Connection, record: dict) -> None:
    """ Inserts record into the table

    :param db_conn: database connection
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
    db_conn.cursor().execute(sql, params)


def __get_raw_financial_data(url, payload) -> Dict:
    """ Retrieve the financial data of a given stock from the given URL

    :param url: the API endpoint where we'll get the data from
    :param payload: parameters of our query
    :return: financial data in dictionary format
    """
    try:
        # setting timeout in case the server is not responding in a timely
        # manner. connect timeout = 3.0 sec, read timeout = 7.5s
        response = requests.get(url=url, params=payload, timeout=(3.0, 7.5))
        data = response.json()
        return data
    except Timeout as t:
        LOGGER.error(f'Timeout occurs. Unable to fetch data from {url}')
        raise t
    except JSONDecodeError as err:
        LOGGER.error('Failed to parse response as JSON.')
        raise err


def __process_raw_data(stock_name: str, raw_data: dict) -> list:
    """ Process raw financial data to keep details we needed.

    :param stock_name: name of stock
    :param raw_data: raw financial data of a stock
    :return: list of processed data
    """
    # if the arguments is empty, return
    if not raw_data:
        return []

    processed_result: List[dict] = []
    today = datetime.today()
    two_weeks_ago_date = __get_min_date_by_week(today, -2).date()

    # looping records from Time Series (Daily)
    for key, value in raw_data['Time Series (Daily)'].items():
        try:
            # AlphaVantage date format might change. With that thought,
            # we parse the date and change it to a format consistent
            # with this project (%Y-%m-%d)
            parsed_date = parser.parse(key).date()

            # AlphaVantage returns 1-2 months worth of data in chronological
            # order. However, we only need data from the most recent two
            # weeks. Any data outside this two-week range will be ignored.
            if __is_within_date_range(two_weeks_ago_date, today.date(),
                                      parsed_date) is False:
                return processed_result

            # making a tuple of dictionary before adding it to a list
            # because it's faster than append().
            processed_result += {
                "symbol": f"{stock_name}",
                "date": f"{parsed_date.strftime('%Y-%m-%d')}",
                "open_price": f"{value['1. open']}",
                "close_price": f"{value['4. close']}",
                "volume": f"{value['6. volume']}"
            },
        except (parser.ParserError, OverflowError):
            LOGGER.error(f'Failed to parse date of value = {key}.')
            # If the date cannot be parsed, then move to next data
            continue
    return processed_result


def __get_min_date_by_week(based_date: datetime, week_num: int) -> datetime:
    """
    Get the date 14 days before the given date.
    :param based_date: date used to calculate the relative date
    :param week_num: number of weeks
    :return: the calculated date
    """
    return based_date + relativedelta(weeks=week_num)


def __is_within_date_range(min_date: date, max_date: date,
                           target_date: date) -> bool:
    """
    Checks if the target date is between min and max date, inclusive.
    :param min_date: Minimum value of date range
    :param max_date: Max value of data range
    :param target_date: the date in question
    :return: True if the target date is within the range, otherwise, false.
    """
    return min_date <= target_date <= max_date


def start_data_retrieval() -> None:
    """ Entry point in retrieving financial data of target stocks. """
    app_config = get_config()
    stock_names = app_config['stock_name']
    api_endpoint = app_config['stocks_endpoint']
    env_vars = dotenv_values(".env")

    # We are not catching any MySQL connection exception so it will bubble up
    financial_data_dao = __create_db_conn(env_vars)

    for stock_name in stock_names:
        payload = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': stock_name,
            'interval': '60min',
            'apikey': env_vars['STOCK_ENDPOINT_API_KEY']
        }

        result = __get_raw_financial_data(api_endpoint, payload)
        for datum in __process_raw_data(stock_name, result):
            __insert_record(financial_data_dao, datum)

    __close_db_conn(financial_data_dao)


if __name__ == '__main__':
    LOGGER.info("Start data retrieval")
    start_data_retrieval()
    LOGGER.info("End data retrieval")
