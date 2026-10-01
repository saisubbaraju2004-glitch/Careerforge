from flask import Blueprint, render_template, request, jsonify
from services.placement_service import PlacementService
from services.ai_service import AIService
from services.career_engine import CareerEngine

placements_bp = Blueprint("placements", __name__)
career_engine = CareerEngine()
ai_service = AIService(career_engine=career_engine)
placement_service = PlacementService(ai_service=ai_service)

@placements_bp.route("/placements", methods=["GET"])
def placements_page():
    return render_template("placements.html")

@placements_bp.route("/placements/company/<company_id>", methods=["GET"])
def placement_company_detail_page(company_id):
    return render_template("placement_company.html", company_id=company_id)

@placements_bp.route("/api/placements/profile", methods=["GET", "POST"])
def manage_placement_profile():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            profile = placement_service.get_user_profile(data)
            return jsonify({"success": True, "data": profile}), 200
        else:
            profile = placement_service.get_user_profile({})
            return jsonify({"success": True, "data": profile}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placements_bp.route("/api/placements/companies", methods=["GET"])
def get_companies():
    try:
        companies = placement_service.get_all_companies({})
        return jsonify({"success": True, "data": companies}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placements_bp.route("/api/placements/eligible", methods=["GET"])
def get_eligible():
    try:
        eligible_comps = placement_service.get_eligible_companies({})
        return jsonify({"success": True, "data": eligible_comps}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placements_bp.route("/api/placements/company/<company_id>", methods=["GET"])
def get_company_detail(company_id):
    try:
        company = placement_service.get_company_by_id(company_id, {})
        return jsonify({"success": True, "data": company}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placements_bp.route("/api/placements/readiness", methods=["GET", "POST"])
def calculate_readiness():
    try:
        data = request.get_json(silent=True) or {} if request.method == "POST" else {}
        readiness = placement_service.calculate_placement_readiness(profile_data=data.get("profile"), user_scores=data.get("scores"))
        return jsonify({"success": True, "data": readiness}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placements_bp.route("/api/placements/company-plan", methods=["GET", "POST"])
def generate_company_plan():
    try:
        data = request.get_json(silent=True) or {} if request.method == "POST" else {}
        company_id = data.get("company_id") or request.args.get("company_id") or "zenvexa-tech"
        plan = placement_service.generate_company_prep_plan(company_id, data.get("profile"))
        return jsonify({"success": True, "data": plan}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placements_bp.route("/api/placements/coach", methods=["POST"])
def placement_coach():
    try:
        data = request.get_json(silent=True) or {}
        prompt = data.get("prompt", "")
        profile = data.get("profile", {})
        result = placement_service.generate_placement_coach(prompt, profile)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placements_bp.route("/api/placements/daily-mission", methods=["GET", "POST"])
def get_placement_daily_mission():
    try:
        data = request.get_json(silent=True) or {} if request.method == "POST" else {}
        mission = placement_service.generate_placement_daily_mission(data.get("profile"))
        return jsonify({"success": True, "data": mission}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placements_bp.route("/api/placements/analytics", methods=["GET"])
def get_placement_analytics():
    try:
        analytics = placement_service.calculate_placement_analytics([])
        return jsonify({"success": True, "data": analytics}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placements_bp.route("/api/placements/report", methods=["GET", "POST"])
def generate_placement_report():
    try:
        data = request.get_json(silent=True) or {} if request.method == "POST" else {}
        report = placement_service.generate_placement_report(data.get("profile"))
        return jsonify({"success": True, "data": report}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
