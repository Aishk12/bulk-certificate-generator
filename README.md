# Bulk Certificate Generator

A backend API built with **Python and FastAPI** for generating certificates in bulk from a predefined certificate template.

The application accepts a list of recipients, creates a certificate generation job, generates one PDF certificate for each recipient, tracks the generation progress, handles individual failures without stopping the complete job, and provides an API to retrieve generated certificates.

---

## Features

* Create bulk certificate generation jobs
* Accept multiple recipients in a single request
* Validate recipient names and email addresses
* Generate individual PDF certificates
* Use a predefined certificate template
* Process certificate generation in the background
* Track job status and generation progress
* Track individual recipient status
* Handle individual certificate generation failures independently
* Retrieve generated certificates through an API
* Store job, recipient, and certificate information in a relational database
* Automated tests using pytest
* Interactive API documentation using Swagger UI

---

## Technology Stack

* **Python**
* **FastAPI** – REST API framework
* **SQLite** – Relational database for local development
* **SQLAlchemy** – Database ORM
* **Pydantic** – Request validation
* **ReportLab** – PDF certificate generation
* **Uvicorn** – ASGI server
* **pytest** – Automated testing
* **HTTPX** – API testing support

---

## Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── __init__.py
│   │
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── certificate.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── certificate_service.py
│       └── job_service.py
│
├── generated/
│   └── .gitkeep
│
├── templates/
│   └── certificate_template.py
│
├── tests/
│   ├── __init__.py
│   ├── test_jobs.py
│   ├── test_validation.py
│   ├── test_generation.py
│   └── test_certificates.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## How the Application Works

The application follows this workflow:

```text
Client
   |
   | POST /api/jobs/
   v
Create Generation Job
   |
   v
Validate Recipient Data
   |
   v
Store Job + Recipients in Database
   |
   v
Start Background Certificate Generation
   |
   +-------------------+
   |                   |
   v                   v
Recipient 1        Recipient 2
   |                   |
   v                   v
Generate PDF       Generate PDF
   |                   |
   v                   v
COMPLETED          COMPLETED / FAILED
   |                   |
   +---------+---------+
             |
             v
       Update Job Status
             |
             v
GET /api/jobs/{job_id}
             |
             v
View Progress & Results
             |
             v
GET /api/certificates/{certificate_id}
             |
             v
Download/View PDF
```

Each recipient is processed independently. If certificate generation fails for one recipient, the other valid recipients continue to be processed.

---

## Database Design

The application uses three main tables.

### 1. Jobs

Stores information about each certificate generation request.

Important fields:

* `id`
* `event_name`
* `course_name`
* `date`
* `status`
* `total_count`
* `success_count`
* `failed_count`
* `created_at`
* `completed_at`

### 2. Recipients

Stores individual recipient information for each job.

Important fields:

* `id`
* `job_id`
* `name`
* `email`
* `status`
* `error_message`

### 3. Certificates

Stores information about successfully generated certificates.

Important fields:

* `id`
* `recipient_id`
* `file_path`
* `created_at`

### Relationship

```text
Job
 |
 | 1
 |
 |----< Many Recipients
              |
              | 0 or 1
              |
              v
         Certificate
```

One job can contain multiple recipients.

Each recipient can have zero or one generated certificate.

---

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Move into the project directory:

