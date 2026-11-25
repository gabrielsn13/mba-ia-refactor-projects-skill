import os
import unittest

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_URI", "sqlite:///:memory:")

from src.app import create_app
from src.database.db import db


class SmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config.update(TESTING=True)
        cls.client = cls.app.test_client()
        with cls.app.app_context():
            db.create_all()

    def test_public_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_tasks_require_authentication(self):
        response = self.client.get("/tasks")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
