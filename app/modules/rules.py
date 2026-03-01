from typing import Callable, Tuple, Any


class Rule:
    """
    Represents a single decision rule with a condition and weight.
    
    Each rule examines a specific field and determines whether a condition
    is satisfied. If triggered, its weight is added to the cumulative score.
    """
    
    def __init__(
        self,
        name: str,
        column: str,
        condition: Callable[[Any, Any], bool],
        threshold: Any,
        weight: int,
        description: str = ""
    ):
        self.name = name
        self.column = column
        self.condition = condition
        self.threshold = threshold
        self.weight = weight
        self.description = description
    
    def evaluate(self, row: dict) -> Tuple[bool, int]:
        """
        Evaluate the rule against a single record.
        
        Returns:
            Tuple of (is_triggered, weight_contribution)
        """
        value = row.get(self.column)
        if value is None:
            return False, 0
        
        try:
            if self.condition(value, self.threshold):
                return True, self.weight
        except (TypeError, ValueError):
            return False, 0
        
        return False, 0
    
    def __repr__(self) -> str:
        return f"Rule(name='{self.name}', column='{self.column}', weight={self.weight})"


def less_than(value: Any, threshold: Any) -> bool:
    """Condition: value < threshold"""
    return float(value) < float(threshold)


def greater_than(value: Any, threshold: Any) -> bool:
    """Condition: value > threshold"""
    return float(value) > float(threshold)


def less_than_or_equal(value: Any, threshold: Any) -> bool:
    """Condition: value <= threshold"""
    return float(value) <= float(threshold)


def greater_than_or_equal(value: Any, threshold: Any) -> bool:
    """Condition: value >= threshold"""
    return float(value) >= float(threshold)


def equals(value: Any, threshold: Any) -> bool:
    """Condition: value == threshold"""
    return value == threshold


DEFAULT_RULES = [
    Rule(
        name="Short Tenure",
        column="Tenure",
        condition=less_than,
        threshold=12,
        weight=15,
        description="Customer has been with the company for less than 12 months"
    ),
    Rule(
        name="Very Short Tenure",
        column="Tenure",
        condition=less_than,
        threshold=6,
        weight=10,
        description="Customer has been with the company for less than 6 months"
    ),
    Rule(
        name="High Late Payments",
        column="Late_Payments",
        condition=greater_than,
        threshold=3,
        weight=20,
        description="Customer has more than 3 late payments on record"
    ),
    Rule(
        name="Moderate Late Payments",
        column="Late_Payments",
        condition=greater_than,
        threshold=1,
        weight=10,
        description="Customer has more than 1 late payment on record"
    ),
    Rule(
        name="Low Revenue",
        column="Revenue",
        condition=less_than,
        threshold=1000,
        weight=15,
        description="Customer generates less than $1,000 in revenue"
    ),
    Rule(
        name="Very Low Revenue",
        column="Revenue",
        condition=less_than,
        threshold=500,
        weight=10,
        description="Customer generates less than $500 in revenue"
    ),
    Rule(
        name="High Revenue Contributor",
        column="Revenue",
        condition=greater_than,
        threshold=5000,
        weight=-10,
        description="Customer generates more than $5,000 in revenue (reduces risk)"
    ),
]


def get_default_rules():
    """Return the default set of rules for evaluation."""
    return DEFAULT_RULES.copy()
