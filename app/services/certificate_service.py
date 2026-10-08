from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from pathlib import Path


# Folder where certificates will be saved
OUTPUT_FOLDER = Path("generated")

OUTPUT_FOLDER.mkdir(exist_ok=True)


def generate_certificate(
    recipient_name,
    course_name,
    event_name,
    certificate_date,
    certificate_id
):
    # Create file name
    file_path = OUTPUT_FOLDER / f"{certificate_id}.pdf"

    # Create PDF
    pdf = canvas.Canvas(
        str(file_path),
        pagesize=A4
    )

    width, height = A4

    # Title
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(
        width / 2,
        height - 70 * mm,
        "CERTIFICATE OF COMPLETION"
    )

    # Subtitle
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(
        width / 2,
        height - 95 * mm,
        "This certificate is proudly presented to"
    )

    # Recipient name
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(
        width / 2,
        height - 115 * mm,
        recipient_name
    )

    # Course
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(
        width / 2,
        height - 140 * mm,
        f"for successfully completing {course_name}"
    )

    # Event
    pdf.drawCentredString(
        width / 2,
        height - 155 * mm,
        f"Event: {event_name}"
    )

    # Date
    pdf.drawCentredString(
        width / 2,
        height - 170 * mm,
        f"Date: {certificate_date}"
    )

    # Certificate ID
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(
        width / 2,
        30 * mm,
        f"Certificate ID: {certificate_id}"
    )

    # Save PDF
    pdf.save()

    return str(file_path)


# Generate certificates for all recipients in a job
def generate_certificates_for_job(job, db):

    # Import Certificate model
    from app.database.models import Certificate

    # Change job status
    job.status = "PROCESSING"
    db.commit()

    # Process every recipient
    for recipient in job.recipients:

        try:
            # Generate unique certificate ID
            import uuid

            certificate_id = str(uuid.uuid4())

            # Generate PDF
            file_path = generate_certificate(
                recipient_name=recipient.name,
                course_name=job.course_name,
                event_name=job.event_name,
                certificate_date=job.date,
                certificate_id=certificate_id
            )

            # Save certificate information in database
            certificate = Certificate(
                id=certificate_id,
                recipient_id=recipient.id,
                file_path=file_path
            )

            db.add(certificate)

            # Mark recipient as successful
            recipient.status = "COMPLETED"
            recipient.error_message = None

            # Increase successful count
            job.success_count += 1

        except Exception as e:

            # Mark only this recipient as failed
            recipient.status = "FAILED"
            recipient.error_message = str(e)

            # Increase failed count
            job.failed_count += 1

        # Save changes after each recipient
        db.commit()

    # Determine final job status
    if job.failed_count == 0:
        job.status = "COMPLETED"

    elif job.success_count == 0:
        job.status = "FAILED"

    else:
        job.status = "COMPLETED_WITH_ERRORS"

    db.commit()