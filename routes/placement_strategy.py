from flask import Blueprint, render_template, request, jsonify
from services.placement_strategy_service import PlacementStrategyService
from services.ai_service import AIService
from services.career_engine import CareerEngine

placement_strategy_bp = Blueprint("placement_strategy", __name__)
career_engine = CareerEngine()
ai_service = AIService(career_engine=career_engine)
strategy_service = PlacementStrategyService(ai_service=ai_service)

@placement_strategy_bp.route("/placement-strategy", methods=["GET"])
def placement_strategy_page():
    return render_template("placement_strategy.html")

@placement_strategy_bp.route("/placement-strategy/company/<company_id>", methods=["GET"])
def company_war_room_page(company_id):
    return render_template("placement_war_room.html", company_id=company_id)

@placement_strategy_bp.route("/api/placement-strategy/rankings", methods=["GET", "POST"])
def get_rankings():
    try:
        data = request.get_json(silent=True) or {} if request.method == "POST" else {}
        rankings = strategy_service.calculate_company_rankings(data.get("profile"), data.get("scores"))
        return jsonify({"success": True, "data": rankings}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placement_strategy_bp.route("/api/placement-strategy/company/<company_id>", methods=["GET"])
def get_company_war_room(company_id):
    try:
        details = strategy_service.get_war_room_details(company_id, {}, {})
        return jsonify({"success": True, "data": details}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placement_strategy_bp.route("/api/placement-strategy/analyze", methods=["POST"])
def analyze_placement_strategy():
    try:
        data = request.get_json(silent=True) or {}
        rankings = strategy_service.calculate_company_rankings(data.get("profile"), data.get("scores"))
        next_action = strategy_service.calculate_smart_next_action(data.get("profile"), data.get("scores"))
        command = strategy_service.generate_daily_command(data.get("profile"), data.get("scores"))
        
        return jsonify({
            "success": True,
            "data": {
                "rankings": rankings,
                "top_target": rankings[0] if rankings else {},
                "next_action": next_action,
                "daily_command": command
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placement_strategy_bp.route("/api/placement-strategy/war-plan", methods=["GET", "POST"])
def get_war_plan():
    try:
        data = request.get_json(silent=True) or {} if request.method == "POST" else {}
        comp_id = data.get("company_id") or request.args.get("company_id") or "zenvexa-tech"
        comp = strategy_service.get_war_room_details(comp_id, data.get("profile"), data.get("scores")).get("company", {})
        plan = strategy_service.generate_adaptive_war_plan(comp, data.get("scores"))
        return jsonify({"success": True, "data": plan}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placement_strategy_bp.route("/api/placement-strategy/daily-command", methods=["GET", "POST"])
def get_daily_command():
    try:
        data = request.get_json(silent=True) or {} if request.method == "POST" else {}
        command = strategy_service.generate_daily_command(data.get("profile"), data.get("scores"))
        return jsonify({"success": True, "data": command}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placement_strategy_bp.route("/api/placement-strategy/next-action", methods=["GET", "POST"])
def get_smart_next_action():
    try:
        data = request.get_json(silent=True) or {} if request.method == "POST" else {}
        action = strategy_service.calculate_smart_next_action(data.get("profile"), data.get("scores"))
        return jsonify({"success": True, "data": action}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placement_strategy_bp.route("/api/placement-strategy/apply-decision", methods=["GET", "POST"])
def get_apply_decision():
    try:
        data = request.get_json(silent=True) or {} if request.method == "POST" else {}
        comp_id = data.get("company_id") or request.args.get("company_id") or "zenvexa-tech"
        comp = strategy_service.get_war_room_details(comp_id, data.get("profile"), data.get("scores")).get("company", {})
        decision = strategy_service.calculate_apply_decision(comp)
        return jsonify({"success": True, "data": decision}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placement_strategy_bp.route("/api/placement-strategy/readiness", methods=["GET", "POST"])
def get_readiness():
    try:
        data = request.get_json(silent=True) or {} if request.method == "POST" else {}
        readiness = strategy_service.placement_service.calculate_placement_readiness(data.get("profile"), data.get("scores"))
        return jsonify({"success": True, "data": readiness}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
