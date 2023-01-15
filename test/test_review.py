import unittest
import time

from .request_sending import *
from .server_port import PORT
from .user_data import *

from datetime import datetime


class ReviewTest(unittest.TestCase):
    passenger_id = None
    passenger_body = None
    review_body = None

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
        self.assertEqual(response.text, 'Ride does not exist!')

    def test_03_post_vehicle_review(self):
        data = {
            "rating": 3,
            "comment": "The driver was driving really fast"
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.ride_id}/vehicle', data=data, jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.__class__.review_body = response_data
        self.assertEqual('id' in response_data, True)
        self.assertEqual(response_data['rating'], data['rating'])
        self.assertEqual(response_data['comment'], data['comment'])
        self.assertEqual(response_data['passenger']['id'], PASSENGER_ID)
        self.assertEqual(response_data['passenger']['email'], PASSENGER_EMAIL)

    def test_04_get_vehicle_reviews_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/vehicle/{self.__class__.ride_id}')
        self.assertEqual(response.status_code, 401)

    def test_05_get_vehicle_reviews_unexisting_ride(self):
        response = send_get_request(url=f'{self.base_path}/vehicle/321', jwt=self.passenger)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Vehicle does not exist!')

    def test_06_get_vehicle_reviews(self):
        response = send_get_request(url=f'{self.base_path}/vehicle/{self.__class__.ride_id}', jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(self.__class__.review_body in response_data['results'])

    def test_07_post_driver_review_unauthorized(self):
        data = {
          "rating": 3,
          "comment": "The driver was driving really fast"
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.ride_id}/driver', data=data)
        self.assertEqual(response.status_code, 401)

    def test_08_post_driver_review_unexisting_ride(self):
        data = {
          "rating": 3,
          "comment": "The driver was driving really fast"
        }
        response = send_post_request(url=f'{self.base_path}/321/driver', data=data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Ride does not exist!')

    def test_09_post_driver_review_user(self):
        data = {
          "rating": 3,
          "comment": "The driver was driving really fast"
        }
        response = send_post_request(url=f'{self.base_path}/{self.__class__.ride_id}/driver', data=data, jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.__class__.review_body = response_data
        self.assertEqual('id' in response_data, True)
        self.assertEqual(response_data['rating'], data['rating'])
        self.assertEqual(response_data['comment'], data['comment'])
        self.assertEqual(response_data['passenger']['id'], PASSENGER_ID)
        self.assertEqual(response_data['passenger']['email'], PASSENGER_EMAIL)

    def test_10_get_driver_reviews_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/driver/{self.__class__.ride_id}')
        self.assertEqual(response.status_code, 401)

    def test_11_get_driver_reviews_unexisting_ride(self):
        response = send_get_request(url=f'{self.base_path}/driver/321', jwt=self.passenger)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Driver does not exist!')

    def test_12_get_driver_reviews(self):
        response = send_get_request(url=f'{self.base_path}/driver/{self.__class__.ride_id}', jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(self.__class__.review_body in response_data['results'])

    def test_13_get_ride_reviews_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/{self.ride_id}')
        self.assertEqual(response.status_code, 401)

    def test_14_get_ride_reviews_unexisting_ride(self):
        response = send_get_request(url=f'{self.base_path}/123456', jwt=self.passenger)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Ride does not exist!')

    def test_15_get_ride_reviews(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.ride_id}', jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data[0]['driverReview']['rating'], self.__class__.review_body['rating'])
        self.assertEqual(response_data[0]['driverReview']['comment'], self.__class__.review_body['comment'])
        self.assertEqual(response_data[0]['driverReview']['passenger']['id'], PASSENGER_ID)
        self.assertEqual(response_data[0]['driverReview']['passenger']['email'], PASSENGER_EMAIL)
