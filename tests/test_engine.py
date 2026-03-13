import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modules.engine import DecisionEngine, EvaluationResult, get_classification
from app.modules.rules import Rule, less_than, greater_than


class TestEvaluationResult:
    """Tests for the EvaluationResult class."""
    
    def test_result_creation(self):
        result = EvaluationResult(
            record_id="R001",
            total_score=25,
            classification="Medium Risk",
            triggered_rules=[{"name": "Test", "weight": 25}],
            explanation="Test explanation"
        )
        assert result.record_id == "R001"
        assert result.total_score == 25
        assert result.classification == "Medium Risk"
        assert len(result.triggered_rules) == 1
    
    def test_result_to_dict(self):
        result = EvaluationResult(
            record_id="R001",
            total_score=25,
            classification="Medium Risk",
            triggered_rules=[{"name": "Test", "weight": 25}],
            explanation="Test explanation"
        )
        d = result.to_dict()
        assert d['record_id'] == "R001"
        assert d['total_score'] == 25
        assert d['classification'] == "Medium Risk"
        assert d['rules_count'] == 1
        assert d['explanation'] == "Test explanation"


class TestDecisionEngine:
    """Tests for the DecisionEngine class."""
    
    def test_engine_with_default_rules(self):
        engine = DecisionEngine()
        assert len(engine.rules) >= 5
    
    def test_engine_with_custom_rules(self):
        custom_rules = [
            Rule("Test1", "Tenure", less_than, 10, 5),
            Rule("Test2", "Revenue", greater_than, 100, 10)
        ]
        engine = DecisionEngine(rules=custom_rules)
        assert len(engine.rules) == 2
    
    def test_evaluate_single_record_no_triggers(self):
        rules = [
            Rule("Short Tenure", "Tenure", less_than, 12, 15)
        ]
        engine = DecisionEngine(rules=rules)
        
        row = {"Record_ID": "R001", "Tenure": 24, "Late_Payments": 0, "Revenue": 5000}
        result = engine.evaluate_record(row)
        
        assert result.record_id == "R001"
        assert result.total_score == 0
        assert result.classification == "Low Risk"
        assert len(result.triggered_rules) == 0
    
    def test_evaluate_single_record_with_trigger(self):
        rules = [
            Rule("Short Tenure", "Tenure", less_than, 12, 15)
        ]
        engine = DecisionEngine(rules=rules)
        
        row = {"Record_ID": "R001", "Tenure": 6, "Late_Payments": 0, "Revenue": 5000}
        result = engine.evaluate_record(row)
        
        assert result.record_id == "R001"
        assert result.total_score == 15
        assert result.classification == "Low Risk"
        assert len(result.triggered_rules) == 1
    
    def test_evaluate_multiple_rules_cumulative_score(self):
        rules = [
            Rule("Rule1", "Tenure", less_than, 12, 10),
            Rule("Rule2", "Late_Payments", greater_than, 2, 20)
        ]
        engine = DecisionEngine(rules=rules)
        
        row = {"Record_ID": "R001", "Tenure": 6, "Late_Payments": 5, "Revenue": 5000}
        result = engine.evaluate_record(row)
        
        assert result.total_score == 30
        assert result.classification == "Medium Risk"
        assert len(result.triggered_rules) == 2
    
    def test_evaluate_high_risk_classification(self):
        rules = [
            Rule("Rule1", "Tenure", less_than, 12, 25),
            Rule("Rule2", "Late_Payments", greater_than, 2, 20)
        ]
        engine = DecisionEngine(rules=rules)
        
        row = {"Record_ID": "R001", "Tenure": 6, "Late_Payments": 5, "Revenue": 5000}
        result = engine.evaluate_record(row)
        
        assert result.total_score == 45
        assert result.classification == "High Risk"
    
    def test_evaluate_dataset(self):
        rules = [Rule("Test", "Tenure", less_than, 12, 10)]
        engine = DecisionEngine(rules=rules)
        
        df = pd.DataFrame({
            'Record_ID': ['R001', 'R002', 'R003'],
            'Tenure': [6, 24, 8],
            'Late_Payments': [0, 0, 0],
            'Revenue': [1000, 2000, 3000]
        })
        
        results = engine.evaluate_dataset(df)
        
        assert len(results) == 3
        assert results[0].total_score == 10
        assert results[1].total_score == 0
        assert results[2].total_score == 10
    
    def test_evaluate_dataset_classifications(self):
        rules = [
            Rule("Test1", "Tenure", less_than, 12, 25),
            Rule("Test2", "Late_Payments", greater_than, 3, 20)
        ]
        engine = DecisionEngine(rules=rules)
        
        df = pd.DataFrame({
            'Record_ID': ['R001', 'R002', 'R003'],
            'Tenure': [6, 24, 6],
            'Late_Payments': [5, 0, 0],
            'Revenue': [1000, 2000, 3000]
        })
        
        results = engine.evaluate_dataset(df)
        
        assert results[0].classification == "High Risk"
        assert results[1].classification == "Low Risk"
        assert results[2].classification == "Medium Risk"
    
    def test_get_rules_summary(self):
        engine = DecisionEngine()
        summary = engine.get_rules_summary()
        
        assert len(summary) >= 5
        for rule_info in summary:
            assert 'name' in rule_info
            assert 'column' in rule_info
            assert 'weight' in rule_info
    
    def test_get_classification_thresholds(self):
        thresholds = DecisionEngine.get_classification_thresholds()
        
        assert 'High Risk' in thresholds
        assert 'Medium Risk' in thresholds
        assert 'Low Risk' in thresholds
        assert thresholds['High Risk'] == 40
        assert thresholds['Medium Risk'] == 20
