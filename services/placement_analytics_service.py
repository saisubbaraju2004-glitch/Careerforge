class PlacementAnalyticsService:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service

    def get_readiness_analytics(self, summary):
        measured = {
            "resume": _valid_score(summary.get("ats_score")),
            "interview": _valid_score(summary.get("interview_score")),
        }
        observed = [score for score in measured.values() if score is not None]
        return {
            "overall": round(sum(observed) / len(observed)) if observed else None,
            "dsa": None,
            "aptitude": None,
            "coding": None,
            "core_cs": None,
            "resume": measured["resume"],
            "interview": measured["interview"],
            "communication": _average_interview_dimension(summary, "communication"),
            "projects": None,
            "data_status": "observed_metrics" if observed else "insufficient_data",
            "measured_dimensions": len(observed),
            "disclaimer": "Only scores recorded from your resume and interview activity are shown; unmeasured factors are unavailable.",
        }

    def calculate_placement_probabilities(self, summary):
        return {
            "interview_probability": None,
            "offer_probability": None,
            "placement_readiness_probability": None,
            "data_status": "no_validated_prediction_model",
            "disclaimer": "No validated placement prediction model or outcome dataset is configured. Probabilities are intentionally unavailable.",
        }

    def get_company_predictions(self, summary):
        company_data = {}
        for application in summary.get("applications", []):
            company = application.get("company")
            if not isinstance(company, str) or not company.strip():
                continue
            stats = company_data.setdefault(company, {"applications": 0, "interviews": 0, "offers": 0})
            stats["applications"] += 1
            status = application.get("status")
            stats["interviews"] += status in {"Interview", "Offer"}
            stats["offers"] += status == "Offer"

        return [
            {
                "company": company,
                **stats,
                "observed_interview_rate": round(stats["interviews"] / stats["applications"] * 100),
                "observed_offer_rate": round(stats["offers"] / stats["applications"] * 100),
                "data_type": "observed_history",
            }
            for company, stats in sorted(company_data.items())
        ]

    def get_conversion_funnel(self, summary):
        statuses = summary.get("application_statuses", {})
        applications = sum(statuses.values())
        assessments = sum(statuses.get(status, 0) for status in ("Assessment", "Interview", "Offer"))
        interviews = sum(statuses.get(status, 0) for status in ("Interview", "Offer"))
        offers = statuses.get("Offer", 0)
        return {
            "applications": applications,
            "assessments": assessments,
            "interviews": interviews,
            "offers": offers,
            "app_to_assessment_pct": _rate(assessments, applications),
            "assessment_to_interview_pct": _rate(interviews, assessments),
            "interview_to_offer_pct": _rate(offers, interviews),
            "data_status": "observed_application_records",
        }

    def detect_weakness_risks(self, summary):
        risks = []
        if summary.get("resume_count", 0) == 0:
            risks.append({
                "risk": "Resume Data",
                "severity": "HIGH",
                "description": "No resume analysis is recorded for this account.",
            })
        if summary.get("interview_count", 0) == 0:
            risks.append({
                "risk": "Interview Evidence",
                "severity": "MEDIUM",
                "description": "No interview answer scores are recorded yet.",
            })
        if summary.get("application_count", 0) == 0:
            risks.append({
                "risk": "Application Activity",
                "severity": "LOW",
                "description": "No job applications are recorded for funnel analysis.",
            })
        if not risks:
            risks.append({
                "risk": "Data Coverage",
                "severity": "LOW",
                "description": "Risks are limited to gaps evidenced in your recorded activity; no predictive model is configured.",
            })
        return risks

    def get_placement_trends(self, summary):
        return {
            "readiness_trend": None,
            "ats_trend": None,
            "interview_trend": None,
            "job_match_trend": None,
            "data_status": "insufficient_history",
            "disclaimer": "Trends require dated score snapshots; current activity records do not establish a historical baseline.",
        }

    def predict_goal_progress(self, summary):
        current = self.get_readiness_analytics(summary)["overall"]
        return {
            "current_pct": current,
            "target_pct": 90,
            "remaining_gap": max(0, 90 - current) if current is not None else None,
            "top_3_actions": _next_actions(summary),
            "data_status": "observed_metrics" if current is not None else "insufficient_data",
        }


def _valid_score(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 100:
        return None
    return round(value)


def _average_interview_dimension(summary, dimension):
    values = [
        interview.get("breakdown", {}).get(dimension)
        for interview in summary.get("interviews", [])
        if isinstance(interview.get("breakdown"), dict)
    ]
    scores = [_valid_score(value) for value in values]
    scores = [score for score in scores if score is not None]
    return round(sum(scores) / len(scores)) if scores else None


def _rate(numerator, denominator):
    return f"{round(numerator / denominator * 100)}%" if denominator else "0%"


def _next_actions(summary):
    actions = []
    if not summary.get("resume_count"):
        actions.append("Analyze a resume to establish an ATS baseline.")
    if not summary.get("completed_lessons"):
        actions.append("Complete a lesson to begin recording learning progress.")
    if not summary.get("interview_count"):
        actions.append("Submit an interview answer to create an observed score.")
    if not summary.get("application_count"):
        actions.append("Record an application to start measuring the application funnel.")
    return actions[:3] or ["Continue recording activity to build a personal trend history."]
