from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.task import Task
from app.models.employee import Employee
from app.models.recommendation import Recommendation
from app.models.assignment import Assignment
from app.models.run_log import RunLog
from app.schemas.recommendation import RecommendationRead, ManagerOverride
from app.services.recommendation_engine import RecommendationEngine
from app.services.ai_service import GeminiAnalyzer
from app.services.jira_service import JiraClient
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate/{task_id}", response_model=list[RecommendationRead])
async def generate_recommendations(task_id: int, db: AsyncSession = Depends(get_db)):
    stmt_task = select(Task).where(Task.id == task_id)
    res_task = await db.execute(stmt_task)
    task = res_task.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    stmt_emp = select(Employee).where(Employee.availability_status != "unavailable")
    res_emp = await db.execute(stmt_emp)
    employees = res_emp.scalars().all()

    if not employees:
        raise HTTPException(status_code=400, detail="No available employees found")

    task_data = {
        "id": task.id,
        "required_skills": task.required_skills or [],
        "difficulty_score": task.difficulty_score or "medium",
        "task_type": task.task_type,
    }

    employees_data = []
    for emp in employees:
        past_types = []
        stmt_past = (
            select(Task.task_type)
            .join(Assignment, Assignment.task_id == Task.id)
            .where(Assignment.employee_id == emp.id)
        )
        res_past = await db.execute(stmt_past)
        for pt in res_past.scalars().all():
            if pt:
                past_types.append(pt)

        employees_data.append(
            {
                "id": emp.id,
                "name": emp.name,
                "skills": emp.skills or [],
                "experience_years": emp.experience_years,
                "availability_status": emp.availability_status,
                "current_workload_score": emp.current_workload_score,
                "past_task_types": past_types,
            }
        )

    engine = RecommendationEngine()
    matches = engine.rank_employees(task_data, employees_data)[:3]

    ai = GeminiAnalyzer()
    recommendations = []

    for match in matches:
        try:
            reason = await ai.generate_recommendation_reason(
                task.title,
                match.employee_name,
                next(
                    (
                        e["skills"]
                        for e in employees_data
                        if e["id"] == match.employee_id
                    ),
                    [],
                ),
                match.total_score,
                match.breakdown.model_dump(),
            )
        except Exception:
            reason = (
                f"{match.employee_name} is recommended with a match score of "
                f"{match.total_score:.0%}. Skill match: {match.breakdown.skill_match:.0%}, "
                f"experience fit: {match.breakdown.experience:.0%}, "
                f"availability: {match.breakdown.availability:.0%}."
            )

        rec = Recommendation(
            task_id=task.id,
            recommended_employee_id=match.employee_id,
            match_score=match.total_score,
            confidence_level=match.confidence,
            reason=reason,
            manager_action="pending",
        )
        db.add(rec)
        recommendations.append(rec)

    log = RunLog(
        run_type="recommendation",
        status="success",
        input_data={"task_id": task.id, "candidates": len(employees_data)},
        output_data={"matches": len(matches)},
    )
    db.add(log)
    await db.commit()

    for r in recommendations:
        await db.refresh(r)

    result = []
    for r in recommendations:
        emp_stmt = select(Employee.name).where(Employee.id == r.recommended_employee_id)
        emp_name = (await db.execute(emp_stmt)).scalar_one_or_none()
        read = RecommendationRead(
            id=r.id,
            task_id=r.task_id,
            recommended_employee_id=r.recommended_employee_id,
            employee_name=emp_name,
            match_score=r.match_score,
            reason=r.reason,
            confidence_level=r.confidence_level,
            manager_action=r.manager_action,
            created_at=r.created_at,
        )
        result.append(read)

    return result


@router.get("/{task_id}", response_model=list[RecommendationRead])
async def get_recommendations(task_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Recommendation).where(Recommendation.task_id == task_id)
    res = await db.execute(stmt)
    recs = res.scalars().all()

    result = []
    for r in recs:
        emp_stmt = select(Employee.name).where(Employee.id == r.recommended_employee_id)
        emp_name = (await db.execute(emp_stmt)).scalar_one_or_none()
        result.append(
            RecommendationRead(
                id=r.id,
                task_id=r.task_id,
                recommended_employee_id=r.recommended_employee_id,
                employee_name=emp_name,
                match_score=r.match_score,
                reason=r.reason,
                confidence_level=r.confidence_level,
                manager_action=r.manager_action,
                created_at=r.created_at,
            )
        )
    return result


