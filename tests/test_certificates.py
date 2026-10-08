
from fastapi.testclient import TestClient

from app.main import app
from app.database.database import SessionLocal
from app.database.models import Certificate


client = TestClient(app)


def test_get_certificate():

    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Certificate Retrieval Test",
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

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    db = SessionLocal()

    try:
        certificate = (
            db.query(Certificate)
            .join(Certificate.recipient)
            .filter(Certificate.recipient.has(job_id=job_id))
            .first()
        )

        assert certificate is not None

        certificate_id = certificate.id

    finally:
        db.close()

    response = client.get(
        f"/api/certificates/{certificate_id}"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

