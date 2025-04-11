import unittest
import requests


class TestJobsAPI(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:5000/api"

    def test_get_all_jobs(self):
        response = requests.get(f"{self.BASE_URL}/jobs")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("jobs", data)
        self.assertIsInstance(data["jobs"], list)

    def test_get_one_job_success(self):
        job_id = 1
        response = requests.get(f"{self.BASE_URL}/jobs/{job_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("job", data)
        self.assertEqual(data["job"]["id"], job_id)

    def test_get_one_job_invalid_id(self):
        job_id = 999
        response = requests.get(f"{self.BASE_URL}/jobs/{job_id}")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Job not found")

    def test_get_one_job_invalid_string(self):
        invalid_job_id = "string"
        response = requests.get(f"{self.BASE_URL}/jobs/{invalid_job_id}")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Job not found")


if __name__ == "__main__":
    unittest.main()
