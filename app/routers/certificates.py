from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import GenerationJob, Certificate
from ..schemas import GenerationJobCreate
from ..services.certificate_service import generate_certificate


router = APIRouter(
    prefix="/api/certificates",
    tags=["Certificates"]
)


# ---------------------------------------------------------
# 1. CREATE BULK CERTIFICATE GENERATION JOB
# ---------------------------------------------------------

@router.post("/jobs")
def create_generation_job(
    job_data: GenerationJobCreate,
    db: Session = Depends(get_db)
):
    # Create generation job
    job = GenerationJob(
        event_name=job_data.event_name,
        event_date=job_data.event_date,
        status="PENDING",
        total_certificates=len(job_data.recipients),
        successful_certificates=0,
        failed_certificates=0
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # Generate certificates for each recipient
    for recipient in job_data.recipients:

        certificate = Certificate(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=recipient.email,
            status="PENDING"
        )

        db.add(certificate)
        db.commit()
        db.refresh(certificate)

        try:
            # Generate PDF
            file_path = generate_certificate(certificate.id,
                recipient.name,
                job_data.event_name,
                job_data.event_date
            )

            # Update certificate
            certificate.status = "SUCCESS"
            certificate.file_path = file_path

            job.successful_certificates += 1

        except Exception as e:

            certificate.status = "FAILED"
            certificate.error_message = str(e)

            job.failed_certificates += 1

        db.commit()

    # Update final job status
    if job.failed_certificates == 0:
        job.status = "COMPLETED"
    elif job.successful_certificates == 0:
        job.status = "FAILED"
    else:
        job.status = "COMPLETED_WITH_ERRORS"

    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "status": job.status,
        "total_certificates": job.total_certificates,
        "successful_certificates": job.successful_certificates,
        "failed_certificates": job.failed_certificates,
        "message": "Certificate generation completed"
    }


# ---------------------------------------------------------
# 2. GET GENERATION JOB STATUS
# ---------------------------------------------------------

@router.get("/jobs/{job_id}")
def get_generation_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id
    ).first()

    if not job:
        return {
            "error": "Generation job not found"
        }

    return {
        "job_id": job.id,
        "event_name": job.event_name,
        "event_date": job.event_date,
        "status": job.status,
        "total_certificates": job.total_certificates,
        "successful_certificates": job.successful_certificates,
        "failed_certificates": job.failed_certificates
    }


# ---------------------------------------------------------
# 3. GET ALL CERTIFICATES FOR A JOB
# ---------------------------------------------------------

@router.get("/jobs/{job_id}/certificates")
def get_job_certificates(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id
    ).first()

    if not job:
        return {
            "error": "Generation job not found"
        }

    certificates = db.query(Certificate).filter(
        Certificate.job_id == job_id
    ).all()

    return {
        "job_id": job_id,
        "certificates": [
            {
                "certificate_id": certificate.id,
                "recipient_name": certificate.recipient_name,
                "recipient_email": certificate.recipient_email,
                "status": certificate.status,
                "download_url": (
                    f"/api/certificates/{certificate.id}"
                    if certificate.status == "SUCCESS"
                    else None
                ),
                "error_message": certificate.error_message
            }
            for certificate in certificates
        ]
    }


# ---------------------------------------------------------
# 4. DOWNLOAD / RETRIEVE INDIVIDUAL CERTIFICATE
# ---------------------------------------------------------

@router.get("/{certificate_id}")
def get_certificate(
    certificate_id: int,
    db: Session = Depends(get_db)
):
    certificate = db.query(Certificate).filter(
        Certificate.id == certificate_id
    ).first()

    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    if certificate.status != "SUCCESS":
        return {
            "error": "Certificate was not generated successfully"
        }

    return FileResponse(
        path=certificate.file_path,
        media_type="application/pdf",
        filename=f"certificate_{certificate.id}.pdf"
    )