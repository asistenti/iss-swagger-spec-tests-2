import unittest
import time

from .request_sending import send_post_request, send_get_request, send_put_request, send_delete_request
from .server_port import PORT
from .user_data import *

from datetime import datetime


class DriverTest(unittest.TestCase):
    passenger_id = None
    passenger_body = None

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


    def setUpDrivers(self):
        request_body = {
            "name": "Available",
            "surname": "Driver",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381123123",
            "email": "available.driver@email.com",
            "address": "Bulevar Oslobodjenja 74",
            "password": "NekaSifra123"
        }
        response = send_post_request(data=request_body, url=f'http://localhost:{PORT}/api/driver', jwt=self.admin)
        response_body = response.json()
        self.available_driver_id = response_body['id']
        self.assertEqual(response.status_code, 200)

        available_driver_login = {
            'email': ADMIN_EMAIL,
            'password': ADMIN_PASSWORD
        }
        response = send_post_request(data=available_driver_login, url=f'http://localhost:{PORT}/api/user/login')
        self.available_driver_token = response.json()['accessToken']

        # Start working hour and make this driver active
        response = send_post_request(data={"start": "2023-01-13T17:39:17.081Z"}, url=f'http://localhost:{PORT}/api/user/login')

        request_body = {
            "name": "Inactive",
            "surname": "Driver",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381123123",
            "email": "inactive.driver@email.com",
            "address": "Bulevar Oslobodjenja 74",
            "password": "NekaSifra123"
        }
        response = send_post_request(data=request_body, url=f'http://localhost:{PORT}/api/driver', jwt=self.admin)
        response_body = response.json()
        self.inactive_driver_id = response_body['id']
        self.assertEqual(response.status_code, 200)

        available_driver_login = {
            'email': ADMIN_EMAIL,
            'password': ADMIN_PASSWORD
        }
        response = send_post_request(data=available_driver_login, url=f'http://localhost:{PORT}/api/user/login')
        self.available_driver_token = response.json()['accessToken']


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
            "email": "pera.peric@email.com",
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

        request_body = {
            "name": "Unavailable",
            "surname": "Driver",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381123123",
            "email": "unavailable.driver@email.com",
            "address": "Bulevar Oslobodjenja 74",
            "password": "NekaSifra123"
        }
        response = send_post_request(data=request_body, url=self.base_path, jwt=self.admin)
        self.assertEqual(response.status_code, 200)
        self.__class__.unavailable_driver_id = response_body['id']
        self.__class__.unavailable_driver = response_body

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
        response = send_post_request(data=request_body, url=self.base_path, jwt=self.driver)
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
        response = send_post_request(data=request_body, url=self.base_path, jwt=self.driver)
        self.assertEqual(response.status_code, 400)

    def test_06_create_driver_email_already_exists(self):
        request_body = {
            "name": "Available",
            "surname": "Driver",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381123123",
            "email": "available.driver@email.com",
            "address": "Bulevar Oslobodjenja 74",
            "password": "NekaSifra123"
        }
        response = send_post_request(data=request_body, url=self.base_path, jwt=self.driver)
        self.assertEqual(response.status_code, 400)

    def test_07_getting_drivers_unauthorized(self):
        query_params = {
            'page': 1,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}', query_params=query_params)
        self.assertEqual(response.status_code, 401)

    def test_09_getting_drivers(self):
        query_params = {
            'page': 1,
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
        response = send_get_request(
            url=f'{self.base_path}/{self.__class__.available_driver_id}',
            jwt=self.available_driver_token
        )
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertEqual(response_body['id'], self.__class__.available_driver_id)
        self.assertEqual(response_body['name'], self.__class__.available_driver['name'])
        self.assertEqual(response_body['surname'], self.__class__.available_driver['surname'])
        self.assertEqual(response_body['telephoneNumber'], self.__class__.available_driver['telephoneNumber'])
        self.assertEqual(response_body['email'], self.__class__.available_driver['email'])
        self.assertEqual(response_body['address'], self.__class__.available_driver['address'])

    def test_13_driver_details_not_exist(self):
        response = send_get_request(url=f'{self.base_path}/123456', jwt=self.passenger)
        self.assertEqual(response.status_code, 404)

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
        response = send_put_request(
            data=request_body,
            url=f'{self.base_path}/{self.__class__.available_driver_id}',
            jwt=self.driver
        )
        self.assertEqual(response.status_code, 403)

    def test_16_update_existing_driver(self):
        request_body = {
            "name": "Available",
            "surname": "Driver",
            "profilePicture": "U3dhZ2dlciByb2Nrcw==",
            "telephoneNumber": "+381021650650",
            "email": "available.driver@email.com",
            "address": "Bulevar Oslobodjenja 84",
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.available_driver_id}', jwt=self.available_driver_id)
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
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.available_driver_id}', jwt=self.available_driver_id)
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
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.available_driver_id}', jwt=self.available_driver_id)
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
        response = send_put_request(data=request_body, url=f'{self.base_path}/654321', jwt=self.available_driver_id)
        self.assertEqual(response.status_code, 404)

    # Documents
    def test_20_add_driver_document_unauthorized(self):
        request_body = {
            "name": "Vozačka dozvola",
            "documentImage": "U3dhZ2dlciByb2Nrcw="
        }
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/documents', data=request_body,)
        self.assertEqual(response.status_code, 401)

    def test_21_add_driver_document_forbidden(self):
        request_body = {
            "name": "Vozačka dozvola",
            "documentImage": "U3dhZ2dlciByb2Nrcw="
        }
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/documents', data=request_body, jwt=self.passenger)
        self.assertEqual(response.status_code, 403)
        
    def test_22_add_driver_document(self):
        request_body = {
            "name": "Vozačka dozvola",
            "documentImage": "U3dhZ2dlciByb2Nrcw="
        }
        response = send_post_request(
            url=f'{self.base_path}/{self.__class__.available_driver_id}/documents',
            data=request_body,
            jwt=self.available_driver_token
        )
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.__class__.driver_document = response_body
    
    def test_23_get_driver_documents(self):
        response = send_get_request(
            url=f'{self.base_path}/{self.__class__.available_driver_id}/documents',
            jwt=self.available_driver_token
        )
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertIsNotNone(response_body)
        self.assertEqual(response_body, self.__class__.driver_document)

    def test_24_get_driver_documents_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/documents')
        self.assertEqual(response.status_code, 401)

    def test_25_get_driver_documents_forbidden(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/documents', jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_26_delete_driver_documents_unauthorized(self):
        document_id = self.__class__.driver_document["id"]
        response = send_delete_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/documents/{document_id}')
        self.assertEqual(response.status_code, 401)

    def test_27_delete_driver_documents_forbidden(self):
        document_id = self.__class__.driver_document["id"]
        response = send_delete_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/documents/{document_id}', jwt=self.passenger)
        self.assertEqual(response.status_code, 403)
    
    def test_28_delete_driver_documents_not_found(self):
        document_id = "123"
        response = send_delete_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/documents/{document_id}', jwt=self.available_driver_id)
        self.assertEqual(response.status_code, 404)

    # Vehicles
    def test_29_add_vehicle_document_unauthorized(self):
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

    def test_30_add_driver_vehicle_forbidden(self):
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
        
    def test_31_add_driver_vehicle_invalid_request(self):
        request_body = {
            "vehicleType": "",
            "model": "",
            "licenseNumber": "",
            "currentLocation": {
                "address": "",
                "latitude": "abc",
                "longitude": "abc"
            },
            "passengerSeats": "abc",
            "babyTransport": "123",
            "petTransport": "123"
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', data=request_body, jwt=self.available_driver_id)
        self.assertEqual(response.status_code, 400)

    def test_32_add_driver_vehicle(self):
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
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', data=request_body, jwt=self.available_driver_id)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.__class__.driver_vehicle = response_body
    
    def test_33_get_driver_vehicle(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', jwt=self.available_driver_id)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertIsNotNone(response_body)
        self.assertEqual(response_body, self.__class__.driver_vehicle)

    def test_34_get_driver_vehicle_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle')
        self.assertEqual(response.status_code, 401)

    def test_35_get_driver_vehicle_forbidden(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_36_delete_driver_vehicle_unauthorized(self):
        response = send_delete_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle')
        self.assertEqual(response.status_code, 401)

    def test_37_delete_driver_vehicle_forbidden(self):
        response = send_delete_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', jwt=self.passenger)
        self.assertEqual(response.status_code, 403)
    
    def test_38_delete_driver_vehicle_not_found(self):
        response = send_delete_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/vehicle', jwt=self.available_driver_id)
        self.assertEqual(response.status_code, 404)

    # Working hour
    def test_39_add_working_hour_unauthorized(self):
        request_body = {
          "start": self.working_time_start
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour',
                                     data=request_body)
        self.assertEqual(response.status_code, 401)

    def test_40_add_working_hour_forbidden(self):
        request_body = {
            "start": self.working_time_start
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour',
                                     data=request_body, jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_41_add_working_hour_invalid_request(self):
        request_body = {
            "start": "abc"
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour',
                                     data=request_body, jwt=self.available_driver_token)
        self.assertEqual(response.status_code, 400)

    def test_42_add_working_hour(self):
        request_body = {
            "start": self.working_time_start
        }

        response = send_post_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour',
                                     data=request_body, jwt=self.available_driver_id)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.__class__.driver_working_hour = response_body

    def test_43_get_working_hours(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour',
                                    jwt=self.available_driver_id)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertIsNotNone(response_body)
        self.assertEqual(response_body, self.__class__.driver_working_hour)

    def test_44_get_working_hours_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour')
        self.assertEqual(response.status_code, 401)

    def test_45_get_working_hours_forbidden(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour',
                                    jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_46_get_working_hour_details(self):
        working_hour_id = self.__class__.driver_working_hour["id"]
        response = send_get_request(
            url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour/{working_hour_id}',
            jwt=self.available_driver_id
        )
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertIsNotNone(response_body)
        self.assertEqual(response_body, self.__class__.driver_working_hour)

    def test_47_get_working_hour_details_unauthorized(self):
        working_hour_id = self.__class__.driver_working_hour["id"]
        response = send_get_request(
            url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour/{working_hour_id}'
        )
        self.assertEqual(response.status_code, 401)

    def test_48_get_working_hour_details_forbidden(self):
        working_hour_id = self.__class__.driver_working_hour["id"]
        response = send_get_request(
            url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour/{working_hour_id}',
            jwt=self.passenger
        )
        self.assertEqual(response.status_code, 403)

    def test_49_get_unexisting_working_hour_details(self):
        response = send_get_request(
            url=f'{self.base_path}/{self.__class__.available_driver_id}/working-hour/123',
            jwt=self.available_driver_id
        )
        self.assertEqual(response.status_code, 404)
