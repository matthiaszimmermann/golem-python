## Query Builder

### Features

- JOOQ-style field operations: .eq(), .gt(), .in_(), etc."
- Boolean complete: .and_(), .or_(), .not_() with function variants"
- System fields (ID, OWNER) are compile-time constants"
- User annotations are dynamic: ANNOTATIONS.any_field"
- Rich set of comparison operators")
- Multiple ways to create conditions (builder, functions, fields)"


### Examples
Run examples
```python
uv run src/qb/examples.py
```


## Core Boolean Operators

### AND Operations
- **Method chaining**: `condition1.and_(condition2)`
- **Function form**: `and_(condition1, condition2, ...)`
- **Expression output**: Uses `&&` operator

### OR Operations
- **Method chaining**: `condition1.or_(condition2)`
- **Function form**: `or_(condition1, condition2, ...)`
- **Expression output**: Uses `||` operator

### NOT Operations (NEW!)
- **Method chaining**: `condition.not_()`
- **Function form**: `not_(condition)`
- **Expression output**: Uses `!()` wrapper

## Examples

```python
from qb.qb import ANNOTATIONS, and_, or_, not_

# Basic boolean operations
is_active = ANNOTATIONS.status.eq("active")
is_premium = ANNOTATIONS.tier.eq("premium")

# AND: active AND premium
both = is_active.and_(is_premium)
# OR: active OR premium
either = is_active.or_(is_premium)
# NOT: NOT active
not_active = is_active.not_()

# Complex compositions
complex_query = not_(and_(
    ANNOTATIONS.age.gt(30),
    or_(
        ANNOTATIONS.status.eq("inactive"),
        ANNOTATIONS.tier.eq("basic")
    )
))
# Result: !((age > 30 && (status = "inactive" || tier = "basic")))
```
