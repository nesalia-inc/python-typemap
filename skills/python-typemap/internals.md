# Internals and Architecture

Understanding how python-typemap works internally.

## Project Structure

```
packages/typemap/
├── src/typemap/
│   ├── __init__.py           # Main exports
│   ├── typing.py             # Type operator definitions
│   └── type_eval/
│       ├── __init__.py       # eval_typing exports
│       ├── _eval_types_impl.py  # Core evaluation logic
│       ├── _eval_typing.py    # Main eval function
│       ├── _box.py           # Class boxing
│       ├── _eval_context.py   # Context management
│       └── _helpers.py        # Utility functions
├── typemap_extensions/       # Public API (re-exports)
└── tests/
```

## Core Components

### 1. Type Operators (`typing.py`)

Type operators are defined as special generic classes:

```python
class _TupleLikeOperator(typing.Generic[T], typing._TupleLikeTarget):
    """Base class for tuple-like type operators."""
    pass

class Member[N: str, T, Q: MemberQuals = typing.Never, ...]:
    """Member descriptor with name, type, and qualifiers."""
    type name = N
    type type = T
    type quals = Q

class KeyOf[T](_TupleLikeOperator):
    """TypeScript's keyof operator."""
    pass

class Partial[T](_TupleLikeOperator):
    """Make all fields optional."""
    pass
```

**Key Design Pattern:** Uses `typing.Generic` with subscript syntax for type parameters.

### 2. Evaluation Context (`_eval_context.py`)

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class EvalContext:
    """Context for type evaluation."""
    resolved: dict[type, Any] = field(default_factory=dict)
    seen: set[type] = field(default_factory=set)
    ns: dict[str, Any] = field(default_factory=dict)
```

**Purpose:**
- `resolved`: Memoization cache for evaluated types
- `seen`: Cycle detection for recursive types
- `ns`: Namespace for type name resolution

### 3. Singledispatch Evaluation (`_eval_types_impl.py`)

```python
from functools import singledispatch

@singledispatch
def _eval_types_impl(obj: Any, ctx: EvalContext) -> Any:
    """Default handler - return as-is."""
    return obj

@_eval_types_impl.register
def _eval_type_alias(obj: types.TypeAliasType, ctx: EvalContext):
    """Handle type aliases."""
    ...

@_eval_types_impl.register
def _eval_union(obj: types.UnionType, ctx: EvalContext):
    """Handle Union types."""
    ...

@_eval_types_impl.register
def _eval_literal(obj: types.LiteralGenericAlias, ctx: EvalContext):
    """Handle Literal types."""
    ...
```

**Benefits:**
- Extensible by registering new handlers
- Falls back to default for unknown types
- Clear separation of concerns

### 4. Class Boxing (`_box.py`)

Boxes classes for safe evaluation:

```python
def box_cache(cls: type, ctx: EvalContext) -> Any:
    """Cache and box class evaluations."""
    key = (cls, id(ctx.resolved))
    if key in _box_cache:
        return _box_cache[key]

    boxed = _box_class(cls, ctx)
    _box_cache[key] = boxed
    return boxed
```

### 5. Main Evaluation Loop (`_eval_typing.py`)

```python
import contextvars

_current_context: contextvars.ContextVar[EvalContext | None] = \
    contextvars.ContextVar('current_context', default=None)

def eval_typing(expr: Any, *, ensure_context: bool = True) -> Any:
    """Evaluate a type expression at runtime."""
    if ensure_context:
        with _ensure_context() as ctx:
            return _eval_types_impl(expr, ctx)
    else:
        ctx = _current_context.get()
        if ctx is None:
            raise TypeMapError("No evaluation context")
        return _eval_types_impl(expr, ctx)
```

## Custom GenericAlias Classes

### _IterSafeGenericAlias

Allows safe iteration over unevaluated types:

```python
class _IterSafeGenericAlias:
    """Generic alias that safely handles iteration."""
    def __init__(self, origin, args):
        self.__origin__ = origin
        self.__args__ = args

    def __iter__(self):
        """Safely iterate without evaluating."""
        for arg in self.__args__:
            yield arg
```

### _BoolGenericAlias

Boolean evaluation with context:

```python
class _BoolGenericAlias:
    """Boolean operations on types."""
    def __and__(self, other):
        return _eval_bool_and(self, other)

    def __or__(self, other):
        return _eval_bool_or(self, other)
```

### _AssociatedTypeGenericAlias

Associated type access:

```python
class _AssociatedTypeGenericAlias:
    """访问 associated types."""
    def __get__(self, instance, owner):
        return _eval_associated_type(owner, self.__args__)
```

## Error Handling

### StuckException

Raised when type operators receive type variable arguments:

```python
class StuckException(TypeMapError):
    """Type evaluation is stuck waiting for concrete type."""
    pass
```

**When it happens:**
- `KeyOf[T]` where `T` is still a TypeVar
- Other operators without enough context

### TypeMapError

General type evaluation errors:

```python
class TypeMapError(Exception):
    """Base exception for typemap errors."""
    pass
```

## Thread Safety

Uses `contextvars` for thread-local context:

```python
import contextvars

# Each thread gets its own context
_current_context: contextvars.ContextVar[EvalContext | None] = \
    contextvars.ContextVar('current_context', default=None)
```

## Extension Points

### Adding New Type Handlers

```python
from typemap.type_eval._eval_types_impl import _eval_types_impl

@_eval_types_impl.register
def _eval_my_custom_type(obj: MyCustomType, ctx: EvalContext):
    """Handle MyCustomType evaluation."""
    # Custom logic here
    return transformed_result
```

### Adding New Type Operators

```python
from typemap.typing import _TupleLikeOperator

class MyOperator[T](_TupleLikeOperator):
    """Custom type operator."""
    pass
```

## Performance Considerations

1. **Memoization**: `ctx.resolved` caches all evaluations
2. **Cycle Detection**: `ctx.seen` prevents infinite loops
3. **Lazy Boxing**: Classes are boxed only when needed
4. **Context Isolation**: Each `eval_typing` call is independent

## Testing Internals

```python
# Direct context testing
ctx = EvalContext()
result = _eval_types_impl(some_type_expr, ctx)

# Check memoization
assert some_type_expr in ctx.resolved

# Check cycle detection
ctx.seen.add(type(some_type_expr))
# Should raise StuckException if encountered again
```
