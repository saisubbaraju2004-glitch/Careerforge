from flask import Blueprint, request, jsonify, render_template
from services.career_engine import CareerEngine
from services.ai_service import AIService

from services.progress_service import ProgressService

career_bp = Blueprint("career", __name__)
career_engine = CareerEngine()
ai_service = AIService(career_engine=career_engine)
progress_service = ProgressService(career_engine=career_engine)

@career_bp.route("/career", methods=["GET"])
def career_guide_page():
    return render_template("index.html")

@career_bp.route("/api/roles", methods=["GET"])
def get_roles():
    try:
        roles = career_engine.get_roles()
        return jsonify({"success": True, "data": roles}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@career_bp.route("/api/career-plan", methods=["POST"])
def generate_career_plan():
    try:
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Request body must be a JSON object."}), 400
        
        candidate_name = data.get("name", "Candidate")
        target_role_id = data.get("target_role", "python_backend_developer")
        current_skills = data.get("current_skills", [])
        hours_input = data.get("hours_per_day", 2)
        if not isinstance(candidate_name, str) or not isinstance(target_role_id, str):
            return jsonify({"success": False, "error": "Name and target_role must be strings."}), 400
        if not isinstance(current_skills, list) or any(not isinstance(skill, str) for skill in current_skills):
            return jsonify({"success": False, "error": "current_skills must be a list of strings."}), 400
        if isinstance(hours_input, bool) or not isinstance(hours_input, (int, float, str)):
            return jsonify({"success": False, "error": "hours_per_day must be a positive number."}), 400
        try:
            hours_per_day = float(hours_input)
        except ValueError:
            return jsonify({"success": False, "error": "hours_per_day must be a positive number."}), 400
        if not 0 < hours_per_day <= 24:
            return jsonify({"success": False, "error": "hours_per_day must be between 0 and 24."}), 400

        # Skill gap analysis
        gap_analysis = career_engine.analyze_skill_gap(target_role_id, current_skills)

        # Career Diagnosis
        diagnosis = ai_service.generate_career_diagnosis(
            gap_analysis["role_title"],
            current_skills,
            gap_analysis["missing_skills"],
            gap_analysis["readiness_score"]
        )

        # 30-Day Adaptive Plan
        thirty_day_plan = ai_service.generate_career_plan(
            gap_analysis["role_title"],
            current_skills,
            gap_analysis["missing_skills"],
            hours_per_day
        )

        # Portfolio Project Recommendation
        project_rec = ai_service.generate_project_recommendation(
            gap_analysis["role_title"],
            current_skills,
            gap_analysis["missing_skills"]
        )

        # Progress, Heatmap, Radar, Next Best Action
        skill_heatmap = progress_service.calculate_skill_heatmap(target_role_id, current_skills)
        career_radar = progress_service.calculate_career_radar(gap_analysis)
        next_best_action = progress_service.determine_next_best_action(
            gap_analysis["readiness_score"],
            ats_score=75,
            missing_skills=gap_analysis["missing_skills"],
            interview_score=70,
            app_count=0
        )

        ai_fallback_notice = None
        if not ai_service.gemini_key:
            ai_fallback_notice = "AI personalization is currently unavailable. Showing your rule-based career plan."

        response_payload = {
            "candidate_name": candidate_name,
            "target_role": gap_analysis["role_title"],
            "target_role_id": target_role_id,
            "readiness_score": gap_analysis["readiness_score"],
            "strong_skills": gap_analysis["strong_skills"],
            "improvement_skills": gap_analysis["improvement_skills"],
            "missing_skills": gap_analysis["missing_skills"],
            "diagnosis": diagnosis,
            "thirty_day_plan": thirty_day_plan,
            "recommended_project": project_rec,
            "resources": gap_analysis["resources"],
            "skill_heatmap": skill_heatmap,
            "career_radar": career_radar,
            "next_best_action": next_best_action,
            "ai_fallback_notice": ai_fallback_notice
        }

        return jsonify({"success": True, "data": response_payload}), 200


    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to generate career plan: {str(e)}"}), 500
