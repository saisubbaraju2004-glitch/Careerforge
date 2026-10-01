from flask import Blueprint, request, jsonify, render_template
from services.career_intelligence_service import CareerIntelligenceService
from services.ai_service import AIService
from services.career_engine import CareerEngine

intelligence_bp = Blueprint("intelligence", __name__)
career_engine = CareerEngine()
ai_service = AIService(career_engine=career_engine)
intelligence_service = CareerIntelligenceService(ai_service=ai_service)

@intelligence_bp.route("/intelligence", methods=["GET"])
def intelligence_page():
    return render_template("intelligence.html")

@intelligence_bp.route("/api/career-intelligence", methods=["GET", "POST"])
def get_career_intelligence():
    try:
        data = request.get_json(silent=True) or {} if request.method == "POST" else {}
        
        # Calculate career intelligence
        result = intelligence_service.analyze_career_intelligence(data)
        
        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to compute career intelligence: {str(e)}"
        }), 500
