import uuid
from datetime import datetime, timezone
from flask import Blueprint, current_app, g, render_template, request, jsonify
from services.interview_intelligence_service import InterviewIntelligenceService
from services.ai_service import AIService
from services.user_store import add_user_record, get_user_records, get_user_summary

interview_intel_bp = Blueprint("interview_intel", __name__)
ai_service = AIService()
interview_intel_service = InterviewIntelligenceService(ai_service)


def _database_url():
    return current_app.config["DATABASE_URL"]


@interview_intel_bp.route("/interview-intelligence", methods=["GET"])
def interview_intelligence_page():
    return render_template("interview_intelligence.html")

@interview_intel_bp.route("/api/interview-intelligence/start", methods=["POST"])
def start_interview():
    try:
        data = request.get_json(silent=True) or {}
        role = data.get("role", "Python Backend Developer")
        company = data.get("company", "TechForge Solutions")
        round_type = data.get("round", "Technical Interview")

        session = interview_intel_service.start_interview_session(role, company, round_type)
        add_user_record(
            _database_url(),
            g.user_id,
            "interview_session",
            session["session_id"],
            {
                "role": role,
                "company": company,
                "round_type": round_type,
                "started_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return jsonify({"success": True, "data": session}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@interview_intel_bp.route("/api/interview-intelligence/analyze", methods=["POST"])
def analyze_answer():
    try:
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Request body must be a JSON object."}), 400
        question = data.get("question", "")
        answer = data.get("answer", "")
        role = data.get("role", "Python Backend Developer")
        expected_keywords = data.get("expected_keywords", [])
        if not isinstance(question, str) or not question.strip():
            return jsonify({"success": False, "error": "question is required."}), 400
        if not isinstance(answer, str) or not answer.strip():
            return jsonify({"success": False, "error": "answer is required."}), 400
        if not isinstance(role, str) or not isinstance(expected_keywords, list) or any(
            not isinstance(keyword, str) for keyword in expected_keywords
        ):
            return jsonify({"success": False, "error": "role and expected_keywords have invalid types."}), 400

        analysis = interview_intel_service.analyze_answer(question, answer, role, expected_keywords)
        session_id = data.get("session_id")
        if session_id is not None and not isinstance(session_id, str):
            return jsonify({"success": False, "error": "session_id must be a string."}), 400
        add_user_record(
            _database_url(),
            g.user_id,
            "interview",
            f"{session_id or 'standalone'}:{uuid.uuid4().hex}",
            {
                "score": analysis["score"],
                "breakdown": analysis.get("breakdown", {}),
                "role": role,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return jsonify({"success": True, "data": analysis}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@interview_intel_bp.route("/api/interview-intelligence/next-question", methods=["POST"])
def next_question():
    try:
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Request body must be a JSON object."}), 400
        role = data.get("role", "Python Backend Developer")
        company = data.get("company", "TechForge Solutions")
        previous_score = data.get("previous_score", 75)
        if not isinstance(role, str) or not isinstance(company, str):
            return jsonify({"success": False, "error": "role and company must be strings."}), 400
        if isinstance(previous_score, bool) or not isinstance(previous_score, (int, float)) or not 0 <= previous_score <= 100:
            return jsonify({"success": False, "error": "previous_score must be a number from 0 to 100."}), 400

        difficulty = "Hard" if previous_score >= 85 else ("Medium" if previous_score >= 60 else "Easy")
        q = interview_intel_service.generate_question(role, company, "Technical", difficulty=difficulty)
        return jsonify({"success": True, "data": q}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@interview_intel_bp.route("/api/interview-intelligence/final-report", methods=["POST"])
def final_report():
    try:
        data = request.get_json(silent=True) or {}
        answers = data.get("answers", [])
        report = interview_intel_service.generate_final_report(answers)
        return jsonify({"success": True, "data": report}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@interview_intel_bp.route("/api/interview-intelligence/history", methods=["GET"])
def get_history():
    try:
        sessions = get_user_records(_database_url(), g.user_id, "interview_session")
        answers = get_user_records(_database_url(), g.user_id, "interview")
        history = [
            {
                "date": item.get("recorded_at", item.get("started_at", ""))[:10],
                "role": item.get("role", "Interview practice"),
                "company": item.get("company"),
                "score": item.get("score"),
                "status": "SCORED" if item.get("score") is not None else "STARTED",
            }
            for item in sorted(sessions + answers, key=lambda entry: entry.get("recorded_at", entry.get("started_at", "")), reverse=True)
        ]
        return jsonify({"success": True, "data": history}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@interview_intel_bp.route("/api/interview-intelligence/readiness", methods=["GET"])
def get_readiness():
    try:
        summary = get_user_summary(_database_url(), g.user_id)
        interviews = summary["interviews"]
        scores = [item["score"] for item in interviews if isinstance(item.get("score"), (int, float))]
        metrics = {}
        for dimension in ("technical", "communication", "confidence", "problem_solving", "hr", "project_explanation"):
            values = [
                item.get("breakdown", {}).get(dimension)
                for item in interviews
                if isinstance(item.get("breakdown"), dict)
                and isinstance(item.get("breakdown", {}).get(dimension), (int, float))
            ]
            metrics[dimension] = round(sum(values) / len(values)) if values else None
        score = round(sum(scores) / len(scores)) if scores else None
        status = "NOT ENOUGH DATA" if score is None else ("READY" if score >= 80 else "IN PROGRESS")
        return jsonify({"success": True, "data": {"status": status, "score": score, "metrics": metrics}}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
