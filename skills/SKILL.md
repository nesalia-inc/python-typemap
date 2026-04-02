---
name: python-typemap
description: Python 3.14+ type manipulation library inspired by TypeScript. Use when working with type-level operations, evaluating type expressions at runtime, or when asked about PEP 827 type operators. Supports type introspection, transformation, and runtime type evaluation.
disable-model-invocation: false
allowed-tools: Read,Grep,Glob,Bash
---

# Python Typemap Skill

A skill for working with python-typemap - a PEP 827 type manipulation library for Python 3.14+.

## Quick Usage

```python
from typemap import eval_typing
import typemap_extensions as tm

# Get type operators
tm.KeyOf[T]      # TypeScript's keyof
tm.Partial[T]    # Make fields optional
tm.Pick[T, K]    # Select fields
tm.Omit[T, K]    # Exclude fields
tm.Iter[T]       # Iterate over type
tm.Attrs[T]      # Get type attributes
```

## What is python-typemap?

Python-typemap brings **TypeScript-inspired type operators** to Python. It provides:

- **Type Operators**: `Member`, `KeyOf`, `Partial`, `Pick`, `Omit`, `Iter`, `Attrs`, etc.
- **Runtime Evaluation**: `eval_typing()` evaluates type expressions at runtime
- **Type Introspection**: Inspect and transform types programmatically

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Type Operators** | Classes that manipulate types (like TypeScript's utility types) |
| **Member** | Access type members with name, type, and qualifiers |
| **EvalContext** | Context for tracking resolved types during evaluation |
| **Singledispatch** | Pattern for handling different type implementations |

## Key Type Operators

| Operator | Purpose | Example |
|----------|---------|---------|
| `KeyOf[T]` | Get all keys of a type | `KeyOf[User]` → `tuple[Literal['name'], Literal['age']]` |
| `Partial[T]` | Make all fields optional | `Partial[User]` → all fields `\| None` |
| `Pick[T, K]` | Select specific fields | `Pick[User, 'name']` → only `name` field |
| `Omit[T, K]` | Remove specific fields | `Omit[User, 'password']` → without password |
| `Iter[T]` | Iterate over type elements | `Iter[list[int]]` → `int` |
| `Attrs[T]` | Get type attributes | `Attrs[User]` → tuple of Member descriptors |
| `Param[T, N]` | Get Nth parameter | `Param[func, 0]` → first param type |
| `Return[T]` | Get return type | `Return[func]` → function return type |
| `Required[T]` | Make all fields required | `Required[Partial[User]]` → revert Partial |
| `Readonly[T]` | Make fields immutable | `Readonly[User]` → immutable fields |

## Runtime Evaluation

The `eval_typing()` function evaluates type expressions at runtime:

```python
from typemap import eval_typing
import typemap_extensions as tm

class User:
    name: str
    age: int

# Get keys of User
keys = eval_typing(tm.KeyOf[User])
# Result: tuple[Literal['name'], Literal['age']]

# Make User partial
PartialUser = eval_typing(tm.Partial[User])
# Result: User with all fields optional
```

## Additional Resources

For detailed information on each feature:

- [type-operators.md](python-typemap/type-operators.md) - All type operators explained
- [runtime-evaluation.md](python-typemap/runtime-evaluation.md) - How eval_typing works
- [member.md](python-typemap/member.md) - Member type descriptor
- [patterns.md](python-typemap/patterns.md) - Common usage patterns
- [examples.md](python-typemap/examples.md) - Practical examples
- [internals.md](python-typemap/internals.md) - Architecture and internals
- [errors.md](python-typemap/errors.md) - Error handling
