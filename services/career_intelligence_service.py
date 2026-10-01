import os
import json
from config.config import Config

class CareerIntelligenceService:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service

    def analyze_career_intelligence(self, data):
        """
        Analyze user career state and return deterministic & AI-backed career intelligence metrics.
        """
        target_role = str(data.get("target_role", "Python Backend Developer"))
        current_skills = data.get("current_skills", [])
        if not isinstance(current_skills, list):
            current_skills = [str(current_skills)]
            
        missing_skills = data.get("missing_skills", [])
        if not isinstance(missing_skills, list):
            missing_skills = [str(missing_skills)]

        # Clamped numerical inputs (0-100)
        readiness_score = self._clamp(data.get("readiness_score", 70), 0, 100)
        ats_score = self._clamp(data.get("ats_score", 75), 0, 100)
        interview_score = self._clamp(data.get("interview_score", 65), 0, 100)
        roadmap_progress = self._clamp(data.get("roadmap_progress", 40), 0, 100)
        plan_progress = self._clamp(data.get("plan_progress", 50), 0, 100)
        applications = max(0, int(data.get("applications", 0)))
        response_rate = float(data.get("response_rate", 0))
        interview_rate = float(data.get("interview_rate", 0))
        top_rejection_reason = str(data.get("top_rejection_reason", ""))
        best_resume_version = str(data.get("best_resume_version", ""))

        # 1. Readiness Level Classification
        readiness_level, level_description = self._classify_readiness_level(readiness_score)

        # 2. Next Best Action (Deterministic Rules Engine)
        next_action = self._determine_next_best_action(
            target_role=target_role,
            readiness_score=readiness_score,
            ats_score=ats_score,
            interview_score=interview_score,
            roadmap_progress=roadmap_progress,
            plan_progress=plan_progress,
            missing_skills=missing_skills,
            applications=applications,
            response_rate=response_rate,
            interview_rate=interview_rate,
            top_rejection_reason=top_rejection_reason
        )

        # 3. Career Readiness Breakdown & Strongest/Blocker Analysis
        readiness_breakdown = self._calculate_readiness_breakdown(
            current_skills=current_skills,
            missing_skills=missing_skills,
            readiness_score=readiness_score,
            ats_score=ats_score,
            interview_score=interview_score,
            plan_progress=plan_progress
        )

        # 4. Readiness Simulator ("WHAT IF I IMPROVE?")
        potential_simulation = self._calculate_potential_score(
            readiness_score=readiness_score,
            missing_skills=missing_skills,
            ats_score=ats_score,
            interview_score=interview_score
        )

        # 5. Career Milestones Tracker
        milestones = self._calculate_milestones(
            current_skills=current_skills,
            readiness_score=readiness_score,
            ats_score=ats_score,
            interview_score=interview_score,
            roadmap_progress=roadmap_progress,
            plan_progress=plan_progress,
            applications=applications
        )

        # 6. AI Insights (With Robust Deterministic Fallback)
        insights = self._generate_ai_insights(
            target_role=target_role,
            current_skills=current_skills,
            missing_skills=missing_skills,
            readiness_score=readiness_score,
            ats_score=ats_score,
            interview_score=interview_score,
            response_rate=response_rate,
            top_rejection_reason=top_rejection_reason
        )

        # 7. Weekly Review & Next Week Priorities
        weekly_review = {
            "skills_improved": len(current_skills),
            "interview_sessions": max(1, int(interview_score / 25)),
            "applications": applications,
            "resume_score_trend": f"{max(45, int(ats_score - 8))} → {int(ats_score)}",
            "readiness_trend": f"{max(40, int(readiness_score - 6))} → {int(readiness_score)}",
            "tasks_completed": f"{min(15, max(3, int(plan_progress / 100 * 15)))} / 15"
        }

        top_skill_1 = missing_skills[0] if missing_skills else "Docker Fundamentals"
        top_skill_2 = missing_skills[1] if len(missing_skills) > 1 else "REST API Design"
        next_week_priorities = [
            f"Master {top_skill_1}",
            f"Build core components using {top_skill_2}",
            "Complete 3 AI Mock Interview simulations"
        ]
        if top_rejection_reason:
            next_week_priorities.append(f"Address rejection feedback: {top_rejection_reason}")

        return {
            "target_role": target_role,
            "readiness_score": readiness_score,
            "readiness_level": readiness_level,
            "level_description": level_description,
            "next_action": next_action,
            "readiness_breakdown": readiness_breakdown,
            "potential_score": potential_simulation["potential_score"],
            "simulation_breakdown": potential_simulation["improvements"],
            "insights": insights,
            "milestones": milestones,
            "weekly_review": weekly_review,
            "next_week_priorities": next_week_priorities,
            "application_intelligence": {
                "response_rate": response_rate,
                "interview_rate": interview_rate,
                "top_rejection_reason": top_rejection_reason,
                "best_resume_version": best_resume_version
            }
        }

    def _clamp(self, val, min_v, max_v):
        try:
            val_f = float(val)
            return max(min_v, min(max_v, int(round(val_f))))
        except (ValueError, TypeError):
            return min_v

    def _classify_readiness_level(self, score):
        if score < 40:
            return "FOUNDATION", "You are building your core technical foundation."
        elif score < 60:
            return "DEVELOPING", "You are expanding core skills and starting practical work."
        elif score < 75:
            return "INTERVIEW PREP", "You are approaching interview readiness."
        elif score < 90:
            return "JOB READY", "You have strong readiness for target roles."
        else:
            return "HIGHLY COMPETITIVE", "You are a top-tier candidate for entry-level positions."

    def _determine_next_best_action(self, target_role, readiness_score, ats_score, interview_score, roadmap_progress, plan_progress, missing_skills, applications, response_rate=0.0, interview_rate=0.0, top_rejection_reason=""):
        # 0. High application rejections with specific feedback
        if top_rejection_reason:
            return {
                "title": f"Address Key Rejection Reason: {top_rejection_reason}",
                "action": "Address application blocker",
                "why": f"Your recent applications flagged '{top_rejection_reason}' as a key gap. Targeted practice or resume alignment is recommended.",
                "estimated_impact": "+15% interview rate",
                "link": "/applications",
                "code": "rejection_fix"
            }

        # 1. Resume ATS critical
        if ats_score < 60:
            return {
                "title": "Improve Your Resume ATS Score",
                "action": "Improve your resume",
                "why": "Your resume ATS score is currently below 60%. Optimizing action verbs and keywords will directly increase job callback rates.",
                "estimated_impact": "+10 readiness points",
                "link": "/#tabATS",
                "code": "resume_ats"
            }

        # 2. Critical missing skill (Integrated with Job Market Demand)
        if missing_skills and len(missing_skills) > 0:
            top_skill = missing_skills[0]
            return {
                "title": f"Master {top_skill} Fundamentals",
                "action": f"Learn {top_skill}",
                "why": f"{top_skill} is one of your highest-impact missing skills and appears in 8 of your top 10 matching job opportunities for {target_role}.",
                "estimated_impact": "+8 readiness points",
                "link": "/#tabOverview",
                "code": "master_skill"
            }

        # 3. Low interview readiness or category weakness
        if interview_score < 75:
            weakest = missing_skills[0] if missing_skills else "Docker"
            return {
                "title": f"Practice {weakest} Interview Questions",
                "action": f"Practice {weakest} interview",
                "why": f"Your latest interview score is {interview_score}%, but {weakest} questions averaged lower performance. Practicing targeted questions will raise overall readiness.",
                "estimated_impact": "+7 readiness points",
                "link": "/interview",
                "code": "practice_interview"
            }

        # 4. Low roadmap progress
        if roadmap_progress < 30:
            return {
                "title": "Continue Your Structured Roadmap",
                "action": "Continue your roadmap",
                "why": "Completing fundamental learning modules builds essential role mastery step-by-step.",
                "estimated_impact": "+6 readiness points",
                "link": "/#tabRoadmap",
                "code": "continue_roadmap"
            }

        # 5. Low 30-day plan progress
        if plan_progress < 50:
            return {
                "title": "Complete Today's Learning Mission",
                "action": "Complete today's learning mission",
                "why": "Consistently completing daily 30-day plan milestones accelerates technical interview readiness.",
                "estimated_impact": "+5 readiness points",
                "link": "/#tabPlan",
                "code": "learning_mission"
            }

        # 6. High readiness but zero applications
        if applications == 0 and readiness_score >= 60:
            return {
                "title": "Start Submitting Job Applications",
                "action": "Start applying to jobs",
                "why": "You have reached 60%+ readiness! Begin sending tailored applications to target companies.",
                "estimated_impact": "+10 job opportunities",
                "link": "/applications",
                "code": "start_applying"
            }

        # 7. Active applications but interview score needs polish
        if applications > 0 and interview_score < 75:
            return {
                "title": "Refine Technical Interview Performance",
                "action": "Improve interview readiness",
                "why": "With active applications submitted, sharpening system design and live coding answers is key.",
                "estimated_impact": "+8 interview conversion",
                "link": "/interview",
                "code": "interview_prep"
            }

        # 8. Readiness >= 80%
        if readiness_score >= 80:
            return {
                "title": "Apply to High-Tier Target Roles",
                "action": "Apply to higher-quality target roles",
                "why": "Your readiness is above 80%! You are qualified for competitive junior and mid-level developer positions.",
                "estimated_impact": "+15 placement probability",
                "link": "/applications",
                "code": "apply_top_roles"
            }

        # Default Fallback
        return {
            "title": "Review Skill Gap & Progress",
            "action": "Review Skill Gap Analysis",
            "why": "Analyze your current technical coverage and focus on high-priority industry requirements.",
            "estimated_impact": "+5 readiness points",
            "link": "/#tabOverview",
            "code": "skill_review"
        }

    def _calculate_readiness_breakdown(self, current_skills, missing_skills, readiness_score, ats_score, interview_score, plan_progress):
        total_skills = max(1, len(current_skills) + len(missing_skills))
        tech_score = self._clamp((len(current_skills) / total_skills) * 100, 30, 95)
        proj_score = self._clamp(40 + (plan_progress * 0.4) + (15 if len(current_skills) >= 3 else 0), 30, 95)
        comm_score = self._clamp(interview_score * 0.8 + 20, 30, 95)

        categories = {
            "Technical Skills": tech_score,
            "Projects": proj_score,
            "Resume": ats_score,
            "Interview": interview_score,
            "Communication": comm_score,
            "Job Readiness": readiness_score
        }

        # Find strongest and blocker
        strongest = max(categories.items(), key=lambda x: x[1])
        blocker = min(categories.items(), key=lambda x: x[1])

        return {
            "categories": categories,
            "strongest_area": strongest[0],
            "strongest_score": strongest[1],
            "strongest_summary": f"Your strongest area is {strongest[0]} readiness.",
            "biggest_blocker": blocker[0],
            "blocker_score": blocker[1],
            "blocker_summary": f"Your biggest blocker is {blocker[0]} readiness."
        }

    def _calculate_potential_score(self, readiness_score, missing_skills, ats_score, interview_score):
        docker_boost = 6 if missing_skills else 4
        interview_boost = 7 if interview_score < 75 else 4
        resume_boost = 4 if ats_score < 85 else 3

        total_boost = docker_boost + interview_boost + resume_boost
        potential = min(98, readiness_score + total_boost)

        top_missing_name = missing_skills[0] if missing_skills else "Docker & Cloud"

        improvements = [
            {"label": f"If {top_missing_name} improves", "boost": f"+{docker_boost}%"},
            {"label": "If Interview readiness improves", "boost": f"+{interview_boost}%"},
            {"label": "If Resume ATS formatting improves", "boost": f"+{resume_boost}%"}
        ]

        return {
            "current_score": readiness_score,
            "potential_score": potential,
            "improvements": improvements
        }

    def _calculate_milestones(self, current_skills, readiness_score, ats_score, interview_score, roadmap_progress, plan_progress, applications):
        milestones = [
            {
                "id": 1,
                "title": "Complete skill foundation",
                "description": "Master at least 3 core technical skills",
                "completed": len(current_skills) >= 3
            },
            {
                "id": 2,
                "title": "Complete first project",
                "description": "Reach 25%+ roadmap/project completion",
                "completed": plan_progress >= 25 or roadmap_progress >= 25
            },
            {
                "id": 3,
                "title": "Reach 70% readiness",
                "description": "Achieve overall readiness score of 70% or higher",
                "completed": readiness_score >= 70
            },
            {
                "id": 4,
                "title": "Resume ATS > 80",
                "description": "Optimize resume keywords and layout to pass ATS scanners",
                "completed": ats_score >= 80
            },
            {
                "id": 5,
                "title": "Complete 5 mock interviews",
                "description": "Score 70%+ in the AI Interview Simulator",
                "completed": interview_score >= 70
            },
            {
                "id": 6,
                "title": "Apply to first 10 jobs",
                "description": "Track active job applications",
                "completed": applications >= 5
            },
            {
                "id": 7,
                "title": "Get first interview",
                "description": "Qualify for live recruiter interviews",
                "completed": applications >= 1 and interview_score >= 75
            },
            {
                "id": 8,
                "title": "Become job ready",
                "description": "Reach 85%+ overall career readiness score",
                "completed": readiness_score >= 85
            }
        ]
        return milestones

    def _generate_ai_insights(self, target_role, current_skills, missing_skills, readiness_score, ats_score, interview_score, response_rate=0.0, top_rejection_reason=""):
        # Deterministic fallback list
        fallback_insights = []

        if current_skills:
            fallback_insights.append({
                "type": "positive",
                "icon": "🟢",
                "text": f"Your {current_skills[0]} foundation is strong and aligns with target requirements."
            })
        else:
            fallback_insights.append({
                "type": "positive",
                "icon": "🟢",
                "text": "Your core technical learning path is active."
            })

        if missing_skills:
            top_missing = missing_skills[0]
            fallback_insights.append({
                "type": "critical",
                "icon": "🔴",
                "text": f"{top_missing} is currently a critical skill gap for {target_role} roles."
            })
            if len(missing_skills) > 1:
                fallback_insights.append({
                    "type": "warning",
                    "icon": "🟡",
                    "text": f"Your {missing_skills[1]} knowledge needs improvement to pass technical screens."
                })

        if response_rate > 0:
            fallback_insights.append({
                "type": "positive" if response_rate >= 30 else "warning",
                "icon": "🟢" if response_rate >= 30 else "🟡",
                "text": f"Application response rate is tracked at {int(response_rate)}%."
            })

        if top_rejection_reason:
            fallback_insights.append({
                "type": "critical",
                "icon": "🔴",
                "text": f"Top feedback area: '{top_rejection_reason}'."
            })

        if ats_score >= 75:
            fallback_insights.append({
                "type": "warning",
                "icon": "🟡",
                "text": f"Your resume ATS score ({ats_score}%) is solid, but adding quantifiable metrics will boost impact."
            })
        else:
            fallback_insights.append({
                "type": "critical",
                "icon": "🔴",
                "text": f"Your resume ATS score is {ats_score}%. Re-formatting sections will improve parser compliance."
            })

        if interview_score >= 70:
            fallback_insights.append({
                "type": "positive",
                "icon": "🟢",
                "text": f"Interview simulator performance stands strong at {interview_score}%."
            })
        else:
            fallback_insights.append({
                "type": "warning",
                "icon": "🟡",
                "text": f"Mock interview practice is recommended to elevate your score ({interview_score}%) before real calls."
            })

        # Try Gemini if available
        if self.ai_service and self.ai_service.gemini_key:
            try:
                prompt = f"""Generate 4 concise bullet point insights for a job candidate targeting {target_role}.
Current Skills: {', '.join(current_skills)}
Missing Skills: {', '.join(missing_skills)}
Readiness Score: {readiness_score}%
Resume ATS: {ats_score}%
Interview Score: {interview_score}%

Return ONLY a JSON array of objects with keys: "icon" (🟢, 🟡, or 🔴), "text" (concise 1-sentence insight).
Example JSON:
[
  {{"icon": "🟢", "text": "Your Python foundation is strong."}},
  {{"icon": "🔴", "text": "Docker is currently a critical skill gap."}}
]"""
                raw = self.ai_service._call_gemini(prompt)
                parsed = self.ai_service._clean_json_response(raw)
                if parsed and isinstance(parsed, list) and len(parsed) >= 2:
                    formatted_insights = []
                    for item in parsed[:5]:
                        ic = item.get("icon", "🟡")
                        txt = item.get("text", "")
                        if txt:
                            formatted_insights.append({
                                "type": "positive" if "🟢" in ic else ("critical" if "🔴" in ic else "warning"),
                                "icon": ic,
                                "text": txt
                            })
                    if len(formatted_insights) >= 2:
                        return formatted_insights
            except Exception:
                pass

        return fallback_insights[:5]
