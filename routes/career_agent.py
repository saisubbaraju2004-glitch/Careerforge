from flask import Blueprint, render_template, request, jsonify
from services.career_agent_service import CareerAgentService
from services.ai_service import AIService
from services.career_engine import CareerEngine

career_agent_bp = Blueprint("career_agent", __name__)
career_engine = CareerEngine()
ai_service = AIService(career_engine=career_engine)
agent_service = CareerAgentService(ai_service=ai_service)

@career_agent_bp.route("/career-agent", methods=["GET"])
def career_agent_page():
    return render_template("career_agent.html")

@career_agent_bp.route("/api/career-agent/context", methods=["GET"])
def get_unified_context():
    try:
        context = agent_service.build_unified_context({})
        return jsonify({"success": True, "data": context}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@career_agent_bp.route("/api/career-agent/analyze", methods=["POST"])
def analyze_career_agent():
    try:
        data = request.get_json(silent=True) or {}
        result = agent_service.analyze_career_agent(data)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@career_agent_bp.route("/api/career-agent/chat", methods=["POST"])
def agent_chat():
    try:
        data = request.get_json(silent=True) or {}
        user_prompt = data.get("prompt", "")
        raw_context = data.get("context", {})
        result = agent_service.generate_agent_chat(user_prompt, raw_context)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@career_agent_bp.route("/api/career-agent/daily-mission", methods=["GET", "POST"])
def get_daily_mission():
    try:
        data = request.get_json(silent=True) or {}
        time_available = data.get("time_available") or data.get("time_minutes") or 60
        result = agent_service.generate_daily_mission(data, time_minutes=time_available)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@career_agent_bp.route("/api/career-agent/weekly-review", methods=["GET", "POST"])
def get_weekly_review():
    try:
        data = request.get_json(silent=True) or {}
        result = agent_service.generate_weekly_review(data)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@career_agent_bp.route("/api/career-agent/career-report", methods=["GET", "POST"])
def generate_career_report():
    try:
        data = request.get_json(silent=True) or {}
        result = agent_service.generate_career_report(data)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@career_agent_bp.route("/api/career-agent/complete-action", methods=["POST"])
def complete_action():
    try:
        data = request.get_json(silent=True) or {}
        action_name = data.get("action", "Action")
        duration = data.get("duration", 30)
        
        return jsonify({
            "success": True,
            "data": {
                "message": f"Successfully completed '{action_name}'!",
                "streak_incremented": True,
                "action": action_name,
                "duration": duration
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
