from urllib.parse import urlparse
from flask import Blueprint, current_app, g, render_template, request, jsonify, Response
from services.application_intelligence_service import ApplicationIntelligenceService
from services.ai_service import AIService
from services.career_engine import CareerEngine
from services.user_store import delete_user_record, get_user_records, replace_user_records, set_user_record

applications_bp = Blueprint("applications", __name__)
career_engine = CareerEngine()
ai_service = AIService(career_engine=career_engine)
app_intel_service = ApplicationIntelligenceService(ai_service=ai_service)

@applications_bp.route("/applications", methods=["GET"])
def applications_page():
    return render_template("applications.html")

@applications_bp.route("/applications/<app_id>", methods=["GET"])
def application_detail_page(app_id):
    return render_template("application_detail.html", app_id=app_id)

@applications_bp.route("/api/applications", methods=["GET"])
def get_applications():
    applications = get_user_records(current_app.config["DATABASE_URL"], g.user_id, "application")
    return jsonify({"success": True, "data": applications}), 200

@applications_bp.route("/api/applications", methods=["POST"])
def save_applications():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("applications"), list):
        return jsonify({"success": False, "error": "applications must be a JSON array."}), 400
    applications = data["applications"]
    if len(applications) > 500:
        return jsonify({"success": False, "error": "At most 500 applications may be saved."}), 400
    validated = []
    seen_ids = set()
    for item in applications:
        normalized, error = _validate_application(item)
        if error:
            return jsonify({"success": False, "error": error}), 400
        if normalized["id"] in seen_ids:
            return jsonify({"success": False, "error": "Application IDs must be unique."}), 400
        seen_ids.add(normalized["id"])
        validated.append(normalized)
    replace_user_records(
        current_app.config["DATABASE_URL"], g.user_id, "application", validated
    )
    return jsonify({"success": True, "data": validated}), 200


@applications_bp.route("/api/applications/<app_id>", methods=["GET", "PUT", "DELETE"])
def get_application_detail(app_id):
    database_url = current_app.config["DATABASE_URL"]
    if request.method == "DELETE":
        if not delete_user_record(database_url, g.user_id, "application", app_id):
            return jsonify({"success": False, "error": "Application not found."}), 404
        return jsonify({"success": True, "message": "Application deleted."}), 200
    if request.method == "PUT":
        normalized, error = _validate_application(request.get_json(silent=True))
        if error:
            return jsonify({"success": False, "error": error}), 400
        normalized["id"] = app_id
        set_user_record(database_url, g.user_id, "application", app_id, normalized)
        return jsonify({"success": True, "data": normalized}), 200
    application = next(
        (
            item for item in get_user_records(database_url, g.user_id, "application")
            if item["id"] == app_id
        ),
        None,
    )
    return jsonify({"success": True, "data": application or {"id": app_id, "status": "not_found"}}), 200

@applications_bp.route("/api/applications/follow-up", methods=["POST"])
def generate_followup():
    try:
        data = request.get_json() or {}
        company = data.get("company", "Tech Firm")
        role = data.get("role", "Python Backend Developer")
        days_waiting = data.get("days_since_application", 7)
        status = data.get("status", "Applied")

        result = app_intel_service.generate_followup(company, role, days_waiting, status)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@applications_bp.route("/api/applications/priority", methods=["POST"])
def calculate_priority():
    try:
        data = request.get_json() or {}
        result = app_intel_service.calculate_priority(data)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@applications_bp.route("/api/applications/analytics", methods=["POST", "GET"])
def get_analytics():
    try:
        data = request.get_json(silent=True) if request.method == "POST" else None
        if data is not None and not isinstance(data, dict):
            return jsonify({"success": False, "error": "Request body must be a JSON object."}), 400
        apps = get_user_records(current_app.config["DATABASE_URL"], g.user_id, "application")
        result = app_intel_service.calculate_analytics(apps)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@applications_bp.route("/api/applications/coach", methods=["POST"])
def application_coach():
    try:
        data = request.get_json() or {}
        user_prompt = data.get("prompt", "")
        analytics_data = data.get("analytics", {})
        applications = data.get("applications", [])

        result = app_intel_service.generate_coach_advice(user_prompt, analytics_data, applications)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@applications_bp.route("/api/applications/export", methods=["POST"])
def export_applications():
    try:
        data = request.get_json() or {}
        apps = data.get("applications", [])
        csv_data = app_intel_service.export_csv(apps)

        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=careerforge_applications_report.csv"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def _validate_application(item):
    if not isinstance(item, dict):
        return None, "Each application must be a JSON object."
    app_id = item.get("id")
    company = item.get("company")
    role = item.get("role")
    status = item.get("status", "Applied")
    date = item.get("date", "")
    url = item.get("url", "")
    if not isinstance(app_id, str) or not app_id.strip() or len(app_id) > 100:
        return None, "Application id must be a non-empty string of at most 100 characters."
    if not isinstance(company, str) or not company.strip() or len(company) > 200:
        return None, "Company must be a non-empty string of at most 200 characters."
    if not isinstance(role, str) or not role.strip() or len(role) > 200:
        return None, "Role must be a non-empty string of at most 200 characters."
    if not isinstance(status, str) or status not in {"Wishlist", "Applied", "Assessment", "Interview", "Offer", "Rejected"}:
        return None, "Application status is invalid."
    if not isinstance(date, str) or len(date) > 32:
        return None, "Application date must be a string of at most 32 characters."
    if not isinstance(url, str) or len(url) > 2048:
        return None, "Application URL must be a string of at most 2048 characters."
    if url and urlparse(url).scheme not in {"http", "https"}:
        return None, "Application URL must use HTTP or HTTPS."
    return {
        "id": app_id.strip(),
        "company": company.strip(),
        "role": role.strip(),
        "status": status,
        "date": date,
        "url": url,
    }, None
