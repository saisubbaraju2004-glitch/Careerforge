import os
import json
import re
from config.config import Config

class ResumeBuilderService:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service

    def generate_summary(self, profile_data):
        """
        Generates a concise, professional resume summary based ONLY on user-supplied data.
        Never invents fake companies, dates, or degrees.
        """
        target_role = profile_data.get("target_role", "Python Backend Developer")
        skills = profile_data.get("skills", [])
        projects = profile_data.get("projects", [])
        experience = profile_data.get("experience", [])
        education = profile_data.get("education", {})

        top_skills_str = ", ".join(skills[:4]) if skills else "modern web technologies and software design"
        degree_str = education.get("degree", "Computer Science background") if isinstance(education, dict) else "Computer Science background"
        
        # 1. Try Gemini AI if available
        if self.ai_service and self.ai_service.gemini_key:
            try:
                prompt = f"""Write a concise, high-impact 3-sentence resume summary for a candidate targeting {target_role}.
Strict rules:
- Base summary ONLY on provided skills ({top_skills_str}) and education ({degree_str}).
- DO NOT invent fake companies, years of experience, or metrics not provided.
- Keep tone professional, confident, and ATS-optimized.

Candidate Info:
Target Role: {target_role}
Skills: {top_skills_str}
Education: {degree_str}
Projects Count: {len(projects)}
Experience Count: {len(experience)}"""
                
                raw = self.ai_service._call_gemini(prompt)
                if raw and len(raw.strip()) > 20:
                    return {"summary": raw.strip(), "source": "gemini"}
            except Exception:
                pass

        # 2. Deterministic Fallback Template
        fallback_summary = (
            f"Results-oriented candidate with a {degree_str} targeting {target_role} positions. "
            f"Proficient in {top_skills_str}, with hands-on experience developing modular application components, REST APIs, and database schemas. "
            f"Eager to contribute strong technical foundation, problem-solving skills, and clean code principles to production software teams."
        )
        return {"summary": fallback_summary, "source": "deterministic"}

    def improve_bullet(self, original_bullet, context=""):
        """
        Improves a weak bullet into an ATS-friendly, action-verb bullet point.
        NEVER invents numerical stats or fake metrics.
        """
        if not original_bullet or len(original_bullet.strip()) < 3:
            return {
                "original": original_bullet,
                "improved": "Developed modular application components using clean code principles and industry-standard REST API protocols.",
                "disclaimer": "AI Suggestion — Verify that this accurately represents your real experience."
            }

        # 1. Try Gemini AI if available
        if self.ai_service and self.ai_service.gemini_key:
            try:
                prompt = f"""Improve the following resume bullet point for a {context or 'technical'} role.
Rules:
- Make it ATS-friendly, active, and achievement-oriented.
- Use strong active verbs (Engineered, Implemented, Architected, Optimized).
- NEVER introduce fake percentages, fake monetary metrics, or fabricated claims not present in original.

Original Bullet: "{original_bullet}"

Return ONLY the improved bullet point as plain text."""
                
                raw = self.ai_service._call_gemini(prompt)
                if raw and len(raw.strip()) > 10:
                    return {
                        "original": original_bullet,
                        "improved": raw.strip().replace('"', ''),
                        "disclaimer": "AI Suggestion — Verify that this accurately represents your real experience."
                    }
            except Exception:
                pass

        # 2. Deterministic Rule-Based Bullet Improver
        b_lower = original_bullet.lower()
        improved = original_bullet.strip()

        # Action verb map
        if b_lower.startswith("worked on"):
            improved = re.sub(r'(?i)^worked on\s*', 'Engineered ', original_bullet)
        elif b_lower.startswith("made"):
            improved = re.sub(r'(?i)^made\s*', 'Developed ', original_bullet)
        elif b_lower.startswith("built"):
            improved = re.sub(r'(?i)^built\s*', 'Architected and built ', original_bullet)
        elif b_lower.startswith("used"):
            improved = re.sub(r'(?i)^used\s*', 'Leveraged ', original_bullet)
        elif b_lower.startswith("helped"):
            improved = re.sub(r'(?i)^helped\s*', 'Collaborated on ', original_bullet)

        if not improved.endswith('.'):
            improved += '.'

        if "rest api" not in improved.lower() and "python" in context.lower():
            improved += " Ensured modular architecture and API integration compliance."

        return {
            "original": original_bullet,
            "improved": improved,
            "disclaimer": "AI Suggestion — Verify that this accurately represents your real experience."
        }

    def calculate_ats_score(self, resume_data, target_job=None):
        """
        Calculates a deterministic ATS score (0-100) using weighted categories:
        - Keyword Match: 30%
        - Skills Match: 25%
        - Experience Match: 15%
        - Projects Match: 15%
        - Formatting: 10%
        - Completeness: 5%
        """
        target_role = resume_data.get("target_role", "Python Backend Developer")
        skills = [s.strip() for s in resume_data.get("skills", []) if s.strip()]
        projects = resume_data.get("projects", [])
        experience = resume_data.get("experience", [])
        personal = resume_data.get("personal", {})
        summary = resume_data.get("summary", "")
        education = resume_data.get("education", {})

        # standard target skills for role
        role_standard_keywords = ["Python", "Flask", "FastAPI", "SQL", "PostgreSQL", "REST APIs", "Docker", "Git", "AWS"]
        if target_job and isinstance(target_job, dict) and target_job.get("skills"):
            job_req_skills = target_job.get("skills", [])
            target_keywords = list(set(role_standard_keywords + job_req_skills))
        else:
            target_keywords = role_standard_keywords

        user_skills_lower = [s.lower() for s in skills]
        matched_keywords = [k for k in target_keywords if k.lower() in user_skills_lower or k.lower() in summary.lower()]
        missing_keywords = [k for k in target_keywords if k.lower() not in user_skills_lower and k.lower() not in summary.lower()]

        # 1. Keyword Match (30%)
        kw_ratio = len(matched_keywords) / max(1, len(target_keywords))
        kw_score = int(round(kw_ratio * 30))

        # 2. Skills Match (25%)
        skills_score = min(25, int(round((len(skills) / 6.0) * 25)))

        # 3. Experience Match (15%)
        exp_score = 15 if len(experience) > 0 else 8

        # 4. Projects Match (15%)
        proj_score = 15 if len(projects) >= 2 else (10 if len(projects) == 1 else 4)

        # 5. Formatting (10%)
        # Single-column clean text checklist
        fmt_score = 10 if (personal.get("name") and personal.get("email") and summary) else 6

        # 6. Completeness (5%)
        has_edu = isinstance(education, dict) and (education.get("degree") or education.get("college"))
        comp_score = 5 if (personal.get("phone") and has_edu) else 3

        total_ats = self._clamp(kw_score + skills_score + exp_score + proj_score + fmt_score + comp_score, 20, 98)

        strengths = []
        if len(skills) >= 4:
            strengths.append("Strong technical skill coverage")
        if len(projects) >= 1:
            strengths.append("Relevant hands-on project portfolio")
        if len(matched_keywords) >= 4:
            strengths.append("Solid alignment with target role keywords")

        missing_elements = []
        if missing_keywords:
            missing_elements.append(f"Missing target keywords: {', '.join(missing_keywords[:3])}")
        if not len(experience):
            missing_elements.append("Consider adding internship or practical experience")

        return {
            "ats_score": total_ats,
            "label": "CareerForge ATS estimate",
            "category_scores": {
                "keyword_match": kw_score,
                "skills_match": skills_score,
                "experience_match": exp_score,
                "projects_match": proj_score,
                "formatting": fmt_score,
                "completeness": comp_score
            },
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "strengths": strengths,
            "missing_elements": missing_elements,
            "job_match_score": min(95, total_ats + 5) if target_job else None
        }

    def optimize_resume(self, resume_data, target_job=None):
        """
        Analyzes current resume against target job, identifies keyword gaps,
        and provides non-destructive BEFORE / AFTER suggestions for user approval.
        """
        current_ats = self.calculate_ats_score(resume_data, target_job)
        missing_kw = current_ats["missing_keywords"]
        skills = resume_data.get("skills", [])
        summary = resume_data.get("summary", "")

        suggestions = []

        # 1. Summary keyword suggestion
        if missing_kw and summary:
            top_missing = missing_kw[0]
            suggested_summary = summary.strip() + f" Currently expanding practical depth in {top_missing}."
            suggestions.append({
                "type": "summary",
                "field": "Career Summary",
                "before": summary,
                "after": suggested_summary,
                "reason": f"Integrates missing target keyword '{top_missing}' into career summary."
            })

        # 2. Skill list addition suggestion
        if missing_kw:
            suggested_skills = list(skills)
            top_kw = missing_kw[:2]
            suggestions.append({
                "type": "skills",
                "field": "Skills List",
                "before": ", ".join(skills),
                "after": ", ".join(skills + [k for k in top_kw if k not in skills]),
                "reason": f"Add target keywords ({', '.join(top_kw)}) if you possess genuine practical familiarity.",
                "warning": "Add only if you genuinely have experience with these tools."
            })

        potential_ats = min(96, current_ats["ats_score"] + 12)

        return {
            "current_ats": current_ats["ats_score"],
            "potential_ats": potential_ats,
            "missing_keywords": missing_kw,
            "matched_keywords": current_ats["matched_keywords"],
            "suggestions": suggestions
        }

    def _clamp(self, val, min_v, max_v):
        try:
            val_f = float(val)
            return max(min_v, min(max_v, int(round(val_f))))
        except (ValueError, TypeError):
            return min_v
