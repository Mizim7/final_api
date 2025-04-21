import unittest
import json
from main import app, db
from models import User


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_users_empty(self):
        response = self.app.get('/api/v2/users')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['users'], [])

    def test_post_user_success(self):
        user_data = {
            "email": "test@example.com",
            "password": "securepassword",
            "name": "Test User",
            "city_from": "Moscow"
        }
        response = self.app.post('/api/v2/users', json=user_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['user']['email'], user_data['email'])

    def test_post_user_missing_fields(self):
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "city_from": "Moscow"
        }
        response = self.app.post('/api/v2/users', json=user_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", data['message'])
        self.assertEqual(data['message']['password'], "Password cannot be blank!")

    def test_post_user_duplicate_email(self):
        user_data = {
            "email": "test@example.com",
            "password": "securepassword",
            "name": "Test User",
            "city_from": "Moscow"
        }
        self.app.post('/api/v2/users', json=user_data)
        response = self.app.post('/api/v2/users', json=user_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'User with this email already exists')

    def test_get_user_by_id_success(self):
        user_data = {
            "email": "test@example.com",
            "password": "securepassword",
            "name": "Test User",
            "city_from": "Moscow"
        }
        post_response = self.app.post('/api/v2/users', json=user_data)
        user_id = json.loads(post_response.data)['user']['id']
        response = self.app.get(f'/api/v2/users/{user_id}')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['user']['id'], user_id)

    def test_get_user_by_id_not_found(self):
        response = self.app.get('/api/v2/users/999')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], 'User not found')

    def test_delete_user_success(self):

        user_data = {
            "email": "test@example.com",
            "password": "securepassword",
            "name": "Test User",
            "city_from": "Moscow"
        }
        post_response = self.app.post('/api/v2/users', json=user_data)
        user_id = json.loads(post_response.data)['user']['id']
        response = self.app.delete(f'/api/v2/users/{user_id}')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'User deleted successfully')

    def test_delete_user_not_found(self):
        response = self.app.delete('/api/v2/users/999')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], 'User not found')


if __name__ == '__main__':
    unittest.main()
