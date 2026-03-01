import pandas as pd
from typing import Tuple, List, Optional

REQUIRED_COLUMNS = ['Record_ID', 'Tenure', 'Late_Payments', 'Revenue']

COLUMN_TYPES = {
    'Record_ID': 'string',
    'Tenure': 'numeric',
    'Late_Payments': 'numeric',
    'Revenue': 'numeric'
}


class ValidationError:
    def __init__(self, error_type: str, message: str, details: Optional[str] = None):
        self.error_type = error_type
        self.message = message
        self.details = details
    
    def to_dict(self) -> dict:
        return {
            'error_type': self.error_type,
            'message': self.message,
            'details': self.details
        }


def validate_csv_file(file_path: str) -> Tuple[bool, Optional[pd.DataFrame], List[ValidationError]]:
    """
    Validate a CSV file for required schema and data types.
    
    Returns:
        Tuple of (is_valid, dataframe_or_none, list_of_errors)
    """
    errors = []
    
    try:
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        errors.append(ValidationError(
            'EMPTY_FILE',
            'The uploaded file is empty.',
            'Please upload a CSV file with data.'
        ))
        return False, None, errors
    except Exception as e:
        errors.append(ValidationError(
            'PARSE_ERROR',
            'Failed to parse CSV file.',
            str(e)
        ))
        return False, None, errors
    
    if df.empty:
        errors.append(ValidationError(
            'EMPTY_DATASET',
            'The CSV file contains no data rows.',
            'Please upload a file with at least one data record.'
        ))
        return False, None, errors
    
    missing_columns = check_required_columns(df)
    if missing_columns:
        errors.append(ValidationError(
            'MISSING_COLUMNS',
            f'Required columns are missing: {", ".join(missing_columns)}',
            f'Required columns: {", ".join(REQUIRED_COLUMNS)}'
        ))
        return False, None, errors
    
    type_errors = validate_column_types(df)
    if type_errors:
        for error in type_errors:
            errors.append(error)
        return False, None, errors
    
    return True, df, errors


def check_required_columns(df: pd.DataFrame) -> List[str]:
    """Check if all required columns are present in the dataframe."""
    missing = []
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            missing.append(col)
    return missing


def validate_column_types(df: pd.DataFrame) -> List[ValidationError]:
    """Validate that columns have correct data types."""
    errors = []
    
    for col, expected_type in COLUMN_TYPES.items():
        if col not in df.columns:
            continue
            
        if expected_type == 'numeric':
            non_numeric = validate_numeric_column(df, col)
            if non_numeric:
                errors.append(ValidationError(
                    'INVALID_TYPE',
                    f'Column "{col}" contains non-numeric values.',
                    f'Invalid values found at rows: {non_numeric[:5]}{"..." if len(non_numeric) > 5 else ""}'
                ))
    
    null_errors = check_null_values(df)
    errors.extend(null_errors)
    
    return errors


def validate_numeric_column(df: pd.DataFrame, column: str) -> List[int]:
    """
    Check if a column contains only numeric values.
    Returns list of row indices with non-numeric values.
    """
    invalid_rows = []
    for idx, value in enumerate(df[column]):
        try:
            if pd.isna(value):
                invalid_rows.append(idx + 1)
            else:
                float(value)
        except (ValueError, TypeError):
            invalid_rows.append(idx + 1)
    return invalid_rows


def check_null_values(df: pd.DataFrame) -> List[ValidationError]:
    """Check for null values in required numeric columns."""
    errors = []
    numeric_cols = [col for col, typ in COLUMN_TYPES.items() if typ == 'numeric']
    
    for col in numeric_cols:
        if col in df.columns:
            null_count = df[col].isna().sum()
            if null_count > 0:
                null_rows = df[df[col].isna()].index.tolist()
                null_rows = [r + 1 for r in null_rows]
                errors.append(ValidationError(
                    'NULL_VALUES',
                    f'Column "{col}" contains {null_count} null value(s).',
                    f'Null values at rows: {null_rows[:5]}{"..." if len(null_rows) > 5 else ""}'
                ))
    
    return errors
