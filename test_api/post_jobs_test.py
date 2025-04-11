import unittest
import requests


class TestPostJobsAPI(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:5000/api"

    def test_post_job_success(self):
        data = {
            "job_title": "Test Job",
            "team_leader_id": 1,
            "work_size": 5,
            "collaborators": "2, 3",
            "is_finished": False,
            "categories": [1]
        }

        response = requests.post(f"{self.BASE_URL}/jobs", json=data)
        self.assertEqual(response.status_code, 201)

        response_data = response.json()
        self.assertIn("success", response_data)
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["job"]["job_title"], "Test Job")

        get_response = requests.get(f"{self.BASE_URL}/jobs")
        self.assertEqual(get_response.status_code, 200)
        jobs = get_response.json().get("jobs", [])
        job_titles = [job["job_title"] for job in jobs]
        self.assertIn("Test Job", job_titles)

    def test_post_job_missing_required_field(self):
        data = {
            "team_leader_id": 1,
            "work_size": 5,
            "collaborators": "2, 3",
            "is_finished": False,
            "categories": [1]
        }

        response = requests.post(f"{self.BASE_URL}/jobs", json=data)
        self.assertEqual(response.status_code, 400)

        response_data = response.json()
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Missing required field: job_title")

    def test_post_job_invalid_team_leader_id(self):
        data = {
            "job_title": "Invalid Team Leader",
            "team_leader_id": "not_a_number",
            "work_size": 5,
            "collaborators": "2, 3",
            "is_finished": False,
            "categories": [1]
        }

        response = requests.post(f"{self.BASE_URL}/jobs", json=data)
        self.assertEqual(response.status_code, 400)

        response_data = response.json()
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Invalid data type for team_leader_id or work_size")

    def test_post_job_invalid_categories(self):
        data = {
            "job_title": "Invalid Categories",
            "team_leader_id": 1,
            "work_size": 5,
            "collaborators": "2, 3",
            "is_finished": False,
            "categories": ["not_a_number", 999]
        }

        response = requests.post(f"{self.BASE_URL}/jobs", json=data)
        self.assertEqual(response.status_code, 400)

        response_data = response.json()
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Invalid category IDs")


if __name__ == "__main__":
    unittest.main()

