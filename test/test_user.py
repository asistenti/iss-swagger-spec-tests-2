import unittest
import time

from .request_sending import *
from .server_port import PORT
from .user_data import *


class UserTest(unittest.TestCase):
    user_id = None
    user_body = None
    ride_id = None
    ride_body = None
    message_id = None
    message_body = None
    note_id = None
    note_body = None

    @classmethod
    def setUpClass(cls):
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
        self.base_path = f'http://localhost:{PORT}/api/user'
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

    def test_01_change_password_unauthorized(self):
        request_body = {
            'newPassword': 'NekaSifra456',
            'oldPassword': 'NekaSifra123'
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.user_id}/changePassword')
        self.assertEqual(response.status_code, 401)

    def test_02_change_password_not_matching(self):
        request_body = {
            'newPassword': 'NekaSifra456',
            'oldPassword': 'NekaSifra456'
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.user_id}/changePassword', jwt=self.passenger)
        self.assertEqual(response.status_code, 400)
        response_body = response.json()
        self.assertEqual(response_body['message'], 'Current password is not matching!')

    def test_03_change_password(self):
        request_body = {
            'newPassword': 'NekaSifra456',
            'oldPassword': 'NekaSifra123'
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.user_id}/changePassword', jwt=self.passenger)
        self.assertEqual(response.status_code, 204)

    def test_04_change_password_to_old_value(self):
        request_body = {
            'newPassword': 'NekaSifra123',
            'oldPassword': 'NekaSifra456'
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.user_id}/changePassword', jwt=self.passenger)
        self.assertEqual(response.status_code, 204)

    def test_05_change_password_invalid_inputs(self):
        request_body = {
            'newPassword': 'sifra',
            'oldPassword': 'sifra'
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.user_id}/changePassword', jwt=self.passenger)
        self.assertEqual(response.status_code, 400)

    def test_06_change_password_none_inputs(self):
        request_body = {
            'newPassword': None,
            'oldPassword': None
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.user_id}/changePassword', jwt=self.passenger)
        self.assertEqual(response.status_code, 400)

    def test_07_change_password_user_not_exist(self):
        request_body = {
            'newPassword': 'NekaSifra456',
            'oldPassword': 'NekaSifra123'
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/456789/changePassword', jwt=self.passenger)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'User does not exist!')

    def test_08_reset_password(self):
        response = send_get_request(url=f'{self.base_path}/{self.__class__.user_id}/resetPassword')
        self.assertEqual(response.status_code, 204)

    def test_09_reset_password_user_not_exist(self):
        response = send_get_request(url=f'{self.base_path}/456789/resetPassword')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'User does not exist!')

    def test_10_reset_password_code_expired(self):
        request_body = {
            'code': PASSWORD_RESET_CODE_EXPIRED,
            'newPassword': 'NekaSifra789'
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{PASSWORD_RESET_USER_ID_EXPIRED}/resetPassword')
        self.assertEqual(response.status_code, 400)
        response_body = response.json()
        self.assertEqual(response_body['message'], 'Code is expired or not correct!')

    def test_11_reset_password_user_not_exist(self):
        request_body = {
            'code': PASSWORD_RESET_CODE,
            'newPassword': 'NekaSifra789'
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/456789/resetPassword')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'User does not exist!')

    def test_12_reset_password(self):
        request_body = {
            'code': PASSWORD_RESET_CODE,
            'newPassword': 'NekaSifra789'
        }
        response = send_put_request(data=request_body, url=f'{self.base_path}/{self.__class__.user_id}/resetPassword')
        self.assertEqual(response.status_code, 204)

    def test_13_rides_of_user_unauthorized(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/{self.__class__.user_id}/ride', query_params=query_params)
        self.assertEqual(response.status_code, 401)

    def test_14_rides_of_user_forbidden(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/{self.__class__.user_id}/ride', query_params=query_params, jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_15_rides_of_user_not_exist(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/12345/ride', query_params=query_params, jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'User does not exist!')

    def test_16_rides_of_user(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/{self.__class__.user_id}/ride', query_params=query_params, jwt=self.admin)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertTrue(self.__class__.ride_body in response_body['results'])
    
    def test_17_getting_users_unauthorized(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}', query_params=query_params)
        self.assertEqual(response.status_code, 401)

    def test_18_getting_users_forbidden(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}', query_params=query_params, jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_19_getting_users(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}', query_params=query_params, jwt=self.admin)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertTrue(self.__class__.user_body in response_body['results'])

    def test_20_login_wrong_username(self):
        request_body = {
            'email': 'aaaa@gmail.com',
            'password': 'NekaSifra789'
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/login')
        self.assertEqual(response.status_code, 400)
        response_body = response.json()
        self.assertEqual(response_body['message'], 'Wrong username or password!')

    def test_21_login_wrong_password(self):
        request_body = {
            'email': 'pera.peric123321@gmail.com',
            'password': 'NekaRandomSifra869'
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/login')
        self.assertEqual(response.status_code, 400)
        response_body = response.json()
        self.assertEqual(response_body['message'], 'Wrong username or password!')

    def test_22_login_wrong_inputs(self):
        request_body = {
            'email': 'aaaa',
            'password': 'sifra'
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/login')
        self.assertEqual(response.status_code, 400)

    def test_23_login_none_inputs(self):
        request_body = {
            'email': None,
            'password': None
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/login')
        self.assertEqual(response.status_code, 400)

    def test_24_login(self):
        request_body = {
            'email': PASSENGER_EMAIL,
            'password': PASSENGER_PASSWORD
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/login')
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual('accessToken' in response_body, True)
        self.assertEqual('refreshToken' in response_body, True)

    def test_25_send_message_unauthorized(self):
        request_body = {
            'message': 'Some message',
            'type': 'RIDE',
            'rideId': RIDE_ID_FOR_MESSAGES
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/{ADMIN_ID}/message')
        self.assertEqual(response.status_code, 401)

    def test_26_send_message_invalid_inputs(self):
        request_body = {
            'message': 'abcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghij123',
            'type': 'RIDE123',
            'rideId': 'abc'
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/{ADMIN_ID}/message', jwt=self.passenger)
        self.assertEqual(response.status_code, 400)

    def test_27_send_message_none_inputs(self):
        request_body = {
            'message': None,
            'type': None,
            'rideId': None
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/{ADMIN_ID}/message', jwt=self.passenger)
        self.assertEqual(response.status_code, 400)

    def test_28_send_message_receiver_not_exist(self):
        request_body = {
            'message': 'Some message',
            'type': 'RIDE',
            'rideId': RIDE_ID_FOR_MESSAGES
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/123456789/message', jwt=self.passenger)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Receiver does not exist!')

    def test_29_send_message_ride_not_exist(self):
        request_body = {
            'message': 'Some message',
            'type': 'RIDE',
            'rideId': 1234567
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/{ADMIN_ID}/message', jwt=self.passenger)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Ride does not exist!')

    def test_30_send_message(self):
        request_body = {
            'message': 'Some message',
            'type': 'RIDE',
            'rideId': RIDE_ID_FOR_MESSAGES
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/{ADMIN_ID}/message', jwt=self.passenger)
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual('id' in response_body, True)
        self.assertEqual('timeOfSending' in response_body, True)
        self.assertEqual(response_body['senderId'], PASSENGER_ID)
        self.assertEqual(response_body['receiverId'], ADMIN_ID)
        self.assertEqual(response_body['message'], request_body['message'])
        self.assertEqual(response_body['type'], request_body['type'])
        self.assertEqual(response_body['rideId'], RIDE_ID_FOR_MESSAGES)
        self.__class__.message_id = response_body['id']
        self.__class__.message_body = response_body

    def test_31_getting_user_messages_unauthorized(self):
        response = send_get_request(url=f'{self.base_path}/{PASSENGER_ID}/message')
        self.assertEqual(response.status_code, 401)

    def test_32_getting_user_messages_user_not_exist(self):
        response = send_get_request(url=f'{self.base_path}/1234567/message', jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'User does not exist!')

    def test_33_getting_user_messages(self):
        response = send_get_request(url=f'{self.base_path}/{PASSENGER_ID}/message', jwt=self.admin)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertTrue(self.__class__.message_body in response_body['results'])

    def test_34_block_user_unauthorized(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{PASSENGER_ID}/block')
        self.assertEqual(response.status_code, 401)

    def test_35_block_user_forbidden(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{PASSENGER_ID}/block', jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_36_block_user_not_exist(self):
        response = send_put_request(data=None, url=f'{self.base_path}/12345678/block', jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'User does not exist!')

    def test_37_block_user(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{PASSENGER_ID}/block', jwt=self.admin)
        self.assertEqual(response.status_code, 204)

    def test_38_block_user_already_blocked(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{PASSENGER_ID}/block', jwt=self.admin)
        self.assertEqual(response.status_code, 400)
        response_body = response.json()
        self.assertEqual(response_body['message'], 'User already blocked!')

    def test_39_unblock_user_unauthorized(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{PASSENGER_ID}/unblock')
        self.assertEqual(response.status_code, 401)

    def test_40_unblock_user_forbidden(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{PASSENGER_ID}/unblock', jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_41_unblock_user_not_exist(self):
        response = send_put_request(data=None, url=f'{self.base_path}/12345678/unblock', jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'User does not exist!')

    def test_42_unblock_user(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{PASSENGER_ID}/unblock', jwt=self.admin)
        self.assertEqual(response.status_code, 204)

    def test_43_unblock_user_not_blocked(self):
        response = send_put_request(data=None, url=f'{self.base_path}/{PASSENGER_ID}/unblock', jwt=self.admin)
        self.assertEqual(response.status_code, 400)
        response_body = response.json()
        self.assertEqual(response_body['message'], 'User is not blocked!')

    def test_44_send_note_unauthorized(self):
        request_body = {
            'message': 'Some note',
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/{PASSENGER_ID}/note')
        self.assertEqual(response.status_code, 401)

    def test_45_send_note_forbidden(self):
        request_body = {
            'message': 'Some note',
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/{PASSENGER_ID}/note', jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_46_send_note_invalid_inputs(self):
        request_body = {
            'message': 'abcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghij123',
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/{PASSENGER_ID}/note', jwt=self.admin)
        self.assertEqual(response.status_code, 400)

    def test_47_send_note_none_inputs(self):
        request_body = {
            'message': None
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/{PASSENGER_ID}/note', jwt=self.admin)
        self.assertEqual(response.status_code, 400)

    def test_48_send_message_user_not_exist(self):
        request_body = {
            'message': 'Some note'
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/123456789/note', jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'User does not exist!')

    def test_49_send_note(self):
        request_body = {
            'message': 'Some note'
        }
        response = send_post_request(data=request_body, url=f'{self.base_path}/{PASSENGER_ID}/note', jwt=self.admin)
        self.assertEqual(response.status_code, 200)
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual('id' in response_body, True)
        self.assertEqual('date' in response_body, True)
        self.assertEqual(response_body['message'], request_body['message'])
        self.__class__.note_id = response_body['id']
        self.__class__.note_body = response_body

    def test_50_getting_notes_unauthorized(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/{PASSENGER_ID}/note', query_params=query_params)
        self.assertEqual(response.status_code, 401)

    def test_51_getting_notes_forbidden(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/{PASSENGER_ID}/note', query_params=query_params, jwt=self.passenger)
        self.assertEqual(response.status_code, 403)

    def test_52_getting_notes_user_not_exist(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/7654321/note', query_params=query_params, jwt=self.admin)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'User does not exist!')

    def test_53_getting_notes(self):
        query_params = {
            'page': 0,
            'size': 1000,
        }
        response = send_get_request(url=f'{self.base_path}/{PASSENGER_ID}/note', query_params=query_params, jwt=self.admin)
        response_body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.__class__.note_body in response_body['results'], True)
