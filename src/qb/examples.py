import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qb.qb import QueryBuilder, ID, OWNER, EXPIRES_AT, ANNOTATIONS, and_, or_, not_, field

print("=== QB Examples - JOOQ-Inspired Query Builder ===\n")

# Example 1: System fields only
print("1. System fields:")
query1 = QueryBuilder().where(
    ID.eq("batch123")
).build()
print(f"   ID.eq('batch123') -> {query1}")
assert query1 == '$id = "batch123"'

query1b = QueryBuilder().where(EXPIRES_AT.lt(123456789)).build()
print(f"   EXPIRES_AT.lt(123456789) -> {query1b}")
assert query1b == '$expires_at < 123456789'

# Example 2: User annotations only
print("\n2. User annotations:")
query2 = QueryBuilder().where(ANNOTATIONS.color.eq("red")).build()
print(f"   ANNOTATIONS.color.eq('red') -> {query2}")
assert query2 == 'color = "red"'

query2b = QueryBuilder().where(ANNOTATIONS.size.gt(10)).build()
print(f"   ANNOTATIONS.size.gt(10) -> {query2b}")
assert query2b == 'size > 10'

# Example 3: Bracket notation for annotations
print("\n3. Bracket notation:")
query3 = QueryBuilder().where(ANNOTATIONS["field-with-dash"].eq("value")).build()
print(f"   ANNOTATIONS['field-with-dash'].eq('value') -> {query3}")
assert query3 == 'field-with-dash = "value"'

# Example 4: Mixed system + user annotations
print("\n4. Mixed system + user annotations:")
query4 = QueryBuilder().where(
    ID.eq("batch123").and_(ANNOTATIONS.color.eq("red"))
).build()
print(f"   ID.eq('batch123').and_(ANNOTATIONS.color.eq('red')) -> {query4}")
assert query4 == '($id = "batch123" && color = "red")'

# Example 5: Complex condition composition
print("\n5. Complex condition composition:")
query5 = QueryBuilder().where(
    ID.eq("batch123").and_(
        ANNOTATIONS.color.eq("red").or_(ANNOTATIONS.color.eq("blue"))
    )
).build()
print(f"   Complex OR within AND -> {query5}")
assert query5 == '($id = "batch123" && (color = "red" || color = "blue"))'

# Example 6: Multiple conditions with QueryBuilder chaining
print("\n6. QueryBuilder chaining:")
query6 = QueryBuilder().where(ID.eq("test")).and_(ANNOTATIONS.size.gt(10)).build()
print(f"   where().and_() chaining -> {query6}")
assert query6 == '($id = "test" && size > 10)'

# Example 7: Using convenience functions
print("\n7. Convenience functions:")
complex_condition = and_(
    ID.eq("batch"),
    or_(ANNOTATIONS.color.eq("red"), ANNOTATIONS.color.eq("blue")),
    ANNOTATIONS.size.ge(10)
)
query7 = QueryBuilder().where(complex_condition).build()
print(f"   and_(...) / or_(...) functions -> {query7}")
expected7 = '(($id = "batch" && (color = "red" || color = "blue")) && size >= 10)'
assert query7 == expected7

# Example 8: Field operations variety
print("\n8. Various field operations:")
query8a = QueryBuilder().where(ANNOTATIONS.priority.in_("high", "medium")).build()
print(f"   .in_() operation -> {query8a}")
assert query8a == 'priority IN ("high", "medium")'

query8a_int = QueryBuilder().where(ANNOTATIONS.level.in_(1, 2, 3)).build()
print(f"   .in_() integers -> {query8a_int}")
assert query8a_int == 'level IN (1, 2, 3)'

query8b = QueryBuilder().where(ANNOTATIONS.name.like("%test%")).build()
print(f"   .like() operation -> {query8b}")
assert query8b == 'name LIKE "%test%"'

query8c = QueryBuilder().where(ANNOTATIONS.score.ge(85)).build()
print(f"   .ge() operation -> {query8c}")
assert query8c == 'score >= 85'

# Example 9: Dynamic field creation
# Example 8d: Negative integer validation
print("\n   Negative integer validation:")
try:
    bad_query = QueryBuilder().where(ANNOTATIONS.size.gt(-5)).build()
    print("   ERROR: Should have raised exception for negative value")
except ValueError as e:
    print(f"   ✅ Correctly caught negative value: {e}")
    assert str(e) == "Only positive values are allowed for integer fields"

print("\n9. Dynamic field creation:")
custom_field = field("dynamic_attribute")
query9 = QueryBuilder().where(custom_field.eq("value")).build()
print(f"   field('dynamic_attribute').eq('value') -> {query9}")
assert query9 == 'dynamic_attribute = "value"'

# Example 10: Real-world complex query
print("\n10. Real-world complex query:")
real_world = QueryBuilder().where(
    and_(
        ID.eq("batch456"),
        OWNER.eq("0xabcd1234"),
        or_(
            ANNOTATIONS.status.eq("active"),
            and_(
                ANNOTATIONS.status.eq("pending"),
                ANNOTATIONS.priority.eq("high")
            )
        ),
        ANNOTATIONS.created_date.gt("2024-01-01")
    )
).build()
print(f"    Real-world query -> {real_world}")
expected_real = '((($id = "batch456" && $owner = "0xabcd1234") && (status = "active" || (status = "pending" && priority = "high"))) && created_date > "2024-01-01")'
assert real_world == expected_real

# Example 11: NOT operator examples
print("\n11. NOT operator examples:")

# Simple NOT
not_active = not_(ANNOTATIONS.status.eq("active"))
print(f"    not_(status.eq('active')) -> {not_active.expression}")
assert not_active.expression == "!(status = \"active\")"

# NOT with complex condition
not_old_and_expensive = not_(and_(ANNOTATIONS.age.gt(30), ANNOTATIONS.price.gt(100)))
print(f"    not_(age > 30 AND price > 100) -> {not_old_and_expensive.expression}")
assert not_old_and_expensive.expression == "!((age > 30 && price > 100))"

# Double negation
not_not_finished = not_(not_(ANNOTATIONS.status.eq("completed")))
print(f"    not_(not_(status = 'completed')) -> {not_not_finished.expression}")
assert not_not_finished.expression == "!(!(status = \"completed\"))"

# NOT with OR condition
not_cheap_or_small = not_(or_(ANNOTATIONS.price.lt(50), ANNOTATIONS.size.eq("small")))
print(f"    not_(price < 50 OR size = 'small') -> {not_cheap_or_small.expression}")
assert not_cheap_or_small.expression == "!((price < 50 || size = \"small\"))"

print("\n✅ All QB examples passed!")
