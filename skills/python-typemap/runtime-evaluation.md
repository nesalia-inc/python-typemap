# Runtime Evaluation

The `eval_typing()` function is the core of python-typemap - it evaluates type expressions at runtime.

## Overview

```python
from typemap import eval_typing
import typemap_extensions as tm

result = eval_typing(tm.KeyOf[SomeType])
```

## How It Works

### 1. Entry Point

`eval_typing()` is defined in `typemap/type_eval/__init__.py`:

```python
def eval_typing(expr: Any, *, ensure_context: bool = True) -> Any:
    """Evaluate a type expression at runtime."""
```

### 2. Context Management

The evaluation uses `EvalContext` to track:
- **resolved**: Memoization of evaluated types
- **seen**: Types currently being evaluated (for recursion detection)
- **ns**: Namespace for type resolution

```python
from typemap.type_eval._eval_types_impl import EvalContext

ctx = EvalContext(
    resolved={},  # Memoization cache
    seen=set(),   # For cycle detection
    ns={}         # Type namespace
)
```

### 3. Singledispatch Implementation

The evaluation uses Python's `singledispatch` to handle different type kinds:

```python
from functools import singledispatch

@singledispatch
def _eval_types_impl(obj: Any, ctx: EvalContext) -> Any:
    """Default handler - return as-is."""
    return obj

@_eval_types_impl.register
def _eval_literal(obj: typing._LiteralGenericAlias, ctx: EvalContext):
    """Handle Literal types."""
    ...

@_eval_types_impl.register
def _eval_special_form(obj: typing._SpecialForm, ctx: EvalContext):
    """Handle special forms like Union, Optional."""
    ...
```

### 4. Custom GenericAlias Classes

Python-typemap uses custom `GenericAlias` classes for special behaviors:

| Class | Purpose |
|-------|---------|
| `_IterSafeGenericAlias` | Safe iteration over unevaluated types |
| `_BoolGenericAlias` | Boolean evaluation with context |
| `_AssociatedTypeGenericAlias` | Associated type access |

## Context Helpers

### _ensure_context()

Ensures an evaluation context exists:

```python
from typemap.type_eval._eval_types_impl import _ensure_context

with _ensure_context() as ctx:
    result = _eval_types_impl(expr, ctx)
```

### _child_context()

Creates a child context for nested evaluation:

```python
with _child_context(ctx) as child_ctx:
    # Nested evaluation uses child_ctx
    ...
```

## Caching Strategy

### box_cache

Classes are boxed (wrapped) once and cached:

```python
from typemap.type_eval._box import box_cache

boxed = box_cache(cls, ctx)
# Cached by (cls, id(ctx.resolved))
```

### resolved / seen

The `resolved` dict memoizes type evaluations:
```python
ctx.resolved[type(obj)] = result
```

The `seen` set detects recursion:
```python
if type(obj) in ctx.seen:
    raise RecursionError("Cycle detected")
ctx.seen.add(type(obj))
try:
    ...
finally:
    ctx.seen.discard(type(obj))
```

## Evaluation Flow

```
eval_typing(expr)
    ↓
_ensure_context() → creates EvalContext
    ↓
_eval_types_impl(expr, ctx)
    ↓
[dispatch based on type]
    ↓
Result (possibly cached)
```

## Thread Safety

Context uses `contextvars` for thread-local storage:

```python
import contextvars

_current_context: contextvars.ContextVar[EvalContext | None] = ...
```

This ensures each thread has its own evaluation context.

## Advanced Usage

### Custom Type Evaluation

To add support for custom types:

```python
from typemap.type_eval._eval_types_impl import _eval_types_impl

@_eval_types_impl.register
def _eval_my_type(obj: MyCustomType, ctx: EvalContext):
    """Handle MyCustomType evaluation."""
    # Custom logic
    return transformed_result
```

### Namespace Control

Pass custom namespaces for type resolution:

```python
ctx = EvalContext(ns={'MyType': MyType, 'Optional': Optional})
result = eval_typing(expr, ensure_context=False)
```
