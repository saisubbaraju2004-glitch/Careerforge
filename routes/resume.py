import uuid
from datetime import datetime, timezone
from pathlib import Path
from flask import Blueprint, current_app, g, request, jsonify, render_template
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from config.config import Config
from services.resume_parser import ResumeParser
from services.ats_engine import ATSEngine
from services.career_engine import CareerEngine
from services.ai_service import AIService
from services.resume_builder_service import ResumeBuilderService
from services.job_matching_service import JobMatchingService
from services.user_store import add_user_record
from services.resume_storage import (
    StorageConfigurationError,
    StorageOperationError,
    delete_resume,
    upload_resume,
)

resume_bp = Blueprint("resume", __name__)
career_engine = CareerEngine()
ats_engine = ATSEngine(career_engine=career_engine)
ai_service = AIService(career_engine=career_engine)
resume_builder_service = ResumeBuilderService(ai_service=ai_service)
job_matching_service = JobMatchingService(ai_service=ai_service)

@resume_bp.route("/resume-builder", methods=["GET"])
def resume_builder_page():
    return render_template("resume_builder.html")

@resume_bp.route("/api/analyze-resume", methods=["POST"])
def analyze_resume():
    stored_object_path = None
    try:
        file = request.files.get("resume_file") or request.files.get("resume") or request.files.get("file")
        if not file:
            return jsonify({"success": False, "error": "No resume file uploaded."}), 400

        if file.filename == "":
            return jsonify({"success": False, "error": "Selected file is empty."}), 400

        if not ResumeParser.allowed_file(file.filename, Config.ALLOWED_EXTENSIONS):
            return jsonify({
                "success": False,
                "error": f"Invalid file type. Allowed formats: {', '.join(Config.ALLOWED_EXTENSIONS)}"
            }), 400
        if not ResumeParser.validate_upload(file.filename, file.mimetype or "", file.stream):
            return jsonify({
                "success": False,
                "error": "File content or MIME type does not match the selected resume format."
            }), 400

        filename = secure_filename(file.filename)
        if not filename:
            return jsonify({"success": False, "error": "Invalid filename."}), 400
        extension = Path(filename).suffix.lower()
        content = file.stream.read(current_app.config["MAX_CONTENT_LENGTH"] + 1)
        if len(content) > current_app.config["MAX_CONTENT_LENGTH"]:
            limit_mb = current_app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
            return jsonify({"success": False, "error": f"Resume file exceeds the {limit_mb}MB limit."}), 413
        if not content:
            return jsonify({"success": False, "error": "Selected file is empty."}), 400

        target_role_id = request.form.get("target_role", "python_backend_developer")
        declared_skills_raw = request.form.get("current_skills", "")
        declared_skills = [s.strip() for s in declared_skills_raw.split(",") if s.strip()]

        # 1. Extract resume text
        try:
            resume_text = ResumeParser.extract_text_from_bytes(content, filename)
        except Exception:
            return jsonify({"success": False, "error": "Unable to parse the uploaded resume."}), 400
        if not resume_text or len(resume_text.strip()) < 20:
            return jsonify({
                "success": False,
                "error": "Could not extract readable text from document. Please upload a clear PDF or DOCX file."
            }), 400

        # 2. Extract found skills
        parsed_skills = ResumeParser.extract_skills_from_text(resume_text)
        all_skills = list(set(declared_skills + parsed_skills))

        # 3. Deterministic ATS Score calculation
        ats_result = ats_engine.calculate_ats_score(resume_text, target_role_id, declared_skills=all_skills)

        # 4. AI-Enhanced feedback & bullet rewrites
        role_title = target_role_id.replace("_", " ").title()
        ai_feedback = ai_service.generate_resume_analysis(
            role_title,
            all_skills,
            resume_text,
            weak_bullets=ats_result.get("weak_bullets")
        )

        payload = {
            "ats_score": ats_result["overall_ats"],
            "score_breakdown": ats_result["breakdown"],
            "parsed_skills": parsed_skills,
            "strengths": ai_feedback.get("strengths", []),
            "missing_keywords": ats_result.get("missing_keywords", []),
            "improvement_areas": ai_feedback.get("improvement_areas", []),
            "bullet_rewrites": ai_feedback.get("bullet_rewrites", []),
            "ats_recommendations": ai_feedback.get("ats_recommendations", [])
        }
        record = {
            "ats_score": payload["ats_score"],
            "skills": payload["parsed_skills"],
            "target_role": role_title,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }
        if current_app.config["DATABASE_URL"].startswith("postgresql+psycopg://"):
            content_type = ResumeParser.canonical_mimetype(filename)
            stored_object_path = upload_resume(
                supabase_url=current_app.config["SUPABASE_URL"],
                service_role_key=current_app.config["SUPABASE_SERVICE_ROLE_KEY"],
                bucket=current_app.config["SUPABASE_STORAGE_BUCKET"],
                user_id=g.user_id,
                filename=filename,
                content_type=content_type,
                content=content,
            )
            record["storage"] = {
                "provider": "supabase",
                "bucket": current_app.config["SUPABASE_STORAGE_BUCKET"],
                "object_path": stored_object_path,
                "filename": filename,
                "content_type": content_type,
                "size_bytes": len(content),
            }

        try:
            add_user_record(
                current_app.config["DATABASE_URL"],
                g.user_id,
                "resume",
                uuid.uuid4().hex,
                record,
            )
        except Exception:
            if stored_object_path:
                try:
                    delete_resume(
                        supabase_url=current_app.config["SUPABASE_URL"],
                        service_role_key=current_app.config["SUPABASE_SERVICE_ROLE_KEY"],
                        bucket=current_app.config["SUPABASE_STORAGE_BUCKET"],
                        object_path=stored_object_path,
                    )
                except StorageOperationError:
                    current_app.logger.error("Failed to remove an unreferenced resume object.")
            raise

        return jsonify({"success": True, "data": payload}), 200

    except RequestEntityTooLarge:
        limit_mb = current_app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
        return jsonify({
            "success": False,
            "error": f"Uploaded file exceeds maximum limit ({limit_mb}MB)."
        }), 413
    except StorageConfigurationError:
        return jsonify({"success": False, "error": "Resume storage is not configured."}), 503
    except StorageOperationError:
        return jsonify({"success": False, "error": "Resume storage is temporarily unavailable."}), 503
    except Exception as error:
        current_app.logger.error("Resume analysis failed (%s)", type(error).__name__)
        return jsonify({"success": False, "error": "Resume analysis failed."}), 500

