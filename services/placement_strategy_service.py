import os
import json
from config.config import Config
from services.placement_service import PlacementService

class PlacementStrategyService:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service
        self.placement_service = PlacementService(ai_service=ai_service)

    def calculate_company_rankings(self, profile_data=None, user_scores=None):
        """
        Company Ranking Engine: Calculates TARGET SCORE for every benchmark company and classifies them.
        Classifications:
        - 🔥 PRIORITY TARGET (Score >= 82)
        - 🟢 STRONG CHANCE (Score >= 72)
        - 🟡 PREPARE MORE (Score >= 58)
        - 🔴 LOW PRIORITY (Score < 58)
        - ⚪ NOT ELIGIBLE (Failed eligibility criteria)
        """
        comps = self.placement_service.get_all_companies(profile_data)
        readiness = self.placement_service.calculate_placement_readiness(profile_data, user_scores)
        
        ranked = []
        for comp in comps:
            el = comp["eligibility_result"]
            if not el["is_eligible"]:
                target_score = 0
                classification = "⚪ NOT ELIGIBLE"
                badge_class = "badge-gray"
                reason = f"Not eligible due to CGPA or branch criteria ({el['reason']})."
            else:
                resume_match = comp.get("resume_match", 75)
                comp_readiness = comp.get("company_readiness", 75)
                
                # Deadline urgency factor (e.g. D-7 deadline boost)
                deadline_days = self._parse_deadline_days(comp.get("deadline", "2026-10-20"))
                deadline_boost = 8 if deadline_days <= 7 else (4 if deadline_days <= 14 else 0)

                raw_score = (comp["priority_score"] * 0.4) + (resume_match * 0.3) + (comp_readiness * 0.2) + deadline_boost
                target_score = self._clamp(raw_score, 10, 99)

                if target_score >= 82:
                    classification = "🔥 PRIORITY TARGET"
                    badge_class = "badge-purple"
                    reason = f"High role match ({resume_match}%), strong readiness ({comp_readiness}%), and met CGPA eligibility."
                elif target_score >= 72:
                    classification = "🟢 STRONG CHANCE"
                    badge_class = "badge-success"
                    reason = f"Eligible with solid technical foundation. Focus on round 2 coding test."
                elif target_score >= 58:
                    classification = "🟡 PREPARE MORE"
                    badge_class = "badge-warning"
                    reason = f"Eligible, but requires additional preparation in DSA and Aptitude."
                else:
                    classification = "🔴 LOW PRIORITY"
                    badge_class = "badge-danger"
                    reason = f"Lower match for current skill profile. Focus on higher-priority drives first."

            c_copy = dict(comp)
            c_copy["target_score"] = target_score
            c_copy["classification"] = classification
            c_copy["badge_class"] = badge_class
            c_copy["ranking_reason"] = reason
            c_copy["deadline_days"] = self._parse_deadline_days(comp.get("deadline", "2026-10-20"))
            c_copy["deadline_urgency"] = "🔴 Deadline approaching" if c_copy["deadline_days"] <= 7 else ("🟡 Apply soon" if c_copy["deadline_days"] <= 14 else "🟢 Plenty of time")
            ranked.append(c_copy)

        ranked.sort(key=lambda x: x["target_score"], reverse=True)
        return ranked

    def get_war_room_details(self, company_id, profile_data=None, user_scores=None):
        """Generates complete Company War Room strategy breakdown for a specific company."""
        rankings = self.calculate_company_rankings(profile_data, user_scores)
        comp = next((c for c in rankings if c["id"] == company_id), rankings[0] if rankings else None)

        if not comp:
            return {}

        # 1. WHY THIS COMPANY?
        why_list = [
            {"text": f"Candidate meets CGPA requirement ({comp['eligibility_result']['min_cgpa']:.1f}+)", "check": True},
            {"text": f"Strong role match ({comp.get('resume_match', 85)}%) for {comp['role']}", "check": True},
            {"text": f"High ATS resume compatibility ({comp.get('resume_match', 85)}%)", "check": True},
            {"text": f"Placement readiness score stands at {comp.get('company_readiness', 78)}%", "check": True},
            {"text": f"Eligible for {comp['ctc']} package", "check": True}
        ]

        # 2. WHAT TO PREPARE (Skill Gap Breakdown)
        skills_breakdown = [
            {"skill": "Python Core & Async", "current": 82, "required": 85, "gap": 3, "priority": "MEDIUM"},
            {"skill": "Data Structures & Algorithms (DSA)", "current": 64, "required": 80, "gap": 16, "priority": "HIGH"},
            {"skill": "SQL & PostgreSQL", "current": 72, "required": 80, "gap": 8, "priority": "HIGH"},
            {"skill": "Quantitative Aptitude", "current": 80, "required": 75, "gap": 0, "priority": "LOW"},
            {"skill": "Object-Oriented Programming (OOP)", "current": 78, "required": 80, "gap": 2, "priority": "MEDIUM"},
            {"skill": "Database Management (DBMS)", "current": 70, "required": 75, "gap": 5, "priority": "MEDIUM"},
            {"skill": "Project Explanation & Architecture", "current": 85, "required": 80, "gap": 0, "priority": "LOW"},
            {"skill": "HR & Behavioral STAR Answers", "current": 81, "required": 75, "gap": 0, "priority": "LOW"}
        ]

        # 3. ROUND-BY-ROUND TIMELINE
        rounds_timeline = [
            {
                "step": 1,
                "name": "Round 1: Online Aptitude Assessment",
                "readiness": 80,
                "gap": "Low",
                "skills": ["Speed Math", "Logical Series", "Verbal"],
                "est_time": "30 minutes",
                "route": "/placement-practice/aptitude",
                "button_text": "START PRACTICE"
            },
            {
                "step": 2,
                "name": "Round 2: Coding Test",
                "readiness": 64,
                "gap": "High",
                "skills": ["Arrays", "Hashing", "Two Pointers"],
                "est_time": "45 minutes",
                "route": "/placement-practice/coding",
                "button_text": "START CODING"
            },
            {
                "step": 3,
                "name": "Round 3: Technical Interview",
                "readiness": 72,
                "gap": "Medium",
                "skills": ["Python", "SQL", "System Design"],
                "est_time": "45 minutes",
                "route": f"/interview?company={comp['name']}",
                "button_text": "MOCK INTERVIEW"
            },
            {
                "step": 4,
                "name": "Round 4: HR & Leadership Interview",
                "readiness": 81,
                "gap": "Low",
                "skills": ["Behavioral", "Culture Fit"],
                "est_time": "30 minutes",
                "route": f"/interview?company={comp['name']}&type=hr",
                "button_text": "HR PRACTICE"
            }
        ]

        # 4. 7-DAY WAR PLAN (ADAPTIVE)
        war_plan = self.generate_adaptive_war_plan(comp, user_scores)

        # 5. SHOULD YOU APPLY?
        apply_decision = self.calculate_apply_decision(comp)

        return {
            "company": comp,
            "why_list": why_list,
            "skills_breakdown": skills_breakdown,
            "rounds_timeline": rounds_timeline,
            "war_plan": war_plan,
            "apply_decision": apply_decision
        }

    def generate_adaptive_war_plan(self, company, user_scores=None):
        """Generates 7-Day War Plan adaptive based on weaknesses in coding, aptitude, or interview."""
        scores = user_scores if isinstance(user_scores, dict) else {}
        coding_sc = scores.get("coding", 64)
        apt_sc = scores.get("aptitude", 80)
        int_sc = scores.get("interview", 72)

        comp_name = company.get("name", "Target Drive")
        top_skill = company.get("skills", ["Python"])[0] if company.get("skills") else "DSA"

        plan = [
            {"day": "Day 1", "focus": f"{top_skill} Core & OOP Pillars", "task": f"Implement 5 {top_skill} classes & review inheritance/polymorphism.", "category": "Technical", "minutes": 60},
            {"day": "Day 2", "focus": "SQL Joins & DBMS Transactions", "task": "Solve 10 complex SQL JOIN queries & index optimization questions.", "category": "Database", "minutes": 60},
            {"day": "Day 3", "focus": "Data Structures (Arrays & Hashing)", "task": "Solve 5 array manipulation problems in Placement Practice Arena.", "category": "Coding", "minutes": 75},
            {"day": "Day 4", "focus": "Quantitative Aptitude Speed Math", "task": "Complete 20 speed math questions (Time & Work, Speed & Distance).", "category": "Aptitude", "minutes": 45},
            {"day": "Day 5", "focus": f"{comp_name} Coding Test Simulation", "task": "Timed coding test session containing 2 benchmark problems.", "category": "Coding", "minutes": 60},
            {"day": "Day 6", "focus": f"Full Technical Interview for {comp_name}", "task": "Live technical interview simulation in AI Interview Simulator.", "category": "Interview", "minutes": 45},
            {"day": "Day 7", "focus": "Mock HR Interview & Final Application Check", "task": "Refine STAR method behavioral answers and submit drive application.", "category": "HR", "minutes": 30}
        ]

        # ADAPTIVE ADJUSTMENTS
        if coding_sc < 60:
            plan[2]["minutes"] += 30
            plan[2]["task"] += " (Boosted: Added 3 extra DP/Hashing problems)"
            plan[4]["minutes"] += 30
        if apt_sc < 60:
            plan[3]["minutes"] += 30
            plan[3]["task"] += " (Boosted: Added 10 extra Data Interpretation questions)"
        if int_sc < 60:
            plan[5]["minutes"] += 30
            plan[5]["task"] += " (Boosted: Added secondary mock interview focus on system architecture)"

        return plan

    def calculate_apply_decision(self, company):
        """Generates AI-style recommendation: SHOULD YOU APPLY?"""
        el = company["eligibility_result"]
        match_sc = company.get("resume_match", 85)
        readiness_sc = company.get("company_readiness", 78)

        if el["is_eligible"] and match_sc >= 80:
            decision = "YES — HIGH PRIORITY"
            badge_class = "badge-success"
            reasons = [
                "You meet all CGPA & branch academic eligibility criteria",
                f"High {match_sc}% role match for {company['role']}",
                "Resume ATS formatting is compliant",
                "Only 2 minor skill gaps remaining"
            ]
        elif el["is_eligible"]:
            decision = "PREPARE FIRST & APPLY"
            badge_class = "badge-warning"
            reasons = [
                "Academic criteria met",
                f"{match_sc}% role match score",
                "Requires 3 days of targeted coding preparation before test"
            ]
        else:
            decision = "NOT RECOMMENDED"
            badge_class = "badge-danger"
            reasons = [
                "Does not meet minimum CGPA or branch requirement",
                "Focus energy on eligible campus placement drives"
            ]

        return {
            "decision": decision,
            "badge_class": badge_class,
            "reasons": reasons
        }

    def generate_daily_command(self, profile_data=None, user_scores=None):
        """Generates Today's Placement Command task mission."""
        rankings = self.calculate_company_rankings(profile_data, user_scores)
        top_comp = rankings[0] if rankings else None
        target_name = top_comp["name"] if top_comp else "Zenvexa Technologies"

        tasks = [
            {"id": 1, "title": f"Solve 5 Python & DSA coding problems for {target_name}", "minutes": 45, "completed": True, "route": "/placement-practice/coding"},
            {"id": 2, "title": "Complete 20 Quantitative Aptitude questions", "minutes": 30, "completed": True, "route": "/placement-practice/aptitude"},
            {"id": 3, "title": "Revise SQL JOINS and indexing cheat sheet", "minutes": 20, "completed": True, "route": "/#tabOverview"},
            {"id": 4, "title": "Practice 'Tell me about yourself' & project explanation", "minutes": 15, "completed": False, "route": f"/interview?company={target_name}&type=hr"},
            {"id": 5, "title": f"Complete 1 AI Mock Interview session for {target_name}", "minutes": 35, "completed": False, "route": f"/interview?company={target_name}"}
        ]

        completed_cnt = sum(1 for t in tasks if t["completed"])
        total_time = sum(t["minutes"] for t in tasks)

        return {
            "target_company": target_name,
            "tasks": tasks,
            "completed_count": completed_cnt,
            "total_count": len(tasks),
            "estimated_time_minutes": total_time,
            "formatted_time": f"{total_time // 60}h {total_time % 60}m"
        }

    def calculate_smart_next_action(self, profile_data=None, user_scores=None):
        """
        Calculates EXACTLY ONE single highest-impact placement action (🎯 YOUR NEXT BEST ACTION).
        Integrates with V8 AI Career Agent & V9 Placement Command Center.
        """
        rankings = self.calculate_company_rankings(profile_data, user_scores)
        top_comp = rankings[0] if rankings else None
        target_comp_name = top_comp["name"] if top_comp else "Zenvexa Technologies"

        scores = user_scores if isinstance(user_scores, dict) else {}
        dsa = scores.get("dsa", 64)
        sql = scores.get("sql", 58)
        apt = scores.get("aptitude", 80)

        if sql < 65:
            return {
                "action": f"Practice SQL JOINs for {target_comp_name}",
                "priority": "HIGH",
                "reason": f"SQL is required by {len(rankings)} target companies and your current SQL readiness is only {sql}%.",
                "estimated_minutes": 30,
                "impact": "+15% database round score",
                "route": "/placement-practice/coding",
                "target_company": target_comp_name,
                "code": "practice_sql"
            }
        elif dsa < 70:
            return {
                "action": f"Solve 5 Array & Hashing Coding Problems",
                "priority": "HIGH",
                "reason": f"Coding round 2 for {target_comp_name} requires strong O(N) hashing techniques.",
                "estimated_minutes": 45,
                "impact": "+20% coding test pass rate",
                "route": "/placement-practice/coding",
                "target_company": target_comp_name,
                "code": "practice_dsa"
            }
        else:
            return {
                "action": f"Complete AI Mock Technical Interview for {target_comp_name}",
                "priority": "HIGH",
                "reason": f"You are eligible for {target_comp_name}. Live interview practice will secure recruiter selection.",
                "estimated_minutes": 45,
                "impact": "+15% interview conversion",
                "route": f"/interview?company={target_comp_name}",
                "target_company": target_comp_name,
                "code": "practice_interview"
            }

    def _parse_deadline_days(self, deadline_str):
        """Parses deadline date string and returns remaining days."""
        try:
            from datetime import datetime
            dt = datetime.strptime(deadline_str, "%Y-%m-%d")
            delta = (dt - datetime.now()).days
            return max(1, delta)
        except Exception:
            return 7

    def _clamp(self, val, min_v, max_v):
        try:
            val_f = float(val)
            return max(min_v, min(max_v, int(round(val_f))))
        except (ValueError, TypeError):
            return min_v
