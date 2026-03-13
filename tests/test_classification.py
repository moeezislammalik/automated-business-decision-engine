import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modules.engine import (
    get_classification,
    generate_explanation,
    CLASSIFICATION_THRESHOLDS
)


class TestClassificationThresholds:
    """Tests for classification threshold logic."""
    
    def test_high_risk_at_threshold(self):
        """Score exactly at high risk threshold should be High Risk."""
        assert get_classification(40) == 'High Risk'
    
    def test_high_risk_above_threshold(self):
        """Score above high risk threshold should be High Risk."""
        assert get_classification(55) == 'High Risk'
        assert get_classification(100) == 'High Risk'
    
    def test_medium_risk_at_threshold(self):
        """Score exactly at medium risk threshold should be Medium Risk."""
        assert get_classification(20) == 'Medium Risk'
    
    def test_medium_risk_between_thresholds(self):
        """Score between medium and high thresholds should be Medium Risk."""
        assert get_classification(25) == 'Medium Risk'
        assert get_classification(39) == 'Medium Risk'
    
    def test_low_risk_below_threshold(self):
        """Score below medium risk threshold should be Low Risk."""
        assert get_classification(0) == 'Low Risk'
        assert get_classification(10) == 'Low Risk'
        assert get_classification(19) == 'Low Risk'
    
    def test_boundary_medium_to_high(self):
        """Test boundary between medium and high risk."""
        assert get_classification(39) == 'Medium Risk'
        assert get_classification(40) == 'High Risk'
    
    def test_boundary_low_to_medium(self):
        """Test boundary between low and medium risk."""
        assert get_classification(19) == 'Low Risk'
        assert get_classification(20) == 'Medium Risk'
    
    def test_negative_score(self):
        """Negative scores should be Low Risk."""
        assert get_classification(-5) == 'Low Risk'
        assert get_classification(-10) == 'Low Risk'


class TestExplanationGeneration:
    """Tests for explanation trace generation."""
    
    def test_explanation_no_rules_triggered(self):
        """Test explanation when no rules are triggered."""
        explanation = generate_explanation('R001', 0, 'Low Risk', [])
        assert 'R001' in explanation
        assert 'No rules were triggered' in explanation
        assert 'Low Risk' in explanation
    
    def test_explanation_with_triggered_rules(self):
        """Test explanation with triggered rules."""
        triggered = [
            {'name': 'Short Tenure', 'weight': 15, 'description': 'Tenure < 12 months'},
            {'name': 'High Late Payments', 'weight': 20, 'description': 'Late payments > 3'}
        ]
        explanation = generate_explanation('R002', 35, 'Medium Risk', triggered)
        
        assert 'R002' in explanation
        assert 'Short Tenure' in explanation
        assert 'High Late Payments' in explanation
        assert '35' in explanation
        assert 'Medium Risk' in explanation
    
    def test_explanation_contains_weight_sum(self):
        """Test that explanation shows weight calculation."""
        triggered = [
            {'name': 'Rule1', 'weight': 10, 'description': 'Desc1'},
            {'name': 'Rule2', 'weight': 15, 'description': 'Desc2'}
        ]
        explanation = generate_explanation('R003', 25, 'Medium Risk', triggered)
        
        assert 'Score Calculation' in explanation
        assert '25' in explanation
    
    def test_explanation_high_risk_threshold_text(self):
        """Test high risk threshold explanation."""
        triggered = [{'name': 'Rule', 'weight': 45, 'description': 'Desc'}]
        explanation = generate_explanation('R004', 45, 'High Risk', triggered)
        
        assert '>= 40' in explanation
    
    def test_explanation_medium_risk_threshold_text(self):
        """Test medium risk threshold explanation."""
        triggered = [{'name': 'Rule', 'weight': 25, 'description': 'Desc'}]
        explanation = generate_explanation('R005', 25, 'Medium Risk', triggered)
        
        assert '>= 20' in explanation
        assert '< 40' in explanation
    
    def test_explanation_low_risk_threshold_text(self):
        """Test low risk threshold explanation."""
        triggered = [{'name': 'Rule', 'weight': 10, 'description': 'Desc'}]
        explanation = generate_explanation('R006', 10, 'Low Risk', triggered)
        
        assert '< 20' in explanation
