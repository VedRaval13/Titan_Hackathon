from app.services.recommendation_engine import RecommendationEngine

def test_skill_match_perfect():
    engine = RecommendationEngine()
    score = engine.skill_match_score(['python', 'sql'], ['python', 'sql'])
    assert score == 1.0

def test_skill_match_partial():
    engine = RecommendationEngine()
    score = engine.skill_match_score(['python', 'sql', 'docker'], ['python', 'sql'])
    assert 0.6 < score < 0.7

def test_skill_match_none():
    engine = RecommendationEngine()
    score = engine.skill_match_score(['python', 'sql'], ['react', 'css'])
    assert score == 0.0

def test_skill_match_case_insensitive():
    engine = RecommendationEngine()
    score = engine.skill_match_score(['Python', 'SQL'], ['python', 'sql'])
    assert score == 1.0

def test_experience_score_easy():
    engine = RecommendationEngine()
    assert engine.experience_score(1, 'easy') == 1.0
    assert engine.experience_score(6, 'easy') == 0.8

def test_experience_score_hard():
    engine = RecommendationEngine()
    assert engine.experience_score(1, 'hard') == 0.2
    assert engine.experience_score(6, 'hard') == 1.0

def test_workload_penalty():
    engine = RecommendationEngine()
    low = engine.workload_score(2.0)
    high = engine.workload_score(8.0)
    assert low > high

def test_availability_unavailable():
    engine = RecommendationEngine()
    score = engine.availability_score('unavailable', 0.0)
    assert score == 0.0

def test_rank_order(sample_task_data, sample_employees_data):
    engine = RecommendationEngine()
    results = engine.rank_employees(sample_task_data, sample_employees_data)
    assert len(results) == 3
    assert results[0].total_score >= results[1].total_score >= results[2].total_score
    assert results[0].employee_name == 'Alice Chen'
    assert results[0].rank == 1
    assert results[1].rank == 2

def test_compute_match_score_breakdown(sample_task_data):
    engine = RecommendationEngine()
    emp = {'id': 1, 'name': 'Test', 'skills': ['python', 'fastapi'], 'experience_years': 4, 'availability_status': 'available', 'current_workload_score': 3.0, 'past_task_types': ['backend']}
    result = engine.compute_match_score(sample_task_data, emp)
    assert 0.0 <= result.total_score <= 1.0
    assert result.breakdown.skill_match >= 0.0
    assert result.breakdown.experience >= 0.0
