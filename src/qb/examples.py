import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qb.qb import QueryBuilder, eq, and_, or_

# Simple group syntax (your original request)
query1 = QueryBuilder().and_(eq("color", "red"), eq("size", 10)).build()
print("Query 1:", query1)
assert query1 == '(color = "red" && size = "10")'

# Complex grouping
query2 = QueryBuilder().and_(
    eq("id", "batch123"),
    or_(eq("color", "red"), eq("color", "blue"))
).build()
print("Query 2:", query2)
assert query2 == '(id = "batch123" && (color = "red" || color = "blue"))'

# Mixed usage (chaining + groups)
query3 = QueryBuilder().by_id("batch123").and_(eq("color", "red"), eq("size", 10)).build()
print("Query 3:", query3)
assert query3 == 'id = "batch123" && (color = "red" && size = "10")'

# Nested groups
query4 = QueryBuilder().and_(
    eq("id", "test"),
    or_(
        and_(eq("color", "red"), eq("size", 10)),
        and_(eq("color", "blue"), eq("size", 12))
    )
).build()
print("Query 4:", query4)
assert query4 == '(id = "test" && ((color = "red" && size = "10") || (color = "blue" && size = "12")))'
