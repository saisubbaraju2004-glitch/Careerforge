from flask import Blueprint, render_template, request, jsonify
from services.career_engine import CareerEngine
from services.ai_service import AIService
from services.progress_service import ProgressService

progress_bp = Blueprint("progress", __name__)
career_engine = CareerEngine()
ai_service = AIService(career_engine=career_engine)
progress_service = ProgressService(career_engine=career_engine)

@progress_bp.route("/progress")
def progress_page():
    return render_template("progress.html")

@progress_bp.route("/api/career-coach", methods=["POST"])
def career_coach():
    try:
        data = request.get_json() or {}
        user_prompt = data.get("prompt", "")
        target_role = data.get("target_role", "Python Backend Developer")
        current_skills = data.get("current_skills", [])
        missing_skills = data.get("missing_skills", [])
        readiness_score = data.get("readiness_score", 50)
        ats_score = data.get("ats_score", 75)
        interview_score = data.get("interview_score", 70)
        roadmap_progress = data.get("roadmap_progress", 40)
        plan_progress = data.get("plan_progress", 50)
        applications = data.get("applications", 0)

        # 1. Gemini AI response if configured
        if ai_service.gemini_key and user_prompt:
            prompt = f"""You are an empathetic, highly strategic Senior Technical Career Coach advising a candidate.
Target Role: {target_role}
Current Skills: {', '.join(current_skills) if current_skills else 'Python, SQL'}
Missing Skills: {', '.join(missing_skills) if missing_skills else 'Docker, REST APIs'}
Career Readiness: {readiness_score}%
Resume ATS Score: {ats_score}%
Interview Mock Score: {interview_score}%
Roadmap Progress: {roadmap_progress}%
30-Day Plan Progress: {plan_progress}%
Job Applications Sent: {applications}

User Question: "{user_prompt}"

Provide a concise, direct 2-3 paragraph answer giving actionable advice tailored to their exact metrics. Reference their specific missing skills, readiness score, and highest-priority next step."""
            
            ai_reply = ai_service._call_gemini(prompt)
            if ai_reply and len(ai_reply.strip()) > 10:
                return jsonify({"success": True, "data": {"reply": ai_reply.strip()}}), 200

        # 2. Rule-Based Fallback Coach Responses
        top_missing = missing_skills[0] if missing_skills else 'Docker'
        fallback_replies = {
            "What should I do next?": f"Your highest-priority action is **{top_missing}**. Your technical foundation is solid ({readiness_score}% readiness), but {top_missing} is currently limiting your backend readiness. Complete the {top_missing} module before adding another project.",
            "What should I learn today?": f"Focus on closing your primary missing core skill: **{top_missing}**. Complete Day 1 tasks for this skill in your 30-Day Plan.",
            "Why is my readiness score low?": f"Your readiness score ({readiness_score}%) reflects missing core technical criteria required for {target_role} technical screens. Mastering {', '.join(missing_skills[:2]) if missing_skills else 'core tools'} will boost your score significantly.",
            "What should I improve in my resume?": f"Your current resume ATS score is {ats_score}%. Ensure standard single-column formatting and integrate missing target keywords: {', '.join(missing_skills[:3]) if missing_skills else 'REST API, Docker'}.",
            "Am I ready for a Python interview?": f"With an interview evaluation of {interview_score}%, you have strong basic concepts. Practice explaining system architecture trade-offs and code execution flow in the AI Interview Simulator.",
            "What project should I build next?": f"Build a **Production-Ready {target_role} API Suite** incorporating {', '.join(missing_skills[:2]) if missing_skills else 'PostgreSQL and Docker'} to prove end-to-end competency to recruiters.",
            "What should I do this week?": f"Complete Week 1 of your 30-Day Plan, polish your resume bullet points, and practice 5 technical questions in the AI Interview Simulator."
        }

        reply = fallback_replies.get(
            user_prompt,
            f"Your highest-priority action is **{top_missing}**. Focus on closing this critical skill gap to boost your readiness score ({readiness_score}%)."
        )

        return jsonify({"success": True, "data": {"reply": reply}}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"Career coach error: {str(e)}"}), 500
