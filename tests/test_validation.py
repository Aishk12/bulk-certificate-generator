from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_invalid_email():
    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop 2026",
            "course_name": "Python Backend Development",
            "date": "2026-10-08",
            "recipients": [
                {
                    "name": "Aishwarya Kamble",
                    "email": "invalid-email"
                }
            ]
        }
    )

    assert response.status_code == 422

