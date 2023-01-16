import unittest
import time

from .request_sending import *
from .server_port import PORT
from .user_data import *


class PassengerTest(unittest.TestCase):
    passenger_id = None
    passenger_body = None
    ride_id = None
    ride_body = None

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
            'passengers': [],
            'vehicleType': 'STANDARD',
            'babyTransport': True,
            'petTransport': True,
            'scheduleTime': None
        }
        response = send_post_request(data=request_body, url=f'http://localhost:{PORT}/api/ride', jwt=passenger)
        response_body = response.json()
        cls.ride_id = response_body['id']
        driver_login_data = {
            'email': response_body['driver']['email'],
            'password': ASSIGNED_DRIVER_PASSWORD
        }
        response = send_post_request(data=driver_login_data, url=f'http://localhost:{PORT}/api/user/login')
        driver = response.json()['accessToken']
        time.sleep(1)
        send_put_request(data=request_body, url=f'http://localhost:{PORT}/api/ride/{cls.ride_id}/accept', jwt=driver)
        time.sleep(1)
        send_put_request(data=request_body, url=f'http://localhost:{PORT}/api/ride/{cls.ride_id}/start', jwt=driver)
        time.sleep(1)
        send_put_request(data=request_body, url=f'http://localhost:{PORT}/api/ride/{cls.ride_id}/end', jwt=driver)
        time.sleep(1)
        response = send_get_request(url=f'http://localhost:{PORT}/api/ride/{cls.ride_id}', jwt=passenger)
        response_body = response.json()
        response_body.pop('status')
        cls.ride_body = response_body

    def setUp(self):
        time.sleep(1)
        self.base_path = f'http://localhost:{PORT}/api/passenger'
        passenger_login_data = {
            'email': PASSENGER_EMAIL,
            'password': PASSENGER_PASSWORD
        }
        response = send_post_request(data=passenger_login_data, url=f'http://localhost:{PORT}/api/user/login')
        self.passenger = response.json()['accessToken']
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

    def test_01_create_passenger(self):
        request_body = {
            "name": "Pera",
            "surname": "Perić",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381123123",
            "email": "pera.peric@email.com",
            "address": "Bulevar Oslobodjenja 74",
            "password": "NekaSifra123"
        }
        response = send_post_request(data=request_body, url=self.base_path)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.__class__.passenger_id = response_body['id']
        self.__class__.passenger_body = response_body
        self.assertIsNotNone(response_body['id'])
        self.assertEqual(response_body['name'], request_body['name'])
        self.assertEqual(response_body['surname'], request_body['surname'])
        self.assertEqual(response_body['telephoneNumber'], request_body['telephoneNumber'])
        self.assertEqual(response_body['email'], request_body['email'])
        self.assertEqual(response_body['address'], request_body['address'])

    def test_02_create_passenger_invalid_inputs(self):
        request_body = {
            "name": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "surname": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "profilePicture": None,
            "telephoneNumber": "abcdabcdabcdabcdabcd",
            "email": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "address": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "password": "123"
        }
        response = send_post_request(data=request_body, url=self.base_path)
        self.assertEqual(response.status_code, 400)

    def test_03_create_passenger_none_inputs(self):
        request_body = {
            "name": None,
            "surname": None,
            "profilePicture": None,
            "telephoneNumber": None,
            "email": None,
            "address": None,
            "password": None
        }
        response = send_post_request(data=request_body, url=self.base_path)
        self.assertEqual(response.status_code, 400)

    def test_04_create_passenger_email_already_exists(self):
        request_body = {
            "name": "Pera",
            "surname": "Perić",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381123123",
            "email": "pera.peric@email.com",
            "address": "Bulevar Oslobodjenja 74",
            "password": "NekaSifra123"
        }
        response = send_post_request(data=request_body, url=self.base_path)
        self.assertEqual(response.status_code, 400)
        response_body = response.json()
        self.assertEqual(response_body['message'], 'User with that email already exists!')

    def test_05_getting_passengers_unauthorized(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}', query_params=query_params)
        self.assertEqual(response.status_code, 401)

    def test_06_getting_passengers_forbidden(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}', query_params=query_params, jwt=self.driver)
        self.assertEqual(response.status_code, 403)

    def test_07_getting_passengers(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}', query_params=query_params, jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertTrue(self.__class__.passenger_body in response_body['results'])

    def test_08_activate_passenger_account(self):
        response = send_get_request(url=f'{self.base_path}/activate/{ACCOUNT_ACTIVATION_ID}')
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertEqual(response_body['message'], 'Successful account activation!')

    def test_09_activate_passenger_account_activation_expired(self):
        response = send_get_request(url=f'{self.base_path}/activate/{ACCOUNT_ACTIVATION_ID_EXPIRED}')
        self.assertEqual(response.status_code, 400)
        response_body = response.json()
        self.assertEqual(response_body['message'], 'Activation expired. Register again!')

    def test_10_activate_passenger_account_not_exist(self):
        response = send_get_request(url=f'{self.base_path}/activate/{ACCOUNT_ACTIVATION_ID_NON_EXISTING}')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Activation with entered id does not exist!')

    def test_11_passenger_details_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.passenger_id}')
        self.assertEqual(response.status_code, 401)

    def test_12_passenger_details(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.passenger_id}', jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertEqual(response_body['id'], self.__class__.passenger_id)
        self.assertEqual(response_body['name'], self.__class__.passenger_body['name'])
        self.assertEqual(response_body['surname'], self.__class__.passenger_body['surname'])
        self.assertEqual(response_body['telephoneNumber'], self.__class__.passenger_body['telephoneNumber'])
        self.assertEqual(response_body['email'], self.__class__.passenger_body['email'])
        self.assertEqual(response_body['address'], self.__class__.passenger_body['address'])

    def test_13_passenger_details_not_exist(self):
        response = send_get_request(url=f'{self.base_path}/123456', jwt=self.passenger)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Passenger does not exist!')

    def test_14_update_existing_passenger_unauthorized(self):
        request_body = {
            "name": "Pera123",
            "surname": "Perić123",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381021650650",
            "email": "pera.peric123@email.com",
            "address": "Bulevar Oslobodjenja 84",
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.passenger_id}')
        self.assertEqual(response.status_code, 401)

    def test_15_update_existing_passenger_forbidden(self):
        request_body = {
            "name": "Pera123",
            "surname": "Perić123",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381021650650",
            "email": "pera.peric123@email.com",
            "address": "Bulevar Oslobodjenja 84",
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.passenger_id}', jwt=self.driver)
        self.assertEqual(response.status_code, 403)

    def test_16_update_existing_passenger(self):
        request_body = {
            "name": "Pera123",
            "surname": "Perić123",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381021650650",
            "email": "pera.peric123@email.com",
            "address": "Bulevar Oslobodjenja 84",
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.passenger_id}', jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertIsNotNone(response_body['id'])
        self.assertEqual(response_body['name'], request_body['name'])
        self.assertEqual(response_body['surname'], request_body['surname'])
        self.assertEqual(response_body['telephoneNumber'], request_body['telephoneNumber'])
        self.assertEqual(response_body['email'], request_body['email'])
        self.assertEqual(response_body['address'], request_body['address'])

    def test_17_update_existing_passenger_invalid_inputs(self):
        request_body = {
            "name": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "surname": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "profilePicture": None,
            "telephoneNumber": "abcdabcdabcdabcdabcd",
            "email": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "address": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.passenger_id}', jwt=self.passenger)
        self.assertEqual(response.status_code, 400)

    def test_18_update_existing_passenger_none_inputs(self):
        request_body = {
            "name": None,
            "surname": None,
            "profilePicture": None,
            "telephoneNumber": None,
            "email": None,
            "address": None,
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.passenger_id}', jwt=self.passenger)
        self.assertEqual(response.status_code, 400)

    def test_19_update_non_existing_passenger(self):
        request_body = {
            "name": "Pera123",
            "surname": "Perić123",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381021650650",
            "email": "pera.peric123@email.com",
            "address": "Bulevar Oslobodjenja 84",
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/654321', jwt=self.passenger)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Passenger does not exist!')

    def test_20_getting_passenger_rides_unauthorized(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/{PASSENGER_ID}/ride', query_params=query_params)
        self.assertEqual(response.status_code, 401)

    def test_21_getting_passenger_rides_forbidden(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/{PASSENGER_ID}/ride', query_params=query_params, jwt=self.driver)
        self.assertEqual(response.status_code, 403)

    def test_22_getting_passenger_rides_not_exist(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/12345679/ride', query_params=query_params, jwt=self.passenger)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Passenger does not exist!')

    def test_23_getting_passenger_rides(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/{PASSENGER_ID}/ride', query_params=query_params, jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertEqual(self.__class__.ride_body in response_body['results'], True)
