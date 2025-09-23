from typing import Any, List, Union

# Standalone condition functions
def eq(field: str, value: Any) -> str:
    """Create an equality condition: field = "value"."""
    return f'{field} = "{value}"'

def ne(field: str, value: Any) -> str:
    """Create a not-equal condition: field != "value"."""
    return f'{field} != "{value}"'

def gt(field: str, value: Any) -> str:
    """Create a greater-than condition: field > "value"."""
    return f'{field} > "{value}"'

def lt(field: str, value: Any) -> str:
    """Create a less-than condition: field < "value"."""
    return f'{field} < "{value}"'

def and_(*conditions: Union[str, "QueryGroup"]) -> "QueryGroup":
    """Create an AND group of conditions."""
    return QueryGroup("&&", list(conditions))

def or_(*conditions: Union[str, "QueryGroup"]) -> "QueryGroup":
    """Create an OR group of conditions."""
    return QueryGroup("||", list(conditions))

class QueryGroup:
    """Represents a group of conditions with an operator."""

    def __init__(self, operator: str, conditions: List[Union[str, "QueryGroup"]]) -> None:
        self.operator = operator
        self.conditions = conditions

    def to_string(self) -> str:
        """Convert the group to a query string."""
        condition_strings = []
        for condition in self.conditions:
            if isinstance(condition, QueryGroup):
                condition_strings.append(f"({condition.to_string()})")
            else:
                condition_strings.append(str(condition))

        return f" {self.operator} ".join(condition_strings)

class QueryBuilder:
    """Fluent API for building GolemBase entity queries."""

    def __init__(self) -> None:
        self._parts: List[Union[str, QueryGroup]] = []

    def where(self, field: str, operator: str, value: Any) -> "QueryBuilder":
        """Add a WHERE condition with field = value."""
        condition = f'{field} {operator} "{value}"'
        self._parts.append(condition)
        return self

    def equals(self, field: str, value: Any) -> "QueryBuilder":
        """Add equality condition: field = "value"."""
        return self.where(field, "=", value)

    def eq(self, field: str, value: Any) -> "QueryBuilder":
        """Add equality condition: field = "value" (alias for equals)."""
        return self.equals(field, value)

    def by_id(self, entity_id: str) -> "QueryBuilder":
        """Filter by entity ID."""
        return self.equals("id", entity_id)

    def and_(self, *conditions: Union[str, QueryGroup]) -> "QueryBuilder":
        """Add an AND group of conditions."""
        group = QueryGroup("&&", list(conditions))
        self._parts.append(group)
        return self

    def or_(self, *conditions: Union[str, QueryGroup]) -> "QueryBuilder":
        """Add an OR group of conditions."""
        group = QueryGroup("||", list(conditions))
        self._parts.append(group)
        return self

    def build(self) -> str:
        """Build the final query string."""
        if not self._parts:
            return ""

        result_parts = []
        for part in self._parts:
            if isinstance(part, QueryGroup):
                if len(part.conditions) > 1:
                    result_parts.append(f"({part.to_string()})")
                else:
                    result_parts.append(part.to_string())
            else:
                result_parts.append(str(part))

        return " && ".join(result_parts)
