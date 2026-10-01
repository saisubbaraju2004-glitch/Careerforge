from services.ai_service import AIService
from services.career_agent_service import CareerAgentService
from services.job_match_service import JobMatchService
from services.placement_strategy_service import PlacementStrategyService
from services.placement_analytics_service import _valid_score


class CareerOSService:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service or AIService()
        self.career_agent_service = CareerAgentService(self.ai_service)
        self.job_match_service = JobMatchService(self.ai_service)
        self.placement_strategy_service = PlacementStrategyService(self.ai_service)

    def get_unified_overview(self, summary):
        observed = [
            score for score in (
                _valid_score(summary.get("ats_score")),
                _valid_score(summary.get("interview_score")),
            )
            if score is not None
        ]
        return {
            "overall_readiness": round(sum(observed) / len(observed)) if observed else None,
            "placement_readiness": None,
            "job_match_score": self._job_match_score(summary),
            "ats_score": _valid_score(summary.get("ats_score")),
            "interview_score": _valid_score(summary.get("interview_score")),
            "skill_progress": min(100, round(summary.get("completed_lessons", 0) / 30 * 100)),
            "application_progress": summary.get("application_count", 0),
            "career_momentum": "ACTIVE" if any(observed) or summary.get("completed_lessons") or summary.get("application_count") else "NO DATA",
            "health_status": "OBSERVED DATA" if observed else "NEEDS DATA",
            "health_color": "badge-success" if observed else "badge-warning",
            "data_status": "observed_activity" if observed else "insufficient_data",
            "disclaimer": "Observed activity scores are not calibrated placement predictions.",
        }

    def get_smart_next_action(self, summary):
        if not summary.get("resume_count"):
            return _action("Analyze your resume", "Upload a resume to establish your first recorded ATS score.", "/")
        if not summary.get("completed_lessons"):
            return _action("Complete a learning lesson", "No lesson completions are recorded for this account yet.", "/learning")
        if not summary.get("interview_count"):
            return _action("Practice an interview answer", "Record an answer to establish an observed interview score.", "/interview-intelligence")
        if not summary.get("application_count"):
            return _action("Record a job application", "Your application funnel needs recorded applications before it can show conversion metrics.", "/applications")
        return _action("Review your recorded activity", "Use the latest observed resume, interview, and application records to choose your next step.", "/placement-analytics")

    def get_todays_command_center(self, summary):
        task_state = {item["id"]: bool(item.get("completed")) for item in summary.get("career_tasks", [])}
        tasks = [
            ("resume", "Resume", "Analyze a resume and review its recorded ATS score", not bool(summary.get("resume_count"))),
            ("lesson", "Learning", "Complete a lesson in the Personalized Learning Engine", not bool(summary.get("completed_lessons"))),
            ("interview", "Interview", "Practice and submit an interview answer", not bool(summary.get("interview_count"))),
            ("application", "Applications", "Record and update a job application", not bool(summary.get("application_count"))),
            ("analytics", "Analytics", "Review observed application and interview activity", bool(summary.get("application_count"))),
        ]
        return [
            {
                "id": task_id,
                "category": category,
                "task": task,
                "done": task_state.get(task_id, inferred_done),
            }
            for task_id, category, task, inferred_done in tasks
        ]

    def get_career_timeline(self, summary):
        return [
            {"phase": "Resume", "status": "Recorded" if summary.get("resume_count") else "No data yet", "active": bool(summary.get("resume_count"))},
            {"phase": "Learning", "status": f"{summary.get('completed_lessons', 0)} lessons completed", "active": bool(summary.get("completed_lessons"))},
            {"phase": "Applications", "status": f"{summary.get('application_count', 0)} recorded", "active": bool(summary.get("application_count"))},
            {"phase": "Interviews", "status": f"{summary.get('interview_count', 0)} answers scored", "active": bool(summary.get("interview_count"))},
            {"phase": "Offers", "status": f"{summary.get('application_statuses', {}).get('Offer', 0)} recorded", "active": bool(summary.get("application_statuses", {}).get("Offer", 0))},
        ]

    def process_unified_chat(self, message, summary):
        msg_lower = (message or "").lower()
        resume = summary.get("ats_score")
        interview = summary.get("interview_score")
        applications = summary.get("application_count", 0)
        lessons = summary.get("completed_lessons", 0)
        if "resume" in msg_lower or "ats" in msg_lower:
            reply = f"Your latest recorded ATS score is {resume}/100." if resume is not None else "There is no resume analysis recorded yet. Upload a resume to establish an ATS baseline."
        elif "interview" in msg_lower:
            reply = f"Your average recorded interview answer score is {interview}/100." if interview is not None else "There are no interview answer scores recorded yet. Submit a practice answer to establish a baseline."
        elif "application" in msg_lower or "placement" in msg_lower or "offer" in msg_lower:
            reply = f"You have {applications} recorded applications. Offer likelihood is not estimated because no validated prediction model is configured."
        elif "learn" in msg_lower or "lesson" in msg_lower:
            reply = f"You have completed {lessons} lessons in this account."
        else:
            reply = (
                f"Your account contains {summary.get('resume_count', 0)} resume analyses, "
                f"{lessons} completed lessons, {summary.get('interview_count', 0)} scored interview answers, "
                f"and {applications} applications. Placement probabilities are not available."
            )
        return {
            "reply": reply,
            "suggested_actions": [
                {"label": "Analyze Resume", "url": "/"},
                {"label": "Practice Interview", "url": "/interview-intelligence"},
                {"label": "Review Applications", "url": "/applications"},
            ],
        }

    def get_executive_report(self, summary):
        observed = []
        if summary.get("ats_score") is not None:
            observed.append(f"Latest ATS score: {summary['ats_score']}/100")
        if summary.get("interview_score") is not None:
            observed.append(f"Average interview answer score: {summary['interview_score']}/100")
        return {
            "position": "Career activity summary",
            "observed_metrics": observed,
            "record_counts": {
                "resume_analyses": summary.get("resume_count", 0),
                "lessons_completed": summary.get("completed_lessons", 0),
                "interview_answers": summary.get("interview_count", 0),
                "applications": summary.get("application_count", 0),
            },
            "data_gaps": _data_gaps(summary),
            "prediction_status": "Unavailable: no validated placement prediction model is configured.",
        }

    def global_search(self, query):
        q = (query or "").strip().lower()
        jobs = self.job_match_service.get_all_jobs_and_companies()
        results = [
            {
                "title": item["title"],
                "type": "Company" if item.get("type") == "placement_company" else "Job Role",
                "url": item.get("apply_url", "/job-match"),
            }
            for item in jobs
            if q and (
                q in item.get("title", "").lower()
                or q in item.get("company", "").lower()
                or any(q in skill.lower() for skill in item.get("skills", []))
            )
        ]
        return results[:50]

    def _job_match_score(self, summary):
        skills = summary.get("skills", [])
        if not skills:
            return None
        candidate_skills = {skill.casefold() for skill in skills if isinstance(skill, str)}
        job_scores = [
            round(sum(skill.casefold() in candidate_skills for skill in job.get("skills", [])) / len(job["skills"]) * 100)
            for job in self.job_match_service.get_all_jobs_and_companies()
            if job.get("skills")
        ]
        return max(job_scores) if job_scores else None


def _action(title, why, url):
    return {
        "title": title,
        "priority": "NEXT",
        "estimated_time": "Based on your current account data",
        "why": why,
        "expected_impact": "No impact estimate is available without a validated model.",
        "action_url": url,
    }


def _data_gaps(summary):
    gaps = []
    if not summary.get("resume_count"):
        gaps.append("No resume analysis recorded.")
    if not summary.get("completed_lessons"):
        gaps.append("No learning completions recorded.")
    if not summary.get("interview_count"):
        gaps.append("No interview scores recorded.")
    if not summary.get("application_count"):
        gaps.append("No applications recorded.")
    return gaps
