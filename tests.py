# coding=utf-8


import json
import os
import random
import unittest

from app import create_app
from app.enums import BoxType, Priority
from app.models import db
from config import Env, load_initial_db_data


class _CommonLogicTestCase(unittest.TestCase):
    """
    Class to encapsultae some common logic for all test cases.
    """

    def setUp(self):
        self.app = create_app(Env.TESTING)
        self.client = self.app.test_client()
        self.carrier_endpoint = '/api/shipping/carriers'
        self.shipping_cost_endpoint = '/api/shipping/costs'
        with self.app.app_context():
            db.create_all()
            load_initial_db_data(self.app, db)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


class CarriersEndpointTestCase(_CommonLogicTestCase):
    """
    Test cases for the carrier API endpoint.
    """

    def test_http_methods(self):
        # Checking allowed methods
        response = self.client.get(self.carrier_endpoint)
        response_json = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_json), 2)  # We have 2 carriers in DB
        # Checking unallowed HTTP methods
        self.assertEqual(self.client.post(self.carrier_endpoint).status_code, 405)
        self.assertEqual(self.client.put(self.carrier_endpoint).status_code, 405)
        self.assertEqual(self.client.patch(self.carrier_endpoint).status_code, 405)
        self.assertEqual(self.client.delete(self.carrier_endpoint).status_code, 405)

    def test_retrieve(self):
        response = self.client.get(self.carrier_endpoint)
        response_json = response.get_json()
        self.assertEqual(response.status_code, 200)
        for expected_attr in ('code', 'name', 'shipment_methods', 'enabled'):
            self.assertIn(expected_attr, response_json[0])


class ShippingCostsEndpointTestCase(_CommonLogicTestCase):
    """
    Test cases for the shipping cost API endpoint.
    """

    def test_http_methods(self):
        # Testing allowed methods
        response = self.client.post(self.shipping_cost_endpoint)
        response_json = response.get_json()
        self.assertEqual(response.status_code, 400)  # No data to return, empty requests are not allowed
        self.assertEqual(len(response_json['message']), 4)  # 4 missing params
        # Testing unallowed methods
        self.assertEqual(self.client.get(self.shipping_cost_endpoint).status_code, 405)
        self.assertEqual(self.client.put(self.shipping_cost_endpoint).status_code, 405)
        self.assertEqual(self.client.patch(self.shipping_cost_endpoint).status_code, 405)
        self.assertEqual(self.client.delete(self.shipping_cost_endpoint).status_code, 405)

    def test_create(self):
        # Testing happy path
        request_data = {
            'address': '123 Fake St, Springfield',
            'weight': 33,
            'priority': Priority.ONE.value,
            'box_type': BoxType.MEDIUM.value,
            'test_mode': True,
        }
        response = self.client.post(self.shipping_cost_endpoint, json=request_data)
        response_json = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response_json))
        for expected_attr in ('carrier', 'error', 'cost'):
            self.assertIn(expected_attr, response_json[0])
        self.assertEqual(response_json[0]['error'], '')
        self.assertEqual(type(response_json[0]['cost']), int)

        # Testing different combinations of bad input data
        malformed_request_data_1 = {  # Missing data
            'address': '123 Fake St, Springfield',
            'weight': 33,
            'test_mode': True,
        }
        malformed_request_data_2 = {  # Invalid data type for 'weight'
            'address': '123 Fake St, Springfield',
            'weight': 'ASD',
            'priority': Priority.ONE.value,
            'box_type': BoxType.MEDIUM.value,
            'test_mode': True,
        }
        malformed_request_data_3 = {  # Invalid value for 'priority'
            'address': '123 Fake St, Springfield',
            'weight': 33,
            'priority': 7,
            'box_type': BoxType.MEDIUM.value,
            'test_mode': True,
        }
        response_with_error_1 = self.client.post(self.shipping_cost_endpoint, json=malformed_request_data_1)
        response_with_error_2 = self.client.post(self.shipping_cost_endpoint, json=malformed_request_data_2)
        response_with_error_3 = self.client.post(self.shipping_cost_endpoint, json=malformed_request_data_3)
        self.assertEqual(response_with_error_1.status_code, 400)
        self.assertEqual(response_with_error_2.status_code, 400)
        self.assertEqual(response_with_error_3.status_code, 400)
        (self.assertIn(x, response_with_error_1.get_json()) for x in ('priority', 'box_type'))
        (self.assertIn(x, response_with_error_2.get_json()) for x in ('weight'))
        (self.assertIn(x, response_with_error_1.get_json()) for x in ('priority'))


if __name__ == '__main__':
    unittest.main()