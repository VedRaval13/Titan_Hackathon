from app.services.jira_service import JiraClient

def test_clean_jira_task_basic():
    client = JiraClient()
    raw = {
        'key': 'PROJ-123',
        'fields': {
            'summary': 'Implement user authentication',
            'description': {'type': 'doc', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Add JWT-based auth to the API'}]}]},
            'priority': {'name': 'High'},
            'status': {'name': 'To Do'},
            'duedate': '2026-12-31',
            'issuetype': {'name': 'Task'},
            'labels': ['backend', 'security']
        }
    }
    result = client.clean_jira_task(raw)
    assert result['jira_issue_key'] == 'PROJ-123'
    assert result['title'] == 'Implement user authentication'
    assert 'JWT-based auth' in result['description']
    assert result['priority'] == 'high'
    assert result['status'] == 'open'

def test_clean_jira_task_missing_fields():
    client = JiraClient()
    raw = {
        'key': 'PROJ-456',
        'fields': {
            'summary': 'Simple task',
            'description': None,
            'priority': None,
            'status': {'name': 'In Progress'},
            'duedate': None,
            'issuetype': {'name': 'Bug'},
            'labels': []
        }
    }
    result = client.clean_jira_task(raw)
    assert result['jira_issue_key'] == 'PROJ-456'
    assert result['title'] == 'Simple task'
    assert result['description'] == ''
    assert result['priority'] == 'medium'
    assert result['status'] == 'in_progress'

def test_clean_jira_task_done_status():
    client = JiraClient()
    raw = {
        'key': 'PROJ-789',
        'fields': {
            'summary': 'Completed task',
            'description': None,
            'priority': {'name': 'Low'},
            'status': {'name': 'Done'},
            'duedate': None,
            'issuetype': {'name': 'Story'},
            'labels': []
        }
    }
    result = client.clean_jira_task(raw)
    assert result['status'] == 'done'
