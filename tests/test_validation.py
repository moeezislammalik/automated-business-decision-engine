import pytest
import pandas as pd
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modules.validation import (
    validate_csv_file,
    check_required_columns,
    validate_column_types,
    REQUIRED_COLUMNS
)


def create_temp_csv(content: str) -> str:
    """Helper to create a temporary CSV file for testing."""
    fd, path = tempfile.mkstemp(suffix='.csv')
    with os.fdopen(fd, 'w') as f:
        f.write(content)
    return path


class TestValidation:
    """Tests for the validation module."""
    
    def test_valid_csv_passes_validation(self):
        csv_content = """Record_ID,Tenure,Late_Payments,Revenue
R001,24,0,5000
R002,12,2,3000
R003,6,5,1500"""
        path = create_temp_csv(csv_content)
        
        try:
            is_valid, df, errors = validate_csv_file(path)
            assert is_valid is True
            assert df is not None
            assert len(errors) == 0
            assert len(df) == 3
        finally:
            os.remove(path)
    
    def test_missing_required_column_fails(self):
        csv_content = """Record_ID,Tenure,Late_Payments
R001,24,0
R002,12,2"""
        path = create_temp_csv(csv_content)
        
        try:
            is_valid, df, errors = validate_csv_file(path)
            assert is_valid is False
            assert df is None
            assert len(errors) > 0
            assert any('Revenue' in e.message for e in errors)
        finally:
            os.remove(path)
    
    def test_empty_file_fails(self):
        path = create_temp_csv("")
        
        try:
            is_valid, df, errors = validate_csv_file(path)
            assert is_valid is False
            assert df is None
            assert len(errors) > 0
        finally:
            os.remove(path)
    
    def test_non_numeric_value_fails(self):
        csv_content = """Record_ID,Tenure,Late_Payments,Revenue
R001,twenty-four,0,5000
R002,12,2,3000"""
        path = create_temp_csv(csv_content)
        
        try:
            is_valid, df, errors = validate_csv_file(path)
            assert is_valid is False
            assert len(errors) > 0
        finally:
            os.remove(path)
    
    def test_check_required_columns_all_present(self):
        df = pd.DataFrame({
            'Record_ID': ['R001'],
            'Tenure': [12],
            'Late_Payments': [0],
            'Revenue': [1000]
        })
        missing = check_required_columns(df)
        assert len(missing) == 0
    
    def test_check_required_columns_missing(self):
        df = pd.DataFrame({
            'Record_ID': ['R001'],
            'Tenure': [12]
        })
        missing = check_required_columns(df)
        assert 'Late_Payments' in missing
        assert 'Revenue' in missing
