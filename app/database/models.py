import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_name = Column(String, nullable=False)
    course_name = Column(String, nullable=False)
    date = Column(String, nullable=False)

    status = Column(String, default="PENDING")

    total_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    recipients = relationship(
        "Recipient",
        back_populates="job",
        cascade="all, delete-orphan"
    )


class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True, autoincrement=True)

    job_id = Column(
        String,
        ForeignKey("jobs.id"),
        nullable=False
    )

    name = Column(String, nullable=False)
    email = Column(String, nullable=False)

    status = Column(String, default="PENDING")
    error_message = Column(String, nullable=True)

    job = relationship(
        "Job",
        back_populates="recipients"
    )

    certificate = relationship(
        "Certificate",
        back_populates="recipient",
        uselist=False,
        cascade="all, delete-orphan"
    )


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    recipient_id = Column(
        Integer,
        ForeignKey("recipients.id"),
        nullable=False
    )

    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    recipient = relationship(
        "Recipient",
        back_populates="certificate"
    )