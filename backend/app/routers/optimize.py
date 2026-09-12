from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.task import Task
from app.models.employee import Employee
from app.models.assignment import Assignment
from app.models.recommendation import Recommendation
from app.models.run_log import RunLog
from app.services.optimization_engine import WorkloadOptimizer
from app.services.jira_service import JiraClient
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ApplyOptimizationRequest(BaseModel):
    assignment_map: dict[str, int]


async def _gather_optimization_data(db: AsyncSession):
    stmt_tasks = select(Task).where(
        Task.status == "open", Task.assigned_employee_id == None  # noqa: E711
    )
    tasks = (await db.execute(stmt_tasks)).scalars().all()

    stmt_emp = select(Employee)
    employees = (await db.execute(stmt_emp)).scalars().all()

    tasks_data = [
        {
            "id": t.id,
            "required_skills": t.required_skills or [],
            "estimated_hours": (
                t.ai_analysis.get("estimated_hours", 4.0)
                if t.ai_analysis and isinstance(t.ai_analysis, dict)
                else 4.0
            ),
        }
        for t in tasks
    ]
    emp_data = [
        {
            "id": e.id,
            "skills": e.skills or [],
            "current_workload_score": e.current_workload_score,
            "availability_status": e.availability_status,
        }
        for e in employees
    ]

    return tasks_data, emp_data


@router.post("/run")
async def run_optimization(db: AsyncSession = Depends(get_db)):
    tasks_data, emp_data = await _gather_optimization_data(db)

    if not tasks_data:
        return {
            "status": "no_tasks",
            "message": "No open unassigned tasks to optimize.",
            "assignment_map": {},
            "workload_distribution": {},
        }

    optimizer = WorkloadOptimizer()
    result = optimizer.optimize(tasks_data, emp_data)

    log = RunLog(
        run_type="optimization",
        status=result["status"],
        input_data={"tasks_count": len(tasks_data), "employees_count": len(emp_data)},
        output_data=result,
    )
    db.add(log)
    await db.commit()

    return result


@router.get("/preview")
async def preview_optimization(db: AsyncSession = Depends(get_db)):
    tasks_data, emp_data = await _gather_optimization_data(db)

    if not tasks_data:
        return {
            "status": "no_tasks",
            "message": "No open unassigned tasks to optimize.",
            "assignment_map": {},
            "workload_distribution": {},
            "before_workload": {e["id"]: e["current_workload_score"] for e in emp_data},
            "after_workload": {e["id"]: e["current_workload_score"] for e in emp_data},
        }

    optimizer = WorkloadOptimizer()
    return optimizer.preview(tasks_data, emp_data)


@router.post("/apply")
async def apply_optimization(
    req: ApplyOptimizationRequest, db: AsyncSession = Depends(get_db)
):
    count = 0
    jira_sync_tasks = []

    for task_id_str, emp_id in req.assignment_map.items():
        task_id = int(task_id_str)
        stmt_task = select(Task).where(Task.id == task_id)
        task = (await db.execute(stmt_task)).scalars().first()

        stmt_emp = select(Employee).where(Employee.id == emp_id)
        emp = (await db.execute(stmt_emp)).scalars().first()

        if not task or not emp:
            continue

        assignment = Assignment(task_id=task.id, employee_id=emp.id, status="active")
        db.add(assignment)

        task.assigned_employee_id = emp.id
        task.status = "in_progress"

        hours = (
            task.ai_analysis.get("estimated_hours", 4.0)
            if task.ai_analysis and isinstance(task.ai_analysis, dict)
            else 4.0
        )
        emp.current_workload_score += hours

        rec = Recommendation(
            task_id=task.id,
            recommended_employee_id=emp.id,
            match_score=1.0,
            confidence_level="high",
            reason="Assigned via automated workload optimization.",
            manager_action="approved",
        )
        db.add(rec)
        count += 1

        # Collect Jira-linked tasks for sync after commit
        if task.jira_issue_key:
            jira_sync_tasks.append((task.jira_issue_key, emp.email, emp.name))

    log = RunLog(
        run_type="optimization_apply",
        status="success",
        input_data={"applied_count": count},
    )
    db.add(log)
    await db.commit()

    # Sync assignments to Jira
    if jira_sync_tasks:
        jira = JiraClient()
        if jira.is_configured():
            for issue_key, emp_email, emp_name in jira_sync_tasks:
                await jira.update_issue_assignee(issue_key, emp_email, emp_name)
                await jira.update_issue_status(issue_key, "in_progress")

    return {"status": "applied", "assignments_created": count}
