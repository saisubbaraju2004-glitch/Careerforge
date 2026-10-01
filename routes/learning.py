from datetime import datetime, timedelta, timezone
from flask import Blueprint, current_app, g, render_template, request, jsonify
from services.learning_engine_service import LearningEngineService, VALID_RESOURCE_URLS
from services.ai_service import AIService
from services.user_store import get_user_records, get_user_summary, set_user_record

learning_bp = Blueprint("learning", __name__)
ai_service = AIService()
learning_service = LearningEngineService(ai_service)

@learning_bp.route("/learning", methods=["GET"])
def learning_page():
    return render_template("learning.html")

@learning_bp.route("/api/learning/profile", methods=["GET"])
def get_learning_profile():
    try:
        gaps = learning_service.analyze_skill_gaps()
        path = learning_service.generate_learning_path()
        summary = _learning_summary()
        return jsonify({
            "success": True,
            "data": {
                "skill_gaps": gaps,
                "learning_path": path,
                "streak": summary["learning_streak"],
                "hours_learned": summary["learning_hours"],
                "completed_lessons": summary["completed_lessons"]
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@learning_bp.route("/api/learning/analyze", methods=["POST"])
def analyze_learning_gaps():
    try:
        data = request.get_json(silent=True) or {}
        skills = data.get("skills", [])
        role = data.get("role", "Python Backend Developer")

        gaps = learning_service.analyze_skill_gaps(skills, role)
        return jsonify({"success": True, "data": gaps}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@learning_bp.route("/api/learning/daily", methods=["POST"])
def get_daily_mission():
    try:
        data = request.get_json(silent=True) or {}
        t = data.get("time", "1 hour")
        mission = learning_service.get_daily_mission(t)
        return jsonify({"success": True, "data": mission}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@learning_bp.route("/api/learning/plan", methods=["POST"])
def get_30_day_plan():
    try:
        plan = learning_service.generate_30_day_plan()
        return jsonify({"success": True, "data": plan}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@learning_bp.route("/api/learning/complete", methods=["POST"])
def complete_lesson():
    try:
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Request body must be a JSON object."}), 400
        lesson_id = data.get("lesson_id", "day_1")
        if not isinstance(lesson_id, str) or not lesson_id.strip() or len(lesson_id) > 100:
            return jsonify({"success": False, "error": "lesson_id must be a non-empty string of at most 100 characters."}), 400
        completed_at = datetime.now(timezone.utc).isoformat()
        set_user_record(
            current_app.config["DATABASE_URL"],
            g.user_id,
            "lesson",
            lesson_id,
            {"lesson_id": lesson_id, "completed_at": completed_at, "hours": 0.5},
        )
        summary = _learning_summary()
        return jsonify({
            "success": True,
            "message": f"Lesson {lesson_id} marked complete!",
            "new_streak": summary["learning_streak"],
            "new_hours": summary["learning_hours"]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@learning_bp.route("/api/learning/progress", methods=["GET"])
def get_learning_progress():
    try:
        summary = _learning_summary()
        week_ago = (datetime.now(timezone.utc).date() - timedelta(days=6)).isoformat()
        weekly_lessons = sum(
            1 for lesson in get_user_records(current_app.config["DATABASE_URL"], g.user_id, "lesson")
            if lesson.get("completed_at", "")[:10] >= week_ago
        )
        return jsonify({
            "success": True,
            "data": {
                "streak_days": summary["learning_streak"],
                "total_hours": summary["learning_hours"],
                "weekly_completion_rate": f"{min(100, round(weekly_lessons / 7 * 100))}%",
                "completed_lessons": summary["completed_lessons"],
                "skill_progress": []
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@learning_bp.route("/api/learning/resources", methods=["GET"])
def get_resources():
    try:
        return jsonify({"success": True, "data": VALID_RESOURCE_URLS}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@learning_bp.route("/api/learning/next", methods=["GET"])
def get_next_recommendation():
    try:
        rec = learning_service.get_next_recommendation()
        return jsonify({"success": True, "data": rec}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def _learning_summary():
    summary = get_user_summary(current_app.config["DATABASE_URL"], g.user_id)
    return {
        key: summary[key]
        for key in ("learning_streak", "learning_hours", "completed_lessons")
    }
