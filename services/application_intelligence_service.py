import os
import json
import csv
import io
from datetime import datetime
from config.config import Config

class ApplicationIntelligenceService:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service

    def calculate_priority(self, app_data):
        """
        Calculates deterministic priority score (0-100) and next action based on:
        Job Match, ATS Score, Interview Score, Days Waiting, and Status.
        """
        match_score = self._clamp(app_data.get("match_score", 75), 0, 100)
        ats_score = self._clamp(app_data.get("ats_score", 75), 0, 100)
        interview_score = self._clamp(app_data.get("interview_score", 70), 0, 100) if app_data.get("interview_score") is not None else 65
        days_waiting = max(0, int(app_data.get("days_waiting", 3)))
        status = str(app_data.get("status", "Applied"))

        # Status weight
        status_weights = {
            "Interview": 25,
            "Assessment": 20,
            "Applied": 15,
            "Wishlist": 10,
            "Offer": 30,
            "Rejected": 0
        }
        status_weight = status_weights.get(status, 15)

        # Weighted calculation
        raw_priority = (match_score * 0.3) + (ats_score * 0.25) + (interview_score * 0.2) + (min(15, days_waiting * 2)) + status_weight
        final_priority = self._clamp(raw_priority, 10, 98)

        if final_priority >= 85:
            tier = "HIGH PRIORITY"
            badge_color = "purple"
        elif final_priority >= 65:
            tier = "MEDIUM PRIORITY"
            badge_color = "cyan"
        else:
            tier = "LOW PRIORITY"
            badge_color = "gray"

        # Deterministic Next Action Logic
        if status == "Interview":
            next_action = "Prepare for technical interview"
            reason = "Active interview scheduled. Practice job-specific questions."
        elif status == "Assessment":
            next_action = "Complete technical assessment"
            reason = "Assessment phase active. Focus on code quality and API design."
        elif status == "Applied" and days_waiting >= 5:
            next_action = "Follow up with recruiter"
            reason = f"Application pending for {days_waiting} days without activity."
        elif status == "Applied":
            next_action = "Wait for response or prep interview"
            reason = "Application recently submitted."
        elif status == "Offer":
            next_action = "Review offer details & respond"
            reason = "Offer extended! Evaluate compensation & terms."
        elif status == "Rejected":
            next_action = "Analyze rejection reason & target new role"
            reason = "Application closed. Review skill gaps."
        else:
            next_action = "Submit formal application"
            reason = "Job currently saved in Wishlist."

        # Application Health
        if status in ["Rejected", "Offer"]:
            health = "Closed"
            health_badge = "gray"
        elif days_waiting <= 5:
            health = "Healthy"
            health_badge = "green"
        elif days_waiting <= 12:
            health = "Needs Attention"
            health_badge = "yellow"
        else:
            health = "Stale"
            health_badge = "red"

        return {
            "priority_score": final_priority,
            "tier": tier,
            "badge_color": badge_color,
            "next_action": next_action,
            "reason": reason,
            "health": health,
            "health_badge": health_badge,
            "health_label": f"CareerForge recommendation: {health}"
        }

    def generate_followup(self, company, role, days_waiting=7, status="Applied"):
        """Generates a professional recruiter follow-up message."""
        days_waiting = max(1, int(days_waiting))
        
        # 1. Try Gemini AI if available
        if self.ai_service and self.ai_service.gemini_key:
            try:
                prompt = f"""Write a polite, professional 3-paragraph recruiter follow-up message for a candidate.
Company: {company}
Role: {role}
Days Waiting: {days_waiting}
Status: {status}

Output plain text with Subject line and email body. Keep tone confident and professional."""
                raw = self.ai_service._call_gemini(prompt)
                if raw and len(raw.strip()) > 20:
                    return {"message": raw.strip(), "source": "gemini"}
            except Exception:
                pass

        # 2. Deterministic Fallback Message Template
        fallback_msg = (
            f"Subject: Follow-up — {role} Application ({company})\n\n"
            f"Dear Hiring Team at {company},\n\n"
            f"I hope this message finds you well. I am writing to follow up regarding my application for the {role} position submitted {days_waiting} days ago.\n\n"
            f"I remain very enthusiastic about the opportunity to contribute to {company}'s engineering goals. "
            f"Please let me know if you require any additional information, code samples, or references.\n\n"
            f"Thank you for your time and consideration.\n\n"
            f"Best regards,\nCandidate"
        )
        return {"message": fallback_msg, "source": "deterministic"}

    def calculate_analytics(self, applications):
        """Calculates response analytics, conversion rates, resume performance, and rejection patterns."""
        if not isinstance(applications, list):
            applications = []

        total_apps = len(applications)
        applied_cnt = sum(1 for a in applications if a.get("status") == "Applied")
        assess_cnt = sum(1 for a in applications if a.get("status") == "Assessment")
        interview_cnt = sum(1 for a in applications if a.get("status") == "Interview")
        offer_cnt = sum(1 for a in applications if a.get("status") == "Offer")
        rejected_cnt = sum(1 for a in applications if a.get("status") == "Rejected")
        wishlist_cnt = sum(1 for a in applications if a.get("status") == "Wishlist")

        # Conversion rates (safe division)
        responses = assess_cnt + interview_cnt + offer_cnt
        resp_rate = int(round((responses / max(1, total_apps - wishlist_cnt)) * 100)) if total_apps > 0 else 0
        int_rate = int(round((interview_cnt / max(1, total_apps - wishlist_cnt)) * 100)) if total_apps > 0 else 0
        offer_rate = int(round((offer_cnt / max(1, total_apps - wishlist_cnt)) * 100)) if total_apps > 0 else 0

        int_conversion = int(round((interview_cnt / max(1, responses)) * 100)) if responses > 0 else 0
        offer_conversion = int(round((offer_cnt / max(1, interview_cnt)) * 100)) if interview_cnt > 0 else 0

        # Resume performance comparison
        resume_perf = {}
        for a in applications:
            v = a.get("resume_version") or "Standard Resume"
            if v not in resume_perf:
                resume_perf[v] = {"apps": 0, "interviews": 0}
            resume_perf[v]["apps"] += 1
            if a.get("status") in ["Interview", "Offer"]:
                resume_perf[v]["interviews"] += 1

        resume_summary = []
        best_resume = None
        best_ratio = -1

        for v, stats in resume_perf.items():
            ratio = stats["interviews"] / max(1, stats["apps"])
            resume_summary.append({
                "version": v,
                "applications": stats["apps"],
                "interviews": stats["interviews"],
                "conversion": f"{int(round(ratio * 100))}%"
            })
            if ratio > best_ratio:
                best_ratio = ratio
                best_resume = v

        resume_note = f"{best_resume or 'Resume v2'} has a higher interview conversion in your recorded application data." if best_resume else "Record more applications to compare resume versions."

        # Match score range performance
        match_perf = {"high": {"apps": 0, "ints": 0}, "medium": {"apps": 0, "ints": 0}, "low": {"apps": 0, "ints": 0}}
        for a in applications:
            sc = a.get("match_score", 70)
            st = a.get("status")
            is_int = 1 if st in ["Interview", "Offer"] else 0
            if sc >= 80:
                match_perf["high"]["apps"] += 1
                match_perf["high"]["ints"] += is_int
            elif sc >= 60:
                match_perf["medium"]["apps"] += 1
                match_perf["medium"]["ints"] += is_int
            else:
                match_perf["low"]["apps"] += 1
                match_perf["low"]["ints"] += is_int

        # Rejection Patterns
        rejection_counts = {"Resume": 0, "Skills": 0, "Interview": 0, "Experience": 0, "Unknown": 0}
        for a in applications:
            if a.get("status") == "Rejected":
                reason = a.get("rejection_reason") or "Unknown"
                if reason in rejection_counts:
                    rejection_counts[reason] += 1
                else:
                    rejection_counts["Unknown"] += 1

        top_rejection = max(rejection_counts.items(), key=lambda x: x[1])[0] if rejected_cnt > 0 else "None"
        rejection_note = f"{top_rejection} performance is the most common known rejection reason in your recorded data." if rejected_cnt > 0 else "No rejections recorded."

        return {
            "total_applications": total_apps,
            "applied": applied_cnt,
            "assessment": assess_cnt,
            "interview": interview_cnt,
            "offers": offer_cnt,
            "rejected": rejected_cnt,
            "wishlist": wishlist_cnt,
            "response_rate": resp_rate,
            "interview_rate": int_rate,
            "offer_rate": offer_rate,
            "interview_conversion": int_conversion,
            "offer_conversion": offer_conversion,
            "resume_performance": resume_summary,
            "best_resume": best_resume,
            "resume_note": resume_note,
            "match_performance": match_perf,
            "rejection_patterns": rejection_counts,
            "top_rejection_reason": top_rejection,
            "rejection_note": rejection_note
        }

    def generate_coach_advice(self, user_prompt, analytics_data, applications):
        """AI Application Coach guidance based on recorded user application data."""
        if not user_prompt:
            user_prompt = "Which applications should I prioritize?"

        # 1. Try Gemini if available
        if self.ai_service and self.ai_service.gemini_key:
            try:
                prompt = f"""You are an expert AI Career Coach analyzing a candidate's job application pipeline.
Data:
Total Applications: {analytics_data.get('total_applications', 0)}
Interviews: {analytics_data.get('interview', 0)}
Offers: {analytics_data.get('offers', 0)}
Response Rate: {analytics_data.get('response_rate', 0)}%
Best Resume: {analytics_data.get('best_resume', 'Python Backend Resume')}
Top Rejection Reason: {analytics_data.get('top_rejection_reason', 'None')}

User Question: "{user_prompt}"

Provide a concise, direct 2-paragraph answer with specific recommendations based on their recorded metrics."""
                raw = self.ai_service._call_gemini(prompt)
                if raw and len(raw.strip()) > 10:
                    return {"reply": raw.strip()}
            except Exception:
                pass

        # 2. Deterministic Fallback Coach Replies
        p_lower = user_prompt.lower()
        if "follow up" in p_lower:
            reply = f"Prioritize following up on applications sitting in **Applied** status for over 5 days without response. Your highest-match applications (80%+) should receive a polite recruiter follow-up message first."
        elif "resume" in p_lower:
            reply = f"Based on your recorded data, **{analytics_data.get('best_resume', 'Resume v2')}** is generating higher interview conversion. Use this template when applying to competitive positions."
        elif "reject" in p_lower:
            reply = f"Your recorded data indicates **{analytics_data.get('top_rejection_reason', 'Interview performance')}** as a primary factor. Practice mock technical interviews in the AI Interview Simulator before next calls."
        else:
            reply = f"Focus your energy on high-priority applications with Match Scores above 80%. Your response rate stands at {analytics_data.get('response_rate', 40)}%."

        return {"reply": reply}

    def export_csv(self, applications):
        """Exports applications data as CSV formatted text."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Company", "Role", "Status", "Applied Date", "Match Score (%)", 
            "ATS Score (%)", "Interview Score (%)", "Resume Version", "Location", "Notes"
        ])

        for a in applications:
            writer.writerow([
                a.get("company", ""),
                a.get("role", ""),
                a.get("status", "Applied"),
                a.get("applied_date", ""),
                a.get("match_score", ""),
                a.get("ats_score", ""),
                a.get("interview_score", ""),
                a.get("resume_version", ""),
                a.get("location", ""),
                a.get("notes", "")
            ])

        return output.getvalue()

    def _clamp(self, val, min_v, max_v):
        try:
            val_f = float(val)
            return max(min_v, min(max_v, int(round(val_f))))
        except (ValueError, TypeError):
            return min_v
