import unittest
import json
from main import app, db
from models import Jobs, Category


class TestJobsAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()

    def test_post_job_success(self):
        """Тест успешного добавления работы."""
        job_data = {
            "job_title": "Develop new AI model",
            "team_leader_id": 1,
            "work_size": 40,
            "collaborators": "2,3",
            "is_finished": False,
            "category_ids": [1, 2]
        }
        response = self.app.post('/api/v2/jobs', json=job_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['job']['job_title'], job_data['job_title'])
        self.assertEqual(data['job']['categories'], ["Engineering", "Science"])

    def test_post_job_invalid_category(self):
        """Тест добавления работы с несуществующей категорией."""
        job_data = {
            "job_title": "Develop new AI model",
            "team_leader_id": 1,
            "work_size": 40,
            "collaborators": "2,3",
            "is_finished": False,
            "category_ids": [999]
        }
        response = self.app.post('/api/v2/jobs', json=job_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'One or more categories do not exist')

    def test_get_job_by_id_success(self):
        """Тест успешного получения работы по ID."""
        job_data = {
            "job_title": "Develop new AI model",
            "team_leader_id": 1,
            "work_size": 40,
            "collaborators": "2,3",
            "is_finished": False,
            "category_ids": [1, 2]
        }
        post_response = self.app.post('/api/v2/jobs', json=job_data)
        job_id = json.loads(post_response.data)['job']['id']
        response = self.app.get(f'/api/v2/jobs/{job_id}')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['job']['id'], job_id)

    def test_get_job_by_id_not_found(self):
        """Тест получения несуществующей работы по ID."""
        response = self.app.get('/api/v2/jobs/999')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], 'Job not found')

    def test_put_job_success(self):
        """Тест успешного обновления работы."""
        job_data = {
            "job_title": "Develop new AI model",
            "team_leader_id": 1,
            "work_size": 40,
            "collaborators": "2,3",
            "is_finished": False,
            "category_ids": [1, 2]
        }
        post_response = self.app.post('/api/v2/jobs', json=job_data)
        job_id = json.loads(post_response.data)['job']['id']

        updated_data = {
            "job_title": "Updated Job Title",
            "team_leader_id": 2,
            "work_size": 50,
            "collaborators": "1,2",
            "is_finished": True,
            "category_ids": [2, 3]
        }
        response = self.app.put(f'/api/v2/jobs/{job_id}', json=updated_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['job']['job_title'], updated_data['job_title'])
        self.assertEqual(data['job']['categories'], ["Science", "Management"])

    def test_delete_job_success(self):
        """Тест успешного удаления работы."""
        job_data = {
            "job_title": "Develop new AI model",
            "team_leader_id": 1,
            "work_size": 40,
            "collaborators": "2,3",
            "is_finished": False,
            "category_ids": [1, 2]
        }
        post_response = self.app.post('/api/v2/jobs', json=job_data)
        job_id = json.loads(post_response.data)['job']['id']

        response = self.app.delete(f'/api/v2/jobs/{job_id}')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Job deleted successfully')

    def test_delete_job_not_found(self):
        """Тест удаления несуществующей работы."""
        response = self.app.delete('/api/v2/jobs/999')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], 'Job not found')


if __name__ == '__main__':
    unittest.main()
