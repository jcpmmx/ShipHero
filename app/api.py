# coding=utf-8


import os
import random

import requests
from flask import current_app
from flask_restful import fields, reqparse, Api, Resource, abort, marshal_with

from app.enums import BoxType, Priority
from app.models import Carrier
from config import Env


class CarriersEndpoint(Resource):
    """
    API endpoint to get all supported carriers.
    """
    _RESPONSE_FIELDS = {
        'code': fields.String(attribute='code'),
        'name': fields.String,
        'shipment_methods': fields.Raw,
        'enabled': fields.Boolean,
    }

    @marshal_with(_RESPONSE_FIELDS)
    def get(self):
        return Carrier.get_all()


class ShippingCostsEndpoint(Resource):
    """
    API endpoint to get the shipping cost of a given package (as described by its address, weight, priority anf box 
    type) for all available carriers.
    """
    request_parser = reqparse.RequestParser(bundle_errors=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_parser.add_argument(
            'address', type=str, required=True, help='Destination to calculate shipment costs for'
        )
        self.request_parser.add_argument('weight', type=int, required=True, help='Weight of the package in lb')
        self.request_parser.add_argument(
            'priority', type=int, required=True, choices=Priority.choices(), help='Valid values: 1 (top) to 5 (least)'
        )
        self.request_parser.add_argument(
            'box_type', type=str, required=True, choices=BoxType.choices(), help='Valid values: small, medium, big'
        )
        # To disable self._verify_data()'s randomness so HTTP 400 is not raised
        self.request_parser.add_argument('test_mode', type=bool, default=False)

    def post(self):
        response_data = []
        request_data = self.request_parser.parse_args()
        self._verify_data(request_data)

        # Querying all carriers available
        for carrier in Carrier.get_all_enabled():
            carrier_api_endpoint_url = carrier.api_endpoint_url

            # Small hack: using Flask's test client for our mocked carrier APIs, thus making requests from localhost and
            # test cases succeed. Best approach is pointing to real APIs and mocking responses in test cases.
            response = current_app.test_client().post(carrier.api_endpoint_url, json=request_data)
            response_data.append(self._handle_carrier_response(carrier, response))

        return response_data, 200

    def _verify_data(self, data):
        """
        Verifies if the request data is OK. If not, aborts with HTTP 400.
        """
        # Example checks:
        # - If the address is valid in format and has coverage
        # - If the weight makes sense for the type of box selected
        # For now, it's just gonna abort randomly (70% chance of success)
        if not data['test_mode'] and not random.choices((0, 1), weights=(0.3, 0.7), k=1)[0]:
            abort(400, message='Shame! http://weknowmemes.com/wp-content/uploads/2013/09/boo-bitch-aaron-paul-gif.png')

    def _handle_carrier_response(self, carrier, response):
        """
        Method that takes the raw response from carriers' APIs and returns a dict with proper data to our API users.

        Note that response is a Flask's Response object.
        """
        error_message = ''
        carrier_cost = -1
        if response.status_code == 200:
            # We're assuming their response is consistent
            carrier_cost = response.get_json()['cost']

        # Error from carrier API
        elif response.status_code == 404 or response.status_code >= 500:
            # In here, we would handle the carriers' API response accordingly (e.g. logging, email notification, ...)
            error_message = 'Blame {}! https://memegenerator.net/img/instances/44786501.jpg'.format(carrier.name)
        # Unexpected error
        else:
            error_message = "Whoops, our mistake! https://i.imgur.com/NAJE0d0.png"

        return {
            'carrier': carrier.code,
            'error': error_message,
            'cost': carrier_cost,
        }


def configure_api(app):
    """
    Attaches an API to the given Flask app.
    """
    api = Api(app)
    api.add_resource(CarriersEndpoint, '/api/shipping/carriers')
    api.add_resource(ShippingCostsEndpoint, '/api/shipping/costs')
