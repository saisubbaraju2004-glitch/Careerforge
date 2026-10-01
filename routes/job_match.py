from flask import Blueprint, render_template, request, jsonify
from services.job_match_service import JobMatchService
from services.ai_service import AIService

job_match_bp = Blueprint("job_match", __name__)
ai_service = AIService()
job_match_service = JobMatchService(ai_service)

@job_match_bp.route("/job-match")
def job_match_page():
    return render_template("job_match.html")

@job_match_bp.route("/job-match/job/<job_id>")
def job_match_detail_page(job_id):
    return render_template("job_match_detail.html", job_id=job_id)

@job_match_bp.route("/api/job-match/jobs", methods=["GET"])
def get_job_matches():
    try:
        matches = job_match_service.get_all_job_matches()
        return jsonify({
            "success": True,
            "count": len(matches),
            "jobs": matches
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@job_match_bp.route("/api/job-match/top", methods=["GET"])
def get_top_target_jobs():
    try:
        count = request.args.get("count", 4, type=int)
        top_jobs = job_match_service.get_top_target_jobs(count=count)
        return jsonify({
            "success": True,
            "count": len(top_jobs),
            "top_jobs": top_jobs
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@job_match_bp.route("/api/job-match/analyze", methods=["POST"])
def analyze_custom_job():
    try:
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Request body must be a JSON object."}), 400
        job_title = data.get("title", "Target Role")
        company = data.get("company", "Target Company")
        job_description = data.get("description", "")
        resume_text = data.get("resume_text", "")
        if any(not isinstance(value, str) for value in (job_title, company, job_description, resume_text)):
            return jsonify({"success": False, "error": "Job and resume fields must be strings."}), 400

        candidate_profile = job_match_service.get_candidate_profile(resume_text=resume_text)
        
        if job_description:
            result = job_match_service.analyze_custom_job_description(
                job_title=job_title,
                company_name=company,
                job_description=job_description,
                candidate_profile=candidate_profile
            )
        else:
            top_jobs = job_match_service.get_top_target_jobs(candidate_profile=candidate_profile, count=1)
            result = top_jobs[0] if top_jobs else {}

        return jsonify({
            "success": True,
            "candidate_profile": candidate_profile,
            "match": result
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@job_match_bp.route("/api/job-match/job/<job_id>", methods=["GET", "POST"])
def get_job_match_detail(job_id):
    try:
        data = (request.get_json(silent=True) or {}) if request.method == "POST" else {}
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Request body must be a JSON object."}), 400
        resume_text = data.get("resume_text", "")
        if not isinstance(resume_text, str):
            return jsonify({"success": False, "error": "resume_text must be a string."}), 400
        candidate_profile = job_match_service.get_candidate_profile(resume_text=resume_text)

        all_matches = {m["job_id"]: m for m in job_match_service.get_all_job_matches(candidate_profile)}
        
        target_match = all_matches.get(job_id)
        if not target_match:
            # Check placement raw ID format
            target_match = all_matches.get(f"placement_{job_id}")

        if not target_match:
            return jsonify({"success": False, "error": f"Job ID {job_id} not found"}), 404

        # Generate priority decision
        apply_priority = job_match_service.calculate_apply_priority(target_match["job_id"], candidate_profile)

        return jsonify({
            "success": True,
            "job": target_match,
            "apply_priority": apply_priority,
            "candidate_profile": candidate_profile
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@job_match_bp.route("/api/job-match/compare", methods=["GET", "POST"])
def compare_jobs():
    try:
        data = request.get_json(silent=True) or {} if request.method == "POST" else {}
        job_ids = data.get("job_ids") or ["job_py_01", "placement_zenvexa-tech"]
        if not isinstance(job_ids, list) or len(job_ids) < 2:
            job_ids = ["job_py_01", "placement_zenvexa-tech"]

        result = job_match_service.compare_jobs(job_ids)
        return jsonify({
            "success": True,
            "comparison": result
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@job_match_bp.route("/api/job-match/resume-improvements", methods=["POST"])
def generate_resume_improvements():
    try:
        data = request.get_json() or {}
        job_title = data.get("title", "Software Developer")
        company = data.get("company", "Tech Company")
        job_description = data.get("description", "")
        resume_text = data.get("resume_text", "")

        candidate_profile = job_match_service.get_candidate_profile(resume_text=resume_text)
        result = job_match_service.generate_tailored_resume_improvements(
            job_title=job_title,
            company=company,
            job_description=job_description,
            candidate_profile=candidate_profile
        )

        return jsonify({
            "success": True,
            "improvements": result
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@job_match_bp.route("/api/job-match/skills", methods=["GET"])
def get_missing_skills():
    try:
        missing_skills = job_match_service.get_missing_skills_overview()
        return jsonify({
            "success": True,
            "skills": missing_skills
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@job_match_bp.route("/api/job-match/company/<company_id>", methods=["GET"])
def get_company_match(company_id):
    try:
        job_id = f"placement_{company_id}"
        all_matches = {m["job_id"]: m for m in job_match_service.get_all_job_matches()}
        match = all_matches.get(job_id) or all_matches.get(company_id)
        
        if not match:
            return jsonify({"success": False, "error": f"Company {company_id} not found"}), 404

        return jsonify({
            "success": True,
            "company_id": company_id,
            "match": match
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@job_match_bp.route("/api/job-match/apply-priority", methods=["GET", "POST"])
def calculate_apply_priority():
    try:
        data = request.get_json(silent=True) or {} if request.method == "POST" else {}
        job_id = data.get("job_id") or request.args.get("job_id") or "job_py_01"

        priority = job_match_service.calculate_apply_priority(job_id)
        return jsonify({
            "success": True,
            "priority": priority
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