```bash
cd bulk-certificate-generator
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

For Windows:

```bash
venv\Scripts\activate
```

For macOS/Linux:

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run the Application

Start the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

FastAPI automatically provides interactive Swagger documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

The Swagger UI can be used to test the API endpoints directly from the browser.

---

# API Endpoints

## 1. Create Generation Job

### Endpoint

```text
POST /api/jobs/
```

Creates a new certificate generation job for a list of recipients.

### Request Body

```json
{
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
```

### Example Response

```json
{
    "message": "Generation job created successfully",
    "job_id": "generated-job-id",
    "status": "PENDING",
    "total_count": 2
}
```

The returned `job_id` is used to check the generation status.

---

## 2. Get Job Status

### Endpoint

```text
GET /api/jobs/{job_id}
```

Returns the current status and progress of a generation job.

### Example

```text
GET /api/jobs/generated-job-id
```

### Example Response

```json
{
    "job_id": "generated-job-id",
    "event_name": "Python Workshop 2026",
    "course_name": "Python Backend Development",
    "date": "2026-10-08",
    "status": "COMPLETED",
    "total_count": 2,
    "success_count": 2,
    "failed_count": 0,
    "progress": 100,
    "recipients": [
        {
            "recipient_id": 1,
            "name": "Aishwarya Kamble",
            "email": "aishwarya@example.com",
            "status": "COMPLETED",
            "error_message": null,
            "certificate_id": "certificate-id"
        }
    ]
}
```

### Job Statuses

The application supports the following statuses:

* `PENDING` – Job has been created but processing has not started
* `PROCESSING` – Certificate generation is in progress
* `COMPLETED` – All certificates were generated successfully
* `COMPLETED_WITH_ERRORS` – Some certificates succeeded and some failed
* `FAILED` – All certificate generations failed

---

## 3. Retrieve Certificate

### Endpoint

```text
GET /api/certificates/{certificate_id}
```

Returns the generated certificate PDF.

### Example

```text
GET /api/certificates/certificate-id
```

The API returns the certificate as a PDF file.

Generated certificates are stored in the:

```text
generated/
```

directory.

---

# Input Validation

Recipient data is validated using Pydantic.

The following validations are implemented:

### Recipient Name

* Minimum length: 2 characters
* Maximum length: 100 characters

### Email

The email address must have a valid email format.

### Event Name

* Minimum length: 2 characters
* Maximum length: 200 characters

### Course Name

* Minimum length: 2 characters
* Maximum length: 200 characters

### Recipients

At least one recipient is required.

Invalid requests are rejected with HTTP status:

```text
422 Unprocessable Entity
```

---

# Error Handling

A major design requirement is that one failed recipient should not stop the complete generation job.

For example, if a job contains 3 recipients:

```text
Recipient 1 → SUCCESS
Recipient 2 → FAILURE
Recipient 3 → SUCCESS
```

The final job status becomes:

```text
COMPLETED_WITH_ERRORS
```

The job will contain:

```text
Total:     3
Successful: 2
Failed:     1
Progress:  100%
```

The failed recipient also stores an error message that can be viewed through the job status API.

This allows successful certificates to remain available even when another certificate fails.

---

# Background Processing

Certificate generation is performed using FastAPI `BackgroundTasks`.

When a client creates a job:

1. The job is stored in the database.
2. The recipient information is stored.
3. The API returns the `job_id`.
4. Certificate generation runs as a background task.
5. The database is updated as each recipient is processed.
6. The client can use the job status endpoint to monitor progress.

This approach prevents the client request from having to wait for the complete batch generation process.

For a production system with very large workloads, a dedicated task queue such as Celery or another distributed job-processing system could be considered.

---

# Certificate Generation

Certificates are generated as PDF files using ReportLab.

Each certificate contains:

* Certificate title
* Recipient name
* Course name
* Event name
* Completion date
* Unique certificate ID

Each certificate receives a unique ID generated using UUID.

Example:

```text
generated/
├── 7b3c....pdf
├── 91af....pdf
└── c42d....pdf
```

---

# Testing

The project includes automated tests using pytest.

Run all tests with:

```bash
python -m pytest -v
```

The test suite covers:

* Creating a generation job
* Retrieving job status
* Input validation
* Certificate PDF generation
* Individual certificate generation failure
* Retrieving a generated certificate

Current test result:

```text
6 passed
```

---

# Test Scenarios

### Job Creation

Verifies that a valid request creates a generation job and returns a job ID.

### Input Validation

Tests invalid recipient email data and verifies that the API rejects invalid input.

### Certificate Generation

Verifies that a PDF certificate is successfully created.

### Individual Failure

Simulates a certificate generation failure for one recipient and verifies that:

* The failed recipient is marked as `FAILED`
* The error message is stored
* Other recipients continue processing
* The job is marked as `COMPLETED_WITH_ERRORS`

### Certificate Retrieval

Verifies that a generated certificate can be retrieved through the certificate endpoint and returned as a PDF.

---

# Design Decisions

## FastAPI

FastAPI was selected because it provides:

* Simple REST API development
* Automatic request validation
* Automatic Swagger documentation
* Good support for asynchronous/background processing
* Python type hints

## SQLite

SQLite was selected for local development because it is lightweight and does not require a separate database server.

For production deployment, the application can be migrated to PostgreSQL or another relational database.

## SQLAlchemy

SQLAlchemy is used as the ORM to manage database models and relationships.

## ReportLab

ReportLab is used to generate PDF certificates programmatically from the predefined certificate layout.

## BackgroundTasks

FastAPI BackgroundTasks was selected for this implementation because the assignment supports background processing and the expected workload is relatively small.

For a high-volume production system, a distributed task queue would be more appropriate.

## Failure Isolation

Certificate generation is performed inside an individual `try/except` block for each recipient.

This ensures that one failure does not terminate the complete batch.

---

# Future Improvements

Possible improvements for a production-ready version include:

* PostgreSQL database
* Celery or another distributed task queue
* Redis for task management
* Authentication and authorization
* Certificate template upload
* Email delivery of generated certificates
* Certificate verification endpoint
* Bulk CSV/Excel recipient upload
* Pagination for large jobs
* Cloud storage such as AWS S3
* Docker containerization
* Structured application logging
* Retry mechanism for failed certificates
* Rate limiting
* Production deployment configuration

---

# Example Usage

### Step 1 – Start the server

```bash
uvicorn app.main:app --reload
```

### Step 2 – Open Swagger

```text
http://127.0.0.1:8000/docs
```

### Step 3 – Create a job

Send a POST request to:

```text
/api/jobs/
```

with recipient information.

### Step 4 – Copy the job ID

The API returns a unique `job_id`.

### Step 5 – Check job status

Use:

```text
GET /api/jobs/{job_id}
```

to monitor:

* Total recipients
* Successful certificates
* Failed certificates
* Progress percentage
* Individual recipient status
* Certificate IDs

### Step 6 – Retrieve certificates

For a successfully generated recipient, use the returned `certificate_id`:

```text
GET /api/certificates/{certificate_id}
```

The generated PDF certificate will be returned.

---

# Project Objective

The objective of this project is to demonstrate backend development skills including:

* REST API development
* Request validation
* Database design
* ORM usage
* Background processing
* PDF generation
* Error handling
* Job and progress tracking
* Automated testing

The project is designed as a small but complete backend system that can be extended for production use.

