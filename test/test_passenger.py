import unittest
import time

from .request_sending import send_post_request, send_get_request, send_put_request
from .server_port import PORT
from .user_data import *


class PassengerTest(unittest.TestCase):
    passenger_id = None
    passenger_body = None

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
        

    def test_01_create_passenger_unauthorized(self):
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
        self.assertEqual(response.status_code, 401)

    def test_02_create_passenger_forbidden(self):
        request_body = {
            "name": "Pera",
            "surname": "Perić",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381123123",
            "email": "pera.peric@email.com",
            "address": "Bulevar Oslobodjenja 74",
            "password": "NekaSifra123"
        }
        response = send_post_request(data=request_body, url=self.base_path, jwt=self.driver)
        self.assertEqual(response.status_code, 403)

    def test_03_create_passenger(self):
        request_body = {
            "name": "Pera",
            "surname": "Perić",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381123123",
            "email": "pera.peric@email.com",
            "address": "Bulevar Oslobodjenja 74",
            "password": "NekaSifra123"
        }
        response = send_post_request(data=request_body, url=self.base_path, jwt=self.passenger)
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

    def test_04_create_passenger_invalid_inputs(self):
        request_body = {
            "name": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "surname": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "profilePicture": None,
            "telephoneNumber": "abcdabcdabcdabcdabcd",
            "email": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "address": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "password": "123"
        }
        response = send_post_request(data=request_body, url=self.base_path, jwt=self.passenger)
        self.assertEqual(response.status_code, 400)

    def test_05_create_passenger_none_inputs(self):
        request_body = {
            "name": None,
            "surname": None,
            "profilePicture": None,
            "telephoneNumber": None,
            "email": None,
            "address": None,
            "password": None
        }
        response = send_post_request(data=request_body, url=self.base_path, jwt=self.passenger)
        self.assertEqual(response.status_code, 400)

    def test_06_create_passenger_email_already_exists(self):
        request_body = {
            "name": "Pera",
            "surname": "Perić",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381123123",
            "email": "pera.peric@email.com",
            "address": "Bulevar Oslobodjenja 74",
            "password": "NekaSifra123"
        }
        response = send_post_request(data=request_body, url=self.base_path, jwt=self.passenger)
        self.assertEqual(response.status_code, 400)
        response_body = response.json()
        self.assertEqual(response_body['message'], 'User with that email already exists!')

    def test_07_getting_passengers_unauthorized(self):
        query_params = {
            'page': 1,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}', query_params=query_params)
        self.assertEqual(response.status_code, 401)

    def test_08_getting_passengers_forbidden(self):
        query_params = {
            'page': 1,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}', query_params=query_params, jwt=self.driver)
        self.assertEqual(response.status_code, 403)

    def test_09_getting_passengers(self):
        query_params = {
            'page': 1,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}', query_params=query_params, jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertTrue(self.passenger_body in response_body['results'])

    def test_10_activate_passenger_account(self):
        response = send_get_request(url=f'{self.base_path}/activate/{ACCOUNT_ACTIVATION_ID}')
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertEqual(response_body['message'], 'Successful account activation!')

    def test_11_activate_passenger_account_activation_expired(self):
        response = send_get_request(url=f'{self.base_path}/activate/{ACCOUNT_ACTIVATION_ID_EXPIRED}')
        self.assertEqual(response.status_code, 400)
        response_body = response.json()
        self.assertEqual(response_body['message'], 'Activation expired. Register again!')

    def test_12_activate_passenger_account_not_exist(self):
        response = send_get_request(url=f'{self.base_path}/activate/{ACCOUNT_ACTIVATION_ID_NON_EXISTING}')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, 'Activation with entered id does not exist!')

    def test_13_passenger_details_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.passenger_id}')
        self.assertEqual(response.status_code, 401)

    def test_14_passenger_details_forbidden(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.passenger_id}', jwt=self.driver)
        self.assertEqual(response.status_code, 403)

    def test_15_passenger_details(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.passenger_id}', jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertEqual(response_body['id'], self.__class__.passenger_id)
        self.assertEqual(response_body['name'], self.__class__.passenger_body['name'])
        self.assertEqual(response_body['surname'], self.__class__.passenger_body['surname'])
        self.assertEqual(response_body['telephoneNumber'], self.__class__.passenger_body['telephoneNumber'])
        self.assertEqual(response_body['email'], self.__class__.passenger_body['email'])
        self.assertEqual(response_body['address'], self.__class__.passenger_body['address'])

    def test_16_passenger_details_not_exist(self):
        response = send_get_request(url=f'{self.base_path}/123456', jwt=self.passenger)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, 'Passenger does not exist!')

    def test_17_update_existing_passenger_unauthorized(self):
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

    def test_18_update_existing_passenger_forbidden(self):
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

    def test_19_update_existing_passenger(self):
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

    def test_20_update_existing_passenger_invalid_inputs(self):
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

    def test_21_update_existing_passenger_none_inputs(self):
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

    def test_22_update_non_existing_passenger(self):
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
        self.assertEqual(response.content, 'Passenger does not exist!')
