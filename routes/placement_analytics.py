from flask import Blueprint, current_app, g, render_template, jsonify
from services.placement_analytics_service import PlacementAnalyticsService
from services.ai_service import AIService
from services.user_store import get_user_summary

placement_analytics_bp = Blueprint("placement_analytics", __name__)
ai_service = AIService()
analytics_service = PlacementAnalyticsService(ai_service)


def _summary():
    return get_user_summary(current_app.config["DATABASE_URL"], g.user_id)


@placement_analytics_bp.route("/placement-analytics", methods=["GET"])
def placement_analytics_page():
    return render_template("placement_analytics.html")

@placement_analytics_bp.route("/api/placement-analytics/overview", methods=["GET"])
def get_overview():
    try:
        data = analytics_service.get_readiness_analytics(_summary())
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placement_analytics_bp.route("/api/placement-analytics/prediction", methods=["GET"])
def get_prediction():
    try:
        data = analytics_service.calculate_placement_probabilities(_summary())
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placement_analytics_bp.route("/api/placement-analytics/companies", methods=["GET"])
def get_company_predictions():
    try:
        data = analytics_service.get_company_predictions(_summary())
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placement_analytics_bp.route("/api/placement-analytics/funnel", methods=["GET"])
def get_funnel():
    try:
        data = analytics_service.get_conversion_funnel(_summary())
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placement_analytics_bp.route("/api/placement-analytics/trends", methods=["GET"])
def get_trends():
    try:
        data = analytics_service.get_placement_trends(_summary())
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placement_analytics_bp.route("/api/placement-analytics/risks", methods=["GET"])
def get_risks():
    try:
        data = analytics_service.detect_weakness_risks(_summary())
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placement_analytics_bp.route("/api/placement-analytics/goals", methods=["GET"])
def get_goals():
    try:
        data = analytics_service.predict_goal_progress(_summary())
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
