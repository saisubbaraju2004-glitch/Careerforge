from flask import Blueprint, request, jsonify, render_template
from services.job_matching_service import JobMatchingService
from services.ai_service import AIService
from services.career_engine import CareerEngine

jobs_bp = Blueprint("jobs", __name__)
career_engine = CareerEngine()
ai_service = AIService(career_engine=career_engine)
job_matching_service = JobMatchingService(ai_service=ai_service)

@jobs_bp.route("/jobs", methods=["GET"])
def jobs_page():
    return render_template("jobs.html")

@jobs_bp.route("/api/jobs", methods=["GET"])
def get_jobs():
    try:
        filters = {
            "role": request.args.get("role"),
            "location": request.args.get("location"),
            "work_mode": request.args.get("work_mode", "All"),
            "experience": request.args.get("experience", "All")
        }
        jobs = job_matching_service.get_all_jobs(filters)
        return jsonify({"success": True, "data": jobs}), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to retrieve jobs: {str(e)}"}), 500

@jobs_bp.route("/api/jobs/<job_id>", methods=["GET"])
def get_job_detail(job_id):
    try:
        job = job_matching_service.get_job_by_id(job_id)
        if not job:
            return jsonify({"success": False, "error": "Job not found"}), 404
        return jsonify({"success": True, "data": job}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@jobs_bp.route("/api/job-match", methods=["POST"])
def calculate_job_match():
    try:
        data = request.get_json() or {}
        filters = {
            "role": data.get("role_filter"),
            "location": data.get("location_filter"),
            "work_mode": data.get("work_mode", "All"),
            "experience": data.get("experience", "All")
        }
        result = job_matching_service.process_job_matches(data, filters)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to calculate job matches: {str(e)}"}), 500

@jobs_bp.route("/api/job-coach", methods=["POST"])
def job_coach():
    try:
        data = request.get_json() or {}
        job_id = data.get("job_id")
        candidate_profile = data.get("profile", {})
        
        result = job_matching_service.generate_ai_job_pitch(job_id, candidate_profile)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
