import os
import re
from pathlib import Path
from pypdf import PdfReader
from docx import Document

class ResumeParser:
    MIME_TYPES = {
        ".pdf": {"application/pdf", "application/octet-stream"},
        ".docx": {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/octet-stream"
        },
        ".txt": {"text/plain", "application/octet-stream"}
    }

    @staticmethod
    def allowed_file(filename, allowed_extensions):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @staticmethod
    def validate_upload(filename, mimetype, stream):
        extension = Path(filename).suffix.lower()
        if mimetype.lower() not in ResumeParser.MIME_TYPES.get(extension, set()):
            return False

        header = stream.read(1024)
        stream.seek(0)
        if extension == ".pdf":
            return b"%PDF-" in header
        if extension == ".docx":
            return header.startswith(b"PK\x03\x04")
        return b"\x00" not in header

    @staticmethod
    def extract_text(file_path):
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = file_path.suffix.lower()
        if ext == ".pdf":
            return ResumeParser._extract_from_pdf(file_path)
        elif ext == ".docx":
            return ResumeParser._extract_from_docx(file_path)
        elif ext == ".txt":
            return ResumeParser._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def _extract_from_pdf(file_path):
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")
        return text.strip()

    @staticmethod
    def _extract_from_docx(file_path):
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                if paragraph.text:
                    text += paragraph.text + "\n"
        except Exception as e:
            raise ValueError(f"Error parsing DOCX: {str(e)}")
        return text.strip()

    @staticmethod
    def _extract_from_txt(file_path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
        except Exception as e:
            raise ValueError(f"Error reading TXT file: {str(e)}")

    @staticmethod
    def extract_skills_from_text(text, known_skills=None):
        if not known_skills:
            known_skills = [
                "Python", "Flask", "Django", "HTML", "CSS", "JavaScript", "React",
                "Node.js", "SQL", "PostgreSQL", "MySQL", "MongoDB", "REST APIs",
                "Docker", "Git", "Testing", "PyTest", "CI/CD", "AWS", "Tailwind CSS",
                "NumPy", "Pandas", "PyTorch", "Scikit-Learn", "Java", "C++"
            ]
        
        found_skills = []
        text_lower = text.lower()
        for skill in known_skills:
            # Match boundary or word substring safely
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        
        return list(set(found_skills))
