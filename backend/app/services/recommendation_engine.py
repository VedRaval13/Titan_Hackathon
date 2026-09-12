from app.schemas.recommendation import MatchResult, ScoreBreakdown

class RecommendationEngine:
    WEIGHTS = {
        "SKILL_MATCH": 0.35,
        "EXPERIENCE": 0.25,
        "AVAILABILITY": 0.20,
        "WORKLOAD": 0.15,
        "PAST_WORK": 0.05
    }

    @staticmethod
    def skill_match_score(required: list[str], employee_skills: list[str]) -> float:
        if not required:
            return 1.0
        if not required and not employee_skills:
            return 0.0
        
        req_set = {s.lower() for s in required}
        emp_set = {s.lower() for s in employee_skills}
        
        intersection = req_set.intersection(emp_set)
        union = req_set.union(emp_set)
        
        if not union:
            return 0.0
        return len(intersection) / len(union)

    @staticmethod
    def experience_score(years: int, difficulty: str) -> float:
        difficulty = difficulty.lower() if difficulty else "medium"
        if difficulty == "easy":
            if years <= 2: return 1.0
            elif years <= 5: return 0.9
            else: return 0.8
        elif difficulty == "hard":
            if years <= 2: return 0.2
            elif years <= 5: return 0.6
            else: return 1.0
        else:
            if years <= 2: return 0.5
            elif years <= 5: return 1.0
            else: return 0.9

    @staticmethod
    def availability_score(status: str, workload_score: float) -> float:
        status = status.lower()
        if status == "available":
            if workload_score < 4: return 1.0
            elif workload_score < 6: return 0.8
            else: return 0.6
        elif status == "partial":
            return 0.4
        elif status == "busy":
            return 0.2
        return 0.0

    @staticmethod
    def workload_score(current_workload: float) -> float:
        return max(0.0, min(1.0, 1.0 - (current_workload / 10.0)))

    @staticmethod
    def past_work_score(task_type: str | None, past_task_types: list[str]) -> float:
        if not task_type or not past_task_types:
            return 0.5
        count = sum(1 for t in past_task_types if t and t.lower() == task_type.lower())
        return min(1.0, count / max(len(past_task_types), 1))

    def compute_match_score(self, task_data: dict, employee_data: dict) -> MatchResult:
        s_skill = self.skill_match_score(task_data.get("required_skills", []), employee_data.get("skills", []))
        s_exp = self.experience_score(employee_data.get("experience_years", 0), task_data.get("difficulty_score", "medium"))
        
        emp_workload = employee_data.get("current_workload_score", 0.0)
        s_workload = self.workload_score(emp_workload)
        s_avail = self.availability_score(employee_data.get("availability_status", "available"), emp_workload)
        
        s_past = self.past_work_score(task_data.get("task_type"), employee_data.get("past_task_types", []))
        
        total = (
            s_skill * self.WEIGHTS["SKILL_MATCH"] +
            s_exp * self.WEIGHTS["EXPERIENCE"] +
            s_avail * self.WEIGHTS["AVAILABILITY"] +
            s_workload * self.WEIGHTS["WORKLOAD"] +
            s_past * self.WEIGHTS["PAST_WORK"]
        )
        
        if total > 0.8: confidence = "high"
        elif total > 0.5: confidence = "medium"
        else: confidence = "low"
        
        breakdown = ScoreBreakdown(
            skill_match=s_skill,
            experience=s_exp,
            availability=s_avail,
            workload=s_workload,
            past_work=s_past
        )
        
        return MatchResult(
            employee_id=employee_data["id"],
            employee_name=employee_data["name"],
            total_score=total,
            confidence=confidence,
            breakdown=breakdown,
            rank=0
        )

    def rank_employees(self, task_data: dict, employees_data: list[dict]) -> list[MatchResult]:
        results = []
        for emp in employees_data:
            results.append(self.compute_match_score(task_data, emp))
            
        results.sort(key=lambda x: x.total_score, reverse=True)
        for i, res in enumerate(results):
            res.rank = i + 1
            
        return results
