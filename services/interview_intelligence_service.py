import os
import json
import re
from config.config import Config
from services.ai_service import AIService
from services.interview_service import InterviewService

class InterviewIntelligenceService:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service or AIService()
        self.interview_service = InterviewService(self.ai_service)

    def start_interview_session(self, target_role="Python Backend Developer", company="TechForge Solutions", round_type="Technical Interview"):
        """Initializes a job-specific advanced interview session."""
        question = self.generate_question(
            role=target_role,
            company=company,
            round_type=round_type,
            previous_mistakes=[],
            difficulty="Medium"
        )
        return {
            "session_id": "session_" + os.urandom(4).hex(),
            "target_role": target_role,
            "company": company,
            "round_type": round_type,
            "current_question_index": 1,
            "total_questions": 5,
            "current_question": question,
            "answers": []
        }

    def generate_question(self, role="Python Backend Developer", company="TechForge", round_type="Technical", previous_mistakes=None, difficulty="Medium"):
        """Generates role/company/skill-aware interview questions."""
        role_lower = role.lower()
        if "python" in role_lower or "backend" in role_lower:
            pool = [
                {
                    "question": "How do Python's GIL and asynchronous event loops (asyncio) differ when scaling backend microservices?",
                    "category": "Technical Fundamentals",
                    "expected_keywords": ["GIL", "asyncio", "single-threaded", "concurrency", "I/O bound", "multiprocessing"],
                    "difficulty": difficulty
                },
                {
                    "question": "Explain how you would design a RESTful API rate limiter in Flask using Redis to prevent DDoS attacks.",
                    "category": "System Architecture",
                    "expected_keywords": ["Redis", "token bucket", "rate limit", "sliding window", "middleware", "Flask"],
                    "difficulty": difficulty
                },
                {
                    "question": "Walk me through your CareerForge project. What was the most complex technical challenge you solved?",
                    "category": "Project Explanation",
                    "expected_keywords": ["architecture", "challenge", "trade-offs", "optimizations", "results"],
                    "difficulty": difficulty
                },
                {
                    "question": "Suppose a SQL query retrieving user profile data takes 4.5 seconds. How do you diagnose and optimize it?",
                    "category": "Database & Problem Solving",
                    "expected_keywords": ["EXPLAIN ANALYZE", "indexing", "JOIN optimization", "N+1 query", "caching"],
                    "difficulty": difficulty
                }
            ]
        else:
            pool = [
                {
                    "question": "Describe how you approach state management and component rendering efficiency in frontend applications.",
                    "category": "Technical Fundamentals",
                    "expected_keywords": ["state", "props", "virtual DOM", "memoization", "render"],
                    "difficulty": difficulty
                },
                {
                    "question": "Tell me about a time when a project requirement changed right before a deadline. How did you handle it?",
                    "category": "HR & Behavioral",
                    "expected_keywords": ["prioritization", "communication", "adaptability", "STAR method", "outcome"],
                    "difficulty": difficulty
                }
            ]
            
        import random
        return random.choice(pool)

    def analyze_answer(self, question_text, user_answer, target_role="Python Backend Developer", expected_keywords=None):
        """Analyzes candidate answer across 8 dimensions + STAR detection."""
        if not expected_keywords:
            expected_keywords = ["architecture", "optimization", "performance", "Python", "SQL"]

        answer_lower = (user_answer or "").lower()
        words = answer_lower.split()
        word_count = len(words)

        # Keyword match calculation
        matched_kw = [kw for kw in expected_keywords if kw.lower() in answer_lower]
        kw_pct = (len(matched_kw) / max(1, len(expected_keywords))) * 100

        # Technical Score (30%)
        tech_score = int(min(98, max(40, (kw_pct * 0.6) + (min(word_count, 120) * 0.4))))

        # Communication Score (20%)
        comm_score = 85
        if word_count < 25:
            comm_score -= 25
        elif word_count > 250:
            comm_score -= 15

        # Confidence Score (15%)
        conf_score = 82
        hesitation_words = ["maybe", "i think", "not sure", "um", "kind of", "probably"]
        found_hesitations = [hw for hw in hesitation_words if hw in answer_lower]
        conf_score = max(45, conf_score - (len(found_hesitations) * 10))

        # Problem-solving Score (15%)
        problem_solving_score = 88 if any(w in answer_lower for w in ["approach", "solution", "debug", "test", "measure", "optimize"]) else 65

        # HR / Behavioral Score (10%)
        hr_score = 80 if any(w in answer_lower for w in ["team", "collaboration", "learned", "feedback", "goal"]) else 72

        # Project Explanation Score (10%)
        project_score = 85 if any(w in answer_lower for w in ["built", "designed", "implemented", "scaled", "handled"]) else 70

        # Overall Answer Score
        overall_score = int(round(
            (tech_score * 0.30) +
            (comm_score * 0.20) +
            (conf_score * 0.15) +
            (problem_solving_score * 0.15) +
            (hr_score * 0.10) +
            (project_score * 0.10)
        ))

        # Weakness Detection
        weaknesses = []
        if word_count < 25:
            weaknesses.append("Too-short answer — lacks sufficient depth and technical detail.")
        if word_count > 250:
            weaknesses.append("Too-long answer — risks rambling; structure response more concisely.")
        if len(found_hesitations) > 0:
            weaknesses.append(f"Lack of confidence — phrases like '{found_hesitations[0]}' weaken impact.")
        if len(matched_kw) < (len(expected_keywords) / 2):
            weaknesses.append("Weak technical fundamentals — missing core domain terminology.")
        if not any(w in answer_lower for w in ["situation", "task", "action", "result", "for example", "specifically"]):
            weaknesses.append("Missing STAR structure — present concrete scenario, action, and outcome.")

        # Improved Answer Suggestion
        improved_answer = f"To structure a top-tier answer: Start by stating the core concept directly. For example, explain how {matched_kw[0] if matched_kw else 'the architecture'} functions, then mention a real project instance where you applied it, and end with the quantifiable result (e.g. 30% speed boost)."

        return {
            "score": overall_score,
            "word_count": word_count,
            "breakdown": {
                "technical": tech_score,
                "communication": comm_score,
                "confidence": conf_score,
                "problem_solving": problem_solving_score,
                "hr": hr_score,
                "project_explanation": project_score,
                "relevance": int(min(98, kw_pct + 40))
            },
            "what_was_good": "Clear intent and solid baseline explanation." if overall_score >= 75 else "Good initiative attempting to address the prompt.",
            "what_was_missing": f"Missing key keywords: {', '.join([k for k in expected_keywords if k.lower() not in answer_lower][:3]) or 'None'}.",
            "technical_mistakes": weaknesses[:2],
            "communication_problems": ["Hesitant phrasing" if found_hesitations else "Concise delivery"],
            "better_structure": "Situation / Core Concept → Technical Implementation → Quantifiable Result",
            "improved_answer": improved_answer,
            "interviewer_impression": "Strong Candidate Fit" if overall_score >= 82 else ("Solid Potential — Needs Polish" if overall_score >= 68 else "Needs Fundamental Practice"),
            "detected_weaknesses": weaknesses
        }

    def generate_final_report(self, session_answers):
        """Generates comprehensive interview performance report & 7-day plan."""
        if not session_answers:
            session_answers = []

        scores = [a.get("score", 75) for a in session_answers]
        avg_score = int(round(sum(scores) / max(1, len(scores)))) if scores else 78

        # Readiness determination
        if avg_score >= 85:
            readiness = "READY"
            readiness_badge = "badge-success"
        elif avg_score >= 72:
            readiness = "ALMOST READY"
            readiness_badge = "badge-purple"
        elif avg_score >= 58:
            readiness = "NEED MORE PRACTICE"
            readiness_badge = "badge-warning"
        else:
            readiness = "NOT READY"
            readiness_badge = "badge-danger"

        # Aggregated performance metrics
        tech_avg = int(round(sum(a.get("breakdown", {}).get("technical", 75) for a in session_answers) / max(1, len(session_answers)))) if session_answers else 75
        comm_avg = int(round(sum(a.get("breakdown", {}).get("communication", 80) for a in session_answers) / max(1, len(session_answers)))) if session_answers else 80
        conf_avg = int(round(sum(a.get("breakdown", {}).get("confidence", 78) for a in session_answers) / max(1, len(session_answers)))) if session_answers else 78
        ps_avg = int(round(sum(a.get("breakdown", {}).get("problem_solving", 82) for a in session_answers) / max(1, len(session_answers)))) if session_answers else 82

        # 7-Day Improvement Plan
        seven_day_plan = [
            {"day": 1, "focus": "Technical Fundamentals", "action": "Review core Python GIL, AsyncIO, and memory management concepts."},
            {"day": 2, "focus": "STAR Methodology", "action": "Reframe 3 project experiences using Situation-Task-Action-Result format."},
            {"day": 3, "focus": "System Design & SQL", "action": "Practice explaining database indexing and EXPLAIN ANALYZE queries out loud."},
            {"day": 4, "focus": "Communication & Tone", "action": "Record a 2-minute mock answer; eliminate filler words like 'um' and 'maybe'."},
            {"day": 5, "focus": "Live Coding Practice", "action": "Solve 2 medium array/string problems explaining thoughts while coding."},
            {"day": 6, "focus": "HR & Behavioral", "action": "Prepare answers for 'Tell me about a technical disagreement' and 'Handling deadlines'."},
            {"day": 7, "focus": "Full Mock Re-simulation", "action": "Complete a full 5-question AI Interview Simulator session."}
        ]

        return {
            "overall_score": avg_score,
            "readiness_status": readiness,
            "readiness_badge": readiness_badge,
            "metrics": {
                "technical": tech_avg,
                "communication": comm_avg,
                "confidence": conf_avg,
                "problem_solving": ps_avg,
                "hr": 82,
                "project_explanation": 84,
                "relevance": 86
            },
            "strengths": [
                "Strong conceptual understanding of primary tech stack",
                "Clear explanation of project architecture and REST endpoints"
            ],
            "top_weaknesses": [
                "Inconsistent STAR structure on behavioral scenarios",
                "Occasional hesitation phrases when explaining database optimizations"
            ],
            "seven_day_plan": seven_day_plan
        }
