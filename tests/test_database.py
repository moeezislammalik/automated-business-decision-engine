import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modules import database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    original_path = database.DATABASE_PATH
    database.DATABASE_PATH = path
    
    database.init_database()
    
    yield path
    
    database.DATABASE_PATH = original_path
    os.remove(path)


class TestDatabaseInitialization:
    """Tests for database initialization."""
    
    def test_init_creates_tables(self, temp_db):
        """Test that init_database creates required tables."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='evaluation_runs'"
            )
            assert cursor.fetchone() is not None
            
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='results'"
            )
            assert cursor.fetchone() is not None


class TestSaveEvaluationRun:
    """Tests for saving evaluation runs."""
    
    def test_save_single_result(self, temp_db):
        """Test saving a single evaluation result."""
        results = [{
            'record_id': 'R001',
            'total_score': 25,
            'classification': 'Medium Risk',
            'explanation': 'Test explanation'
        }]
        
        run_id = database.save_evaluation_run('test.csv', results)
        
        assert run_id is not None
        assert run_id > 0
    
    def test_save_multiple_results(self, temp_db):
        """Test saving multiple evaluation results."""
        results = [
            {'record_id': 'R001', 'total_score': 10, 'classification': 'Low Risk', 'explanation': 'Exp1'},
            {'record_id': 'R002', 'total_score': 30, 'classification': 'Medium Risk', 'explanation': 'Exp2'},
            {'record_id': 'R003', 'total_score': 50, 'classification': 'High Risk', 'explanation': 'Exp3'}
        ]
        
        run_id = database.save_evaluation_run('multi.csv', results)
        
        run_data = database.get_run_results(run_id)
        assert run_data is not None
        assert len(run_data['results']) == 3


class TestGetEvaluationRuns:
    """Tests for retrieving evaluation runs."""
    
    def test_get_runs_empty(self, temp_db):
        """Test getting runs when database is empty."""
        runs = database.get_evaluation_runs()
        assert runs == []
    
    def test_get_runs_after_save(self, temp_db):
        """Test getting runs after saving."""
        results = [{'record_id': 'R001', 'total_score': 25, 'classification': 'Medium Risk', 'explanation': 'Test'}]
        database.save_evaluation_run('test.csv', results)
        
        runs = database.get_evaluation_runs()
        
        assert len(runs) == 1
        assert runs[0]['filename'] == 'test.csv'
        assert runs[0]['total_records'] == 1


class TestGetRunResults:
    """Tests for retrieving specific run results."""
    
    def test_get_nonexistent_run(self, temp_db):
        """Test getting a run that doesn't exist."""
        result = database.get_run_results(999)
        assert result is None
    
    def test_get_existing_run(self, temp_db):
        """Test getting an existing run."""
        results = [
            {'record_id': 'R001', 'total_score': 45, 'classification': 'High Risk', 'explanation': 'Exp1'}
        ]
        run_id = database.save_evaluation_run('test.csv', results)
        
        run_data = database.get_run_results(run_id)
        
        assert run_data is not None
        assert run_data['filename'] == 'test.csv'
        assert run_data['total_records'] == 1
        assert run_data['results'][0]['record_id'] == 'R001'
        assert run_data['results'][0]['classification'] == 'High Risk'


class TestClassificationSummary:
    """Tests for classification summary."""
    
    def test_summary_counts(self, temp_db):
        """Test classification summary counts."""
        results = [
            {'record_id': 'R001', 'total_score': 10, 'classification': 'Low Risk', 'explanation': 'E1'},
            {'record_id': 'R002', 'total_score': 15, 'classification': 'Low Risk', 'explanation': 'E2'},
            {'record_id': 'R003', 'total_score': 30, 'classification': 'Medium Risk', 'explanation': 'E3'},
            {'record_id': 'R004', 'total_score': 50, 'classification': 'High Risk', 'explanation': 'E4'}
        ]
        run_id = database.save_evaluation_run('test.csv', results)
        
        summary = database.get_classification_summary(run_id)
        
        assert summary['Low Risk'] == 2
        assert summary['Medium Risk'] == 1
        assert summary['High Risk'] == 1
