# coding=utf-8


import os
import random
from time import time

import requests
from flask import current_app
from flask_restful import reqparse, abort, Api, Resource

from app import api, enums

# _FAKEJSON_API_ENDPOINT = 'https://app.fakejson.com/q'
# _FAKEJSON_API_TOKEN = 'tQPCEIEG76UMGolsVx6paQ'


def _build_fakejson_request_data(response_code, original_data):
    """
    Returns a dict with valid data to use in fakeJSON queries.
    """
    return_success = response_code == 200
    request_data = {
        'token': current_app.config['FAKEJSON_API_TOKEN'],
        'data': {
            'error_code': 0 if return_success else response_code,
            'reason': 'OK' if return_success else 'Error {}'.format(response_code),
            'timestamp': 'timeNow',
            'request_data': original_data,
        }
    }
    if return_success:
        request_data['data']['cost'] = 'numberInt'
    return request_data


class CarrierMockEndpoint(api.ShippingCostEndpoint):
    """
    API endpoint logic to mock interactions with any carrier using fakeJSON.
    """

    def post(self, carrier_code):
        # Since we already verified the data, we assume is clean and complies to carrier's API
        original_data = self.request_parser.parse_args()

        # Choosing randomly if our request will succeed or not (90% chance of success)
        response_code = 200 if original_data['test_mode'] else random.choices((200, 500), weights=(0.9, 0.1), k=1)[0]

        # Hitting fakeJSON's API
        request_data = _build_fakejson_request_data(response_code, original_data)
        response = requests.post(current_app.config['FAKEJSON_API_ENDPOINT'], json=request_data, params={'x': time()})
        return response.json(), response_code


def configure_external_apis(app):
    """
    Attaches an API to the given Flask app.
    """
    api = Api(app)
    api.add_resource(CarrierMockEndpoint, '/mock/<string:carrier_code>/shippingcost')
