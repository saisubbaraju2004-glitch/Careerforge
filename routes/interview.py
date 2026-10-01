from flask import Blueprint, render_template, request, jsonify
from services.career_engine import CareerEngine
from services.ai_service import AIService
from services.interview_service import InterviewService
from services.job_matching_service import JobMatchingService

interview_bp = Blueprint("interview", __name__)
career_engine = CareerEngine()
ai_service = AIService(career_engine=career_engine)
interview_service = InterviewService(ai_service=ai_service, career_engine=career_engine)
job_matching_service = JobMatchingService(ai_service=ai_service)

@interview_bp.route("/interview")
def interview_page():
    return render_template("interview.html")

@interview_bp.route("/api/interview/start", methods=["POST"])
def start_interview():
    try:
        data = request.get_json() or {}
        target_role = data.get("target_role", "Python Backend Developer")
        interview_type = data.get("interview_type", "Job-Specific")
        difficulty = data.get("difficulty", "Intermediate")
        count = int(data.get("count", 5))
        job_id = data.get("job_id")
        
        job_info = job_matching_service.get_job_by_id(job_id) if job_id else data.get("job_info", {})
        user_profile = {
            "skills": data.get("skills", []),
            "projects": data.get("projects", [])
        }

        questions = interview_service.generate_interview_questions(
            target_role=target_role,
            interview_type=interview_type,
            difficulty=difficulty,
            count=count,
            job_info=job_info,
            user_profile=user_profile
        )

        return jsonify({
            "success": True,
            "data": {
                "questions": questions,
                "job_info": job_info,
                "target_role": target_role
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to start interview: {str(e)}"}), 500

@interview_bp.route("/api/interview/evaluate", methods=["POST"])
def evaluate_answer():
    try:
        data = request.get_json() or {}
        target_role = data.get("target_role", "Python Backend Developer")
        question = data.get("question", "")
        user_answer = data.get("user_answer", "")
        difficulty = data.get("difficulty", "Intermediate")
        category = data.get("category", "Technical")
        job_skill = data.get("job_skill", "Backend")

        evaluation = interview_service.evaluate_answer(
            target_role=target_role,
            question=question,
            user_answer=user_answer,
            difficulty=difficulty,
            category=category,
            job_skill=job_skill
        )

        return jsonify({"success": True, "data": evaluation}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to evaluate answer: {str(e)}"}), 500

@interview_bp.route("/api/interview/final-report", methods=["POST"])
def final_report():
    try:
        data = request.get_json() or {}
        evaluations = data.get("evaluations", [])
        target_role = data.get("target_role", "Python Backend Developer")
        job_info = data.get("job_info", {})

        report = interview_service.generate_final_report(evaluations, target_role, job_info)
        return jsonify({"success": True, "data": report}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to generate final report: {str(e)}"}), 500

@interview_bp.route("/api/interview/improvement-plan", methods=["GET", "POST"])
def improvement_plan():
    try:
        data = request.get_json(silent=True) or {} if request.method == "POST" else {}
        top_weakness = data.get("top_weakness", "Docker")
        second_weakness = data.get("second_weakness", "System Design")
        target_role = data.get("target_role", "Python Backend Developer")

        plan = interview_service.generate_7day_plan(top_weakness, second_weakness, target_role)
        return jsonify({"success": True, "data": plan}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to generate plan: {str(e)}"}), 500

@interview_bp.route("/api/interview/retry", methods=["POST"])
def retry_interview():
    try:
        data = request.get_json() or {}
        top_weakness = data.get("top_weakness", "Docker")
        second_weakness = data.get("second_weakness", "System Design")
        count = int(data.get("count", 5))

        questions = interview_service.generate_retry_questions(top_weakness, second_weakness, count)
        return jsonify({"success": True, "data": {"questions": questions}}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to generate retry questions: {str(e)}"}), 500

@interview_bp.route("/api/interview/history", methods=["GET"])
def get_history():
    # History endpoint returning template structure for client-side storage
    return jsonify({"success": True, "data": {"status": "client_managed"}}), 200
