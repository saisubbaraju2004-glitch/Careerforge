import json
from pathlib import Path
from config.config import Config

class CareerEngine:
    def __init__(self):
        self.roles_data = self._load_json(Config.DATA_FOLDER / "roles.json")
        self.skills_data = self._load_json(Config.DATA_FOLDER / "skills.json")
        self.resources_data = self._load_json(Config.DATA_FOLDER / "resources.json")

    def _load_json(self, filepath):
        if not filepath.exists():
            return {}
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_roles(self):
        roles_list = []
        for role_id, role_info in self.roles_data.items():
            roles_list.append({
                "id": role_id,
                "title": role_info.get("title", role_id),
                "category": role_info.get("category", "General"),
                "required_skills": role_info.get("required_skills", [])
            })
        return roles_list

    def analyze_skill_gap(self, target_role_id, user_skills):
        role_info = self.roles_data.get(target_role_id, {})
        if not role_info:
            # Fallback if unknown role string passed
            required_skills = ["Python", "REST APIs", "SQL", "Git", "Testing", "Docker"]
            optional_skills = ["PostgreSQL", "CI/CD"]
            role_title = target_role_id.replace("_", " ").title()
        else:
            required_skills = role_info.get("required_skills", [])
            optional_skills = role_info.get("optional_skills", [])
            role_title = role_info.get("title", target_role_id)

        user_skills_lower = [s.strip().lower() for s in user_skills if s.strip()]

        strong_skills = []
        improvement_skills = []
        missing_skills = []

        for req in required_skills:
            req_lower = req.lower()
            if req_lower in user_skills_lower:
                strong_skills.append(req)
            elif any(req_lower in s or s in req_lower for s in user_skills_lower):
                improvement_skills.append(req)
            else:
                missing_skills.append(req)

        # Calculate readiness score deterministically
        total_req = len(required_skills) if required_skills else 1
        matched_score = (len(strong_skills) * 1.0) + (len(improvement_skills) * 0.5)
        raw_percentage = (matched_score / total_req) * 100
        readiness_score = int(min(100, max(15, round(raw_percentage))))

        # Collect curated resources for missing/improvement skills
        skill_resources = {}
        for skill in missing_skills + improvement_skills:
            if skill in self.resources_data:
                skill_resources[skill] = self.resources_data[skill]

        return {
            "role_id": target_role_id,
            "role_title": role_title,
            "readiness_score": readiness_score,
            "strong_skills": strong_skills,
            "improvement_skills": improvement_skills,
            "missing_skills": missing_skills,
            "optional_skills": optional_skills,
            "resources": skill_resources
        }

    def generate_fallback_diagnosis(self, skill_analysis):
        missing = skill_analysis["missing_skills"]
        improvement = skill_analysis["improvement_skills"]
        score = skill_analysis["readiness_score"]
        role_title = skill_analysis["role_title"]

        blockers = []
        rank = 1
        for m in missing[:3]:
            blockers.append({
                "rank": f"0{rank}",
                "skill": m,
                "impact": "HIGH",
                "reason": f"Crucial core requirement for {role_title} technical interviews."
            })
            rank += 1

        for imp in improvement[:2]:
            if rank > 4:
                break
            blockers.append({
                "rank": f"0{rank}",
                "skill": imp,
                "impact": "MEDIUM",
                "reason": "Needs deeper practical hands-on application and project proof."
            })
            rank += 1

        return {
            "diagnosis_summary": f"You have strong foundations, but missing key requirements like {', '.join(missing[:2]) or 'advanced tools'} holds back your readiness for {role_title}.",
            "blockers": blockers,
            "priority_advice": "Focus your immediate 30 days on mastering high-impact missing skills first."
        }

    def generate_fallback_project(self, target_role_title, missing_skills):
        skills_str = ", ".join(missing_skills[:3]) if missing_skills else "REST APIs, PostgreSQL"
        return {
            "title": f"Production-Ready {target_role_title} API Suite",
            "technologies": ["Python", "Flask", "SQL"] + missing_skills[:2],
            "why_this_project": f"This project directly proves your competency in {skills_str}, bridging your current gap for tech interviews.",
            "roadmap": [
                {"week": "Week 1", "focus": "Architecture & Core CRUD Endpoints"},
                {"week": "Week 2", "focus": "Database Schema & Relationships"},
                {"week": "Week 3", "focus": "Authentication & Comprehensive Testing"},
                {"week": "Week 4", "focus": "Containerization (Docker) & Deployment"}
            ]
        }

    def generate_fallback_30_day_plan(self, hours_per_day, missing_skills):
        plan = []
        primary_missing = missing_skills if missing_skills else ["REST APIs", "PostgreSQL", "Docker", "Testing"]
        
        days_per_skill = max(1, 30 // len(primary_missing))
        
        day = 1
        for skill in primary_missing:
            res_info = self.resources_data.get(skill, {
                "documentation": "https://developer.mozilla.org/",
                "tutorial": "https://realpython.com/",
                "practice": "https://leetcode.com/"
            })
            for d in range(days_per_skill):
                if day > 30:
                    break
                
                if d == 0:
                    topic = f"Introduction to {skill} & Core Concepts"
                    obj = [f"Understand fundamental architecture of {skill}", "Set up local development environment"]
                    task = f"Read official documentation and run first 'Hello World' code for {skill}."
                    res_url = res_info.get("documentation", "https://docs.python.org/3/")
                elif d == 1:
                    topic = f"Hands-on {skill} Implementation"
                    obj = [f"Build functional module using {skill}", "Implement basic error handling"]
                    task = f"Write a practical working script incorporating {skill}."
                    res_url = res_info.get("tutorial", "https://realpython.com/")
                else:
                    topic = f"Advanced {skill} Integration & Optimization"
                    obj = [f"Integrate {skill} into existing project", "Write test cases"]
                    task = f"Connect {skill} component to API backend."
                    res_url = res_info.get("practice", "https://leetcode.com/")

                plan.append({
                    "day": day,
                    "topic": topic,
                    "time_est": f"{hours_per_day} hours",
                    "learning_objectives": obj,
                    "resource": res_url,
                    "hands_on_task": task,
                    "checkpoints": ["□ Concept verified", "□ Code executed", "□ Committed to Git"]
                })
                day += 1

        while day <= 30:
            plan.append({
                "day": day,
                "topic": "Final Capstone Integration & Resume Polish",
                "time_est": f"{hours_per_day} hours",
                "learning_objectives": ["Assemble project components", "Prepare interview talking points"],
                "resource": "https://github.com/",
                "hands_on_task": "Push final codebase to GitHub and write detailed README.md.",
                "checkpoints": ["□ Repo public", "□ README live", "□ Resume updated"]
            })
            day += 1

        return plan

