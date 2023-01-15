import unittest
import time

from .request_sending import send_post_request, send_get_request, send_put_request, send_delete_request
from .server_port import PORT
from .user_data import *

from datetime import datetime


class ReviewTest(unittest.TestCase):
    passenger_id = None
    passenger_body = None

    @classmethod
    def setUpClass(cls):
        cls.driver_review = {
          "rating": 3,
          "comment": "The driver was driving really fast",
          "passenger": {
            "id": PASSENGER_ID,
            "email": PASSENGER_EMAIL
          }
        }
        cls.vehicle_review = {
            "rating": 3,
            "comment": "The vehicle was bad and dirty",
            "passenger": {
                "id": PASSENGER_ID,
                "email": PASSENGER_EMAIL
            }
        }
        response = send_get_request(url=f'http://localhost:{PORT}/api/passenger/{PASSENGER_ID}')
        response_body = response.json()
        cls.user_id = response_body['id']
        cls.user_body = response_body
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
        cls.ride_id = response_body['id']
        cls.driver_id = response_body['driver']['id']
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
        time.sleep(1)
        vehicle_data = {
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
        response = send_post_request(
            data=vehicle_data,
            url=f'http://localhost:{PORT}/api/driver/{cls.driver_id}/vehicle',
        )
        cls.vehicle_id = response.json()['id']

    def setUp(self):
        time.sleep(1)
        self.base_path = f'http://localhost:{PORT}/api/review'
        passenger_login_data = {
            'email': PASSENGER_EMAIL,
            'password': PASSENGER_PASSWORD
        }
        response = send_post_request(data=passenger_login_data, url=f'http://localhost:{PORT}/api/user/login')
        self.passenger = response.json()['accessToken']
        admin_login_data = {
            'email': ADMIN_EMAIL,
            'password': ADMIN_PASSWORD
        }
        response = send_post_request(data=admin_login_data, url=f'http://localhost:{PORT}/api/user/login')
        self.admin = response.json()['accessToken']

        driver_login_data = {
            'email': DRIVER_EMAIL,
            'password': DRIVER_PASSWORD
        }
        response = send_post_request(data=driver_login_data, url=f'http://localhost:{PORT}/api/user/login')
        self.driver = response.json()['accessToken']

    # Vehicle review
    def test_01_post_vehicle_review_unauthorized(self):
        data = {
          "rating": 3,
          "comment": "The vehicle was bad and dirty"
        }
        response = send_post_request(url=f'{self.base_path}/{self.ride_id}/vehicle', data=data)
        self.assertEqual(response.status_code, 401)

    def test_02_post_vehicle_review_unexisting_ride(self):
        data = {
            "rating": 3,
            "comment": "The vehicle was bad and dirty"
        }
        response = send_post_request(url=f'{self.base_path}/321/vehicle', data=data)
        self.assertEqual(response.status_code, 404)

    def test_03_post_vehicle_review_passenger_not_in_ride(self):
        data = {
            "rating": 3,
            "comment": "The vehicle was bad and dirty"
        }
        response = send_post_request(url=f'{self.base_path}/{self.ride_id}/vehicle', data=data, jwt=self.driver)
        self.assertEqual(response.status_code, 403)

    def test_04_post_vehicle_review_user(self):
        data = {
            "rating": 3,
            "comment": "The vehicle was bad and dirty"
        }
        response = send_post_request(url=f'{self.base_path}/{self.ride_id}/vehicle', data=data, jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.vehicle_review['id'] = response_data['id']
        # Removed in Python 3.11
        self.assertDictContainsSubset(self.vehicle_review, data)

    def test_05_get_vehicle_reviews_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/{self.ride_id}/vehicle')
        self.assertEqual(response.status_code, 401)

    def test_06_get_vehicle_reviews_unexisting_ride(self):
        response = send_get_request(url=f'{self.base_path}/321/vehicle')
        self.assertEqual(response.status_code, 404)

    def test_07_get_vehicle_reviews(self):
        response = send_get_request(url=f'{self.base_path}/{self.ride_id}/vehicle', jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        # Will fail if the response has extra fields
        self.assertTrue(self.vehicle_review in response_data)

    # Driver reviews
    def test_08_post_driver_review_unauthorized(self):
        data = {
          "rating": 3,
          "comment": "The driver was driving really fast"
        }
        response = send_post_request(url=f'{self.base_path}/{self.ride_id}/driver', data=data)
        self.assertEqual(response.status_code, 401)

    def test_09_post_driver_review_unexisting_ride(self):
        data = {
          "rating": 3,
          "comment": "The driver was driving really fast"
        }
        response = send_post_request(url=f'{self.base_path}/321/driver', data=data)
        self.assertEqual(response.status_code, 404)

    def test_10_post_driver_review_passenger_not_in_ride(self):
        data = {
          "rating": 3,
          "comment": "The driver was driving really fast"
        }
        response = send_post_request(url=f'{self.base_path}/{self.ride_id}/driver', data=data, jwt=self.driver)
        self.assertEqual(response.status_code, 403)

    def test_11_post_driver_review_user(self):
        data = {
          "rating": 3,
          "comment": "The driver was driving really fast"
        }
        response = send_post_request(url=f'{self.base_path}/{self.ride_id}/driver', data=data, jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.driver_review['id'] = response_data['id']
        # Removed in Python 3.11
        self.assertDictContainsSubset(self.driver_review, data)

    def test_12_get_driver_reviews(self):
        response = send_get_request(url=f'{self.base_path}/{self.ride_id}/driver', jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        # Will fail if the response has extra fields
        self.assertTrue(self.driver_review in response_data)

    # Ride reviews
    def test_13_get_ride_reviews_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/{self.ride_id}/vehicle')
        self.assertEqual(response.status_code, 401)

    def test_14_get_ride_reviews_unexisting_ride(self):
        response = send_get_request(url=f'{self.base_path}/{self.ride_id}')
        self.assertEqual(response.status_code, 404)

    def test_15_get_ride_reviews(self):
        response = send_get_request(url=f'{self.base_path}/{self.ride_id}', jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn(self.vehicle_review, response_data)
        self.assertIn(self.driver_review, response_data)
