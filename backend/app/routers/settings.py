from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from app.database import get_db
from app.config import settings
from app.models.task import Task
from app.models.employee import Employee
from app.models.recommendation import Recommendation
from app.models.assignment import Assignment
from app.models.run_log import RunLog
from app.services.jira_service import JiraClient
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class JiraSettings(BaseModel):
    jira_base_url: str = ""
    jira_email: str = ""
    jira_api_token: str = ""
    jira_project_key: str = ""


@router.get("/jira")
async def get_jira_settings():
    """Get current Jira configuration (token is masked)."""
    jira = JiraClient()
    result = {
        "jira_base_url": settings.JIRA_BASE_URL,
        "jira_email": settings.JIRA_EMAIL,
        "jira_api_token": "••••••••" if settings.JIRA_API_TOKEN else "",
        "jira_project_key": settings.JIRA_PROJECT_KEY,
        "configured": jira.is_configured(),
        "connected": False,
        "user": None,
    }

    if jira.is_configured():
        try:
            response = await jira.client.get("/rest/api/3/myself")
            if response.status_code == 200:
                user = response.json()
                result["connected"] = True
                result["user"] = user.get("displayName", user.get("emailAddress", "Unknown"))
        except Exception as e:
            result["error"] = str(e)

    return result


@router.post("/jira")
async def save_jira_settings(data: JiraSettings, db: AsyncSession = Depends(get_db)):
    """Save Jira settings to .env file and reload config.
    If the Jira URL or project key changed, wipes ALL data and pulls fresh from new Jira."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")

    # Detect if this is a different Jira setup
    old_url = settings.JIRA_BASE_URL
    old_project = settings.JIRA_PROJECT_KEY
    new_url = data.jira_base_url or old_url
    new_project = data.jira_project_key or old_project
    jira_changed = (
        (new_url and new_url != old_url) or
        (new_project and new_project != old_project)
    )

    # If Jira setup changed, wipe ALL data for a fresh start
    if jira_changed:
        # Delete in correct order (foreign keys)
        await db.execute(text("DELETE FROM assignments"))
        await db.execute(text("DELETE FROM recommendations"))
        await db.execute(text("DELETE FROM run_logs"))
        await db.execute(text("DELETE FROM tasks"))
        await db.execute(text("DELETE FROM employees"))
        await db.commit()
        logger.info("Jira setup changed: wiped all data for fresh start")

    # Read existing .env
    env_lines = {}
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    env_lines[key.strip()] = val.strip()

    # Update Jira fields
    if data.jira_base_url:
        env_lines["JIRA_BASE_URL"] = data.jira_base_url
    if data.jira_email:
        env_lines["JIRA_EMAIL"] = data.jira_email
    if data.jira_api_token and data.jira_api_token != "••••••••":
        env_lines["JIRA_API_TOKEN"] = data.jira_api_token
    if data.jira_project_key:
        env_lines["JIRA_PROJECT_KEY"] = data.jira_project_key

    # Write back
    with open(env_path, "w") as f:
        for key, val in env_lines.items():
            f.write(f"{key}={val}\n")

    # Update in-memory settings
    if data.jira_base_url:
        settings.JIRA_BASE_URL = data.jira_base_url
    if data.jira_email:
        settings.JIRA_EMAIL = data.jira_email
    if data.jira_api_token and data.jira_api_token != "••••••••":
        settings.JIRA_API_TOKEN = data.jira_api_token
    if data.jira_project_key:
        settings.JIRA_PROJECT_KEY = data.jira_project_key

    # Test connection
    jira = JiraClient()
    connected = False
    user = None
    try:
        response = await jira.client.get("/rest/api/3/myself")
        if response.status_code == 200:
            connected = True
            user = response.json().get("displayName", "Unknown")
    except Exception:
        pass

    # If connected and data was wiped, pull fresh data from new Jira
    tasks_imported = 0
    employees_imported = 0
    if jira_changed and connected:
        try:
            # Import all Jira users as employees
            jira_users = await jira.fetch_all_users()
            for jira_user in jira_users:
                new_emp = Employee(
                    name=jira_user["display_name"],
                    email=jira_user["email"] or f"{jira_user['display_name'].lower().replace(' ', '.')}@jira.user",
                    skills=[],
                    department="From Jira",
                    availability_status="available",
                    jira_account_id=jira_user["account_id"],
                )
                db.add(new_emp)
                employees_imported += 1

            await db.flush()

            # Import all Jira tasks
            raw_issues = await jira.fetch_all_open_tasks()
            all_employees = (await db.execute(
                text("SELECT id, name, email, jira_account_id FROM employees")
            )).fetchall()

            for raw in raw_issues:
                cleaned = jira.clean_jira_task(raw)
                assignee_name = cleaned.pop("assignee_name", None)
                assignee_email = cleaned.pop("assignee_email", None)

                new_task = Task(**cleaned)

                # Match assignee
                if assignee_name or assignee_email:
                    for emp in all_employees:
                        if assignee_email and emp.email and emp.email.lower() == assignee_email.lower():
                            new_task.assigned_employee_id = emp.id
                            if new_task.status == "open":
                                new_task.status = "in_progress"
                            break
                        if assignee_name:
                            first = assignee_name.strip().split()[0].lower()
                            emp_first = emp.name.strip().split()[0].lower()
                            if first == emp_first:
                                new_task.assigned_employee_id = emp.id
                                if new_task.status == "open":
                                    new_task.status = "in_progress"
                                break

                db.add(new_task)
                tasks_imported += 1

            await db.commit()
            logger.info(f"Fresh import: {employees_imported} employees, {tasks_imported} tasks from new Jira")
        except Exception as e:
            logger.warning(f"Failed to import from new Jira: {e}")

    response_data = {
        "status": "saved",
        "configured": jira.is_configured(),
        "connected": connected,
        "user": user,
    }

    if jira_changed:
        response_data["data_cleared"] = True
        response_data["tasks_imported"] = tasks_imported
        response_data["employees_imported"] = employees_imported
        response_data["message"] = (
            f"Fresh start! Imported {employees_imported} team members and "
            f"{tasks_imported} tasks from the new Jira server."
        )

    return response_data


@router.post("/jira/test")
async def test_jira_connection():
    """Test the current Jira connection."""
    jira = JiraClient()
    if not jira.is_configured():
        return {"connected": False, "error": "Jira not configured"}

    try:
        response = await jira.client.get("/rest/api/3/myself")
        if response.status_code == 200:
            user = response.json()
            return {
                "connected": True,
                "user": user.get("displayName"),
                "email": user.get("emailAddress"),
            }
        return {"connected": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"connected": False, "error": str(e)}
