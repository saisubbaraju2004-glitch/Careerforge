import re
from io import BytesIO
from pathlib import Path

import pytest
from docx import Document
from pypdf import PdfWriter

from app import create_app
from routes import resume as resume_routes
from services import resume_storage
from services.resume_parser import ResumeParser
from services.resume_storage import StorageConfigurationError


class FakeBucket:
    def __init__(self):
        self.upload_call = None
        self.removed = None

    def upload(self, path, content, file_options):
        self.upload_call = (path, content, file_options)

    def remove(self, paths):
        self.removed = paths


class FakeStorage:
    def __init__(self, bucket):
        self.bucket = bucket

    def from_(self, bucket_name):
        assert bucket_name == "resumes"
        return self.bucket


class FakeClient:
    def __init__(self, bucket):
        self.storage = FakeStorage(bucket)


def test_storage_upload_uses_private_user_scoped_uuid_path(monkeypatch):
    bucket = FakeBucket()
    monkeypatch.setattr(
        resume_storage, "_supabase_client", lambda url, key: FakeClient(bucket)
    )

    path = resume_storage.upload_resume(
        supabase_url="https://project.example",
        service_role_key="test-only-key",
        bucket="resumes",
        user_id=42,
        filename="resume.pdf",
        content_type="application/pdf",
        content=b"%PDF-test",
    )

    assert re.fullmatch(r"users/42/resumes/[0-9a-f]{32}\.pdf", path)
    assert bucket.upload_call == (
        path,
        b"%PDF-test",
        {"content-type": "application/pdf", "cache-control": "3600", "upsert": "false"},
    )

    resume_storage.delete_resume(
        supabase_url="https://project.example",
        service_role_key="test-only-key",
        bucket="resumes",
        object_path=path,
    )
    assert bucket.removed == [path]


def test_storage_requires_backend_configuration():
    with pytest.raises(StorageConfigurationError):
        resume_storage.upload_resume(
            supabase_url="",
            service_role_key="",
            bucket="resumes",
            user_id=1,
            filename="resume.txt",
            content_type="text/plain",
            content=b"resume",
        )


@pytest.mark.parametrize(
    ("filename", "mimetype", "header", "expected"),
    [
        ("resume.pdf", "application/pdf", b"%PDF-1.7", True),
        (
            "resume.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            b"PK\x03\x04docx",
            True,
        ),
        ("resume.txt", "text/plain", b"CareerForge plain text resume", True),
        ("resume.pdf", "text/plain", b"not a pdf", False),
        ("../resume.exe", "application/octet-stream", b"bad", False),
    ],
)
def test_upload_type_validation(filename, mimetype, header, expected):
    assert ResumeParser.validate_upload(filename, mimetype, BytesIO(header)) is expected


def test_pdf_docx_and_txt_parse_from_memory():
    pdf = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.write(pdf)
    assert ResumeParser.extract_text_from_bytes(pdf.getvalue(), "resume.pdf") == ""

    docx = BytesIO()
    document = Document()
    document.add_paragraph("Candidate has Python, Flask, and PostgreSQL experience.")
    document.save(docx)
    assert "Python" in ResumeParser.extract_text_from_bytes(docx.getvalue(), "resume.docx")

    assert ResumeParser.extract_text_from_bytes(
        b"Candidate has Python, Flask, and PostgreSQL experience.", "resume.txt"
    ).startswith("Candidate")


def test_local_resume_upload_does_not_write_to_uploads(monkeypatch, tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-only-secret",
            "DATABASE_URL": "sqlite:///" + (tmp_path / "upload-test.sqlite3").as_posix(),
            "SESSION_COOKIE_SECURE": False,
            "RATE_LIMIT_AUTH": 100,
            "RATE_LIMIT_DEFAULT": 100,
            "RATE_LIMIT_AI": 100,
        }
    )
    monkeypatch.setattr(
        resume_routes.ai_service,
        "generate_resume_analysis",
        lambda *args, **kwargs: {
            "strengths": [],
            "improvement_areas": [],
            "bullet_rewrites": [],
            "ats_recommendations": [],
        },
    )
    client = app.test_client()
    registration = client.get("/register")
    csrf = re.search(rb'name="csrf_token" value="([^"]+)"', registration.data)
    assert csrf
    response = client.post(
        "/register",
        data={
            "csrf_token": csrf.group(1).decode(),
            "username": "upload-check",
            "password": "test-password-123",
        },
    )
    assert response.status_code == 302

    uploads_dir = Path(__file__).resolve().parents[1] / "uploads"
    before = {item.name for item in uploads_dir.iterdir()} if uploads_dir.exists() else set()
    response = client.post(
        "/api/analyze-resume",
        data={
            "resume_file": (
                BytesIO(b"Candidate has Python, Flask, SQL, and API development experience."),
                "resume.txt",
            )
        },
        content_type="multipart/form-data",
    )
    after = {item.name for item in uploads_dir.iterdir()} if uploads_dir.exists() else set()

    assert response.status_code == 200
    assert before == after
