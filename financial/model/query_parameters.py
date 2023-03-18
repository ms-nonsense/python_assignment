from dataclasses import dataclass
from datetime import date

from marshmallow import Schema, fields, post_load, validate, \
    validates_schema, ValidationError
from typing import Optional, Dict


@dataclass
class QueryParameters:
    """ Dataclass to hold query parameters in a single object."""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    symbol: Optional[str] = None


class OptQueryParametersSchema(Schema):
    """ Schema to hold optional query parameters. """
    # dates not in %Y-%m-%d will be considered invalid.
    start_date = fields.Date()
    end_date = fields.Date()
    symbol = fields.Str(validate=validate.Length(min=1, max=20))

    @validates_schema
    def validate_dates(self, data, **kwargs):
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                raise ValidationError(
                    'End date should be later than start date.')

    @post_load
    def make_query_parameters(self, data: Dict, **kwargs) -> QueryParameters:
        """ Instantiate a QueryParameters object

        :param data: values
        :param kwargs: keyword arguments
        :return: QueryParameter object
        """
        start_date: Optional[date] = data.get('start_date')
        end_date: Optional[date] = data.get('end_date')
        dt_params = {
            'start_date':
            start_date.strftime('%Y-%m-%d') if start_date else None,
            'end_date': end_date.strftime('%Y-%m-%d') if end_date else None
        }

        return QueryParameters(**dt_params, symbol=data.get('symbol'))
