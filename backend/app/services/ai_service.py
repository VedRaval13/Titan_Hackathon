import json
import asyncio
import google.generativeai as genai
from app.config import settings
from app.schemas.ai_analysis import AIAnalysisResult

class GeminiAnalyzer:
    def __init__(self):
        api_key = getattr(settings, "GEMINI_API_KEY", "dummy_key")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def analyze_task(self, title: str, description: str) -> AIAnalysisResult:
        prompt = f"""
        Analyze the following task and return a JSON object with these exact keys:
        - required_skills: list of string technical skills needed
        - difficulty: string ('easy', 'medium', or 'hard')
        - task_type: string ('backend', 'frontend', 'devops', 'qa', 'design', 'data')
        - estimated_hours: integer estimate
        - complexity_notes: brief string explanation

        Task Title: {title}
        Task Description: {description}
        """
        
        delays = [1, 2, 4]
        for delay in delays + [0]:
            try:
                response = await self.model.generate_content_async(prompt)
                text = response.text
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].strip()
                
                data = json.loads(text)
                return AIAnalysisResult(**data)
            except Exception:
                if delay == 0:
                    break
                await asyncio.sleep(delay)
                
        return self._fallback_analysis(title, description)

    def _fallback_analysis(self, title: str, description: str) -> AIAnalysisResult:
        combined = f"{title} {description}".lower()
        skills = []
        keywords = ["python", "react", "javascript", "docker", "kubernetes", "sql", "java", "typescript", "aws", "css", "html", "node", "api", "database", "test", "deploy", "ci/cd", "figma"]
        for kw in keywords:
            if kw in combined:
                skills.append(kw)
        
        task_type = "backend"
        if any(k in combined for k in ["react", "css", "html", "ui"]): task_type = "frontend"
        elif any(k in combined for k in ["docker", "deploy", "k8s", "ci", "kubernetes", "aws"]): task_type = "devops"
        elif any(k in combined for k in ["test", "qa", "bug"]): task_type = "qa"
        elif any(k in combined for k in ["database", "sql", "data", "etl"]): task_type = "data"
        elif any(k in combined for k in ["design", "figma", "ui/ux"]): task_type = "design"

        length = len(combined)
        if length < 100: hours = 4
        elif length < 500: hours = 8
        else: hours = 16

        return AIAnalysisResult(
            required_skills=skills,
            difficulty="medium",
            task_type=task_type,
            estimated_hours=hours,
            complexity_notes="Fallback analysis used due to generation failure."
        )

    async def generate_recommendation_reason(self, task_title: str, employee_name: str, skills: list, score: float, breakdown: dict) -> str:
        skill_pct = round(breakdown.get('skill_match', 0) * 100)
        exp_pct = round(breakdown.get('experience', 0) * 100)
        workload_pct = round(breakdown.get('workload', 0) * 100)
        avail_pct = round(breakdown.get('availability', 0) * 100)
        score_pct = round(score * 100)

        prompt = f"""You are an AI assistant helping managers assign tasks to employees.

Task: "{task_title}"
Recommended Employee: {employee_name}
Their Skills: {', '.join(skills) if skills else 'General'}
Overall Match: {score_pct}%
Skill Match: {skill_pct}%
Experience Fit: {exp_pct}%
Workload Availability: {workload_pct}%

Write exactly 2 sentences explaining why {employee_name} is a great fit for this task.
- Be specific about their skills and availability
- Sound natural and professional
- Do NOT mention percentages or scores
- Do NOT start with the employee name
- Example tone: "With strong Python and API development skills matching all task requirements, this candidate brings 4 years of relevant experience and currently has bandwidth to take on new work."
"""
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception:
            return (
                f"{employee_name} has relevant skills matching this task's requirements "
                f"with a {score_pct}% overall match. Their current workload allows them "
                f"to take on this assignment effectively."
            )
