"""Seed script to populate TITANS database with demo data."""
import asyncio
from sqlalchemy import text
from app.database import async_session_maker, engine, Base
from app.models.employee import Employee
from app.models.task import Task
# Import all models so Base.metadata knows about them
from app.models.recommendation import Recommendation
from app.models.assignment import Assignment
from app.models.run_log import RunLog


EMPLOYEES = [
    {
        "name": "Ved Raval",
        "email": "ved@titans.dev",
        "skills": ["python", "fastapi", "react", "sql", "docker"],
        "experience_years": 4,
        "department": "Engineering",
        "availability_status": "available",
        "current_workload_score": 2.0,
    },
    {
        "name": "Het Patel",
        "email": "het@titans.dev",
        "skills": ["react", "typescript", "tailwind", "node", "figma"],
        "experience_years": 3,
        "department": "Engineering",
        "availability_status": "available",
        "current_workload_score": 1.5,
    },
    {
        "name": "Priya Sharma",
        "email": "priya@titans.dev",
        "skills": ["python", "sql", "aws", "docker", "kubernetes"],
        "experience_years": 6,
        "department": "DevOps",
        "availability_status": "available",
        "current_workload_score": 4.0,
    },
    {
        "name": "Arjun Mehta",
        "email": "arjun@titans.dev",
        "skills": ["java", "spring", "sql", "api", "test"],
        "experience_years": 5,
        "department": "Backend",
        "availability_status": "partial",
        "current_workload_score": 6.5,
    },
    {
        "name": "Sneha Desai",
        "email": "sneha@titans.dev",
        "skills": ["react", "css", "html", "javascript", "ui"],
        "experience_years": 2,
        "department": "Frontend",
        "availability_status": "available",
        "current_workload_score": 1.0,
    },
    {
        "name": "Rohan Gupta",
        "email": "rohan@titans.dev",
        "skills": ["python", "database", "sql", "data", "etl"],
        "experience_years": 7,
        "department": "Data",
        "availability_status": "busy",
        "current_workload_score": 7.5,
    },
]

TASKS = [
    {
        "title": "Build User Authentication API",
        "description": "Implement JWT-based authentication with login, register, and token refresh endpoints.",
        "priority": "high",
        "status": "open",
        "task_type": "backend",
        "required_skills": ["python", "fastapi", "sql"],
        "difficulty_score": "medium",
    },
    {
        "title": "Design Dashboard UI Components",
        "description": "Create reusable React components for the analytics dashboard including charts and stat cards.",
        "priority": "medium",
        "status": "open",
        "task_type": "frontend",
        "required_skills": ["react", "css", "javascript"],
        "difficulty_score": "easy",
    },
    {
        "title": "Set Up CI/CD Pipeline",
        "description": "Configure GitHub Actions for automated testing, Docker image building, and deployment to AWS.",
        "priority": "critical",
        "status": "open",
        "task_type": "devops",
        "required_skills": ["docker", "aws", "kubernetes"],
        "difficulty_score": "hard",
    },
    {
        "title": "Optimize Database Queries",
        "description": "Profile and optimize slow SQL queries in the reporting module. Add proper indexes.",
        "priority": "high",
        "status": "open",
        "task_type": "data",
        "required_skills": ["sql", "database", "python"],
        "difficulty_score": "medium",
    },
    {
        "title": "Implement Real-time Notifications",
        "description": "Add WebSocket support for real-time task assignment notifications.",
        "priority": "medium",
        "status": "open",
        "task_type": "backend",
        "required_skills": ["python", "fastapi", "react"],
        "difficulty_score": "hard",
    },
    {
        "title": "Create Employee Onboarding Form",
        "description": "Build a multi-step onboarding form with validation and file uploads.",
        "priority": "low",
        "status": "open",
        "task_type": "frontend",
        "required_skills": ["react", "typescript", "css"],
        "difficulty_score": "easy",
    },
]


async def seed():
    # Drop all tables and recreate fresh
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        for emp_data in EMPLOYEES:
            session.add(Employee(**emp_data))
        for task_data in TASKS:
            session.add(Task(**task_data))
        await session.commit()

    print(f"[OK] Seeded {len(EMPLOYEES)} employees and {len(TASKS)} tasks!")
    print("\nEmployees:")
    for e in EMPLOYEES:
        print(f"  - {e['name']} ({e['department']}) - {', '.join(e['skills'][:3])}")
    print("\nTasks:")
    for t in TASKS:
        print(f"  - [{t['priority'].upper()}] {t['title']}")
    print("\nDone! Start the server: uvicorn app.main:app --reload --port 8000")


if __name__ == "__main__":
    asyncio.run(seed())
