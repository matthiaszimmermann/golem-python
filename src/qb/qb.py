from typing import Any, List

AND = "&&"
OR = "||"
class Condition:
    """Represents a query condition that can be combined with others."""

    def __init__(self, expression: str):
        self.expression = expression

    def and_(self, other: "Condition") -> "Condition":
        """Combine this condition with another using AND."""
        return Condition(f"({self.expression} {AND} {other.expression})")

    def or_(self, other: "Condition") -> "Condition":
        """Combine this condition with another using OR."""
        return Condition(f"({self.expression} {OR} {other.expression})")

    def not_(self) -> "Condition":
        """Negate this condition using NOT."""
        return Condition(f"!({self.expression})")

    def __str__(self) -> str:
        return self.expression


class Field:
    """Represents a queryable field with comparison operations."""

    def __init__(self, name: str):
        self.name = name

    def _format_value(self, value: Any) -> str:
        """Format value for query string based on type."""
        if isinstance(value, int):
            if value < 0:
                raise ValueError("Only positive values are allowed for integer fields")
            return str(value)
        else:
            return f'"{value}"'

    def eq(self, value: Any) -> Condition:
        """Create equality condition: field = "value" or field = value."""
        return Condition(f'{self.name} = {self._format_value(value)}')

    def ne(self, value: Any) -> Condition:
        """Create not-equal condition: field != "value" or field != value."""
        return Condition(f'{self.name} != {self._format_value(value)}')

    def gt(self, value: Any) -> Condition:
        """Create greater-than condition: field > "value" or field > value."""
        return Condition(f'{self.name} > {self._format_value(value)}')

    def lt(self, value: Any) -> Condition:
        """Create less-than condition: field < "value" or field < value."""
        return Condition(f'{self.name} < {self._format_value(value)}')

    def ge(self, value: Any) -> Condition:
        """Create greater-than-or-equal condition: field >= "value" or field >= value."""
        return Condition(f'{self.name} >= {self._format_value(value)}')

    def le(self, value: Any) -> Condition:
        """Create less-than-or-equal condition: field <= "value" or field <= value."""
        return Condition(f'{self.name} <= {self._format_value(value)}')

    def like(self, pattern: str) -> Condition:
        """Create LIKE condition: field LIKE "pattern"."""
        return Condition(f'{self.name} LIKE "{pattern}"')

    def in_(self, *values: Any) -> Condition:
        """Create IN condition: field IN (value1, value2, ...) with proper value formatting."""
        value_list = ', '.join(self._format_value(v) for v in values)
        return Condition(f'{self.name} IN ({value_list})')


class QueryBuilder:
    """JOOQ-inspired fluent query builder for GolemBase."""

    def __init__(self):
        self._conditions: List[Condition] = []

    def where(self, condition: Condition) -> "QueryBuilder":
        """Add a WHERE condition."""
        self._conditions.append(condition)
        return self

    def and_(self, condition: Condition) -> "QueryBuilder":
        """Add an AND condition to the last condition."""
        if self._conditions:
            last = self._conditions[-1]
            self._conditions[-1] = last.and_(condition)
        else:
            self._conditions.append(condition)
        return self

    def or_(self, condition: Condition) -> "QueryBuilder":
        """Add an OR condition to the last condition."""
        if self._conditions:
            last = self._conditions[-1]
            self._conditions[-1] = last.or_(condition)
        else:
            self._conditions.append(condition)
        return self

    def build(self) -> str:
        """Build the final query string."""
        if not self._conditions:
            return ""
        return " && ".join(str(c) for c in self._conditions)


# System entity attributes (compile-time known)
ID = Field("$id") # entity key
OWNER = Field("$owner")
EXPIRES_AT = Field("$expires_at")
CREATED_AT = Field("$created_at")
UPDATED_AT = Field("$updated_at")


class Annotations:
    """Dynamic field accessor for user-defined annotations."""

    def __getattr__(self, name: str) -> Field:
        """Create a field for any annotation name using dot notation."""
        return Field(name)

    def __getitem__(self, name: str) -> Field:
        """Create a field for any annotation name using bracket notation."""
        return Field(name)


# Global annotations instance for user-defined fields
ANNOTATIONS = Annotations()


# Convenience functions for creating conditions
def and_(*conditions: Condition) -> Condition:
    """Create an AND combination of multiple conditions."""
    if not conditions:
        raise ValueError("At least one condition is required")

    result = conditions[0]
    for condition in conditions[1:]:
        result = result.and_(condition)
    return result


def or_(*conditions: Condition) -> Condition:
    """Create an OR combination of multiple conditions."""
    if not conditions:
        raise ValueError("At least one condition is required")

    result = conditions[0]
    for condition in conditions[1:]:
        result = result.or_(condition)
    return result


def not_(condition: Condition) -> Condition:
    """Create a NOT (negation) of a condition."""
    return condition.not_()


# Additional utility functions
def field(name: str) -> Field:
    """Create a custom field for dynamic field names."""
    return Field(name)


def custom_condition(expression: str) -> Condition:
    """Create a custom condition with raw expression."""
    return Condition(expression)
