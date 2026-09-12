import pytest

@pytest.fixture
def sample_task_data():
    return {
        'required_skills': ['python', 'fastapi', 'sql'],
        'difficulty_score': 'medium',
        'task_type': 'backend'
    }

@pytest.fixture
def sample_employees_data():
    return [
        {
            'id': 1,
            'name': 'Alice Chen',
            'skills': ['python', 'fastapi', 'sql', 'docker'],
            'experience_years': 5,
            'availability_status': 'available',
            'current_workload_score': 2.0,
            'past_task_types': ['backend', 'backend', 'data']
        },
        {
            'id': 2,
            'name': 'Bob Singh',
            'skills': ['react', 'typescript', 'css'],
            'experience_years': 3,
            'availability_status': 'available',
            'current_workload_score': 5.0,
            'past_task_types': ['frontend', 'frontend']
        },
        {
            'id': 3,
            'name': 'Carol Wu',
            'skills': ['python', 'sql', 'aws'],
            'experience_years': 7,
            'availability_status': 'busy',
            'current_workload_score': 7.5,
            'past_task_types': ['backend', 'devops', 'data']
        }
    ]
