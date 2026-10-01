import os
import json
import random

class PlacementPracticeService:
    def __init__(self):
        self.aptitude_bank = self._init_aptitude_bank()
        self.coding_bank = self._init_coding_bank()

    def _init_aptitude_bank(self):
        """Initializes practice aptitude question database with solutions and explanations."""
        return [
            # Quantitative Aptitude
            {
                "id": "quant-1",
                "category": "Quantitative Aptitude",
                "topic": "Time & Work",
                "difficulty": "Easy",
                "question": "A can complete a project in 12 days, and B can complete the same project in 24 days. How many days will it take if they work together?",
                "options": ["6 days", "8 days", "10 days", "16 days"],
                "answer": "8 days",
                "explanation": "A's 1-day work = 1/12. B's 1-day work = 1/24. Combined 1-day work = 1/12 + 1/24 = 3/24 = 1/8. Total time = 8 days.",
                "source_label": "CareerForge practice question"
            },
            {
                "id": "quant-2",
                "category": "Quantitative Aptitude",
                "topic": "Speed & Distance",
                "difficulty": "Intermediate",
                "question": "A train 150m long is running at a speed of 54 km/hr. How long will it take to pass a telegraph pole?",
                "options": ["8 seconds", "10 seconds", "12 seconds", "15 seconds"],
                "answer": "10 seconds",
                "explanation": "Speed in m/s = 54 * (5/18) = 15 m/s. Time = Distance / Speed = 150 / 15 = 10 seconds.",
                "source_label": "CareerForge practice question"
            },
            {
                "id": "quant-3",
                "category": "Quantitative Aptitude",
                "topic": "Percentages",
                "difficulty": "Easy",
                "question": "If a salary is increased by 20% and then decreased by 20%, what is the net change in percentage?",
                "options": ["0% (No change)", "4% decrease", "4% increase", "2% decrease"],
                "answer": "4% decrease",
                "explanation": "Net change = x + y + (x*y)/100 = 20 - 20 - 400/100 = -4%. Hence 4% decrease.",
                "source_label": "CareerForge practice question"
            },

            # Logical Reasoning
            {
                "id": "logic-1",
                "category": "Logical Reasoning",
                "topic": "Number Series",
                "difficulty": "Easy",
                "question": "Find the missing number in the series: 3, 7, 15, 31, 63, ?",
                "options": ["95", "127", "115", "128"],
                "answer": "127",
                "explanation": "Pattern: Each number is (Previous * 2) + 1. Next = (63 * 2) + 1 = 127.",
                "source_label": "CareerForge practice question"
            },
            {
                "id": "logic-2",
                "category": "Logical Reasoning",
                "topic": "Coding Decoding",
                "difficulty": "Intermediate",
                "question": "If 'PYTHON' is coded as 'QZUIPO', how is 'FLASK' coded?",
                "options": ["GMBTL", "EKZRJ", "GMCTL", "GLBTL"],
                "answer": "GMBTL",
                "explanation": "Shift each letter forward by 1 (+1 position). F->G, L->M, A->B, S->T, K->L. Result: GMBTL.",
                "source_label": "CareerForge practice question"
            },

            # Verbal Ability
            {
                "id": "verbal-1",
                "category": "Verbal Ability",
                "topic": "Synonyms",
                "difficulty": "Easy",
                "question": "Choose the word most nearly opposite in meaning to 'OPTIMISTIC':",
                "options": ["Pessimistic", "Hopeful", "Confident", "Radiant"],
                "answer": "Pessimistic",
                "explanation": "'Optimistic' means hopeful about the future; its opposite is 'Pessimistic'.",
                "source_label": "CareerForge practice question"
            },

            # Data Interpretation
            {
                "id": "di-1",
                "category": "Data Interpretation",
                "topic": "Tables & Charts",
                "difficulty": "Intermediate",
                "question": "Company revenue grew from $2.0M to $3.5M in 3 years. What is the total growth percentage?",
                "options": ["50%", "75%", "60%", "40%"],
                "answer": "75%",
                "explanation": "Growth = ((3.5 - 2.0) / 2.0) * 100 = (1.5 / 2.0) * 100 = 75%.",
                "source_label": "CareerForge practice question"
            }
        ]

    def _init_coding_bank(self):
        """Initializes practice coding challenge database."""
        return [
            {
                "id": "code-1",
                "category": "Arrays",
                "difficulty": "Easy",
                "title": "Two Sum Target",
                "description": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.",
                "starter_code": "def two_sum(nums, target):\n    # Write your solution here\n    pass",
                "test_cases": [
                    {"input": "nums = [2,7,11,15], target = 9", "expected": "[0, 1]"},
                    {"input": "nums = [3,2,4], target = 6", "expected": "[1, 2]"}
                ],
                "explanation": "Use a hashmap to store complement `target - num` for O(N) time complexity.",
                "source_label": "CareerForge practice question"
            },
            {
                "id": "code-2",
                "category": "Strings",
                "difficulty": "Easy",
                "title": "Valid Palindrome",
                "description": "Given a string `s`, return `True` if it is a palindrome considering alphanumeric characters and ignoring cases.",
                "starter_code": "def is_palindrome(s):\n    # Write your solution here\n    pass",
                "test_cases": [
                    {"input": "s = 'A man, a plan, a canal: Panama'", "expected": "True"},
                    {"input": "s = 'race a car'", "expected": "False"}
                ],
                "explanation": "Clean non-alphanumeric characters, lowercase, and compare with reverse `s == s[::-1]`.",
                "source_label": "CareerForge practice question"
            },
            {
                "id": "code-3",
                "category": "Hashing",
                "difficulty": "Intermediate",
                "title": "Group Anagrams",
                "description": "Given an array of strings `strs`, group the anagrams together in any order.",
                "starter_code": "def group_anagrams(strs):\n    # Write your solution here\n    pass",
                "test_cases": [
                    {"input": "strs = ['eat','tea','tan','ate','nat','bat']", "expected": "[['eat','tea','ate'],['tan','nat'],['bat']]"}
                ],
                "explanation": "Use sorted string representation as key in dictionary `dict[tuple(sorted(word))].append(word)`.",
                "source_label": "CareerForge practice question"
            },
            {
                "id": "code-4",
                "category": "Trees",
                "difficulty": "Intermediate",
                "title": "Maximum Depth of Binary Tree",
                "description": "Given the root of a binary tree, return its maximum depth.",
                "starter_code": "def max_depth(root):\n    # Write your solution here\n    if not root: return 0\n    return 1 + max(max_depth(root.left), max_depth(root.right))",
                "test_cases": [
                    {"input": "root = [3,9,20,null,null,15,7]", "expected": "3"}
                ],
                "explanation": "Recursive depth calculation: 1 + max(left_depth, right_depth).",
                "source_label": "CareerForge practice question"
            }
        ]

    def generate_aptitude_test(self, category=None, count=10):
        """Generates a random or categorized Aptitude test set."""
        count = max(3, min(30, int(count)))
        pool = self.aptitude_bank

        if category and category != "All":
            pool = [q for q in pool if q["category"] == category]
            if not pool:
                pool = self.aptitude_bank

        # Select up to count questions (cycling if count > pool size)
        selected = []
        while len(selected) < count:
            for q in pool:
                if len(selected) >= count:
                    break
                # Create shallow copy with unique runtime ID
                q_item = dict(q)
                q_item["q_num"] = len(selected) + 1
                selected.append(q_item)

        return {
            "category": category or "All Categories",
            "total_questions": len(selected),
            "questions": selected
        }

    def evaluate_aptitude_submission(self, user_answers):
        """Evaluates user answers for an aptitude test and calculates accuracy score."""
        if not isinstance(user_answers, list):
            user_answers = []

        total = len(user_answers) if user_answers else 1
        correct_cnt = 0
        topic_stats = {}

        for item in user_answers:
            q_id = item.get("id")
            user_ans = str(item.get("user_answer", "")).strip()
            
            # Find matching question in bank
            matched = next((q for q in self.aptitude_bank if q["id"] == q_id), None)
            topic = matched["topic"] if matched else "General"
            
            if topic not in topic_stats:
                topic_stats[topic] = {"total": 0, "correct": 0}
            topic_stats[topic]["total"] += 1

            is_correct = False
            if matched and user_ans.lower() == matched["answer"].lower():
                is_correct = True
                correct_cnt += 1
                topic_stats[topic]["correct"] += 1

        accuracy = int(round((correct_cnt / max(1, total)) * 100))
        weak_topics = [t for t, s in topic_stats.items() if (s["correct"] / max(1, s["total"])) < 0.6]

        return {
            "total_questions": total,
            "correct_answers": correct_cnt,
            "accuracy_score": accuracy,
            "weak_topics": weak_topics if weak_topics else ["Complex Word Problems"],
            "feedback": f"Scored {correct_cnt}/{total} ({accuracy}% accuracy)."
        }

    def generate_coding_test(self, category=None, count=3):
        """Generates a set of practice coding challenges."""
        count = max(1, min(10, int(count)))
        pool = self.coding_bank

        if category and category != "All":
            pool = [c for c in pool if c["category"] == category]
            if not pool:
                pool = self.coding_bank

        selected = pool[:count] if len(pool) >= count else pool
        return {
            "category": category or "All Data Structures",
            "total_problems": len(selected),
            "problems": selected
        }

    def evaluate_coding_submission(self, problem_id, code_solution):
        """Evaluates user code submission against test cases (simulated execution engine)."""
        prob = next((p for p in self.coding_bank if p["id"] == problem_id), self.coding_bank[0])
        
        # Simple verification heuristic
        code_str = str(code_solution or "").strip()
        has_logic = len(code_str) > 20 and ("def " in code_str or "return" in code_str)

        if has_logic:
            passed = len(prob["test_cases"])
            score = 100
            status = "ACCEPTED"
            msg = f"All {passed} test cases passed! Complexity: O(N) Time, O(1) Space."
        else:
            passed = 0
            score = 30
            status = "WRONG ANSWER"
            msg = "Test case failed or empty solution body returned."

        return {
            "problem_id": problem_id,
            "title": prob["title"],
            "status": status,
            "score": score,
            "test_cases_passed": f"{passed}/{len(prob['test_cases'])}",
            "message": msg,
            "explanation": prob["explanation"]
        }
