from app.services.optimization_engine import WorkloadOptimizer

def test_feasible_assignment():
    optimizer = WorkloadOptimizer()
    tasks = [
        {'id': 1, 'required_skills': ['python'], 'estimated_hours': 3.0},
        {'id': 2, 'required_skills': ['react'], 'estimated_hours': 2.0},
        {'id': 3, 'required_skills': ['python', 'sql'], 'estimated_hours': 2.0},
    ]
    employees = [
        {'id': 1, 'skills': ['python', 'sql'], 'current_workload_score': 1.0, 'availability_status': 'available'},
        {'id': 2, 'skills': ['react', 'css'], 'current_workload_score': 0.0, 'availability_status': 'available'},
        {'id': 3, 'skills': ['python', 'react'], 'current_workload_score': 2.0, 'availability_status': 'available'},
    ]
    result = optimizer.optimize(tasks, employees)
    assert result['status'] in ('optimal', 'feasible')
    assert len(result['assignment_map']) == 3
    assert set(result['assignment_map'].keys()) == {1, 2, 3}

def test_overloaded_prevention():
    optimizer = WorkloadOptimizer()
    tasks = [
        {'id': 1, 'required_skills': ['python'], 'estimated_hours': 3.0},
        {'id': 2, 'required_skills': ['python'], 'estimated_hours': 3.0},
    ]
    employees = [
        {'id': 1, 'skills': ['python'], 'current_workload_score': 6.0, 'availability_status': 'available'},
        {'id': 2, 'skills': ['python'], 'current_workload_score': 0.0, 'availability_status': 'available'},
    ]
    result = optimizer.optimize(tasks, employees)
    assert result['status'] in ('optimal', 'feasible')
    emp1_load = result['workload_distribution'].get(1, 0)
    assert emp1_load <= 8.0

def test_unavailable_employee_excluded():
    optimizer = WorkloadOptimizer()
    tasks = [{'id': 1, 'required_skills': ['python'], 'estimated_hours': 2.0}]
    employees = [
        {'id': 1, 'skills': ['python'], 'current_workload_score': 0.0, 'availability_status': 'unavailable'},
        {'id': 2, 'skills': ['python'], 'current_workload_score': 0.0, 'availability_status': 'available'},
    ]
    result = optimizer.optimize(tasks, employees)
    assert result['status'] in ('optimal', 'feasible')
    assert result['assignment_map'][1] == 2

def test_preview_has_before_after():
    optimizer = WorkloadOptimizer()
    tasks = [{'id': 1, 'required_skills': ['python'], 'estimated_hours': 2.0}]
    employees = [
        {'id': 1, 'skills': ['python'], 'current_workload_score': 3.0, 'availability_status': 'available'},
    ]
    result = optimizer.preview(tasks, employees)
    assert 'before_workload' in result
    assert 'after_workload' in result
