class RoadmapService:
    def __init__(self, career_engine=None):
        self.career_engine = career_engine

    def build_personalized_roadmap(self, target_role_id, skill_gap_analysis):
        strong_skills = set(s.lower() for s in skill_gap_analysis.get("strong_skills", []))
        improvement_skills = set(s.lower() for s in skill_gap_analysis.get("improvement_skills", []))
        missing_skills = set(s.lower() for s in skill_gap_analysis.get("missing_skills", []))

        role_info = {}
        if self.career_engine and hasattr(self.career_engine, "roles_data"):
            role_info = self.career_engine.roles_data.get(target_role_id, {})

        roadmap_flow = role_info.get("roadmap_flow", [
            {"name": "Python", "category": "core", "order": 1},
            {"name": "Flask", "category": "framework", "order": 2},
            {"name": "REST APIs", "category": "architecture", "order": 3},
            {"name": "SQL", "category": "database", "order": 4},
            {"name": "PostgreSQL", "category": "database", "order": 5},
            {"name": "Testing", "category": "quality", "order": 6},
            {"name": "Docker", "category": "devops", "order": 7}
        ])

        nodes = []
        for step in roadmap_flow:
            name = step["name"]
            name_lower = name.lower()

            if name_lower in strong_skills:
                status = "know"
                status_label = "Already Know"
                badge = "🟢"
            elif name_lower in improvement_skills:
                status = "improving"
                status_label = "Needs Improvement"
                badge = "🟡"
            else:
                status = "missing"
                status_label = "Missing Skill"
                badge = "🔴"

            nodes.append({
                "name": name,
                "category": step.get("category", "skill"),
                "order": step.get("order", 1),
                "status": status,
                "status_label": status_label,
                "badge": badge
            })

        return {
            "role_title": role_info.get("title", target_role_id.replace("_", " ").title()),
            "nodes": nodes
        }
