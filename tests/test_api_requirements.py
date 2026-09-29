import os
import unittest

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://user:pass@localhost:5432/testdb")

from fastapi.testclient import TestClient

import main


class ApiRequirementsTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_image_upload_requires_allowed_file(self):
        response = self.client.post(
            "/images",
            files={"file": ("bad.txt", b"not an image", "text/plain")},
        )
        self.assertEqual(response.status_code, 400)

    def test_image_upload_with_valid_image_calls_s3(self):
        class FakeS3Client:
            def upload_fileobj(self, fileobj, bucket, key):
                assert bucket == "test-bucket"
                assert key.startswith("images/")
                assert fileobj.read() == b"fake-image"

        def fake_boto3_session(*args, **kwargs):
            return type(
                "Session",
                (),
                {"client": lambda self, service: FakeS3Client()},
            )()

        os.environ["AWS_S3_BUCKET"] = "test-bucket"
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
        os.environ["AWS_ACCESS_KEY_ID"] = "test"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
        original_session = main.boto3.Session
        main.boto3.Session = fake_boto3_session
        try:
            response = self.client.post(
                "/images",
                files={"file": ("image.png", b"fake-image", "image/png")},
            )
        finally:
            main.boto3.Session = original_session

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["message"], "Image uploaded successfully")
        self.assertEqual(payload["bucket"], "test-bucket")


if __name__ == "__main__":
    unittest.main()