@router.post("/{recommendation_id}/approve", response_model=RecommendationRead)
async def approve_recommendation(
    recommendation_id: int, db: AsyncSession = Depends(get_db)
):
    stmt = select(Recommendation).where(Recommendation.id == recommendation_id)
    res = await db.execute(stmt)
    rec = res.scalars().first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.manager_action = "approved"

    stmt_task = select(Task).where(Task.id == rec.task_id)
    task = (await db.execute(stmt_task)).scalars().first()

    stmt_emp = select(Employee).where(Employee.id == rec.recommended_employee_id)
    emp = (await db.execute(stmt_emp)).scalars().first()

    if not task or not emp:
        raise HTTPException(status_code=404, detail="Task or employee not found")

    assignment = Assignment(task_id=task.id, employee_id=emp.id, status="active")
    db.add(assignment)

    task.assigned_employee_id = emp.id
    task.status = "in_progress"

    hours = 2.0
    if task.ai_analysis and isinstance(task.ai_analysis, dict):
        hours = task.ai_analysis.get("estimated_hours", 2.0)
    emp.current_workload_score += hours

    past_ids = list(emp.past_task_ids or [])
    past_ids.append(task.id)
    emp.past_task_ids = past_ids

    db.add(rec)
    db.add(task)
    db.add(emp)
    await db.commit()
    await db.refresh(rec)

    # Sync assignment to Jira
    if task.jira_issue_key:
        jira = JiraClient()
        if jira.is_configured():
            await jira.update_issue_assignee(task.jira_issue_key, emp.email, emp.name)
            await jira.update_issue_status(task.jira_issue_key, "in_progress")

    emp_name_result = (
        await db.execute(
            select(Employee.name).where(Employee.id == rec.recommended_employee_id)
        )
    ).scalar_one_or_none()

    return RecommendationRead(
        id=rec.id,
        task_id=rec.task_id,
        recommended_employee_id=rec.recommended_employee_id,
        employee_name=emp_name_result,
        match_score=rec.match_score,
        reason=rec.reason,
        confidence_level=rec.confidence_level,
        manager_action=rec.manager_action,
        created_at=rec.created_at,
    )


@router.post("/{recommendation_id}/override", response_model=RecommendationRead)
async def override_recommendation(
    recommendation_id: int,
    override: ManagerOverride,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Recommendation).where(Recommendation.id == recommendation_id)
    res = await db.execute(stmt)
    rec = res.scalars().first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.manager_action = "overridden"

    new_rec = Recommendation(
        task_id=rec.task_id,
        recommended_employee_id=override.employee_id,
        match_score=0.0,
        confidence_level="manual",
        reason=override.reason,
        manager_action="approved",
    )
    db.add(new_rec)
    await db.flush()

    stmt_task = select(Task).where(Task.id == rec.task_id)
    task = (await db.execute(stmt_task)).scalars().first()

    stmt_emp = select(Employee).where(Employee.id == override.employee_id)
    emp = (await db.execute(stmt_emp)).scalars().first()

    if not task or not emp:
        raise HTTPException(status_code=404, detail="Task or employee not found")

    assignment = Assignment(task_id=task.id, employee_id=emp.id, status="active")
    db.add(assignment)

    task.assigned_employee_id = emp.id
    task.status = "in_progress"

    hours = 2.0
    if task.ai_analysis and isinstance(task.ai_analysis, dict):
        hours = task.ai_analysis.get("estimated_hours", 2.0)
    emp.current_workload_score += hours

    past_ids = list(emp.past_task_ids or [])
    past_ids.append(task.id)
    emp.past_task_ids = past_ids

    db.add(task)
    db.add(emp)
    await db.commit()
    await db.refresh(new_rec)

    # Sync assignment to Jira
    if task.jira_issue_key:
        jira = JiraClient()
        if jira.is_configured():
            await jira.update_issue_assignee(task.jira_issue_key, emp.email, emp.name)
            await jira.update_issue_status(task.jira_issue_key, "in_progress")

    return RecommendationRead(
        id=new_rec.id,
        task_id=new_rec.task_id,
        recommended_employee_id=new_rec.recommended_employee_id,
        employee_name=emp.name,
        match_score=new_rec.match_score,
        reason=new_rec.reason,
        confidence_level=new_rec.confidence_level,
        manager_action=new_rec.manager_action,
        created_at=new_rec.created_at,
    )
