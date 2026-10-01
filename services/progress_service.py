import json
from config.config import Config

class ProgressService:
    def __init__(self, career_engine=None):
        self.career_engine = career_engine

    def calculate_skill_heatmap(self, target_role_id, user_skills):
        user_skills_lower = set(s.strip().lower() for s in user_skills if s.strip())

        role_info = {}
        if self.career_engine and hasattr(self.career_engine, "roles_data"):
            role_info = self.career_engine.roles_data.get(target_role_id, {})

        required = [s.lower() for s in role_info.get("required_skills", ["python", "flask", "sql", "git", "docker"])]

        categories = {
            "Programming": ["Python", "JavaScript", "HTML", "CSS", "C++", "Java"],
            "Backend": ["Flask", "REST APIs", "Node.js", "Django", "FastAPI"],
            "Database": ["SQL", "PostgreSQL", "MongoDB", "Redis", "MySQL"],
            "AI & ML": ["NumPy", "Pandas", "PyTorch", "Scikit-Learn", "LLM APIs"],
            "DevOps & Tools": ["Docker", "Git", "Testing", "CI/CD", "AWS"],
            "Soft Skills": ["Technical Communication", "System Architecture", "Problem Solving"]
        }

        heatmap = {}
        for cat_name, skill_list in categories.items():
            cat_skills = []
            for s in skill_list:
                s_lower = s.lower()
                if s_lower in user_skills_lower:
                    level = 5  # Strong
                    status = "GREEN"
                    label = "Strong"
                elif any(s_lower in u or u in s_lower for u in user_skills_lower):
                    level = 3  # Intermediate
                    status = "YELLOW"
                    label = "Intermediate"
                elif s_lower in required:
                    level = 1  # Missing core requirement
                    status = "RED"
                    label = "Missing Core"
                else:
                    level = 0  # Not started
                    status = "ORANGE"
                    label = "Not Started"

                cat_skills.append({
                    "name": s,
                    "level": level,
                    "max_level": 5,
                    "percentage": int((level / 5.0) * 100),
                    "status": status,
                    "label": label
                })
            heatmap[cat_name] = cat_skills

        return heatmap

    def calculate_career_radar(self, skill_gap_data, ats_score=75, interview_score=70, app_count=0):
        # Deterministic factor calculation
        readiness = skill_gap_data.get("readiness_score", 50)
        strong_cnt = len(skill_gap_data.get("strong_skills", []))
        total_req = max(1, strong_cnt + len(skill_gap_data.get("missing_skills", [])))

        tech_score = int(round((strong_cnt / total_req) * 100))
        proj_score = min(100, max(40, tech_score + 10))
        resume_score = min(100, max(30, ats_score))
        inter_score = min(100, max(30, interview_score))
        comm_score = min(100, max(45, int((resume_score * 0.4) + (inter_score * 0.6))))
        job_readiness = int(round((tech_score * 0.3) + (proj_score * 0.2) + (resume_score * 0.2) + (inter_score * 0.2) + (comm_score * 0.1)))

        categories = [
            {"category": "Technical Skills", "score": tech_score},
            {"category": "Projects", "score": proj_score},
            {"category": "Resume", "score": resume_score},
            {"category": "Interview", "score": inter_score},
            {"category": "Communication", "score": comm_score},
            {"category": "Job Readiness", "score": job_readiness}
        ]

        overall = int(round(sum(c["score"] for c in categories) / len(categories)))

        return {
            "overall_score": overall,
            "categories": categories
        }

    def determine_next_best_action(self, readiness_score, ats_score, missing_skills, interview_score, app_count):
        if ats_score < 65:
            return {
                "action": "Improve Your Resume ATS Score",
                "why": "Your resume ATS score is currently below 65%. High-impact keywords and formatting adjustments are needed before applying.",
                "button_text": "Optimize Resume",
                "target_tab": "tabATS",
                "icon": "fa-file-contract"
            }
        elif missing_skills and len(missing_skills) > 0:
            top_missing = missing_skills[0]
            return {
                "action": f"Master Core Missing Skill: {top_missing}",
                "why": f"'{top_missing}' is currently your highest-priority missing requirement for passing technical screens.",
                "button_text": "Start Learning Plan",
                "target_tab": "tabPlan",
                "icon": "fa-bullseye"
            }
        elif interview_score < 70:
            return {
                "action": "Practice Technical Interview Simulator",
                "why": "Your technical interview evaluation is below 70%. Practice answering mock questions to build confidence.",
                "button_text": "Start Mock Interview",
                "target_tab": "interview",
                "icon": "fa-microphone"
            }
        elif app_count < 3:
            return {
                "action": "Submit Applications to Target Roles",
                "why": "Your profile & technical readiness are strong! Start applying to open placement positions.",
                "button_text": "View Job Applications",
                "target_tab": "tabJobs",
                "icon": "fa-paper-plane"
            }
        else:
            return {
                "action": "Complete Today's Capstone Development Task",
                "why": "Keep your daily momentum active by building project features and committing to GitHub.",
                "button_text": "View Capstone Roadmap",
                "target_tab": "tabProject",
                "icon": "fa-cube"
            }
