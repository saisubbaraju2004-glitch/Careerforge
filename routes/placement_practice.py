from flask import Blueprint, render_template, request, jsonify
from services.placement_practice_service import PlacementPracticeService

placement_practice_bp = Blueprint("placement_practice", __name__)
practice_service = PlacementPracticeService()

@placement_practice_bp.route("/placement-practice/aptitude", methods=["GET"])
def aptitude_practice_page():
    return render_template("placement_practice.html", default_mode="aptitude")

@placement_practice_bp.route("/placement-practice/coding", methods=["GET"])
def coding_practice_page():
    return render_template("placement_practice.html", default_mode="coding")

@placement_practice_bp.route("/api/placement-practice/aptitude/generate", methods=["POST"])
def generate_aptitude_test():
    try:
        data = request.get_json(silent=True) or {}
        category = data.get("category", "All")
        count = data.get("count", 10)
        test = practice_service.generate_aptitude_test(category=category, count=count)
        return jsonify({"success": True, "data": test}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placement_practice_bp.route("/api/placement-practice/aptitude/submit", methods=["POST"])
def submit_aptitude_test():
    try:
        data = request.get_json(silent=True) or {}
        user_answers = data.get("answers", [])
        result = practice_service.evaluate_aptitude_submission(user_answers)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placement_practice_bp.route("/api/placement-practice/coding/generate", methods=["POST"])
def generate_coding_test():
    try:
        data = request.get_json(silent=True) or {}
        category = data.get("category", "All")
        count = data.get("count", 3)
        test = practice_service.generate_coding_test(category=category, count=count)
        return jsonify({"success": True, "data": test}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@placement_practice_bp.route("/api/placement-practice/coding/submit", methods=["POST"])
def submit_coding_test():
    try:
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Request body must be a JSON object."}), 400
        problem_id = data.get("problem_id", "code-1")
        code_solution = data.get("code", data.get("user_code", ""))
        language = data.get("language", "python")
        if not isinstance(problem_id, str) or not problem_id:
            return jsonify({"success": False, "error": "problem_id must be a non-empty string."}), 400
        if not isinstance(code_solution, str) or not code_solution.strip():
            return jsonify({"success": False, "error": "code is required."}), 400
        if not isinstance(language, str) or language not in {"python", "javascript", "java", "cpp"}:
            return jsonify({"success": False, "error": "Unsupported coding language."}), 400
        result = practice_service.evaluate_coding_submission(problem_id, code_solution)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
