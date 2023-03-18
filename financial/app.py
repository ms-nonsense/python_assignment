import math
from typing import Tuple

from werkzeug.datastructures import MultiDict

from flask import request, Flask, jsonify
from marshmallow import EXCLUDE, ValidationError
from dotenv import dotenv_values

from financial.dao.financial_data_dao import FinancialDataDao
from financial.model.query_parameters import OptQueryParametersSchema

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/')
def index():
    return jsonify({"data": [], "info": {"error": ""}})


@app.errorhandler(404)
def resource_not_found(e):
    """ return 404 and a message for pages not found """
    return jsonify({"data": [], "info": {"error": str(e)}}), 404


@app.route('/api/financial_data')
def financial_data():

    args_dict = request.args.to_dict()
    limit, page = __get_request_page_params(request.args)
    size = 0
    env_vars = dotenv_values(".env")
    print(env_vars)

    try:
        # Parameters not stated in specification are excluded.
        request_params = OptQueryParametersSchema().load(args_dict,
                                                         unknown=EXCLUDE)

        financial_data_dao = FinancialDataDao(env_vars)
        result = financial_data_dao.fetch_record(request_params)

        res = result[(page - 1) * limit:page * limit]
        size = size + len(result)

        return jsonify({
            "data": [p for p in res],
            "pagination": __do_pagination(size, page, limit),
            "info": {
                "error": ""
            }
        })
    except ValidationError as e:
        return jsonify({
            "data": [],
            "pagination": __do_pagination(size, page, limit),
            "info": {
                "error": e.messages
            }
        })


@app.errorhandler(500)
def internal_server_error(e):
    """Return JSON instead of HTML for HTTP errors."""
    return jsonify({"data": [], "info": {"error": str(e)}}), 500


def __do_pagination(data_size: int, offset_page: int,
                    record_per_page: int) -> dict:
    """
    Create dict of pagination info
    :param data_size: size of records
    :param offset_page: offset page num
    :param record_per_page: num of records per page
    :return: dict that holds pagination info
    """
    return {
        "count": data_size,
        "page": offset_page,
        "limit": record_per_page,
        "pages": math.ceil(data_size / record_per_page)
    }


def __get_request_page_params(request_params: MultiDict) -> Tuple[int, int]:
    """
    Get pagination-related query parameters
    :param request_params: query parameters of URL
    :return: tuple of limit and offset_page
    """
    limit = request_params.get('limit', type=int, default=5)
    if limit < 0 or limit == 0:
        limit = 5

    page = request_params.get('page', type=int, default=1)
    if page < 0:
        page = 1

    return limit, page


# TODO:
#  - test

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
