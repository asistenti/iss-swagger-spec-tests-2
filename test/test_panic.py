import unittest
import time

from .request_sending import *
from .server_port import PORT
from .user_data import *


class PanicTest(unittest.TestCase):
    panic_id = None
    panic_body = None

    @classmethod
    def setUpClass(cls):
        passenger_login_data = {
            'email': PASSENGER_EMAIL,
            'password': PASSENGER_PASSWORD
        }
        response = send_post_request(data=passenger_login_data, url=f'http://localhost:{PORT}/api/user/login')
        passenger = response.json()['accessToken']
        time.sleep(1)
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
            'passengers': [
                {
                    'id': PASSENGER_ATTACHED_TO_RIDE_ID,
                    'email': PASSENGER_ATTACHED_TO_RIDE_EMAIL
                }
            ],
            'vehicleType': 'STANDARD',
            'babyTransport': True,
            'petTransport': True,
            'scheduleTime': None
        }
        response = send_post_request(data=request_body, url=f'http://localhost:{PORT}/api/ride', jwt=passenger)
        response_body = response.json()
        ride_id = response_body['id']
        driver_login_data = {
            'email': response_body['driver']['email'],
            'password': ASSIGNED_DRIVER_PASSWORD
        }
        response = send_post_request(data=driver_login_data, url=f'http://localhost:{PORT}/api/user/login')
        driver = response.json()['accessToken']
        time.sleep(1)
        send_put_request(data=request_body, url=f'http://localhost:{PORT}/api/ride/{ride_id}/accept', jwt=driver)
        time.sleep(1)
        send_put_request(data=request_body, url=f'http://localhost:{PORT}/api/ride/{ride_id}/start', jwt=driver)
        time.sleep(1)
        request_body = {
            'reason': 'Some reason'
        }
        response = send_put_request(data=request_body, url=f'http://localhost:{PORT}/api/ride/{ride_id}/panic', jwt=passenger)
        response_body = response.json()
        cls.panic_id = response_body['id']
        cls.panic_body = response_body

    def setUp(self):
        time.sleep(1)
        self.base_path = f'http://localhost:{PORT}/api/panic'
        driver_login_data = {
            'email': DRIVER_EMAIL,
            'password': DRIVER_PASSWORD
        }
        response = send_post_request(data=driver_login_data, url=f'http://localhost:{PORT}/api/user/login')
        self.driver = response.json()['accessToken']
        admin_login_data = {
            'email': ADMIN_EMAIL,
            'password': ADMIN_PASSWORD
        }
        response = send_post_request(data=admin_login_data, url=f'http://localhost:{PORT}/api/user/login')
        self.admin = response.json()['accessToken']

    def test_01_panic_unauthorized(self):
        query_params = {
            'page': 1,
            'size': 1000,
        }
        response = send_get_request(query_params=query_params, url=f'{self.base_path}')
        self.assertEqual(response.status_code, 401)

    def test_02_panic_forbidden(self):
        query_params = {
            'page': 1,
            'size': 1000,
        }
        response = send_get_request(query_params=query_params, url=f'{self.base_path}', jwt=self.driver)
        self.assertEqual(response.status_code, 403)

    def test_03_panic(self):
        query_params = {
            'page': 1,
            'size': 1000,
        }
        response = send_get_request(query_params=query_params, url=f'{self.base_path}', jwt=self.admin)
        response_body = response.json()
        self.assertEqual(self.__class__.panic_body in response_body['results'], True)    
