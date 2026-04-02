# Error Handling

Understanding and handling errors in python-typemap.

## Exception Types

### TypeMapError

Base exception for all typemap errors.

```python
from typemap import TypeMapError

try:
    result = eval_typing(expr)
except TypeMapError as e:
    print(f"Type evaluation failed: {e}")
```

### StuckException

Raised when type evaluation cannot proceed because a type variable hasn't been resolved.

```python
from typemap.type_eval import StuckException

try:
    # T is still a TypeVar, can't evaluate
    result = eval_typing(KeyOf[T])
except StuckException:
    # T needs to be bound to a concrete type
    result = eval_typing(KeyOf[ConcreteType])
```

**Common causes:**
- Passing a TypeVar directly to an operator
- Using unevaluated generics
- Circular type references

### RecursionError

Python's built-in recursion limit exceeded during type evaluation.

```python
# Recursive type that doesn't terminate
type Infinite = list[Infinite]

try:
    eval_typing(Partial[Infinite])
except RecursionError:
    print("Type is infinitely recursive")
```

## Common Errors

### 1. Type Variable Not Bound

```python
from typing import TypeVar

T = TypeVar('T')

# Wrong - T is not bound
KeyOf[T]  # StuckException

# Correct - T is bound to a concrete type
KeyOf[User]
```

### 2. Missing Type Annotation

```python
class MissingAnnotation:
    name: str
    data  # No annotation!

# May cause evaluation issues
eval_typing(Attrs[MissingAnnotation])
# May raise: AttributeError or StuckException
```

### 3. Invalid Type Expression

```python
# Wrong - this is not a valid type expression
eval_typing("User")  # String, not a type

# Correct
eval_typing(User)
eval_typing(KeyOf[User])
```

### 4. Union with Non-Types

```python
# Wrong
Union[str, 123]  # 123 is not a type

# Correct
Union[str, int]
```

## Debugging Tips

### Enable Context Manager

```python
from typemap.type_eval import _ensure_context

with _ensure_context() as ctx:
    result = _eval_types_impl(expr, ctx)
    print(f"Resolved: {ctx.resolved}")
    print(f"Seen: {ctx.seen}")
```

### Check What Was Resolved

```python
ctx = EvalContext()
result = eval_typing(expr, ensure_context=False)

# Inspect cache
for type_obj, resolved in ctx.resolved.items():
    print(f"{type_obj} -> {resolved}")
```

### Verify Type Structure

```python
import typing

def inspect_type(t: type) -> dict:
    """Debug type structure."""
    info = {
        'is_generic': isinstance(t, typing._GenericAlias),
        'is_union': hasattr(t, '__origin__') and t.__origin__ is Union,
        'args': getattr(t, '__args__', ()),
        'origin': getattr(t, '__origin__', None),
    }
    return info
```

## Error Recovery

### Fallback to Default

```python
def safe_eval(expr, default=None):
    """Evaluate with fallback on error."""
    try:
        return eval_typing(expr)
    except (StuckException, TypeMapError) as e:
        warnings.warn(f"Evaluation failed: {e}")
        return default
```

### Partial Evaluation

```python
def try_partial_eval(cls: type, operators: list):
    """Try applying operators, collecting failures."""
    results = {}
    errors = []

    for op in operators:
        try:
            results[op] = eval_typing(op[cls])
        except Exception as e:
            errors.append((op, str(e)))

    return results, errors
```

## Validation Before Evaluation

### Check for TypeVars

```python
from typing import TypeVar, get_args, get_origin

def has_unbound_typevars(t: type) -> bool:
    """Check if type has unresolved TypeVars."""
    if isinstance(t, TypeVar):
        return True
    if hasattr(t, '__args__'):
        return any(has_unbound_typevars(arg) for arg in t.__args__)
    return False

# Before evaluation
if has_unbound_typevars(MyType):
    raise ValueError("Type has unbound TypeVars")
```

### Validate Type Structure

```python
def validate_for_eval(t: type) -> tuple[bool, str]:
    """Validate type can be evaluated."""
    if t is None:
        return False, "Type is None"
    if isinstance(t, str):
        return False, "Type is a string, not a type"
    if isinstance(t, TypeVar):
        return False, f"TypeVar {t} is unbound"
    if not callable(t):
        return False, f"{t} is not callable"
    return True, "OK"
```

## Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('typemap')

# Enable debug logging
logger.setLevel(logging.DEBUG)
```

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `StuckException: cannot evaluate KeyOf[T]` | TypeVar not bound | Provide concrete type |
| `RecursionError` | Infinite type recursion | Break recursive cycle |
| `TypeError: not a type` | Invalid type passed | Check type annotation |
| `AttributeError: no __args__` | Non-generic used as generic | Use correct type |
| `KeyError` | Type not in namespace | Provide namespace context |

## Best Practices

1. **Always bind TypeVars** before passing to operators
2. **Use concrete types** not type aliases when possible
3. **Catch specific exceptions** not just `Exception`
4. **Validate inputs** before expensive evaluations
5. **Cache results** to avoid repeated evaluations
6. **Provide namespace** for custom type resolution
