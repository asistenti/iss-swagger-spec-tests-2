import unittest
import time

from .request_sending import *
from .server_port import PORT
from .user_data import *


class VehicleTest(unittest.TestCase):
    vehicle_id = None

    @classmethod
    def setUpClass(cls):
        driver_login_data = {
            'email': DRIVER_EMAIL,
            'password': DRIVER_PASSWORD
        }
        response = send_post_request(data=driver_login_data, url=f'http://localhost:{PORT}/api/user/login')
        driver = response.json()['accessToken']
        time.sleep(1)
        response = send_get_request(url=f'http://localhost:{PORT}/api/driver/{DRIVER_ID}/vehicle', jwt=driver)
        response_body = response.json()
        cls.vehicle_id = response_body['id']

    def setUp(self):
        time.sleep(1)
        self.base_path = f'http://localhost:{PORT}/api/vehicle'
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

    def test_01_update_vehicle_location_unauthorized(self):
        request_body = {
            'address': 'Neka adresa',
            'latitude': 45.261421,
            'longitude': 19.823026
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.vehicle_id}/location')
        self.assertEqual(response.status_code, 401)

    def test_02_update_vehicle_location_forbidden(self):
        request_body = {
            'address': 'Neka adresa',
            'latitude': 45.261421,
            'longitude': 19.823026
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.vehicle_id}/location', jwt=self.admin)
        self.assertEqual(response.status_code, 403)

    def test_03_update_vehicle_invalid_input(self):
        request_body = {
            'address': 'Neka adresa',
            'latitude': 91,
            'longitude': -181
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.vehicle_id}/location', jwt=self.driver)
        self.assertEqual(response.status_code, 400)

    def test_04_update_vehicle_none_inputs(self):
        request_body = {
            'address': None,
            'latitude': None,
            'longitude': None
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.vehicle_id}/location', jwt=self.driver)
        self.assertEqual(response.status_code, 400)

    def test_05_update_vehicle_not_exist(self):
        request_body = {
            'address': 'Neka adresa',
            'latitude': 45.261421,
            'longitude': 19.823026
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/1234567/location', jwt=self.driver)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Vehicle does not exist!')

    def test_06_update_vehicle_location(self):
        request_body = {
            'address': 'Neka adresa',
            'latitude': 45.261421,
            'longitude': 19.823026
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.vehicle_id}/location', jwt=self.driver)
        self.assertEqual(response.status_code, 204)
