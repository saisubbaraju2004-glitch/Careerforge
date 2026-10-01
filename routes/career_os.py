from flask import Blueprint, current_app, g, render_template, request, jsonify
from services.career_os_service import CareerOSService
from services.ai_service import AIService
from services.user_store import get_user_summary, set_user_record

career_os_bp = Blueprint("career_os", __name__)
ai_service = AIService()
career_os_service = CareerOSService(ai_service)


def _summary():
    return get_user_summary(current_app.config["DATABASE_URL"], g.user_id)


@career_os_bp.route("/career-os", methods=["GET"])
def career_os_page():
    return render_template("career_os.html")

@career_os_bp.route("/api/career-os/overview", methods=["GET"])
def get_overview():
    try:
        summary = _summary()
        data = career_os_service.get_unified_overview(summary)
        action = career_os_service.get_smart_next_action(summary)
        command = career_os_service.get_todays_command_center(summary)
        timeline = career_os_service.get_career_timeline(summary)
        return jsonify({
            "success": True,
            "data": {
                "overview": data,
                "next_action": action,
                "command_center": command,
                "timeline": timeline
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@career_os_bp.route("/api/career-os/action", methods=["POST"])
def complete_action():
    try:
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Request body must be a JSON object."}), 400
        task_id = data.get("task_id", "t1")
        completed = data.get("completed", True)
        if not isinstance(task_id, str) or not task_id or len(task_id) > 100 or not isinstance(completed, bool):
            return jsonify({"success": False, "error": "task_id and completed have invalid values."}), 400
        set_user_record(
            current_app.config["DATABASE_URL"],
            g.user_id,
            "career_task",
            task_id,
            {"completed": completed},
        )
        return jsonify({"success": True, "message": "Task status saved."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@career_os_bp.route("/api/career-os/chat", methods=["POST"])
def unified_chat():
    try:
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Request body must be a JSON object."}), 400
        msg = data.get("message", "")
        if not isinstance(msg, str) or not msg.strip():
            return jsonify({"success": False, "error": "message is required."}), 400
        if len(msg) > 4000:
            return jsonify({"success": False, "error": "message must be 4000 characters or fewer."}), 400
        res = career_os_service.process_unified_chat(msg, _summary())
        return jsonify({"success": True, "data": res}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@career_os_bp.route("/api/career-os/report", methods=["GET"])
def get_executive_report():
    try:
        rep = career_os_service.get_executive_report(_summary())
        return jsonify({"success": True, "data": rep}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@career_os_bp.route("/api/career-os/search", methods=["GET"])
def global_search():
    try:
        q = request.args.get("q", "")
        res = career_os_service.global_search(q)
        return jsonify({"success": True, "data": res}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
