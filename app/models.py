from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String, nullable=False)
    event_date = Column(String, nullable=False)

    total_certificates = Column(Integer, default=0)
    successful_certificates = Column(Integer, default=0)
    failed_certificates = Column(Integer, default=0)

    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)

    certificates = relationship(
        "Certificate",
        back_populates="job",
        cascade="all, delete-orphan"
    )


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(
        Integer,
        ForeignKey("generation_jobs.id"),
        nullable=False
    )

    recipient_name = Column(String, nullable=False)
    recipient_email = Column(String, nullable=False)

    file_path = Column(String, nullable=True)
    status = Column(String, default="PENDING")
    error_message = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship(
        "GenerationJob",
        back_populates="certificates"
    )