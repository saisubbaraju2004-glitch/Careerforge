import os
import json
import re
import logging
from pathlib import Path
from config.config import Config

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self, career_engine=None):
        self.career_engine = career_engine
        self.gemini_key = Config.GEMINI_API_KEY
        self.nvidia_key = Config.NVIDIA_API_KEY

    def _read_prompt_template(self, filename):
        prompt_path = Config.PROMPTS_FOLDER / filename
        if prompt_path.exists():
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def _clean_json_response(self, text):
        if not text:
            return None
        # Remove markdown triple backtick guards if present
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()
        try:
            return json.loads(text)
        except Exception:
            # Attempt regex extraction of JSON object or array
            match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except Exception:
                    return None
            return None

    def _call_gemini(self, prompt):
        if not self.gemini_key:
            return None
        
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(
                api_key=self.gemini_key,
                http_options=types.HttpOptions(timeout=15_000)
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            return response.text
        except Exception as e:
            logger.warning("Gemini API request failed (%s); using fallback.", type(e).__name__)
            return None

    def generate_career_plan(self, target_role, current_skills, missing_skills, hours_per_day):
        template = self._read_prompt_template("career_plan.txt")
        if template and self.gemini_key:
            prompt = template.format(
                target_role=target_role,
                current_skills=", ".join(current_skills),
                missing_skills=", ".join(missing_skills),
                hours_per_day=hours_per_day
            )
            raw_response = self._call_gemini(prompt)
            parsed = self._clean_json_response(raw_response)
            if parsed and "thirty_day_plan" in parsed and len(parsed["thirty_day_plan"]) > 0:
                return parsed["thirty_day_plan"]

        # Deterministic Fallback
        if self.career_engine:
            return self.career_engine.generate_fallback_30_day_plan(hours_per_day, missing_skills)
        return []

    def generate_career_diagnosis(self, target_role, current_skills, missing_skills, readiness_score):
        template = self._read_prompt_template("career_diagnosis.txt")
        if template and self.gemini_key:
            prompt = template.format(
                target_role=target_role,
                current_skills=", ".join(current_skills),
                missing_skills=", ".join(missing_skills),
                readiness_score=readiness_score
            )
            raw_response = self._call_gemini(prompt)
            parsed = self._clean_json_response(raw_response)
            if parsed and "blockers" in parsed:
                return parsed

        # Deterministic Fallback
        if self.career_engine:
            skill_analysis = {
                "missing_skills": missing_skills,
                "improvement_skills": [],
                "readiness_score": readiness_score,
                "role_title": target_role
            }
            return self.career_engine.generate_fallback_diagnosis(skill_analysis)
        return {
            "diagnosis_summary": f"Your profile for {target_role} is developing well.",
            "blockers": [],
            "priority_advice": "Focus on your primary missing core skills."
        }

    def generate_resume_analysis(self, target_role, skills, resume_text, weak_bullets=None):
        template = self._read_prompt_template("resume_analysis.txt")
        if template and self.gemini_key and len(resume_text) > 50:
            prompt = template.format(
                target_role=target_role,
                skills=", ".join(skills),
                resume_text=resume_text[:3000] # Cap text length for safety
            )
            raw_response = self._call_gemini(prompt)
            parsed = self._clean_json_response(raw_response)
            if parsed and ("strengths" in parsed or "bullet_rewrites" in parsed):
                return parsed

        # Fallback bullet rewrites & advice
        default_bullets = weak_bullets if weak_bullets else [
            "Developed a website using Python.",
            "Worked on database queries for backend."
        ]
        
        rewrites = []
        for b in default_bullets:
            rewrites.append({
                "original": b,
                "suggested": f"Engineered a production-ready web application module using Python and REST APIs, incorporating structured error handling and database integration.",
                "reasoning": "Uses strong active verbs, highlights technical stack, and specifies modular software architecture principles."
            })

        return {
            "strengths": [
                f"Strong demonstrable core competence in {', '.join(skills[:3]) if skills else 'programming'}.",
                "Clear project-oriented section organization."
            ],
            "missing_keywords": ["REST API", "Docker", "Unit Testing", "PostgreSQL"],
            "improvement_areas": [
                "Quantify bullet points with measurable impact (e.g., improved load time by 30%).",
                "Ensure standard ATS section headers (Experience, Projects, Education, Skills)."
            ],
            "bullet_rewrites": rewrites,
            "ats_recommendations": [
                "Use a clean single-column layout without tables or graphics.",
                "Ensure standard bullet points (no icons or custom graphics)."
            ]
        }

    def generate_project_recommendation(self, target_role, current_skills, missing_skills):
        if self.career_engine:
            return self.career_engine.generate_fallback_project(target_role, missing_skills)
        return {
            "title": f"Production-Grade {target_role} Platform",
            "technologies": ["Python", "Flask", "REST APIs"],
            "why_this_project": "Builds direct proof for technical recruiters.",
            "roadmap": [
                {"week": "Week 1", "focus": "Core Architecture"},
                {"week": "Week 2", "focus": "Database & Business Logic"},
                {"week": "Week 3", "focus": "Authentication & Testing"},
                {"week": "Week 4", "focus": "Docker & Deployment"}
            ]
        }
