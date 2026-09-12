from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.config import settings
from app.models.task import Task
from app.models.employee import Employee
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.schemas.ai_analysis import AIAnalysisResult
from app.services.jira_service import JiraClient
from app.services.ai_service import GeminiAnalyzer
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def _match_employee(employees, jira_name: str = None, jira_email: str = None):
    """Match a Jira assignee to a TITANS employee by email or name."""
    if not employees:
        return None

    # Try exact email match first
    if jira_email:
        for emp in employees:
            if emp.email and emp.email.lower() == jira_email.lower():
                return emp

    # Try name match (first name)
    if jira_name:
        jira_first = jira_name.strip().split()[0].lower() if jira_name.strip() else ""
        if jira_first:
            for emp in employees:
                emp_first = emp.name.strip().split()[0].lower() if emp.name else ""
                if emp_first == jira_first:
                    return emp

    return None


@router.get("/", response_model=list[TaskRead])
async def list_tasks(
    status: str = None,
    priority: str = None,
    task_type: str = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Task)
    if status:
        stmt = stmt.where(Task.status == status)
    if priority:
        stmt = stmt.where(Task.priority == priority)
    if task_type:
        stmt = stmt.where(Task.task_type == task_type)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/", response_model=TaskRead)
async def create_task(task_in: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Create a task in TITANS. If Jira is configured and push_to_jira=true, also creates it in Jira."""
    task_data = task_in.model_dump()
    push_to_jira = task_data.pop("push_to_jira", False)

    task = Task(**task_data)
    db.add(task)
    await db.commit()
    await db.refresh(task)

    # Push to Jira if requested and configured
    if push_to_jira:
        jira = JiraClient()
        if jira.is_configured() and settings.JIRA_PROJECT_KEY:
            try:
                jira_response = await jira.create_issue(
                    project_key=settings.JIRA_PROJECT_KEY,
                    title=task.title,
                    description=task.description or "",
                    priority=task.priority,
                )
                task.jira_issue_key = jira_response.get("key")
                db.add(task)
                await db.commit()
                await db.refresh(task)
                logger.info(f"Pushed task {task.id} to Jira as {task.jira_issue_key}")
            except Exception as e:
                logger.warning(f"Failed to push task to Jira: {e}")

    return task


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(task_id: int, task_in: TaskUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    updated_fields = task_in.model_dump(exclude_unset=True)
    for k, v in updated_fields.items():
        setattr(task, k, v)

    db.add(task)
    await db.commit()
    await db.refresh(task)

    # Sync changes to Jira if this task is linked
    if task.jira_issue_key:
        jira = JiraClient()
        if jira.is_configured():
            # Sync field changes (title, description, priority)
            await jira.update_issue_fields(
                issue_key=task.jira_issue_key,
                title=updated_fields.get("title"),
                description=updated_fields.get("description"),
                priority=updated_fields.get("priority"),
            )
            # Sync status change via transitions
            if "status" in updated_fields:
                await jira.update_issue_status(task.jira_issue_key, updated_fields["status"])

    return task


@router.post("/{task_id}/analyze", response_model=AIAnalysisResult)
async def analyze_task(task_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    ai = GeminiAnalyzer()
    analysis = await ai.analyze_task(task.title, task.description)

    task.ai_analysis = analysis.model_dump()
    task.required_skills = analysis.required_skills
    task.difficulty_score = analysis.difficulty
    task.task_type = analysis.task_type

    db.add(task)
    await db.commit()
    await db.refresh(task)

    return analysis


# ===================== JIRA SYNC ENDPOINTS =====================


@router.post("/jira/sync")
async def sync_from_jira(db: AsyncSession = Depends(get_db)):
    """Pull ALL open issues from Jira into TITANS. Creates new tasks or updates existing ones.
    Also syncs assignees: if a Jira issue has an assignee, matches them to a TITANS employee."""
    jira = JiraClient()
    if not jira.is_configured():
        raise HTTPException(
            status_code=400,
            detail="Jira not configured. Set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN in your .env file.",
        )

    try:
        raw_issues = await jira.fetch_all_open_tasks()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch from Jira: {str(e)}")

    # Load all employees for assignee matching
    all_employees = (await db.execute(select(Employee))).scalars().all()

    created = 0
    updated = 0

    for raw in raw_issues:
        cleaned = jira.clean_jira_task(raw)
        jira_key = cleaned["jira_issue_key"]

        # Extract assignee info (not a Task column, so pop it)
        assignee_name = cleaned.pop("assignee_name", None)
        assignee_email = cleaned.pop("assignee_email", None)

        stmt = select(Task).where(Task.jira_issue_key == jira_key)
        result = await db.execute(stmt)
        existing = result.scalars().first()

        if existing:
            for k, v in cleaned.items():
                if v is not None:
                    setattr(existing, k, v)

            # Match Jira assignee to a TITANS employee
            if assignee_name or assignee_email:
                matched_emp = _match_employee(all_employees, assignee_name, assignee_email)
                if matched_emp:
                    existing.assigned_employee_id = matched_emp.id
                    if existing.status == "open":
                        existing.status = "in_progress"
            else:
                # Jira issue is unassigned
                existing.assigned_employee_id = None

            updated += 1
        else:
            new_task = Task(**cleaned)

            # Match assignee for new task
            if assignee_name or assignee_email:
                matched_emp = _match_employee(all_employees, assignee_name, assignee_email)
                if matched_emp:
                    new_task.assigned_employee_id = matched_emp.id
                    if new_task.status == "open":
                        new_task.status = "in_progress"

            db.add(new_task)
            created += 1

    await db.commit()

    return {
        "status": "synced",
        "total_jira_issues": len(raw_issues),
        "created": created,
        "updated": updated,
    }


@router.post("/jira/import/{issue_key}", response_model=TaskRead)
async def import_single_jira_issue(issue_key: str, db: AsyncSession = Depends(get_db)):
    """Import a single Jira issue by key (e.g., PROJ-123) into TITANS."""
    jira = JiraClient()
    if not jira.is_configured():
        raise HTTPException(status_code=400, detail="Jira not configured.")

    # Check if already imported
    stmt = select(Task).where(Task.jira_issue_key == issue_key)
    result = await db.execute(stmt)
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Issue {issue_key} already imported as Task #{existing.id}")

    try:
        raw = await jira.fetch_task(issue_key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Jira issue not found: {str(e)}")

    cleaned = jira.clean_jira_task(raw)
    task = Task(**cleaned)
    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task


@router.get("/jira/status")
async def jira_status():
    """Check if Jira integration is configured and reachable."""
    jira = JiraClient()
    if not jira.is_configured():
        return {
            "configured": False,
            "message": "Jira not configured. Set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN in .env",
        }

    try:
        response = await jira.client.get("/rest/api/3/myself")
        if response.status_code == 200:
            user = response.json()
            return {
                "configured": True,
                "connected": True,
                "jira_url": settings.JIRA_BASE_URL,
                "user": user.get("displayName", user.get("emailAddress", "Unknown")),
                "project_key": settings.JIRA_PROJECT_KEY or "Not set",
            }
    except Exception as e:
        return {"configured": True, "connected": False, "error": str(e)}

    return {"configured": True, "connected": False, "error": "Unknown error"}


@router.post("/webhook")
async def webhook(payload: dict, db: AsyncSession = Depends(get_db)):
    """Receive Jira webhook events for real-time sync."""
    client = JiraClient()
    cleaned = await client.webhook_handler(payload)
    if cleaned:
        stmt = select(Task).where(Task.jira_issue_key == cleaned["jira_issue_key"])
        result = await db.execute(stmt)
        existing = result.scalars().first()

        if existing:
            for k, v in cleaned.items():
                setattr(existing, k, v)
        else:
            new_task = Task(**cleaned)
            db.add(new_task)

        await db.commit()
        return {"status": "processed", "jira_key": cleaned["jira_issue_key"]}
    return {"status": "ignored"}
