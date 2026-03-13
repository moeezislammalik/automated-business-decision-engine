import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager


DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'decision_engine.db'
)


def get_db_path() -> str:
    """Return the database file path."""
    return DATABASE_PATH


@contextmanager
def get_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize the database with required tables."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluation_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                total_records INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                record_id TEXT NOT NULL,
                score INTEGER NOT NULL,
                classification TEXT NOT NULL,
                explanation TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (run_id) REFERENCES evaluation_runs (id)
            )
        ''')
        
        conn.commit()


def save_evaluation_run(filename: str, results: List[Dict[str, Any]]) -> int:
    """
    Save a complete evaluation run to the database.
    
    Args:
        filename: Name of the uploaded CSV file
        results: List of evaluation result dictionaries
        
    Returns:
        The run_id of the saved evaluation run
    """
    init_database()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO evaluation_runs (filename, total_records) VALUES (?, ?)',
            (filename, len(results))
        )
        run_id = cursor.lastrowid
        
        for result in results:
            cursor.execute(
                '''INSERT INTO results 
                   (run_id, record_id, score, classification, explanation) 
                   VALUES (?, ?, ?, ?, ?)''',
                (
                    run_id,
                    result['record_id'],
                    result['total_score'],
                    result['classification'],
                    result['explanation']
                )
            )
        
        conn.commit()
        return run_id


def get_evaluation_runs() -> List[Dict[str, Any]]:
    """
    Retrieve all evaluation runs from the database.
    
    Returns:
        List of evaluation run dictionaries with id, filename, total_records, timestamp
    """
    init_database()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT id, filename, total_records, timestamp 
               FROM evaluation_runs 
               ORDER BY timestamp DESC'''
        )
        rows = cursor.fetchall()
        
        return [
            {
                'id': row['id'],
                'filename': row['filename'],
                'total_records': row['total_records'],
                'timestamp': row['timestamp']
            }
            for row in rows
        ]


def get_run_results(run_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve results for a specific evaluation run.
    
    Args:
        run_id: The ID of the evaluation run
        
    Returns:
        Dictionary containing run info and results, or None if not found
    """
    init_database()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, filename, total_records, timestamp FROM evaluation_runs WHERE id = ?',
            (run_id,)
        )
        run_row = cursor.fetchone()
        
        if not run_row:
            return None
        
        cursor.execute(
            '''SELECT record_id, score, classification, explanation, timestamp
               FROM results 
               WHERE run_id = ?
               ORDER BY id''',
            (run_id,)
        )
        result_rows = cursor.fetchall()
        
        return {
            'run_id': run_row['id'],
            'filename': run_row['filename'],
            'total_records': run_row['total_records'],
            'run_timestamp': run_row['timestamp'],
            'results': [
                {
                    'record_id': row['record_id'],
                    'score': row['score'],
                    'classification': row['classification'],
                    'explanation': row['explanation'],
                    'timestamp': row['timestamp']
                }
                for row in result_rows
            ]
        }


def get_classification_summary(run_id: int) -> Dict[str, int]:
    """
    Get classification counts for a specific run.
    
    Args:
        run_id: The ID of the evaluation run
        
    Returns:
        Dictionary with classification counts
    """
    init_database()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT classification, COUNT(*) as count 
               FROM results 
               WHERE run_id = ?
               GROUP BY classification''',
            (run_id,)
        )
        rows = cursor.fetchall()
        
        summary = {'High Risk': 0, 'Medium Risk': 0, 'Low Risk': 0}
        for row in rows:
            summary[row['classification']] = row['count']
        
        return summary


def delete_run(run_id: int) -> bool:
    """
    Delete an evaluation run and its results.
    
    Args:
        run_id: The ID of the evaluation run to delete
        
    Returns:
        True if deleted, False if not found
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM evaluation_runs WHERE id = ?', (run_id,))
        if not cursor.fetchone():
            return False
        
        cursor.execute('DELETE FROM results WHERE run_id = ?', (run_id,))
        cursor.execute('DELETE FROM evaluation_runs WHERE id = ?', (run_id,))
        conn.commit()
        
        return True
