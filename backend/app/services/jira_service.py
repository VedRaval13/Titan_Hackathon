import base64
import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)


def _extract_adf_text(node: dict) -> str:
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(_extract_adf_text(n) for n in node)
    if isinstance(node, dict):
        if node.get("type") == "text":
            return node.get("text", "")
        return _extract_adf_text(node.get("content", []))
    return ""


def _text_to_adf(text: str) -> dict:
    """Convert plain text to Atlassian Document Format (ADF) for Jira API v3."""
    return {
        "version": 1,
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": text}],
            }
        ],
    }


class JiraClient:
    def __init__(self):
        self.base_url = settings.JIRA_BASE_URL
        self.email = settings.JIRA_EMAIL
        self.api_token = settings.JIRA_API_TOKEN
        self.configured = bool(self.base_url and self.email and self.api_token)

        if self.configured:
            auth_str = f"{self.email}:{self.api_token}"
            auth_b64 = base64.b64encode(auth_str.encode()).decode()
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Basic {auth_b64}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        else:
            self.client = None

    def is_configured(self) -> bool:
        return self.configured

    async def fetch_task(self, issue_key: str) -> dict:
        if not self.configured:
            raise RuntimeError("Jira not configured. Set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN in .env")
        response = await self.client.get(f"/rest/api/3/issue/{issue_key}")
        response.raise_for_status()
        return response.json()

    async def fetch_all_users(self) -> list[dict]:
        """Fetch all human users from Jira (filters out bots/apps)."""
        if not self.configured:
            raise RuntimeError("Jira not configured.")
        response = await self.client.get(
            "/rest/api/3/user/search",
            params={"query": "", "maxResults": 100},
        )
        response.raise_for_status()
        users = response.json()
        # Filter to only human accounts
        result = []
        for u in users:
            if u.get("accountType") == "atlassian" and u.get("active", True):
                result.append({
                    "account_id": u.get("accountId", ""),
                    "display_name": u.get("displayName", ""),
                    "email": u.get("emailAddress", ""),
                    "avatar_url": u.get("avatarUrls", {}).get("48x48", ""),
                })
        return result

    async def fetch_all_open_tasks(self) -> list[dict]:
        if not self.configured:
            raise RuntimeError("Jira not configured. Set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN in .env")
        jql = "status != Done ORDER BY created DESC"
        fields = "summary,description,priority,status,issuetype,created,updated,duedate,assignee,labels"
        all_issues = []
        start_at = 0
        max_results = 50

        while True:
            response = await self.client.get(
                "/rest/api/3/search/jql",
                params={"jql": jql, "fields": fields, "startAt": start_at, "maxResults": max_results},
            )
            response.raise_for_status()

            data = response.json()
            issues = data.get("issues", [])
            all_issues.extend(issues)
            total = data.get("total", len(issues))
            if start_at + len(issues) >= total or len(issues) == 0:
                break
            start_at += len(issues)

        return all_issues

    async def create_issue(self, project_key: str, title: str, description: str = "",
                           priority: str = "Medium", issue_type: str = "Task") -> dict:
        """Create a new issue in Jira and return the response with key."""
        if not self.configured:
            raise RuntimeError("Jira not configured. Set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN in .env")

        priority_map = {
            "low": "Low",
            "medium": "Medium",
            "high": "High",
            "critical": "Highest",
        }

        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": title,
                "description": _text_to_adf(description or ""),
                "issuetype": {"name": issue_type},
                "priority": {"name": priority_map.get(priority.lower(), "Medium")},
            }
        }

        response = await self.client.post("/rest/api/3/issue", json=payload)
        response.raise_for_status()
        return response.json()

    async def update_issue_status(self, issue_key: str, status: str) -> bool:
        """Transition a Jira issue to a new status."""
        if not self.configured:
            return False

        try:
            # Get available transitions
            response = await self.client.get(f"/rest/api/3/issue/{issue_key}/transitions")
            response.raise_for_status()
            transitions = response.json().get("transitions", [])

            status_map = {
                "open": "To Do",
                "in_progress": "In Progress",
                "done": "Done",
                "cancelled": "Done",
            }
            target_name = status_map.get(status, status)

            for t in transitions:
                if t["name"].lower() == target_name.lower():
                    await self.client.post(
                        f"/rest/api/3/issue/{issue_key}/transitions",
                        json={"transition": {"id": t["id"]}},
                    )
                    return True
        except Exception as e:
            logger.warning(f"Failed to update Jira status for {issue_key}: {e}")
        return False

    async def update_issue_fields(self, issue_key: str, title: str = None,
                                   description: str = None, priority: str = None) -> bool:
        """Update fields (summary, description, priority) on a Jira issue."""
        if not self.configured:
            return False

        priority_map = {
            "low": "Low", "medium": "Medium", "high": "High", "critical": "Highest",
        }

        fields = {}
        if title is not None:
            fields["summary"] = title
        if description is not None:
            fields["description"] = _text_to_adf(description)
        if priority is not None:
            fields["priority"] = {"name": priority_map.get(priority.lower(), "Medium")}

        if not fields:
            return True

        try:
            response = await self.client.put(
                f"/rest/api/3/issue/{issue_key}",
                json={"fields": fields},
            )
            response.raise_for_status()
            logger.info(f"Updated Jira issue {issue_key} fields: {list(fields.keys())}")
            return True
        except Exception as e:
            logger.warning(f"Failed to update Jira fields for {issue_key}: {e}")
            return False

    async def update_issue_assignee(self, issue_key: str, employee_email: str,
                                     employee_name: str = "") -> bool:
        """Assign a Jira issue to a user by searching their email or name."""
        if not self.configured:
            return False

        try:
            # Search by email first
            response = await self.client.get(
                "/rest/api/3/user/search",
                params={"query": employee_email, "maxResults": 5},
            )
            response.raise_for_status()
            users = response.json()

            # If no match by email, try searching by name
            if not users and employee_name:
                # Try first name (e.g. "Ved Raval" -> "Ved")
                first_name = employee_name.split()[0] if employee_name else ""
                if first_name:
                    response = await self.client.get(
                        "/rest/api/3/user/search",
                        params={"query": first_name, "maxResults": 5},
                    )
                    response.raise_for_status()
                    users = response.json()
                    # Filter out non-human accounts (bots, apps)
                    users = [u for u in users if u.get("accountType") == "atlassian"]

            if not users:
                logger.warning(f"No Jira user found for {employee_name} ({employee_email})")
                return False

            account_id = users[0].get("accountId")
            if not account_id:
                return False

            # Assign the issue
            response = await self.client.put(
                f"/rest/api/3/issue/{issue_key}/assignee",
                json={"accountId": account_id},
            )
            response.raise_for_status()
            logger.info(f"Assigned {issue_key} to {users[0].get('displayName', employee_name)}")
            return True
        except Exception as e:
            logger.warning(f"Failed to assign {issue_key} to {employee_name}: {e}")
            return False

    async def fetch_task_comments(self, issue_key: str) -> list:
        if not self.configured:
            return []
        response = await self.client.get(f"/rest/api/3/issue/{issue_key}/comment")
        response.raise_for_status()
        data = response.json()
        comments = []
        for c in data.get("comments", []):
            comments.append(_extract_adf_text(c.get("body", {})))
        return comments

    def clean_jira_task(self, raw: dict) -> dict:
        jira_issue_key = raw.get("key", "")
        fields = raw.get("fields", {})
        title = fields.get("summary", "")

        description_raw = fields.get("description")
        if description_raw is None:
            description = ""
        elif isinstance(description_raw, dict):
            description = _extract_adf_text(description_raw)
        else:
            description = str(description_raw)

        priority_node = fields.get("priority", {})
        priority = priority_node.get("name", "medium").lower() if priority_node else "medium"
        # Normalize Jira priority names
        priority_normalize = {"lowest": "low", "low": "low", "medium": "medium", "high": "high", "highest": "critical"}
        priority = priority_normalize.get(priority, "medium")

        deadline = fields.get("duedate")

        status_raw = fields.get("status", {}).get("name", "To Do")
        status_map = {"To Do": "open", "In Progress": "in_progress", "Done": "done"}
        status = status_map.get(status_raw, "open")

        labels = fields.get("labels", [])
        task_type = None
        type_keywords = {"backend", "frontend", "devops", "qa", "design", "data"}
        for label in labels:
            if label.lower() in type_keywords:
                task_type = label.lower()
                break

        # Extract assignee info
        assignee_raw = fields.get("assignee")
        assignee_name = None
        assignee_email = None
        if assignee_raw:
            assignee_name = assignee_raw.get("displayName", "")
            assignee_email = assignee_raw.get("emailAddress", "")

        return {
            "jira_issue_key": jira_issue_key,
            "title": title,
            "description": description,
            "priority": priority,
            "deadline": deadline,
            "status": status,
            "task_type": task_type,
            "assignee_name": assignee_name,
            "assignee_email": assignee_email,
        }

    async def webhook_handler(self, payload: dict) -> dict | None:
        event = payload.get("webhookEvent")
        if event in ["jira:issue_created", "jira:issue_updated"]:
            issue_data = payload.get("issue")
            if issue_data:
                return self.clean_jira_task(issue_data)
        return None
