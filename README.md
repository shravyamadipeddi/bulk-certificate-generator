# Bulk Certificate Generator

A FastAPI-based backend application for generating participation certificates in bulk.

The application accepts event information and a list of recipients, generates a PDF certificate for each recipient, stores generation details in a relational database, tracks the generation status, and provides APIs to retrieve generated certificates.

---

## Features

- Bulk certificate generation
- Recipient input validation
- PDF certificate generation using ReportLab
- SQLite relational database
- Generation job tracking
- Successful and failed certificate tracking
- Individual certificate retrieval/download
- Retrieval of all certificates belonging to a job
- Individual certificate failure handling
- Automated API tests using pytest
- Interactive API documentation using Swagger UI

---

## Technology Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- ReportLab
- Pydantic
- Pytest
- Uvicorn

---

## Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   └── certificates.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── certificate_service.py
│   │
│   └── tests/
│       ├── __init__.py
│       └── test_certificates.py
│
├── generated_certificates/
├── certificates.db
├── requirements.txt
└── README.md