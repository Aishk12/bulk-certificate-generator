from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.schemas.certificate import GenerationJobCreate
from app.database.database import get_db, SessionLocal
from app.database.models import Job, Recipient, Certificate
from app.services.certificate_service import generate_certificates_for_job

router = APIRouter()


def run_certificate_generation(job_id: str):
    """
    Background task that generates certificates for a job.
    """

    db = SessionLocal()

    try:
        # Find the job
        job = db.query(Job).filter(Job.id == job_id).first()

        if job:
            generate_certificates_for_job(job, db)

    finally:
        db.close()


@router.post("/api/jobs/")
def create_job(
    request: GenerationJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    # Create the Job
    job = Job(
        event_name=request.event_name,
        course_name=request.course_name,
        date=str(request.date),
        status="PENDING",
        total_count=len(request.recipients)
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # Create Recipients
    for recipient_data in request.recipients:

        recipient = Recipient(
            job_id=job.id,
            name=recipient_data.name,
            email=recipient_data.email,
            status="PENDING"
        )

        db.add(recipient)

    db.commit()

    # Start certificate generation in the background
    background_tasks.add_task(
        run_certificate_generation,
        job.id
    )

    # Return immediately
    return {
        "message": "Generation job created successfully",
        "job_id": job.id,
        "status": job.status,
        "total_count": job.total_count
    }



@router.get("/api/jobs/{job_id}")
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        return {
            "message": "Job not found"
        }

    total = job.total_count
    completed = job.success_count + job.failed_count

    if total > 0:
        progress = int((completed / total) * 100)
    else:
        progress = 0

    recipient_results = []

    for recipient in job.recipients:

        certificate_id = None

        if recipient.certificate:
            certificate_id = recipient.certificate.id

        recipient_results.append({
            "recipient_id": recipient.id,
            "name": recipient.name,
            "email": recipient.email,
            "status": recipient.status,
            "error_message": recipient.error_message,
            "certificate_id": certificate_id
        })

    return {
        "job_id": job.id,
        "event_name": job.event_name,
        "course_name": job.course_name,
        "date": job.date,
        "status": job.status,
        "total_count": total,
        "success_count": job.success_count,
        "failed_count": job.failed_count,
        "progress": progress,
        "recipients": recipient_results
    }



@router.get("/api/certificates/{certificate_id}")
def get_certificate(
    certificate_id: str,
    db: Session = Depends(get_db)
):

    # Find certificate in database
    certificate = (
        db.query(Certificate)
        .filter(Certificate.id == certificate_id)
        .first()
    )

    # Certificate not found
    if not certificate:
        return {
            "message": "Certificate not found"
        }

    # Check whether PDF file exists
    file_path = certificate.file_path

    if not Path(file_path).exists():
        return {
            "message": "Certificate file not found"
        }

    # Return PDF file
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{certificate_id}.pdf"
    )