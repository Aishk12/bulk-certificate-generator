
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_job():
    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop 2026",
            "course_name": "Python Backend Development",
            "date": "2026-10-08",
            "recipients": [
                {
                    "name": "Aishwarya Kamble",
                    "email": "aishwarya@example.com"
                },
                {
                    "name": "Rahul Sharma",
                    "email": "rahul@example.com"
                }
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Generation job created successfully"
    assert "job_id" in data
    assert data["status"] == "PENDING"
    assert data["total_count"] == 2


def test_get_job_status():

    create_response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Status Test",
            "course_name": "Python Backend Development",
            "date": "2026-10-08",
            "recipients": [
                {
                    "name": "Aishwarya Kamble",
                    "email": "aishwarya@example.com"
                }
            ]
        }
    )

    assert create_response.status_code == 200

    job_id = create_response.json()["job_id"]

    response = client.get(f"/api/jobs/{job_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert data["total_count"] == 1
    assert "success_count" in data
    assert "failed_count" in data
    assert "progress" in data
    assert "recipients" in data

