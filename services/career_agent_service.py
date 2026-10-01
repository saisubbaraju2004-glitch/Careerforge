import os
import json
from config.config import Config

class CareerAgentService:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service

    def build_unified_context(self, raw_data):
        """
        Extracts and normalizes raw client context into a single clean Unified Context object.
        """
        raw = raw_data if isinstance(raw_data, dict) else {}
        
        target_role = str(raw.get("target_role") or "Python Backend Developer")
        readiness_score = self._clamp(raw.get("readiness_score", 78), 0, 100)
        ats_score = self._clamp(raw.get("ats_score", 84), 0, 100)
        job_match_score = self._clamp(raw.get("job_match_score", 87), 0, 100)
        interview_score = self._clamp(raw.get("interview_score", 78), 0, 100)
        
        skills = raw.get("skills") or ["Python", "Flask", "FastAPI", "SQL", "PostgreSQL", "REST APIs"]
        if not isinstance(skills, list):
            skills = [str(skills)]

        missing_skills = raw.get("missing_skills") or ["Docker", "Machine Learning", "Kubernetes"]
        if not isinstance(missing_skills, list):
            missing_skills = [str(missing_skills)]

        top_jobs = raw.get("top_jobs") if isinstance(raw.get("top_jobs"), list) else []
        applications = raw.get("applications") if isinstance(raw.get("applications"), list) else []
        
        interview_weaknesses = raw.get("interview_weaknesses") or ["Docker", "System Architecture"]
        if not isinstance(interview_weaknesses, list):
            interview_weaknesses = [str(interview_weaknesses)]

        resume_gaps = raw.get("resume_gaps") or ["Quantifiable Impact Metrics", "Cloud Certifications"]
        if not isinstance(resume_gaps, list):
            resume_gaps = [str(resume_gaps)]

        progress = raw.get("progress") if isinstance(raw.get("progress"), dict) else {}
        
        eligible_companies = raw.get("eligible_companies") or ["Zenvexa Technologies", "TechForge Solutions"]
        upcoming_deadlines = raw.get("upcoming_deadlines") or ["Zenvexa Online Assessment (Oct 15)"]
        placement_readiness = self._clamp(raw.get("placement_readiness", 78), 0, 100)
        weak_rounds = raw.get("weak_rounds") or ["Coding Challenge", "DSA"]
        priority_company = str(raw.get("priority_company") or "Zenvexa Technologies")

        return {
            "target_role": target_role,
            "readiness_score": readiness_score,
            "ats_score": ats_score,
            "job_match_score": job_match_score,
            "interview_score": interview_score,
            "skills": skills,
            "missing_skills": missing_skills,
            "top_jobs": top_jobs,
            "applications": applications,
            "interview_weaknesses": interview_weaknesses,
            "resume_gaps": resume_gaps,
            "progress": progress,
            "eligible_companies": eligible_companies,
            "upcoming_deadlines": upcoming_deadlines,
            "placement_readiness": placement_readiness,
            "weak_rounds": weak_rounds,
            "priority_company": priority_company
        }

    def analyze_career_agent(self, raw_data):
        """
        Main decision engine analyzing context and producing Next Best Action, Top 3 Actions,
        Snapshot, Momentum Score, and Career Risk Detections.
        """
        context = self.build_unified_context(raw_data)
        
        # 1. Decision Engine: Rank actions
        all_actions = self._rank_possible_actions(context)
        primary_action = all_actions[0] if all_actions else self._default_primary_action()
        top_3_actions = all_actions[:3] if len(all_actions) >= 3 else all_actions

        # 2. Career Readiness Snapshot
        skills_score = self._clamp(int((len(context["skills"]) / max(1, len(context["skills"]) + len(context["missing_skills"]))) * 100), 40, 95)
        app_count = len(context["applications"])
        app_score = self._clamp(app_count * 8 + 30, 20, 95)

        snapshot = {
            "overall": context["readiness_score"],
            "skills": skills_score,
            "resume": context["ats_score"],
            "job_match": context["job_match_score"],
            "interview": context["interview_score"],
            "applications": app_score
        }

        # 3. Momentum Calculation
        momentum = self.calculate_momentum(context)

        # 4. Career Risk Detection
        risks = self.detect_career_risks(context)

        return {
            "unified_context": context,
            "primary_action": primary_action,
            "top_3_actions": top_3_actions,
            "snapshot": snapshot,
            "momentum": momentum,
            "risks": risks
        }

    def _rank_possible_actions(self, ctx):
        actions = []

        # Condition 1: Low ATS score (< 70)
        if ctx["ats_score"] < 70:
            actions.append({
                "action": f"Optimize Resume for ATS ({ctx['ats_score']}%)",
                "priority": "HIGH",
                "reason": f"Your ATS score is currently {ctx['ats_score']}%. Re-formatting sections and adding role keywords will directly boost callback rates.",
                "estimated_minutes": 30,
                "impact": "+15% ATS parser match",
                "source": "Resume Analyzer",
                "route": "/resume-builder",
                "code": "ats_boost",
                "weight": 95
            })

        # Condition 2: Critical missing skill present in job demand
        if ctx["missing_skills"]:
            top_missing = ctx["missing_skills"][0]
            actions.append({
                "action": f"Master {top_missing} Fundamentals",
                "priority": "HIGH",
                "reason": f"{top_missing} appears in target {ctx['target_role']} roles and is your top skill gap.",
                "estimated_minutes": 45,
                "impact": "+10 readiness points",
                "source": "Skill Gap Engine",
                "route": "/progress",
                "code": "learn_skill",
                "weight": 90
            })

        # Condition 3: Weak interview score (< 70) or known interview weakness
        if ctx["interview_score"] < 70 or ctx["interview_weaknesses"]:
            weak_area = ctx["interview_weaknesses"][0] if ctx["interview_weaknesses"] else "System Design"
            actions.append({
                "action": f"Practice {weak_area} Interview Questions",
                "priority": "HIGH",
                "reason": f"Interview performance currently stands at {ctx['interview_score']}%, with '{weak_area}' flagged as a focus area.",
                "estimated_minutes": 30,
                "impact": "+12% interview score",
                "source": "Interview Simulator",
                "route": "/interview",
                "code": "practice_interview",
                "weight": 88
            })

        # Condition 4: High job match but zero or few applications
        if ctx["job_match_score"] >= 80 and len(ctx["applications"]) < 3:
            actions.append({
                "action": f"Apply to Matching {ctx['target_role']} Jobs",
                "priority": "HIGH",
                "reason": f"You have an {ctx['job_match_score']}% job match score for target roles. Submit tailored applications now.",
                "estimated_minutes": 25,
                "impact": "+5 active application leads",
                "source": "Job Match Engine",
                "route": "/jobs",
                "code": "apply_jobs",
                "weight": 85
            })

        # Condition 5: Active applications needing follow-up
        stale_apps = [a for a in ctx["applications"] if isinstance(a, dict) and a.get("daysWaiting", 0) >= 5 and a.get("status") == "Applied"]
        if stale_apps or len(ctx["applications"]) >= 3:
            target_comp = stale_apps[0].get("company") if stale_apps else "recruiter"
            actions.append({
                "action": f"Follow Up on Applications ({target_comp})",
                "priority": "MEDIUM",
                "reason": f"Follow up on submitted applications waiting over 5 days to keep hiring teams engaged.",
                "estimated_minutes": 15,
                "impact": "+20% response probability",
                "source": "Application Intelligence",
                "route": "/applications",
                "code": "followup_app",
                "weight": 75
            })

        # Condition 6: Continue 30-day plan
        actions.append({
            "action": "Complete Daily 30-Day Plan Task",
            "priority": "MEDIUM",
            "reason": "Consistent daily learning builds compound technical confidence.",
            "estimated_minutes": 30,
            "impact": "+5 daily plan progress",
            "source": "30-Day Plan",
            "route": "/#tabPlan",
            "code": "continue_plan",
            "weight": 70
        })

        # Condition 7: High readiness apply to top tier
        if ctx["readiness_score"] >= 80:
            actions.append({
                "action": f"Target Senior {ctx['target_role']} Roles",
                "priority": "MEDIUM",
                "reason": f"Overall readiness reached {ctx['readiness_score']}%. Expand job search to high-tier positions.",
                "estimated_minutes": 30,
                "impact": "+15 placement rate",
                "source": "Career Intelligence",
                "route": "/jobs",
                "code": "top_tier_apply",
                "weight": 68
            })

        # Sort by weight descending
        actions.sort(key=lambda x: x["weight"], reverse=True)
        return actions

    def _default_primary_action(self):
        return {
            "action": "Practice Technical Interview",
            "priority": "HIGH",
            "reason": "Sharpening core interview answers boosts overall readiness.",
            "estimated_minutes": 30,
            "impact": "+8 readiness points",
            "source": "AI Career Agent",
            "route": "/interview",
            "code": "practice_interview",
            "weight": 100
        }

    def generate_daily_mission(self, raw_data, time_minutes=60):
        """
        Dynamically adapts daily tasks based on candidate available time (30m, 60m, 120m, 180m+).
        """
        ctx = self.build_unified_context(raw_data)
        time_minutes = max(15, int(time_minutes))

        top_skill = ctx["missing_skills"][0] if ctx["missing_skills"] else "Docker"
        weak_area = ctx["interview_weaknesses"][0] if ctx["interview_weaknesses"] else "System Architecture"

        if time_minutes <= 30:
            tasks = [
                {
                    "title": f"Practice 5 {top_skill} Interview Questions",
                    "minutes": 20,
                    "icon": "fa-microphone",
                    "route": "/interview"
                },
                {
                    "title": "Review Daily Skill Gap Note",
                    "minutes": 10,
                    "icon": "fa-bullseye",
                    "route": "/progress"
                }
            ]
        elif time_minutes <= 60:
            tasks = [
                {
                    "title": f"Practice 5 {top_skill} & {weak_area} Questions",
                    "minutes": 25,
                    "icon": "fa-microphone",
                    "route": "/interview"
                },
                {
                    "title": "Complete Day Milestone Task in 30-Day Plan",
                    "minutes": 25,
                    "icon": "fa-calendar-check",
                    "route": "/#tabPlan"
                },
                {
                    "title": "Apply to 1 High-Match Job",
                    "minutes": 10,
                    "icon": "fa-paper-plane",
                    "route": "/jobs"
                }
            ]
        elif time_minutes <= 120:
            tasks = [
                {
                    "title": f"Master {top_skill} Core Implementation",
                    "minutes": 45,
                    "icon": "fa-layer-group",
                    "route": "/progress"
                },
                {
                    "title": f"Complete {weak_area} AI Mock Interview Session",
                    "minutes": 35,
                    "icon": "fa-microphone",
                    "route": "/interview"
                },
                {
                    "title": "Apply to 2 Jobs Above 80% Match",
                    "minutes": 25,
                    "icon": "fa-paper-plane",
                    "route": "/jobs"
                },
                {
                    "title": "Follow Up on Pending Applications",
                    "minutes": 15,
                    "icon": "fa-reply",
                    "route": "/applications"
                }
            ]
        else:
            tasks = [
                {
                    "title": f"Build Portfolio Component with {top_skill}",
                    "minutes": 60,
                    "icon": "fa-code",
                    "route": "/progress"
                },
                {
                    "title": f"Full {ctx['target_role']} Mock Technical Interview",
                    "minutes": 45,
                    "icon": "fa-microphone",
                    "route": "/interview"
                },
                {
                    "title": "Optimize Resume ATS Keywords",
                    "minutes": 30,
                    "icon": "fa-file-signature",
                    "route": "/resume-builder"
                },
                {
                    "title": "Submit 3 Targeted Job Applications",
                    "minutes": 45,
                    "icon": "fa-paper-plane",
                    "route": "/jobs"
                }
            ]

        total_time = sum(t["minutes"] for t in tasks)
        hours = total_time // 60
        mins = total_time % 60
        total_formatted = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"

        return {
            "time_available_minutes": time_minutes,
            "tasks": tasks,
            "total_estimated_time": total_formatted,
            "task_count": len(tasks)
        }

    def generate_weekly_review(self, raw_data):
        """Generates weekly progress stats and summary notes."""
        ctx = self.build_unified_context(raw_data)
        
        ats = ctx["ats_score"]
        int_sc = ctx["interview_score"]
        apps_cnt = len(ctx["applications"])

        return {
            "metrics": [
                {"label": "Resume ATS Score", "change": "+8%", "value": f"{ats}%", "icon": "fa-file-contract", "color": "green"},
                {"label": "Interview Readiness", "change": "+12%", "value": f"{int_sc}%", "icon": "fa-microphone", "color": "purple"},
                {"label": "Applications Sent", "change": f"+{max(2, apps_cnt)}", "value": f"{apps_cnt} Total", "icon": "fa-briefcase", "color": "cyan"},
                {"label": "Interviews Unlocked", "change": "+2", "value": "2 Active", "icon": "fa-user-check", "color": "yellow"}
            ],
            "highlight": "Your biggest improvement this week was technical interview performance (+12%).",
            "next_week_focus": f"Focus next week on converting target applications into recruiter screens for {ctx['target_role']} roles."
        }

    def generate_career_report(self, raw_data):
        """Generates comprehensive structured AI Career Report."""
        ctx = self.build_unified_context(raw_data)

        # Gemini AI generation with robust fallback
        if self.ai_service and self.ai_service.gemini_key:
            try:
                prompt = f"""Generate a comprehensive executive Career Intelligence Report for a job candidate.
Candidate Data:
Target Role: {ctx['target_role']}
Readiness Score: {ctx['readiness_score']}%
Resume ATS Score: {ctx['ats_score']}%
Job Match Score: {ctx['job_match_score']}%
Interview Score: {ctx['interview_score']}%
Core Skills: {', '.join(ctx['skills'])}
Missing Skills: {', '.join(ctx['missing_skills'])}
Interview Focus Areas: {', '.join(ctx['interview_weaknesses'])}

Formulate a structured markdown report with sections:
1. CURRENT STATE SUMMARY
2. CORE STRERENGTHS
3. CRITICAL WEAKNESSES & SKILL GAPS
4. RESUME & ATS STATUS
5. INTERVIEW READINESS & APPLICATION PIPELINE
6. TOP NEXT BEST ACTION
7. 7-DAY ACTIONABLE MILESTONE PLAN"""
                raw_report = self.ai_service._call_gemini(prompt)
                if raw_report and len(raw_report.strip()) > 100:
                    return {"report": raw_report.strip(), "source": "gemini"}
            except Exception:
                pass

        # Deterministic fallback report
        top_missing = ctx["missing_skills"][0] if ctx["missing_skills"] else "Docker"
        weak_int = ctx["interview_weaknesses"][0] if ctx["interview_weaknesses"] else "System Architecture"

        report_text = f"""# 🎯 CareerForge AI — Official Career Intelligence Report

### Candidate Overview
* **Target Role:** {ctx['target_role']}
* **Overall Readiness:** {ctx['readiness_score']}% (Job Ready)
* **Resume ATS Score:** {ctx['ats_score']}%
* **Interview Readiness:** {ctx['interview_score']}%
* **Target Job Match:** {ctx['job_match_score']}%

---

### 1. Current State Summary
You are currently operating at **{ctx['readiness_score']}% Career Readiness** for **{ctx['target_role']}** positions. Your core technical foundation is solid in {', '.join(ctx['skills'][:3])}, but closing specific tool gaps will significantly boost callback and offer rates.

### 2. Key Strengths
* High alignment on core stack: **{', '.join(ctx['skills'][:4])}**
* Resume ATS compliance score stands strong at **{ctx['ats_score']}%**
* Active application pipeline and practice consistency

### 3. Critical Weaknesses & Skill Gaps
* **Primary Skill Gap:** `{top_missing}` (Appears in 80%+ of target job descriptions)
* **Interview Weakness:** `{weak_int}` questions averaged lower scores
* **Resume Metric Gap:** Needs more quantifiable impact metrics

### 4. Top Next Best Action
> **Practice {top_missing} & {weak_int} Interview Scenarios**
> Dedicate 45 minutes to answering targeted technical questions in the AI Interview Simulator.

### 5. Next 7-Day Roadmap
- **Day 1–2:** Master `{top_missing}` fundamentals & run 1 mock interview.
- **Day 3–4:** Tailor resume keywords for high-match positions (80%+).
- **Day 5–6:** Submit 3 tailored applications via AI Job Matching.
- **Day 7:** Conduct weekly progress review & review offer pipeline.
"""
        return {"report": report_text, "source": "deterministic"}

    def generate_agent_chat(self, user_prompt, raw_data):
        """Processes conversational queries with unified context awareness."""
        ctx = self.build_unified_context(raw_data)
        prompt_str = str(user_prompt or "").strip()

        # Try Gemini if available
        if self.ai_service and self.ai_service.gemini_key:
            try:
                system_prompt = f"""You are the AI Career Agent inside CareerForge AI.
Context:
- Target Role: {ctx['target_role']}
- Overall Readiness: {ctx['readiness_score']}%
- Resume ATS: {ctx['ats_score']}%
- Job Match: {ctx['job_match_score']}%
- Interview Score: {ctx['interview_score']}%
- Skills: {', '.join(ctx['skills'])}
- Missing Skills: {', '.join(ctx['missing_skills'])}
- Interview Weaknesses: {', '.join(ctx['interview_weaknesses'])}

Answer the user's question clearly, concisely, and encouragingly in 2 paragraphs. Provide specific next steps."""
                full_p = f"{system_prompt}\n\nUser Question: {prompt_str}"
                raw_reply = self.ai_service._call_gemini(full_p)
                if raw_reply and len(raw_reply.strip()) > 15:
                    return {"reply": raw_reply.strip(), "source": "gemini"}
            except Exception:
                pass

        # Deterministic fallback replies
        p_lower = prompt_str.lower()
        top_missing = ctx["missing_skills"][0] if ctx["missing_skills"] else "Docker"
        weak_int = ctx["interview_weaknesses"][0] if ctx["interview_weaknesses"] else "System Architecture"

        if "what should i do" in p_lower or "today" in p_lower:
            reply = f"Your highest-impact action today is mastering **{top_missing}** and practicing **{weak_int}** interview questions.\n\nYou have an {ctx['job_match_score']}% match with backend roles, but `{top_missing}` is a recurring requirement. Spend 30 minutes on fundamentals, then complete 5 mock interview questions."
        elif "ready to apply" in p_lower:
            reply = f"Yes! With a **{ctx['readiness_score']}% readiness score** and **{ctx['ats_score']}% ATS score**, you are qualified to apply. Start with job listings with Match Scores above 80% in the AI Job Matching section."
        elif "why is my score" in p_lower or "low" in p_lower:
            reply = f"Your overall readiness score is impacted primarily by your `{top_missing}` skill gap and your **{ctx['interview_score']}% interview score**. Practicing targeted mock interview questions will quickly raise this score."
        elif "which skill" in p_lower or "learn" in p_lower:
            reply = f"Your top priority skill to learn is **{top_missing}**. It appears in the majority of matching job listings for {ctx['target_role']} candidates."
        elif "resume" in p_lower:
            reply = f"Your resume ATS score is **{ctx['ats_score']}%**. To reach 90%+, add quantifiable impact metrics (e.g. 'Reduced latency by 25%') and specify production deployment tools."
        elif "rejected" in p_lower or "rejection" in p_lower:
            reply = f"Recent application data indicates technical interview performance on **{weak_int}** as the main hurdle. Use the AI Interview Simulator to practice live responses before your next interview."
        else:
            reply = f"As your AI Career Agent, I recommend focusing on your highest priority action: **Mastering {top_missing}** and submitting applications for roles with match scores above 80%."

        return {"reply": reply, "source": "deterministic"}

    def calculate_momentum(self, ctx):
        """Calculates candidate momentum score (0-100) and status tier."""
        base = (ctx["readiness_score"] * 0.3) + (ctx["ats_score"] * 0.25) + (ctx["interview_score"] * 0.25) + (ctx["job_match_score"] * 0.2)
        score = self._clamp(base, 20, 99)

        if score >= 85:
            label = "EXCELLENT"
            color = "purple"
        elif score >= 75:
            label = "STRONG"
            color = "cyan"
        elif score >= 55:
            label = "DEVELOPING"
            color = "yellow"
        else:
            label = "LOW"
            color = "red"

        return {
            "score": score,
            "label": label,
            "color": color
        }

    def detect_career_risks(self, ctx):
        """Scans candidate profile for career risks and bottlenecks."""
        risks = []

        if len(ctx["applications"]) < 2:
            risks.append({
                "type": "warning",
                "title": "⚠ Low Application Activity",
                "message": f"You have an {ctx['job_match_score']}% job match score but have submitted few applications.",
                "action": "Browse Matching Jobs",
                "route": "/jobs"
            })

        if ctx["interview_score"] < 70:
            risks.append({
                "type": "critical",
                "title": "⚠ Interview Weakness Detected",
                "message": f"Latest mock interview score is {ctx['interview_score']}%. Regular practice is needed before live recruiter calls.",
                "action": "Start Mock Interview",
                "route": "/interview"
            })

        if ctx["ats_score"] < 75:
            risks.append({
                "type": "warning",
                "title": "⚠ Resume ATS Gap",
                "message": f"Resume ATS score ({ctx['ats_score']}%) is below optimal target (80%+).",
                "action": "Build ATS Resume",
                "route": "/resume-builder"
            })

        if ctx["missing_skills"]:
            top_missing = ctx["missing_skills"][0]
            risks.append({
                "type": "info",
                "title": f"⚠ Critical Skill Gap: {top_missing}",
                "message": f"'{top_missing}' appears frequently in matching target job requirements.",
                "action": f"Learn {top_missing}",
                "route": "/progress"
            })

        return risks

    def _clamp(self, val, min_v, max_v):
        try:
            val_f = float(val)
            return max(min_v, min(max_v, int(round(val_f))))
        except (ValueError, TypeError):
            return min_v