# V5 AI Resume Builder API Endpoints

@resume_bp.route("/api/resume-builder/generate-summary", methods=["POST"])
def generate_summary():
    try:
        data = request.get_json() or {}
        result = resume_builder_service.generate_summary(data)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@resume_bp.route("/api/resume-builder/improve-bullet", methods=["POST"])
def improve_bullet():
    try:
        data = request.get_json() or {}
        bullet = data.get("bullet", "")
        context = data.get("context", "")
        result = resume_builder_service.improve_bullet(bullet, context)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@resume_bp.route("/api/resume-builder/analyze", methods=["POST"])
def analyze_builder_resume():
    try:
        data = request.get_json() or {}
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Request body must be a JSON object."}), 400
        resume_text = data.get("resume_text", "")
        if not isinstance(resume_text, str):
            return jsonify({"success": False, "error": "resume_text must be a string."}), 400
        if len(resume_text) > 30000:
            return jsonify({"success": False, "error": "resume_text must be 30000 characters or fewer."}), 400
        job_id = data.get("job_id")
        target_job = job_matching_service.get_job_by_id(job_id) if job_id else None
        
        result = resume_builder_service.calculate_ats_score(data, target_job)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@resume_bp.route("/api/resume-builder/optimize", methods=["POST"])
def optimize_builder_resume():
    try:
        data = request.get_json() or {}
        job_id = data.get("job_id")
        target_job = job_matching_service.get_job_by_id(job_id) if job_id else None

        result = resume_builder_service.optimize_resume(data, target_job)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@resume_bp.route("/api/resume-builder/template/<template_id>", methods=["GET"])
def get_template(template_id):
    templates = {
        "modern": {"name": "Modern", "font": "Plus Jakarta Sans", "accent": "#4f46e5"},
        "professional": {"name": "Professional", "font": "Georgia, serif", "accent": "#1e293b"},
        "minimal": {"name": "Minimal", "font": "JetBrains Mono, monospace", "accent": "#000000"}
    }
    tmpl = templates.get(template_id, templates["modern"])
    return jsonify({"success": True, "data": tmpl}), 200

@resume_bp.route("/api/resume-builder/export", methods=["POST"])
def export_resume():
    try:
        data = request.get_json() or {}
        # Returns export status payload for client-side print / PDF rendering
        return jsonify({
            "success": True,
            "data": {
                "format": "pdf",
                "template": data.get("template", "modern"),
                "status": "ready"
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
