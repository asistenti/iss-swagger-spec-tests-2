import unittest
import time

from .request_sending import *
from .server_port import PORT
from .user_data import *


class UnregisteredUserTest(unittest.TestCase):
    def setUp(self):
        time.sleep(1)
        self.base_path = f'http://localhost:{PORT}/api/unregisteredUser'

    def test_01_estimation_invalid_inputs(self):
        request_body = {
            'locations': [
                {
                    'departure': {
                        'address': 'Andje Rankovic 2',
                        'latitude': 91,
                        'longitude': 181
                    },
                    'destination': {
                        'address': 'Bele njive 24',
                        'latitude': -181,
                        'longitude': -91
                    }
                }
            ],
            'vehicleType': 'STANDARD123',
            'babyTransport': '123',
            'petTransport': '123',
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}')
        self.assertEqual(response.status_code, 400)

    def test_02_estimation_none_inputs(self):
        request_body = {
            'locations': [
                {
                    'departure': None,
                    'destination': None
                }
            ],
            'vehicleType': None,
            'babyTransport': None,
            'petTransport': None,
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}')
        self.assertEqual(response.status_code, 400)

    def test_03_estimation(self):
        request_body = {
            'locations': [
                {
                    'departure': {
                        'address': 'Andje Rankovic 2',
                        'latitude': 45.247309,
                        'longitude': 19.796717
                    },
                    'destination': {
                        'address': 'Bele njive 24',
                        'latitude': 45.265435,
                        'longitude': 19.847805
                    }
                }
            ],
            'vehicleType': 'STANDARD',
            'babyTransport': True,
            'petTransport': True
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}')
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertEqual('estimatedTimeInMinutes' in response_body, True)
        self.assertEqual('estimatedCost' in response_body, True)
