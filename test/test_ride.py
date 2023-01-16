import unittest
import time

from .request_sending import *
from .server_port import PORT
from .user_data import *


class RideTest(unittest.TestCase):
    driver_email = None
    user_id = None
    user_body = None
    ride_id = None
    ride_body = None

    @classmethod
    def setUpClass(cls):
        response = send_get_request(url=f'http://localhost:{PORT}/api/passenger/{PASSENGER_ID}')
        response_body = response.json()
        cls.user_id = response_body['id']
        cls.user_body = response_body

    def setUp(self):
        time.sleep(1)
        self.base_path = f'http://localhost:{PORT}/api/ride'
        passenger_login_data = {
            'email': PASSENGER_EMAIL,
            'password': PASSENGER_PASSWORD
        }
        response = send_post_request(data=passenger_login_data, url=f'http://localhost:{PORT}/api/user/login')
        self.passenger = response.json()['accessToken']
        if self.__class__.driver_email is not None:
            driver_login_data = {
                'email': self.__class__.driver_email,
                'password': ASSIGNED_DRIVER_PASSWORD
            }
            response = send_post_request(data=driver_login_data, url=f'http://localhost:{PORT}/api/user/login')
            self.driver = response.json()['accessToken']
        admin_login_data = {
            'email': ADMIN_EMAIL,
            'password': ADMIN_PASSWORD
        }
        response = send_post_request(data=admin_login_data, url=f'http://localhost:{PORT}/api/user/login')
        self.admin = response.json()['accessToken']

    def test_01_create_ride_unauthorized(self):
        request_body = None
        response = send_post_request(data=request_body, url=f'{self.base_path}')
        self.assertEqual(response.status_code, 401)

    def test_02_create_ride_forbidden(self):
        request_body = None
        response = send_post_request(data=request_body, url=f'{self.base_path}', jwt=self.admin)
        self.assertEqual(response.status_code, 403)

    def test_03_create_ride_invalid_inputs(self):
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
            'passengers': [
                {
                    'id': 'aaaaaa',
                    'email': 'aaaaaaa'
                }
            ],
            'vehicleType': 'STANDARD123',
            'babyTransport': '123',
            'petTransport': '123',
            'scheduleTime': '123'
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}', jwt=self.passenger)
        self.assertEqual(response.status_code, 400)

    def test_04_none_inputs(self):
        request_body = {
            'locations': [
                {
                    'departure': None,
                    'destination': None
                }
            ],
            'passengers': [
                {
                    'id': None,
                    'email': None
                }
            ],
            'vehicleType': None,
            'babyTransport': None,
            'petTransport': None,
            'scheduleTime': None
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}', jwt=self.passenger)
        self.assertEqual(response.status_code, 400)

    def test_05_create_ride(self):
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
        response = send_post_request(data=request_body, url=f'{self.base_path}', jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.__class__.ride_id = response_body['id']
        self.__class__.ride_body = response_body
        self.__class__.driver_email = response_body['driver']['email']
        self.assertEqual('id' in response_body, True)
        self.assertEqual('startTime' in response_body, True)
        self.assertEqual(response_body['endTime'], None)
        self.assertEqual('totalCost' in response_body, True)
        self.assertEqual(len(response_body['passengers']), 2)
        self.assertEqual('estimatedTimeInMinutes' in response_body, True)
        self.assertEqual(response_body['vehicleType'], 'STANDARD')
        self.assertEqual(response_body['babyTransport'], True)
        self.assertEqual(response_body['petTransport'], True)
        self.assertEqual(response_body['rejection'], None)
        self.assertEqual(response_body['locations'][0]['departure']['address'], 'Andje Rankovic 2')
        self.assertEqual(response_body['locations'][0]['departure']['latitude'], 45.247309)
        self.assertEqual(response_body['locations'][0]['departure']['longitude'], 19.796717)
        self.assertEqual(response_body['locations'][0]['destination']['address'], 'Bele njive 24')
        self.assertEqual(response_body['locations'][0]['destination']['latitude'], 45.265435)
        self.assertEqual(response_body['locations'][0]['destination']['longitude'], 19.847805)
        self.assertEqual(response_body['status'], 'PENDING')
        self.assertEqual('scheduledTime' in response_body, True)

    def test_06_create_ride_already_pending(self):
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
        response = send_post_request(data=request_body, url=f'{self.base_path}', jwt=self.passenger)
        self.assertEqual(response.status_code, 400)
        response_body = response.json()
        self.assertEqual(response_body['message'], 'Cannot create a ride while you have one already pending!')

    def test_07_driver_active_ride_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/driver/{self.__class__.ride_body["driver"]["id"]}/active')
        self.assertEqual(response.status_code, 401)

    def test_08_driver_active_ride_forbidden(self):
        response = send_get_request(url=f'{self.base_path}/driver/{self.__class__.ride_body["driver"]["id"]}/active', jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_09_driver_active_ride_non_exist(self):
        response = send_get_request(url=f'{self.base_path}/driver/1234567/active', jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Active ride does not exist')

    def test_10_driver_active_ride(self):
        response = send_get_request(url=f'{self.base_path}/driver/{self.__class__.ride_body["driver"]["id"]}/active', jwt=self.admin)
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual('id' in response_body, True)
        self.assertEqual('startTime' in response_body, True)
        self.assertEqual(response_body['endTime'], None)
        self.assertEqual('totalCost' in response_body, True)
        self.assertEqual(response_body['driver']['id'], self.__class__.ride_body['driver']['id'])
        self.assertEqual(response_body['driver']['email'], self.__class__.ride_body['driver']['email'])
        self.assertEqual(len(response_body['passengers']), 2)
        self.assertEqual('estimatedTimeInMinutes' in response_body, True)
        self.assertEqual(response_body['vehicleType'], 'STANDARD')
        self.assertEqual(response_body['babyTransport'], True)
        self.assertEqual(response_body['petTransport'], True)
        self.assertEqual(response_body['rejection'], None)
        self.assertEqual(response_body['locations'][0]['departure']['address'], 'Andje Rankovic 2')
        self.assertEqual(response_body['locations'][0]['departure']['latitude'], 45.247309)
        self.assertEqual(response_body['locations'][0]['departure']['longitude'], 19.796717)
        self.assertEqual(response_body['locations'][0]['destination']['address'], 'Bele njive 24')
        self.assertEqual(response_body['locations'][0]['destination']['latitude'], 45.265435)
        self.assertEqual(response_body['locations'][0]['destination']['longitude'], 19.847805)
        self.assertEqual(response_body['status'], 'PENDING')
        self.assertEqual('scheduledTime' in response_body, True)

    def test_11_passenger_active_ride_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/passenger/{PASSENGER_ID}/active')
        self.assertEqual(response.status_code, 401)

    def test_12_passenger_active_ride_forbidden(self):
        response = send_get_request(url=f'{self.base_path}/passenger/{PASSENGER_ID}/active', jwt=self.driver)
        self.assertEqual(response.status_code, 403)

    def test_13_passenger_active_ride_non_exist(self):
        response = send_get_request(url=f'{self.base_path}/passenger/1234567/active', jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Active ride does not exist')

    def test_14_passenger_active_ride(self):
        response = send_get_request(url=f'{self.base_path}/passenger/{PASSENGER_ID}/active', jwt=self.admin)
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual('id' in response_body, True)
        self.assertEqual('startTime' in response_body, True)
        self.assertEqual(response_body['endTime'], None)
        self.assertEqual('totalCost' in response_body, True)
        self.assertEqual(response_body['driver']['id'], self.__class__.ride_body['driver']['id'])
        self.assertEqual(response_body['driver']['email'], self.__class__.ride_body['driver']['email'])
        self.assertEqual(len(response_body['passengers']), 2)
        self.assertEqual('estimatedTimeInMinutes' in response_body, True)
        self.assertEqual(response_body['vehicleType'], 'STANDARD')
        self.assertEqual(response_body['babyTransport'], True)
        self.assertEqual(response_body['petTransport'], True)
        self.assertEqual(response_body['rejection'], None)
        self.assertEqual(response_body['locations'][0]['departure']['address'], 'Andje Rankovic 2')
        self.assertEqual(response_body['locations'][0]['departure']['latitude'], 45.247309)
        self.assertEqual(response_body['locations'][0]['departure']['longitude'], 19.796717)
        self.assertEqual(response_body['locations'][0]['destination']['address'], 'Bele njive 24')
        self.assertEqual(response_body['locations'][0]['destination']['latitude'], 45.265435)
        self.assertEqual(response_body['locations'][0]['destination']['longitude'], 19.847805)
        self.assertEqual(response_body['status'], 'PENDING')
        self.assertEqual('scheduledTime' in response_body, True)

    def test_15_ride_details_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.ride_id}')
        self.assertEqual(response.status_code, 401)

    def test_16_ride_details_does_not_exist(self):
        response = send_get_request(url=f'{self.base_path}/1234567', jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Ride does not exist')

    def test_17_ride_details(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.ride_id}', jwt=self.admin)
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual('id' in response_body, True)
        self.assertEqual('startTime' in response_body, True)
        self.assertEqual(response_body['endTime'], None)
        self.assertEqual('totalCost' in response_body, True)
        self.assertEqual(response_body['driver']['id'], self.__class__.ride_body['driver']['id'])
        self.assertEqual(response_body['driver']['email'], self.__class__.ride_body['driver']['email'])
        self.assertEqual(len(response_body['passengers']), 2)
        self.assertEqual('estimatedTimeInMinutes' in response_body, True)
        self.assertEqual(response_body['vehicleType'], 'STANDARD')
        self.assertEqual(response_body['babyTransport'], True)
        self.assertEqual(response_body['petTransport'], True)
        self.assertEqual(response_body['rejection'], None)
        self.assertEqual(response_body['locations'][0]['departure']['address'], 'Andje Rankovic 2')
        self.assertEqual(response_body['locations'][0]['departure']['latitude'], 45.247309)
        self.assertEqual(response_body['locations'][0]['departure']['longitude'], 19.796717)
        self.assertEqual(response_body['locations'][0]['destination']['address'], 'Bele njive 24')
        self.assertEqual(response_body['locations'][0]['destination']['latitude'], 45.265435)
        self.assertEqual(response_body['locations'][0]['destination']['longitude'], 19.847805)
        self.assertEqual(response_body['status'], 'PENDING')
        self.assertEqual('scheduledTime' in response_body, True)

    def test_18_accept_ride_unauthorized(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/accept')
        self.assertEqual(response.status_code, 401)

    def test_19_accept_ride_forbidden(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/accept', jwt=self.admin)
        self.assertEqual(response.status_code, 403)

    def test_20_accept_ride_not_exist(self):
        response = send_put_request(data=None, url=f'{self.base_path}/1234567/accept', jwt=self.driver)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Ride does not exist!')

    def test_21_accept_ride(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/accept', jwt=self.driver)
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual('id' in response_body, True)
        self.assertEqual('startTime' in response_body, True)
        self.assertEqual(response_body['endTime'], None)
        self.assertEqual('totalCost' in response_body, True)
        self.assertEqual(response_body['driver']['id'], self.__class__.ride_body['driver']['id'])
        self.assertEqual(response_body['driver']['email'], self.__class__.ride_body['driver']['email'])
        self.assertEqual(len(response_body['passengers']), 2)
        self.assertEqual('estimatedTimeInMinutes' in response_body, True)
        self.assertEqual(response_body['vehicleType'], 'STANDARD')
        self.assertEqual(response_body['babyTransport'], True)
        self.assertEqual(response_body['petTransport'], True)
        self.assertEqual(response_body['rejection'], None)
        self.assertEqual(response_body['locations'][0]['departure']['address'], 'Andje Rankovic 2')
        self.assertEqual(response_body['locations'][0]['departure']['latitude'], 45.247309)
        self.assertEqual(response_body['locations'][0]['departure']['longitude'], 19.796717)
        self.assertEqual(response_body['locations'][0]['destination']['address'], 'Bele njive 24')
        self.assertEqual(response_body['locations'][0]['destination']['latitude'], 45.265435)
        self.assertEqual(response_body['locations'][0]['destination']['longitude'], 19.847805)
        self.assertEqual(response_body['status'], 'ACCEPTED')
        self.assertEqual('scheduledTime' in response_body, True)

        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/accept', jwt=self.driver)
        response_body = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_body['message'], 'Cannot accept a ride that is not in status PENDING!')

    def test_22_start_ride_unauthorized(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/start')
        self.assertEqual(response.status_code, 401)

    def test_23_start_ride_forbidden(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/start', jwt=self.admin)
        self.assertEqual(response.status_code, 403)

    def test_24_start_ride_not_exist(self):
        response = send_put_request(data=None, url=f'{self.base_path}/1234567/start', jwt=self.driver)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Ride does not exist!')

    def test_25_start_ride(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/start', jwt=self.driver)
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual('id' in response_body, True)
        self.assertEqual('startTime' in response_body, True)
        self.assertEqual(response_body['endTime'], None)
        self.assertEqual('totalCost' in response_body, True)
        self.assertEqual(response_body['driver']['id'], self.__class__.ride_body['driver']['id'])
        self.assertEqual(response_body['driver']['email'], self.__class__.ride_body['driver']['email'])
        self.assertEqual(len(response_body['passengers']), 2)
        self.assertEqual('estimatedTimeInMinutes' in response_body, True)
        self.assertEqual(response_body['vehicleType'], 'STANDARD')
        self.assertEqual(response_body['babyTransport'], True)
        self.assertEqual(response_body['petTransport'], True)
        self.assertEqual(response_body['rejection'], None)
        self.assertEqual(response_body['locations'][0]['departure']['address'], 'Andje Rankovic 2')
        self.assertEqual(response_body['locations'][0]['departure']['latitude'], 45.247309)
        self.assertEqual(response_body['locations'][0]['departure']['longitude'], 19.796717)
        self.assertEqual(response_body['locations'][0]['destination']['address'], 'Bele njive 24')
        self.assertEqual(response_body['locations'][0]['destination']['latitude'], 45.265435)
        self.assertEqual(response_body['locations'][0]['destination']['longitude'], 19.847805)
        self.assertEqual(response_body['status'], 'STARTED')
        self.assertEqual('scheduledTime' in response_body, True)

        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/start', jwt=self.driver)
        response_body = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_body['message'], 'Cannot start a ride that is not in status ACCEPTED!')

    def test_26_end_ride_unauthorized(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/end')
        self.assertEqual(response.status_code, 401)

    def test_27_end_ride_forbidden(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/end', jwt=self.admin)
        self.assertEqual(response.status_code, 403)

    def test_28_end_ride_not_exist(self):
        response = send_put_request(data=None, url=f'{self.base_path}/1234567/end', jwt=self.driver)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Ride does not exist!')

    def test_29_end_ride(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/end', jwt=self.driver)
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual('id' in response_body, True)
        self.assertEqual('startTime' in response_body, True)
        self.assertIsNotNone(request_body['endTime'])
        self.assertEqual('totalCost' in response_body, True)
        self.assertEqual(response_body['driver']['id'], self.__class__.ride_body['driver']['id'])
        self.assertEqual(response_body['driver']['email'], self.__class__.ride_body['driver']['email'])
        self.assertEqual(len(response_body['passengers']), 2)
        self.assertEqual('estimatedTimeInMinutes' in response_body, True)
        self.assertEqual(response_body['vehicleType'], 'STANDARD')
        self.assertEqual(response_body['babyTransport'], True)
        self.assertEqual(response_body['petTransport'], True)
        self.assertEqual(response_body['rejection'], None)
        self.assertEqual(response_body['locations'][0]['departure']['address'], 'Andje Rankovic 2')
        self.assertEqual(response_body['locations'][0]['departure']['latitude'], 45.247309)
        self.assertEqual(response_body['locations'][0]['departure']['longitude'], 19.796717)
        self.assertEqual(response_body['locations'][0]['destination']['address'], 'Bele njive 24')
        self.assertEqual(response_body['locations'][0]['destination']['latitude'], 45.265435)
        self.assertEqual(response_body['locations'][0]['destination']['longitude'], 19.847805)
        self.assertEqual(response_body['status'], 'FINISHED')
        self.assertEqual('scheduledTime' in response_body, True)

        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/end', jwt=self.driver)
        response_body = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_body['message'], 'Cannot end a ride that is not in status STARTED!')

    def test_30_cancel_ride_unauthorized(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/cancel')
        self.assertEqual(response.status_code, 401)

    def test_31_cancel_ride_forbidden(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/cancel', jwt=self.admin)
        self.assertEqual(response.status_code, 403)

    def test_32_cancel_ride_not_exist(self):
        response = send_put_request(data=None, url=f'{self.base_path}/1234567/cancel', jwt=self.driver)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Ride does not exist!')

    def test_33_cancel_ride(self):
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
        response = send_post_request(data=request_body, url=f'{self.base_path}', jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        driver_login_data = {
            'email': response_body['driver']['email'],
            'password': ASSIGNED_DRIVER_PASSWORD
        }
        response = send_post_request(data=driver_login_data, url=f'http://localhost:{PORT}/api/user/login')
        driver = response.json()['accessToken']
        time.sleep(1)
        request_data = {
            'reason': 'No passengers were at the departure'
        }
        response = send_put_request(data=request_data, url=f'{self.base_path}/{response_body["id"]}/cancel', jwt=driver)
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual('id' in response_body, True)
        self.assertEqual('startTime' in response_body, True)
        self.assertEqual(response_body['endTime'], None)
        self.assertEqual('totalCost' in response_body, True)
        self.assertEqual(len(response_body['passengers']), 2)
        self.assertEqual('estimatedTimeInMinutes' in response_body, True)
        self.assertEqual(response_body['vehicleType'], 'STANDARD')
        self.assertEqual(response_body['babyTransport'], True)
        self.assertEqual(response_body['petTransport'], True)
        self.assertEqual(response_body['rejection']['reason'], 'No passengers were at the departure')
        self.assertEqual('timeOfRejection' in response_body['rejection'], True)
        self.assertEqual(response_body['locations'][0]['departure']['address'], 'Andje Rankovic 2')
        self.assertEqual(response_body['locations'][0]['departure']['latitude'], 45.247309)
        self.assertEqual(response_body['locations'][0]['departure']['longitude'], 19.796717)
        self.assertEqual(response_body['locations'][0]['destination']['address'], 'Bele njive 24')
        self.assertEqual(response_body['locations'][0]['destination']['latitude'], 45.265435)
        self.assertEqual(response_body['locations'][0]['destination']['longitude'], 19.847805)
        self.assertEqual(response_body['status'], 'REJECTED')
        self.assertEqual('scheduledTime' in response_body, True)

        response = send_put_request(data=request_data, url=f'{self.base_path}/{response_body["id"]}/cancel', jwt=driver)
        response_body = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_body['message'], 'Cannot cancel a ride that is not in status PENDING or ACCEPTED!')

    def test_34_withdraw_ride_unauthorized(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/withdraw')
        self.assertEqual(response.status_code, 401)

    def test_35_withdraw_ride_forbidden(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/withdraw', jwt=self.admin)
        self.assertEqual(response.status_code, 403)

    def test_36_withdraw_ride_not_exist(self):
        response = send_put_request(data=None, url=f'{self.base_path}/1234567/withdraw', jwt=self.passenger)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Ride does not exist!')

    def test_37_withdraw_ride(self):
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
        response = send_post_request(data=request_body, url=f'{self.base_path}', jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        time.sleep(1)
        response = send_put_request(data=None, url=f'{self.base_path}/{response_body["id"]}/withdraw', jwt=self.passenger)
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual('id' in response_body, True)
        self.assertEqual('startTime' in response_body, True)
        self.assertEqual(response_body['endTime'], None)
        self.assertEqual('totalCost' in response_body, True)
        self.assertEqual(len(response_body['passengers']), 2)
        self.assertEqual('estimatedTimeInMinutes' in response_body, True)
        self.assertEqual(response_body['vehicleType'], 'STANDARD')
        self.assertEqual(response_body['babyTransport'], True)
        self.assertEqual(response_body['petTransport'], True)
        self.assertEqual(response_body['rejection'], None)
        self.assertEqual(response_body['locations'][0]['departure']['address'], 'Andje Rankovic 2')
        self.assertEqual(response_body['locations'][0]['departure']['latitude'], 45.247309)
        self.assertEqual(response_body['locations'][0]['departure']['longitude'], 19.796717)
        self.assertEqual(response_body['locations'][0]['destination']['address'], 'Bele njive 24')
        self.assertEqual(response_body['locations'][0]['destination']['latitude'], 45.265435)
        self.assertEqual(response_body['locations'][0]['destination']['longitude'], 19.847805)
        self.assertEqual(response_body['status'], 'CANCELED')
        self.assertEqual('scheduledTime' in response_body, True)

        response = send_put_request(data=None, url=f'{self.base_path}/{response_body["id"]}/withdraw', jwt=self.passenger)
        response_body = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual('Cannot cancel a ride that' in response_body['message'], True)

    def test_38_panic_procedure_ride_unauthorized(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/panic')
        self.assertEqual(response.status_code, 401)

    def test_39_panic_procedure_ride_forbidden(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{self.__class__.ride_id}/panic', jwt=self.admin)
        self.assertEqual(response.status_code, 403)

    def test_40_panic_procedure_ride_not_exist(self):
        response = send_put_request(data=None, url=f'{self.base_path}/1234567/panic', jwt=self.passenger)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Ride does not exist!')

    def test_41_panic_procedure(self):
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
        response = send_post_request(data=request_body, url=f'{self.base_path}', jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        time.sleep(1)
        request_body = {
            'reason': 'Driver is constantly listening to bad music!'
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{response_body["id"]}/panic', jwt=self.passenger)
        response_body = response.json()
        self.assertEqual('id' in response_body, True)
        self.assertEqual('user' in response_body, True)
        self.assertEqual('ride' in response_body, True)
        self.assertEqual('time' in response_body, True)
        self.assertEqual(response_body['reason'], 'Driver is constantly listening to bad music!')

    def test_42_favorite_locations_unauthorized(self):
        request_body = None
        response = send_post_request(data=request_body, url=f'{self.base_path}/favorites')
        self.assertEqual(response.status_code, 401)

    def test_43_favorite_locations_forbidden(self):
        request_body = None
        response = send_post_request(data=request_body, url=f'{self.base_path}/favorites', jwt=self.admin)
        self.assertEqual(response.status_code, 403)

    def test_44_favorite_locations_invalid_inputs(self):
        request_body = {
            'favoriteName': 'Home - to - Work',
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
            'passengers': [
                {
                    'id': 'aaaaaa',
                    'email': 'aaaaaaa'
                }
            ],
            'vehicleType': 'STANDARD123',
            'babyTransport': '123',
            'petTransport': '123',
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/favorites', jwt=self.passenger)
        self.assertEqual(response.status_code, 400)

    def test_45_favorite_locations_none_inputs(self):
        request_body = {
            'favoriteName': None,
            'locations': [
                {
                    'departure': None,
                    'destination': None
                }
            ],
            'passengers': [
                {
                    'id': None,
                    'email': None
                }
            ],
            'vehicleType': None,
            'babyTransport': None,
            'petTransport': None
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/favorites', jwt=self.passenger)
        self.assertEqual(response.status_code, 400)

    def test_46_favorite_locations(self):
        request_body = {
            'favoriteName': 'Home - to - Work',
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
            'petTransport': True
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/favorites', jwt=self.passenger)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.__class__.ride_id = response_body['id']
        self.__class__.ride_body = response_body
        self.assertEqual('id' in response_body, True)
        self.assertEqual(len(response_body['passengers']), 2)
        self.assertEqual(response_body['favoriteName'], 'Home - to - Work')
        self.assertEqual(response_body['vehicleType'], 'STANDARD')
        self.assertEqual(response_body['babyTransport'], True)
        self.assertEqual(response_body['petTransport'], True)
        self.assertEqual(response_body['locations'][0]['departure']['address'], 'Andje Rankovic 2')
        self.assertEqual(response_body['locations'][0]['departure']['latitude'], 45.247309)
        self.assertEqual(response_body['locations'][0]['departure']['longitude'], 19.796717)
        self.assertEqual(response_body['locations'][0]['destination']['address'], 'Bele njive 24')
        self.assertEqual(response_body['locations'][0]['destination']['latitude'], 45.265435)
        self.assertEqual(response_body['locations'][0]['destination']['longitude'], 19.847805)

    def test_47_get_favorites_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/favorites')
        self.assertEqual(response.status_code, 401)

    def test_48_get_favorites_forbidden(self):
        response = send_get_request(url=f'{self.base_path}/favorites', jwt=self.admin)
        self.assertEqual(response.status_code, 403)

    def test_49_get_favorites(self):
        response = send_get_request(url=f'{self.base_path}/favorites', jwt=self.passenger)
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.__class__.ride_body in response_body, True)

    def test_50_delete_favorites_unauthorized(self):
        response = send_delete_request(url=f'{self.base_path}/favorites/{self.__class__.ride_id}')
        self.assertEqual(response.status_code, 401)

    def test_51_delete_favorites_forbidden(self):
        response = send_delete_request(url=f'{self.base_path}/favorites/{self.__class__.ride_id}', jwt=self.admin)
        self.assertEqual(response.status_code, 403)

    def test_52_delete_favorites_not_exist(self):
        response = send_delete_request(url=f'{self.base_path}/favorites/1234456', jwt=self.passenger)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Favorite location does not exist!')

    def test_53_delete_favorites(self):
        response = send_delete_request(url=f'{self.base_path}/favorites/{self.__class__.ride_id}', jwt=self.passenger)
        self.assertEqual(response.status_code, 204)
    
    