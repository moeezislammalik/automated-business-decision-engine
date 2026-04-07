import pandas as pd
import time
from typing import List, Dict, Any, Tuple
from app.modules.rules import Rule, get_default_rules


CLASSIFICATION_THRESHOLDS = {
    'High Risk': 40,
    'Medium Risk': 20,
    'Low Risk': 0
}


def get_classification(score: int) -> str:
    """
    Map a score to a classification category based on predefined thresholds.
    
    Thresholds:
        - High Risk: score >= 40
        - Medium Risk: score >= 20
        - Low Risk: score < 20
    """
    if score >= CLASSIFICATION_THRESHOLDS['High Risk']:
        return 'High Risk'
    elif score >= CLASSIFICATION_THRESHOLDS['Medium Risk']:
        return 'Medium Risk'
    else:
        return 'Low Risk'


def generate_explanation(
    record_id: str,
    total_score: int,
    classification: str,
    triggered_rules: List[Dict[str, Any]]
) -> str:
    """
    Generate a human-readable explanation for a record's evaluation.
    
    The explanation includes:
    - List of triggered rules with their weight contributions
    - Total score calculation
    - Classification reasoning
    """
    if not triggered_rules:
        return (
            f"Record {record_id}: No rules were triggered. "
            f"Total score is 0, classified as {classification}."
        )
    
    explanation_parts = [f"Record {record_id} Evaluation:"]
    explanation_parts.append("")
    explanation_parts.append("Triggered Rules:")
    
    for rule in triggered_rules:
        weight_str = f"+{rule['weight']}" if rule['weight'] > 0 else str(rule['weight'])
        explanation_parts.append(
            f"  - {rule['name']}: {rule['description']} "
            f"(Weight: {weight_str})"
        )
    
    explanation_parts.append("")
    weight_sum = " + ".join(
        [str(r['weight']) for r in triggered_rules]
    )
    explanation_parts.append(f"Score Calculation: {weight_sum} = {total_score}")
    explanation_parts.append("")
    
    if classification == 'High Risk':
        threshold_explanation = f"Score {total_score} >= 40 threshold"
    elif classification == 'Medium Risk':
        threshold_explanation = f"Score {total_score} >= 20 threshold (but < 40)"
    else:
        threshold_explanation = f"Score {total_score} < 20 threshold"
    
    explanation_parts.append(f"Classification: {classification} ({threshold_explanation})")
    
    return "\n".join(explanation_parts)


class EvaluationResult:
    """Represents the evaluation result for a single record."""
    
    def __init__(
        self,
        record_id: str,
        total_score: int,
        classification: str,
        triggered_rules: List[Dict[str, Any]],
        explanation: str
    ):
        self.record_id = record_id
        self.total_score = total_score
        self.classification = classification
        self.triggered_rules = triggered_rules
        self.explanation = explanation
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'record_id': self.record_id,
            'total_score': self.total_score,
            'classification': self.classification,
            'triggered_rules': self.triggered_rules,
            'rules_count': len(self.triggered_rules),
            'explanation': self.explanation
        }


class EvaluationMetrics:
    """Performance metrics for an evaluation run."""
    
    def __init__(
        self,
        total_records: int,
        runtime_ms: float,
        records_per_second: float
    ):
        self.total_records = total_records
        self.runtime_ms = runtime_ms
        self.records_per_second = records_per_second
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_records': self.total_records,
            'runtime_ms': round(self.runtime_ms, 2),
            'runtime_formatted': self._format_runtime(),
            'records_per_second': round(self.records_per_second, 1)
        }
    
    def _format_runtime(self) -> str:
        if self.runtime_ms < 1000:
            return f"{self.runtime_ms:.0f} ms"
        else:
            return f"{self.runtime_ms / 1000:.2f} seconds"


class DecisionEngine:
    """
    The core scoring engine that evaluates records against defined rules.
    
    For each record in a dataset, the engine:
    1. Iterates through all defined rules
    2. Evaluates each rule's condition
    3. Accumulates weights from triggered rules
    4. Assigns classification based on thresholds
    5. Generates human-readable explanation
    6. Returns the complete evaluation result
    """
    
    def __init__(self, rules: List[Rule] = None):
        self.rules = rules if rules is not None else get_default_rules()
        self.last_metrics = None
    
    def evaluate_record(self, row: dict) -> EvaluationResult:
        """
        Evaluate a single record against all rules.
        
        Args:
            row: Dictionary representing a single record with column values
            
        Returns:
            EvaluationResult containing score, classification, and explanation
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
        classification = get_classification(total_score)
        explanation = generate_explanation(
            record_id, total_score, classification, triggered_rules
        )
        
        return EvaluationResult(
            record_id, total_score, classification, triggered_rules, explanation
        )
    
    def evaluate_dataset(self, df: pd.DataFrame) -> Tuple[List[EvaluationResult], EvaluationMetrics]:
        """
        Evaluate all records in a dataset with performance tracking.
        
        Args:
            df: Pandas DataFrame containing the dataset
            
        Returns:
            Tuple of (List of EvaluationResult objects, EvaluationMetrics)
        """
        start_time = time.perf_counter()
        
        results = []
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            result = self.evaluate_record(row_dict)
            results.append(result)
        
        end_time = time.perf_counter()
        runtime_ms = (end_time - start_time) * 1000
        total_records = len(results)
        records_per_second = total_records / (runtime_ms / 1000) if runtime_ms > 0 else 0
        
        self.last_metrics = EvaluationMetrics(
            total_records=total_records,
            runtime_ms=runtime_ms,
            records_per_second=records_per_second
        )
        
        return results, self.last_metrics
    
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
    
    @staticmethod
    def get_classification_thresholds() -> Dict[str, int]:
        """Return the classification thresholds."""
        return CLASSIFICATION_THRESHOLDS.copy()
