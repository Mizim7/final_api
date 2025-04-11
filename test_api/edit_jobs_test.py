import unittest
import requests


class TestUpdateJobsAPI(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:5000/api"

    def setUp(self):
        data = {
            "job_title": "Test Job",
            "team_leader_id": 1,
            "work_size": 5,
            "collaborators": "2, 3",
            "is_finished": False
        }
        post_response = requests.post(f"{self.BASE_URL}/jobs", json=data)
        self.assertEqual(post_response.status_code, 201)
        self.job_id = post_response.json()["job"]["id"]

    def tearDown(self):
        requests.delete(f"{self.BASE_URL}/jobs/{self.job_id}")

    def test_update_job_success(self):
        data = {
            "job_title": "Updated Job Title",
            "team_leader_id": 2,
            "work_size": 10,
            "collaborators": "5, 6",
            "is_finished": True
        }
        response = requests.put(f"{self.BASE_URL}/jobs/{self.job_id}", json=data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("success", response_data)
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["job"]["job_title"], "Updated Job Title")
        get_response = requests.get(f"{self.BASE_URL}/jobs")
        self.assertEqual(get_response.status_code, 200)
        jobs = get_response.json().get("jobs", [])
        job_titles = [job["job_title"] for job in jobs]
        self.assertIn("Updated Job Title", job_titles)

    def test_update_job_not_found(self):
        invalid_job_id = 999
        data = {
            "job_title": "Updated Job Title",
            "team_leader_id": 2,
            "work_size": 10,
            "collaborators": "5, 6",
            "is_finished": True
        }
        response = requests.put(f"{self.BASE_URL}/jobs/{invalid_job_id}", json=data)
        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Job not found")

    def test_update_job_invalid_data(self):
        data = {
            "job_title": "Updated Job Title",
            "team_leader_id": "not_a_number",
            "work_size": 10,
            "collaborators": "5, 6",
            "is_finished": True
        }
        response = requests.put(f"{self.BASE_URL}/jobs/{self.job_id}", json=data)
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Invalid data type for one or more fields")


if __name__ == "__main__":
    unittest.main()
