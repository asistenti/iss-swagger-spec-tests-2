import unittest
import time

from .request_sending import *
from .server_port import PORT
from .user_data import *

from datetime import datetime


class DriverTest(unittest.TestCase):
    passenger_id = None
    passenger_body = None

    @classmethod
    def setUpClass(cls):
        time.sleep(1)
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
        cls.driver_with_ride_token = response.json()['accessToken']
        time.sleep(1)
        send_put_request(data=request_body, url=f'http://localhost:{PORT}/api/ride/{cls.ride_id}/accept', jwt=cls.driver_with_ride_token)
        time.sleep(1)
        send_put_request(data=request_body, url=f'http://localhost:{PORT}/api/ride/{cls.ride_id}/start', jwt=cls.driver_with_ride_token)
        time.sleep(1)
        send_put_request(data=request_body, url=f'http://localhost:{PORT}/api/ride/{cls.ride_id}/end', jwt=cls.driver_with_ride_token)
        time.sleep(1)
        response = send_get_request(url=f'http://localhost:{PORT}/api/ride/{cls.ride_id}', jwt=passenger)
        response_body = response.json()
        response_body.pop('status')
        cls.ride_body = response_body

    def setUp(self):
        time.sleep(1)
        self.base_path = f'http://localhost:{PORT}/api/driver'
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
        self.working_time_start = datetime.now().strftime("%Y-%m-%dT%H:%S:%M.000Z")
        self.working_time_end = datetime.now().strftime("%Y-%m-%dT%H:%S:%M.000Z")

    def test_01_create_driver_unauthorized(self):
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

    def test_02_create_driver_forbidden(self):
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

    def test_03_create_driver(self):
        request_body = {
            "name": "Pera",
            "surname": "Perić",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381123123",
            "email": "pera.peric.vozac@email.com",
            "address": "Bulevar Oslobodjenja 74",
            "password": "NekaSifra123"
        }
        response = send_post_request(data=request_body, url=self.base_path, jwt=self.admin)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.__class__.available_driver_id = response_body['id']
        self.__class__.available_driver = response_body
        self.assertIsNotNone(response_body['id'])
        self.assertEqual(response_body['name'], request_body['name'])
        self.assertEqual(response_body['surname'], request_body['surname'])
        self.assertEqual(response_body['telephoneNumber'], request_body['telephoneNumber'])
        self.assertEqual(response_body['email'], request_body['email'])
        self.assertEqual(response_body['address'], request_body['address'])
        driver_login_data = {
            'email': self.__class__.available_driver['email'],
            'password': DRIVER_PASSWORD
        }
        response = send_post_request(data=driver_login_data, url=f'http://localhost:{PORT}/api/user/login')
        self.__class__.available_driver_token = response.json()['accessToken']

    def test_04_create_driver_invalid_inputs(self):
        request_body = {
            "name": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "surname": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "profilePicture": None,
            "telephoneNumber": "abcdabcdabcdabcdabcd",
            "email": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "address": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "password": "123"
        }
        response = send_post_request(data=request_body, url=self.base_path, jwt=self.admin)
        self.assertEqual(response.status_code, 400)

    def test_05_create_driver_none_inputs(self):
        request_body = {
            "name": None,
            "surname": None,
            "profilePicture": None,
            "telephoneNumber": None,
            "email": None,
            "address": None,
            "password": None
        }
        response = send_post_request(data=request_body, url=self.base_path, jwt=self.admin)
        self.assertEqual(response.status_code, 400)

    def test_06_create_driver_email_already_exists(self):
        request_body = {
            "name": "Available",
            "surname": "Driver",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381123123",
            "email": "pera.peric.vozac@email.com",
            "address": "Bulevar Oslobodjenja 74",
            "password": "NekaSifra123"
        }
        response = send_post_request(data=request_body, url=self.base_path, jwt=self.admin)
        self.assertEqual(response.status_code, 400)

    def test_07_getting_drivers_unauthorized(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}', query_params=query_params)
        self.assertEqual(response.status_code, 401)

    def test_08_getting_drivers_forbidden(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}', query_params=query_params, jwt=self.driver)
        self.assertEqual(response.status_code, 403)

    def test_09_getting_drivers(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}', query_params=query_params, jwt=self.admin)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertTrue(self.available_driver in response_body['results'])

    def test_10_driver_details_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}')
        self.assertEqual(response.status_code, 401)

    def test_11_driver_details_forbidden(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}', jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_12_driver_details(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}', jwt=self.admin)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertEqual(response_body['id'], self.__class__.available_driver_id)
        self.assertEqual(response_body['name'], self.__class__.available_driver['name'])
        self.assertEqual(response_body['surname'], self.__class__.available_driver['surname'])
        self.assertEqual(response_body['telephoneNumber'], self.__class__.available_driver['telephoneNumber'])
        self.assertEqual(response_body['email'], self.__class__.available_driver['email'])
        self.assertEqual(response_body['address'], self.__class__.available_driver['address'])

    def test_13_driver_details_not_exist(self):
        response = send_get_request(url=f'{self.base_path}/123456', jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Driver does not exist!')

    def test_14_update_existing_driver_unauthorized(self):
        request_body = {
            "name": "Available",
            "surname": "Driver",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381021650650",
            "email": "available.driver@email.com",
            "address": "Bulevar Oslobodjenja 84",
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.available_driver_id}')
        self.assertEqual(response.status_code, 401)

    def test_15_update_existing_driver_forbidden(self):
        request_body = {
            "name": "Available",
            "surname": "Driver",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381021650650",
            "email": "available.driver@email.com",
            "address": "Bulevar Oslobodjenja 84",
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.available_driver_id}', jwt=self.driver)
        self.assertEqual(response.status_code, 403)

    def test_16_update_existing_driver(self):
        request_body = {
            "name": "Available",
            "surname": "Driver",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381021650650",
            "email": "pera.peric.vozac@email.com",
            "address": "Bulevar Oslobodjenja 84",
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.available_driver_id}', jwt=self.admin)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertIsNotNone(response_body['id'])
        self.assertEqual(response_body['name'], request_body['name'])
        self.assertEqual(response_body['surname'], request_body['surname'])
        self.assertEqual(response_body['telephoneNumber'], request_body['telephoneNumber'])
        self.assertEqual(response_body['email'], request_body['email'])
        self.assertEqual(response_body['address'], request_body['address'])

    def test_17_update_existing_driver_invalid_inputs(self):
        request_body = {
            "name": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "surname": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "profilePicture": None,
            "telephoneNumber": "abcdabcdabcdabcdabcd",
            "email": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "address": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.available_driver_id}', jwt=self.admin)
        self.assertEqual(response.status_code, 400)

    def test_18_update_existing_driver_none_inputs(self):
        request_body = {
            "name": None,
            "surname": None,
            "profilePicture": None,
            "telephoneNumber": None,
            "email": None,
            "address": None,
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.available_driver_id}', jwt=self.admin)
        self.assertEqual(response.status_code, 400)

    def test_19_update_non_existing_driver(self):
        request_body = {
            "name": "Pera123",
            "surname": "Perić123",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381021650650",
            "email": "pera.peric123@email.com",
            "address": "Bulevar Oslobodjenja 84",
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/654321', jwt=self.admin)
        self.assertEqual(response.status_code, 404)

    def test_20_add_driver_document_unauthorized(self):
        request_body = {
            "name": "Vozačka dozvola",
            "documentImage": "U3dhZ2dlciByb2Nrcw="
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/documents', data=request_body)
        self.assertEqual(response.status_code, 401)

    def test_21_add_driver_document_forbidden(self):
        request_body = {
            "name": "Vozačka dozvola",
            "documentImage": "U3dhZ2dlciByb2Nrcw="
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/documents', data=request_body, jwt=self.passenger)
        self.assertEqual(response.status_code, 403)
        
    def test_22_add_driver_document(self):
        request_body = {
            "name": "Vozačka dozvola",
            "documentImage": "U3dhZ2dlciByb2Nrcw="
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/documents', data=request_body, jwt=self.admin)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.__class__.driver_document_id = response_body['id']
        self.__class__.driver_document = response_body
        self.assertEqual('id' in response_body, True)
        self.assertEqual(response_body['name'], request_body['name'])
        self.assertEqual(response_body['documentImage'], request_body['documentImage'])
        self.assertEqual(response_body['driverId'], self.__class__.available_driver_id)

    def test_23_add_driver_document_invalid_inputs(self):
        request_body = {
            "name": "abcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghij123",
            "documentImage": "U3dhZ2dlciByb2Nrcw="
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/documents', data=request_body, jwt=self.admin)
        self.assertEqual(response.status_code, 400)

    def test_24_add_driver_document_none_inputs(self):
        request_body = {
            "name": None,
            "documentImage": None
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/documents', data=request_body, jwt=self.admin)
        self.assertEqual(response.status_code, 400)

    def test_25_add_driver_document_non_existing_driver(self):
        request_body = {
            "name": "Vozačka dozvola",
            "documentImage": "U3dhZ2dlciByb2Nrcw="
        }
        response = send_post_request(url=f'{self.base_path}/123/documents', data=request_body, jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Driver does not exist!')
    
    def test_26_get_driver_documents(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/documents', jwt=self.admin)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertEqual('id' in response_body[0], True)
        self.assertEqual(response_body[0]['name'], 'Vozačka dozvola')
        self.assertEqual(response_body[0]['documentImage'], 'U3dhZ2dlciByb2Nrcw=')
        self.assertEqual(response_body[0]['driverId'], self.__class__.available_driver_id)

    def test_27_get_driver_documents_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/documents')
        self.assertEqual(response.status_code, 401)

    def test_28_get_driver_documents_forbidden(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/documents', jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_29_delete_driver_document_unauthorized(self):
        response = send_delete_request(url=f'{self.base_path}/document/{self.__class__.driver_document_id}')
        self.assertEqual(response.status_code, 401)

    def test_30_delete_driver_document_forbidden(self):
        response = send_delete_request(url=f'{self.base_path}/document/{self.__class__.driver_document_id}', jwt=self.passenger)
        self.assertEqual(response.status_code, 403)
    
    def test_31_delete_driver_document_not_found(self):
        response = send_delete_request(url=f'{self.base_path}/document/123', jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Document does not exist!')

    def test_32_delete_driver_document(self):
        response = send_delete_request(url=f'{self.base_path}/document/{self.__class__.driver_document_id}', jwt=self.admin)
        self.assertEqual(response.status_code, 204)

    def test_33_add_vehicle_unauthorized(self):
        request_body = {
            "vehicleType": "STANDARD",
            "model": "VW Golf 2",
            "licenseNumber": "NS 123-AB",
            "currentLocation": {
                "address": "Bulevar oslobodjenja 46",
                "latitude": 45.267136,
                "longitude": 19.833549
            },
            "passengerSeats": 4,
            "babyTransport": True,
            "petTransport": True
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', data=request_body)
        self.assertEqual(response.status_code, 401)

    def test_34_add_driver_vehicle_forbidden(self):
        request_body = {
            "vehicleType": "STANDARD",
            "model": "VW Golf 2",
            "licenseNumber": "NS 123-AB",
            "currentLocation": {
                "address": "Bulevar oslobodjenja 46",
                "latitude": 45.267136,
                "longitude": 19.833549
            },
            "passengerSeats": 4,
            "babyTransport": True,
            "petTransport": True
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', data=request_body, jwt=self.passenger)
        self.assertEqual(response.status_code, 403)
        
    def test_35_add_driver_vehicle_invalid_request(self):
        request_body = {
            "vehicleType": "fasdfasdfasdf",
            "model": "abcdefghijkabcdefghijkabcdefghijkabcdefghijkabcdefghijkabcdefghijkabcdefghijkabcdefghijkabcdefghijkabcdefghijk",
            "licenseNumber": "abcdefghijkabcdefghijk",
            "currentLocation": {
                "address": "",
                "latitude": "abc",
                "longitude": "abc"
            },
            "passengerSeats": "abc",
            "babyTransport": "123",
            "petTransport": "123"
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', data=request_body, jwt=self.admin)
        self.assertEqual(response.status_code, 400)

    def test_36_add_driver_vehicle_none_inputs(self):
        request_body = {
            "vehicleType": None,
            "model": None,
            "licenseNumber": None,
            "currentLocation": None,
            "passengerSeats": None,
            "babyTransport": "123",
            "petTransport": "123"
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', data=request_body, jwt=self.admin)
        self.assertEqual(response.status_code, 400)

    def test_37_add_driver_vehicle(self):
        request_body = {
            "vehicleType": "STANDARD",
            "model": "VW Golf 2",
            "licenseNumber": "NS 123-AB",
            "currentLocation": {
                "address": "Bulevar oslobodjenja 46",
                "latitude": 45.267136,
                "longitude": 19.833549
            },
            "passengerSeats": 4,
            "babyTransport": True,
            "petTransport": True
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', data=request_body, jwt=self.admin)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.__class__.vehicle_id = response_body['id']
        self.__class__.vehicle = response_body
        self.assertIsNotNone(response_body['id'])
        self.assertIsNotNone(response_body['driverId'])
        self.assertEqual(response_body['vehicleType'], request_body['vehicleType'])
        self.assertEqual(response_body['model'], request_body['model'])
        self.assertEqual(response_body['licenseNumber'], request_body['licenseNumber'])
        self.assertEqual(response_body['currentLocation']['address'], request_body['currentLocation']['address'])
        self.assertEqual(response_body['currentLocation']['latitude'], request_body['currentLocation']['latitude'])
        self.assertEqual(response_body['currentLocation']['longitude'], request_body['currentLocation']['longitude'])
        self.assertEqual(response_body['passengerSeats'], request_body['passengerSeats'])
        self.assertEqual(response_body['babyTransport'], request_body['babyTransport'])
        self.assertEqual(response_body['petTransport'], request_body['petTransport'])

    def test_38_add_driver_vehicle_nonexisting_driver(self):
        request_body = {
            "vehicleType": "STANDARD",
            "model": "VW Golf 2",
            "licenseNumber": "NS 123-AB",
            "currentLocation": {
                "address": "Bulevar oslobodjenja 46",
                "latitude": 45.267136,
                "longitude": 19.833549
            },
            "passengerSeats": 4,
            "babyTransport": True,
            "petTransport": True
        }
        response = send_post_request(url=f'{self.base_path}/123456/vehicle', data=request_body, jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Driver does not exist!')

    def test_39_get_driver_vehicle_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle')
        self.assertEqual(response.status_code, 401)

    def test_40_get_driver_vehicle_forbidden(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_41_get_driver_vehicle(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', jwt=self.admin)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertIsNotNone(response_body)
        self.assertEqual(response_body, self.__class__.vehicle)

    def test_42_change_vehicle_unauthorized(self):
        request_body = {
            "vehicleType": "STANDARD",
            "model": "VW Golf 4",
            "licenseNumber": "NS 123-AB",
            "currentLocation": {
                "address": "Bulevar oslobodjenja 46",
                "latitude": 45.267136,
                "longitude": 19.833549
            },
            "passengerSeats": 4,
            "babyTransport": True,
            "petTransport": True
        }
        response = send_put_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', data=request_body)
        self.assertEqual(response.status_code, 401)

    def test_43_change_driver_vehicle_forbidden(self):
        request_body = {
            "vehicleType": "STANDARD",
            "model": "VW Golf 4",
            "licenseNumber": "NS 123-AB",
            "currentLocation": {
                "address": "Bulevar oslobodjenja 46",
                "latitude": 45.267136,
                "longitude": 19.833549
            },
            "passengerSeats": 4,
            "babyTransport": True,
            "petTransport": True
        }
        response = send_put_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', data=request_body, jwt=self.passenger)
        self.assertEqual(response.status_code, 403)
        
    def test_44_change_driver_vehicle_invalid_request(self):
        request_body = {
            "vehicleType": "fasdfasdfasdf",
            "model": "abcdefghijkabcdefghijkabcdefghijkabcdefghijkabcdefghijkabcdefghijkabcdefghijkabcdefghijkabcdefghijkabcdefghijk",
            "licenseNumber": "abcdefghijkabcdefghijk",
            "currentLocation": {
                "address": "",
                "latitude": "abc",
                "longitude": "abc"
            },
            "passengerSeats": "abc",
            "babyTransport": "123",
            "petTransport": "123"
        }
        response = send_put_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', data=request_body, jwt=self.admin)
        self.assertEqual(response.status_code, 400)

    def test_45_change_driver_vehicle_none_inputs(self):
        request_body = {
            "vehicleType": None,
            "model": None,
            "licenseNumber": None,
            "currentLocation": None,
            "passengerSeats": None,
            "babyTransport": "123",
            "petTransport": "123"
        }
        response = send_put_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', data=request_body, jwt=self.admin)
        self.assertEqual(response.status_code, 400)

    def test_46_change_driver_vehicle(self):
        request_body = {
            "vehicleType": "STANDARD",
            "model": "VW Golf 5",
            "licenseNumber": "NS 123-CD",
            "currentLocation": {
                "address": "Bulevar oslobodjenja 46",
                "latitude": 45.267136,
                "longitude": 19.833549
            },
            "passengerSeats": 4,
            "babyTransport": True,
            "petTransport": True
        }
        response = send_put_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', data=request_body, jwt=self.admin)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.__class__.vehicle_id = response_body['id']
        self.__class__.vehicle = response_body
        self.assertIsNotNone(response_body['id'])
        self.assertIsNotNone(response_body['driverId'])
        self.assertEqual(response_body['vehicleType'], request_body['vehicleType'])
        self.assertEqual(response_body['model'], request_body['model'])
        self.assertEqual(response_body['licenseNumber'], request_body['licenseNumber'])
        self.assertEqual(response_body['currentLocation']['address'], request_body['currentLocation']['address'])
        self.assertEqual(response_body['currentLocation']['latitude'], request_body['currentLocation']['latitude'])
        self.assertEqual(response_body['currentLocation']['longitude'], request_body['currentLocation']['longitude'])
        self.assertEqual(response_body['passengerSeats'], request_body['passengerSeats'])
        self.assertEqual(response_body['babyTransport'], request_body['babyTransport'])
        self.assertEqual(response_body['petTransport'], request_body['petTransport'])

    def test_47_change_driver_vehicle_nonexisting_driver(self):
        request_body = {
            "vehicleType": "STANDARD",
            "model": "VW Golf 6",
            "licenseNumber": "NS 123-EF",
            "currentLocation": {
                "address": "Bulevar oslobodjenja 46",
                "latitude": 45.267136,
                "longitude": 19.833549
            },
            "passengerSeats": 4,
            "babyTransport": True,
            "petTransport": True
        }
        response = send_put_request(url=f'{self.base_path}/123456/vehicle', data=request_body, jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Driver does not exist!')

    def test_48_add_working_hour_unauthorized(self):
        request_body = {
          "start": self.working_time_start
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour', data=request_body)
        self.assertEqual(response.status_code, 401)

    def test_49_add_working_hour_forbidden(self):
        request_body = {
            "start": self.working_time_start
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour', data=request_body, jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_50_add_working_hour_invalid_request(self):
        request_body = {
            "start": "abc"
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour', data=request_body, jwt=self.__class__.available_driver_token)
        self.assertEqual(response.status_code, 400)

    def test_51_add_working_hour_none_inputs(self):
        request_body = {
            "start": None
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour', data=request_body, jwt=self.__class__.available_driver_token)
        self.assertEqual(response.status_code, 400)

    def test_52_add_working_hour(self):
        request_body = {
            "start": self.working_time_start
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour', data=request_body, jwt=self.__class__.available_driver_token)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.__class__.driver_working_hour_id = response_body['id']
        self.__class__.driver_working_hour = response_body
        self.assertIsNotNone(response_body['id'])
        self.assertIsNotNone(response_body['start'])
        self.assertIsNone(response_body['end'])

    def test_53_add_working_hour_shift_already_going(self):
        request_body = {
            "start": self.working_time_start
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour', data=request_body, jwt=self.__class__.available_driver_token)
        self.assertEqual(response.status_code, 400)
        response_body = response.json()
        self.assertEqual(response_body['message'], 'Shift already ongoing!')

    def test_54_change_working_hour_unauthorized(self):
        request_body = {
            "end": self.working_time_end
        }
        response = send_put_request(url=f'{self.base_path}/working-hour/{self.__class__.driver_working_hour_id}', data=request_body)
        self.assertEqual(response.status_code, 401)

    def test_55_change_working_hour_forbidden(self):
        request_body = {
            "end": self.working_time_end
        }
        response = send_put_request(url=f'{self.base_path}/working-hour/{self.__class__.driver_working_hour_id}', data=request_body, jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_56_change_working_hour_invalid_request(self):
        request_body = {
            "end": "abc"
        }
        response = send_put_request(url=f'{self.base_path}/working-hour/{self.__class__.driver_working_hour_id}', data=request_body, jwt=self.__class__.available_driver_token)
        self.assertEqual(response.status_code, 400)

    def test_57_change_working_hour_none_inputs(self):
        request_body = {
            "end": None
        }
        response = send_put_request(url=f'{self.base_path}/working-hour/{self.__class__.driver_working_hour_id}', data=request_body, jwt=self.__class__.available_driver_token)
        self.assertEqual(response.status_code, 400)

    def test_58_change_working_hour(self):
        request_body = {
            "end": self.working_time_end
        }
        response = send_put_request(url=f'{self.base_path}/working-hour/{self.__class__.driver_working_hour_id}', data=request_body, jwt=self.__class__.available_driver_token)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.__class__.driver_working_hour_id = response_body['id']
        self.__class__.driver_working_hour = response_body
        self.assertIsNotNone(response_body['id'])
        self.assertIsNotNone(response_body['start'])
        self.assertIsNotNone(response_body['end'])

    def test_59_change_working_hour_shift_already_going(self):
        request_body = {
            "end": self.working_time_end
        }
        response = send_put_request(url=f'{self.base_path}/working-hour/{self.__class__.driver_working_hour_id}', data=request_body, jwt=self.__class__.available_driver_token)
        self.assertEqual(response.status_code, 400)
        response_body = response.json()
        self.assertEqual(response_body['message'], 'No shift is ongoing!')

    def test_60_get_working_hours_unauthorized(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour', query_params=query_params)
        self.assertEqual(response.status_code, 401)

    def test_61_get_working_hours_forbidden(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour', query_params=query_params, jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_62_get_working_hours(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour', query_params=query_params, jwt=self.admin)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertIsNotNone(response_body)
        self.assertEqual(self.__class__.driver_working_hour in response_body['results'], True)

    def test_63_get_working_hours_nonexisting(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/12345678/working-hour', query_params=query_params, jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Driver does not exist!')

    def test_64_get_working_hour_details_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/working-hour/{self.__class__.driver_working_hour_id}')
        self.assertEqual(response.status_code, 401)

    def test_65_get_working_hour_details_forbidden(self):
        response = send_get_request(url=f'{self.base_path}/working-hour/{self.__class__.driver_working_hour_id}', jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_66_get_working_hour_details(self):
        response = send_get_request(url=f'{self.base_path}/working-hour/{self.__class__.driver_working_hour_id}', jwt=self.admin)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertIsNotNone(response_body)
        self.assertEqual(self.__class__.driver_working_hour, response_body)

    def test_67_get_working_hour_details_nonexisting(self):
        response = send_get_request(url=f'{self.base_path}/working-hour/12345678', jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Working hour does not exist!')

    def test_68_rides_of_driver_unauthorized(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/{self.__class__.ride_body["driver"]["id"]}/ride', query_params=query_params)
        self.assertEqual(response.status_code, 401)

    def test_69_rides_of_driver_forbidden(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/{self.__class__.ride_body["driver"]["id"]}/ride', query_params=query_params, jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_70_rides_of_driver_not_exist(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/12345/ride', query_params=query_params, jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Driver does not exist!')

    def test_71_rides_of_driver(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/{self.__class__.ride_body["driver"]["id"]}/ride', query_params=query_params, jwt=self.driver_with_ride_token)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertTrue(self.__class__.ride_body in response_body['results'])
