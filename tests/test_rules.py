import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modules.rules import (
    Rule, 
    less_than, 
    greater_than, 
    less_than_or_equal,
    greater_than_or_equal,
    equals,
    get_default_rules
)


class TestConditionFunctions:
    """Tests for the condition helper functions."""
    
    def test_less_than_true(self):
        assert less_than(5, 10) is True
    
    def test_less_than_false(self):
        assert less_than(15, 10) is False
    
    def test_less_than_equal_boundary(self):
        assert less_than(10, 10) is False
    
    def test_greater_than_true(self):
        assert greater_than(15, 10) is True
    
    def test_greater_than_false(self):
        assert greater_than(5, 10) is False
    
    def test_greater_than_equal_boundary(self):
        assert greater_than(10, 10) is False


class TestRuleClass:
    """Tests for the Rule class."""
    
    def test_rule_creation(self):
        rule = Rule(
            name="Test Rule",
            column="Tenure",
            condition=less_than,
            threshold=12,
            weight=10,
            description="Test description"
        )
        assert rule.name == "Test Rule"
        assert rule.column == "Tenure"
        assert rule.weight == 10
        assert rule.threshold == 12
    
    def test_rule_evaluate_triggers(self):
        rule = Rule(
            name="Short Tenure",
            column="Tenure",
            condition=less_than,
            threshold=12,
            weight=15
        )
        row = {"Tenure": 6, "Record_ID": "R001"}
        is_triggered, weight = rule.evaluate(row)
        assert is_triggered is True
        assert weight == 15
    
    def test_rule_evaluate_does_not_trigger(self):
        rule = Rule(
            name="Short Tenure",
            column="Tenure",
            condition=less_than,
            threshold=12,
            weight=15
        )
        row = {"Tenure": 24, "Record_ID": "R001"}
        is_triggered, weight = rule.evaluate(row)
        assert is_triggered is False
        assert weight == 0
    
    def test_rule_evaluate_missing_column(self):
        rule = Rule(
            name="Test",
            column="NonExistent",
            condition=less_than,
            threshold=10,
            weight=5
        )
        row = {"Tenure": 6, "Record_ID": "R001"}
        is_triggered, weight = rule.evaluate(row)
        assert is_triggered is False
        assert weight == 0
    
    def test_rule_evaluate_boundary_value(self):
        rule = Rule(
            name="Boundary Test",
            column="Tenure",
            condition=less_than,
            threshold=12,
            weight=10
        )
        row = {"Tenure": 12, "Record_ID": "R001"}
        is_triggered, weight = rule.evaluate(row)
        assert is_triggered is False
        assert weight == 0


class TestDefaultRules:
    """Tests for the default rule set."""
    
    def test_default_rules_count(self):
        rules = get_default_rules()
        assert len(rules) >= 5
    
    def test_default_rules_have_required_attributes(self):
        rules = get_default_rules()
        for rule in rules:
            assert hasattr(rule, 'name')
            assert hasattr(rule, 'column')
            assert hasattr(rule, 'condition')
            assert hasattr(rule, 'threshold')
            assert hasattr(rule, 'weight')
    
    def test_negative_weight_rule_exists(self):
        rules = get_default_rules()
        negative_weights = [r for r in rules if r.weight < 0]
        assert len(negative_weights) >= 1
