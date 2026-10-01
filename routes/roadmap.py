from flask import Blueprint, request, jsonify
from services.career_engine import CareerEngine
from services.roadmap_service import RoadmapService

roadmap_bp = Blueprint("roadmap", __name__)
career_engine = CareerEngine()
roadmap_service = RoadmapService(career_engine=career_engine)

@roadmap_bp.route("/api/roadmap/<role_id>", methods=["GET", "POST"])
def get_roadmap(role_id):
    try:
        if request.method == "POST":
            data = request.get_json() or {}
            user_skills = data.get("current_skills", [])
        else:
            user_skills = request.args.get("skills", "").split(",")

        user_skills = [s.strip() for s in user_skills if s.strip()]

        gap_analysis = career_engine.analyze_skill_gap(role_id, user_skills)
        roadmap_data = roadmap_service.build_personalized_roadmap(role_id, gap_analysis)

        return jsonify({"success": True, "data": roadmap_data}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to generate roadmap: {str(e)}"}), 500
