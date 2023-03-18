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
from typing import Dict
import requests
from requests.exceptions import Timeout, JSONDecodeError
from financial.utilities import get_config

script_location = Path(__file__).absolute().parent
log_conf_loc = script_location / 'financial/conf/logging.conf'
logging.config.fileConfig(log_conf_loc)

LOGGER = logging.getLogger()


def __get_raw_financial_data(url, payload) -> Dict:
    """ Retrieve the financial data of a given stock from the given URL

    :param url: the API endpoint where we'll get the data from
    :param payload: parameters of our query
    :return: financial data in dictionary format
    """
    try:
        # setting timeout in case the server is not responding in a timely manner.
        # connect timeout = 3.0 sec, read timeout = 7.5s
        response = requests.get(url=url, params=payload, timeout=(3.0, 7.5))
        data = response.json()
        return data
    except Timeout:
        LOGGER.warning(f'Timeout occurs. Unable to fetch data from {url}')
        return {}
    except JSONDecodeError:
        LOGGER.warning('Failed to parse response as JSON.')
        return {}


def start_data_retrieval() -> None:
    """ Entry point in retrieving financial data of target stocks. """
    app_config = get_config()
    stock_names = app_config['stock_name']
    api_endpoint = app_config['stocks_endpoint']

    for stock_name in stock_names:
        payload = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': stock_name,
            'interval': '60min',
            'apikey': ''  # TODO change this later on
        }

        result = __get_raw_financial_data(api_endpoint, payload)
        print(result)


if __name__ == '__main__':
    LOGGER.info("Start data retrieval")
    start_data_retrieval()
    LOGGER.info("End data retrieval")

