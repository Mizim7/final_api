import unittest
import requests


class TestDeleteJobsAPI(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:5000/api"

    def setUp(self):
        response = requests.get(f"{self.BASE_URL}/jobs")
        self.assertEqual(response.status_code, 200)
        jobs = response.json().get("jobs", [])
        for job in jobs:
            if job["job_title"] == "Test Job":
                requests.delete(f"{self.BASE_URL}/jobs/{job['id']}")

    def test_delete_job_success(self):
        import uuid
        unique_title = f"Test Job {uuid.uuid4()}"
        data = {
            "job_title": unique_title,
            "team_leader_id": 1,
            "work_size": 5,
            "collaborators": "2, 3",
            "is_finished": False
        }
        post_response = requests.post(f"{self.BASE_URL}/jobs", json=data)
        self.assertEqual(post_response.status_code, 201)
        job_id = post_response.json()["job"]["id"]
        delete_response = requests.delete(f"{self.BASE_URL}/jobs/{job_id}")
        self.assertEqual(delete_response.status_code, 200)
        delete_data = delete_response.json()
        self.assertIn("success", delete_data)
        self.assertTrue(delete_data["success"])
        self.assertEqual(delete_data["message"], "Job deleted successfully")
        get_response = requests.get(f"{self.BASE_URL}/jobs")
        self.assertEqual(get_response.status_code, 200)
        jobs = get_response.json().get("jobs", [])
        job_titles = [job["job_title"] for job in jobs]
        self.assertNotIn(unique_title, job_titles)

    def test_delete_job_not_found(self):
        invalid_job_id = 999
        response = requests.delete(f"{self.BASE_URL}/jobs/{invalid_job_id}")
        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Job not found")

    def test_delete_job_invalid_id(self):
        invalid_job_id = "not_a_number"
        response = requests.delete(f"{self.BASE_URL}/jobs/{invalid_job_id}")
        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Job not found")


if __name__ == "__main__":
    unittest.main()
