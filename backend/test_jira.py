"""Test Jira assignee sync end-to-end."""
import asyncio
from app.services.jira_service import JiraClient
from app.config import settings

async def test():
    jira = JiraClient()

    # Step 1: Find Jira users
    print("--- Searching Jira users ---")
    response = await jira.client.get("/rest/api/3/user/search", params={"query": "", "maxResults": 10})
    users = response.json()
    for u in users:
        print(f"  - {u.get('displayName')} | email: {u.get('emailAddress', 'hidden')} | accountId: {u['accountId']}")

    # Step 2: Try assigning MP-1 to the first user
    if users:
        account_id = users[0]["accountId"]
        print(f"\n--- Assigning MP-1 to {users[0].get('displayName')} ---")
        r = await jira.client.put("/rest/api/3/issue/MP-1/assignee", json={"accountId": account_id})
        print(f"Result: {r.status_code}")
        if r.status_code == 204:
            print("SUCCESS! Check MP-1 in Jira - it should show the assignee now.")
        else:
            print(f"Error: {r.text}")

asyncio.run(test())
