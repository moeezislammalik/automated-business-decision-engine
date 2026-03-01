import pandas as pd
from typing import List, Dict, Any
from app.modules.rules import Rule, get_default_rules


class EvaluationResult:
    """Represents the evaluation result for a single record."""
    
    def __init__(
        self,
        record_id: str,
        total_score: int,
        triggered_rules: List[Dict[str, Any]]
    ):
        self.record_id = record_id
        self.total_score = total_score
        self.triggered_rules = triggered_rules
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'record_id': self.record_id,
            'total_score': self.total_score,
            'triggered_rules': self.triggered_rules,
            'rules_count': len(self.triggered_rules)
        }


class DecisionEngine:
    """
    The core scoring engine that evaluates records against defined rules.
    
    For each record in a dataset, the engine:
    1. Iterates through all defined rules
    2. Evaluates each rule's condition
    3. Accumulates weights from triggered rules
    4. Returns the total score and list of triggered rules
    """
    
    def __init__(self, rules: List[Rule] = None):
        self.rules = rules if rules is not None else get_default_rules()
    
    def evaluate_record(self, row: dict) -> EvaluationResult:
        """
        Evaluate a single record against all rules.
        
        Args:
            row: Dictionary representing a single record with column values
            
        Returns:
            EvaluationResult containing score and triggered rules
        """
        total_score = 0
        triggered_rules = []
        
        for rule in self.rules:
            is_triggered, weight = rule.evaluate(row)
            if is_triggered:
                total_score += weight
                triggered_rules.append({
                    'name': rule.name,
                    'column': rule.column,
                    'weight': weight,
                    'description': rule.description,
                    'threshold': rule.threshold
                })
        
        record_id = str(row.get('Record_ID', 'Unknown'))
        return EvaluationResult(record_id, total_score, triggered_rules)
    
    def evaluate_dataset(self, df: pd.DataFrame) -> List[EvaluationResult]:
        """
        Evaluate all records in a dataset.
        
        Args:
            df: Pandas DataFrame containing the dataset
            
        Returns:
            List of EvaluationResult objects, one per record
        """
        results = []
        
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            result = self.evaluate_record(row_dict)
            results.append(result)
        
        return results
    
    def get_rules_summary(self) -> List[Dict[str, Any]]:
        """Return a summary of all configured rules."""
        return [
            {
                'name': rule.name,
                'column': rule.column,
                'weight': rule.weight,
                'threshold': rule.threshold,
                'description': rule.description
            }
            for rule in self.rules
        ]
