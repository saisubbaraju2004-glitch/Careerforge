import re

class ATSEngine:
    def __init__(self, career_engine=None):
        self.career_engine = career_engine

    def calculate_ats_score(self, resume_text, target_role_id, declared_skills=None):
        if not declared_skills:
            declared_skills = []

        resume_lower = resume_text.lower() if resume_text else ""
        
        # Benchmark lookup
        role_info = {}
        if self.career_engine and hasattr(self.career_engine, "roles_data"):
            role_info = self.career_engine.roles_data.get(target_role_id, {})

        required_skills = role_info.get("required_skills", [
            "Python", "Flask", "REST APIs", "SQL", "Git", "Testing", "Docker"
        ])
        keyword_weights = role_info.get("keyword_weights", {})

        # 1. Skills Match Score (30%)
        found_in_resume = []
        for req in required_skills:
            pattern = r'\b' + re.escape(req.lower()) + r'\b'
            if re.search(pattern, resume_lower):
                found_in_resume.append(req)

        skill_match_pct = int(round((len(found_in_resume) / len(required_skills)) * 100)) if required_skills else 50

        # 2. Keyword Match Score (30%)
        if keyword_weights:
            total_weight = sum(keyword_weights.values())
            earned_weight = sum(w for k, w in keyword_weights.items() if re.search(r'\b' + re.escape(k.lower()) + r'\b', resume_lower))
            keyword_match_pct = int(round((earned_weight / total_weight) * 100)) if total_weight > 0 else skill_match_pct
        else:
            keyword_match_pct = skill_match_pct

        # 3. Structure Score (20%)
        structure_score = 90
        standard_sections = ["experience", "education", "projects", "skills", "certifications"]
        found_sections = [sec for sec in standard_sections if sec in resume_lower]
        section_penalty = (len(standard_sections) - len(found_sections)) * 10
        structure_score = max(50, structure_score - section_penalty)

        # 4. Target Role Relevance Score (20%)
        role_terms = target_role_id.replace("_", " ").split()
        relevance_matches = sum(1 for term in role_terms if term.lower() in resume_lower)
        role_relevance_pct = min(100, max(40, int((relevance_matches / max(1, len(role_terms))) * 100)))

        # 5. Formatting Score
        formatting_score = 95
        if len(resume_text) < 200:
            formatting_score -= 30
        if re.search(r'[^\x00-\x7F]+', resume_text):  # Unusual Unicode symbols/complex graphics artifacts
            formatting_score -= 10

        # Overall Weighted Composite Score
        overall_ats = int(round(
            (keyword_match_pct * 0.30) +
            (skill_match_pct * 0.30) +
            (role_relevance_pct * 0.20) +
            (structure_score * 0.10) +
            (formatting_score * 0.10)
        ))

        overall_ats = min(98, max(25, overall_ats))

        missing_keywords = [req for req in required_skills if req not in found_in_resume]

        # Extract weak bullets for AI rewrite suggestions
        weak_bullets = self._extract_weak_bullets(resume_text)

        return {
            "overall_ats": overall_ats,
            "breakdown": {
                "keyword_match": keyword_match_pct,
                "skills_match": skill_match_pct,
                "role_relevance": role_relevance_pct,
                "structure": structure_score,
                "formatting": formatting_score
            },
            "found_skills": found_in_resume,
            "missing_keywords": missing_keywords,
            "weak_bullets": weak_bullets
        }

    def _extract_weak_bullets(self, text):
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        weak_bullets = []
        
        # Look for passive or generic lines lacking action verbs or metrics
        weak_starters = ["worked on", "developed a", "assisted with", "responsible for", "helped in", "created a"]
        for line in lines:
            line_lower = line.lower()
            if any(starter in line_lower for starter in weak_starters) and len(line) < 100:
                weak_bullets.append(line)
                if len(weak_bullets) >= 3:
                    break
        
        if not weak_bullets:
            weak_bullets = [
                "Developed a website using Python.",
                "Worked on database queries for backend.",
                "Assisted in writing unit tests for the application."
            ]

        return weak_bullets
