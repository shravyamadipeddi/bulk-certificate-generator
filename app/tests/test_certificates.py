from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import GenerationJob, Certificate


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Bulk Certificate Generator API is running"
    }


def test_create_generation_job():
    payload = {
        "event_name": "Test Workshop",
        "event_date": "2026-10-15",
        "recipients": [
            {
                "name": "Test User",
                "email": "test@example.com"
            }
        ]
    }

    response = client.post(
        "/api/certificates/jobs",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert "job_id" in data
    assert data["status"] in [
        "COMPLETED",
        "COMPLETED_WITH_ERRORS"
    ]
    assert data["total_certificates"] == 1


def test_invalid_email():
    payload = {
        "event_name": "Test Workshop",
        "event_date": "2026-10-15",
        "recipients": [
            {
                "name": "Test User",
                "email": "invalid-email"
            }
        ]
    }

    response = client.post(
        "/api/certificates/jobs",
        json=payload
    )

    assert response.status_code == 422


def test_get_generation_job():
    db = SessionLocal()

    job = GenerationJob(
        event_name="Status Test",
        event_date="2026-10-20",
        total_certificates=1,
        successful_certificates=1,
        failed_certificates=0,
        status="COMPLETED"
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    job_id = job.id
    db.close()

    response = client.get(
        f"/api/certificates/jobs/{job_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert data["status"] == "COMPLETED"
    assert data["total_certificates"] == 1


def test_get_job_certificates():
    db = SessionLocal()

    job = GenerationJob(
        event_name="Certificate Test",
        event_date="2026-10-20",
        total_certificates=1,
        successful_certificates=1,
        failed_certificates=0,
        status="COMPLETED"
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    certificate = Certificate(
        job_id=job.id,
        recipient_name="Test Certificate User",
        recipient_email="certificate@example.com",
        status="SUCCESS",
        file_path="generated_certificates/test.pdf"
    )

    db.add(certificate)
    db.commit()

    job_id = job.id
    db.close()

    response = client.get(
        f"/api/certificates/jobs/{job_id}/certificates"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert "certificates" in data
    assert len(data["certificates"]) == 1
    assert data["certificates"][0]["status"] == "SUCCESS"


def test_get_certificate():
    payload = {
        "event_name": "Download Test",
        "event_date": "2026-10-20",
        "recipients": [
            {
                "name": "Download User",
                "email": "download@example.com"
            }
        ]
    }

    response = client.post(
        "/api/certificates/jobs",
        json=payload
    )

    assert response.status_code == 200

    job_data = response.json()

    certificates_response = client.get(
        f"/api/certificates/jobs/{job_data['job_id']}/certificates"
    )

    assert certificates_response.status_code == 200

    certificate_id = certificates_response.json()["certificates"][0][
        "certificate_id"
    ]

    response = client.get(
        f"/api/certificates/{certificate_id}"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_get_invalid_certificate():
    response = client.get(
        "/api/certificates/999999"
    )

    assert response.status_code == 404


def test_individual_certificate_failure(monkeypatch):

    def mock_generate_certificate(
        certificate_id,
        recipient_name,
        event_name,
        event_date
    ):
        if recipient_name == "Failed User":
            raise Exception("Simulated certificate generation failure")

        return f"generated_certificates/test_{certificate_id}.pdf"

    monkeypatch.setattr(
        "app.routers.certificates.generate_certificate",
        mock_generate_certificate
    )

    payload = {
        "event_name": "Python Workshop",
        "event_date": "2026-10-10",
        "recipients": [
            {
                "name": "Successful User",
                "email": "success@example.com"
            },
            {
                "name": "Failed User",
                "email": "failed@example.com"
            },
            {
                "name": "Another Successful User",
                "email": "another@example.com"
            }
        ]
    }

    response = client.post(
        "/api/certificates/jobs",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_certificates"] == 3
    assert data["successful_certificates"] == 2
    assert data["failed_certificates"] == 1
    assert data["status"] == "COMPLETED_WITH_ERRORS"