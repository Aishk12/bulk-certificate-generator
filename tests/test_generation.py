from unittest.mock import patch
from pathlib import Path

from app.services.certificate_service import generate_certificate


def test_generate_certificate():

    certificate_id = "TEST-AUTOMATED-001"

    file_path = generate_certificate(
        recipient_name="Aishwarya Kamble",
        course_name="Python Backend Development",
        event_name="Python Workshop 2026",
        certificate_date="2026-10-08",
        certificate_id=certificate_id
    )

    assert file_path is not None
    assert Path(file_path).exists()
    assert file_path.endswith(".pdf")


def test_individual_certificate_failure():

    from app.database.database import SessionLocal
    from app.database.models import Job, Recipient
    from app.services.certificate_service import generate_certificates_for_job

    db = SessionLocal()

    try:
        job = Job(
            event_name="Failure Test",
            course_name="Python Backend Development",
            date="2026-10-08",
            status="PENDING",
            total_count=2
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        recipient1 = Recipient(
            job_id=job.id,
            name="Aishwarya Kamble",
            email="aishwarya@example.com",
            status="PENDING"
        )

        recipient2 = Recipient(
            job_id=job.id,
            name="Rahul Sharma",
            email="rahul@example.com",
            status="PENDING"
        )

        db.add_all([recipient1, recipient2])
        db.commit()

        original_generate = generate_certificate

        def generate_with_failure(*args, **kwargs):
            if kwargs.get("recipient_name") == "Rahul Sharma":
                raise Exception("Simulated certificate failure")

            return original_generate(*args, **kwargs)

        with patch(
            "app.services.certificate_service.generate_certificate",
            side_effect=generate_with_failure
        ):
            generate_certificates_for_job(job, db)

        db.refresh(job)

        assert job.success_count == 1
        assert job.failed_count == 1
        assert job.status == "COMPLETED_WITH_ERRORS"

        db.refresh(recipient1)
        db.refresh(recipient2)

        assert recipient1.status == "COMPLETED"
        assert recipient2.status == "FAILED"
        assert recipient2.error_message == "Simulated certificate failure"

    finally:
        db.close()



