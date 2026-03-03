# Testing Strategy for Type Helpers

This document outlines how to test the type helpers like Pick, Omit, Partial, and others.

---

## Overview

Testing types in PEP 827 involves two approaches:

1. **Runtime Evaluation** - Using `eval_typing` to verify computed types
2. **Static Type Checking** - Using mypy with `assert_type`

---

## Runtime Testing with eval_typing

### Basic Pattern

```python
from typemap.type_eval import eval_typing
from typemap import Attrs, NewProtocol, Member
from typing import Literal

# Define a helper type
type Pick[T, K] = NewProtocol[*[
    Member[p.name, p.type]
    for p in Iter[Attrs[T]]
    if IsAssignable[p.name, K]
]]

# Test it
class User:
    name: str
    email: str
    age: int

result = eval_typing(Pick[User, Literal['name', 'email']])
# Verify the result contains only name and email
```

### Test Structure

```python
# tests/test_helpers.py
from __future__ import annotations

import pytest
from typemap.type_eval import eval_typing
from typemap import (
    Attrs, Members, Iter, NewProtocol, Member,
    IsAssignable, GetMemberType,
)
from typemap_extensions import GetAnnotations, DropAnnotations
from typing import Literal


class User:
    name: str
    email: str
    age: int


class TestPick:
    """Test Pick type helper"""

    def test_pick_single_key(self):
        """Pick single key from class"""
        # Implementation
        type PickOne[T, K] = NewProtocol[*[
            Member[p.name, p.type]
            for p in Iter[Attrs[T]]
            if IsAssignable[p.name, K]
        ]]

        result = eval_typing(PickOne[User, Literal['name']])
        # Verify structure
        assert hasattr(result, '__annotations__')
        assert 'name' in result.__annotations__
        assert 'email' not in result.__annotations__
        assert 'age' not in result.__annotations__

    def test_pick_multiple_keys(self):
        """Pick multiple keys from class"""
        type PickMany[T, K] = NewProtocol[*[
            Member[p.name, p.type]
            for p in Iter[Attrs[T]]
            if IsAssignable[p.name, K]
        ]]

        result = eval_typing(PickMany[User, Literal['name', 'email']])
        # Verify only name and email
        assert 'name' in result.__annotations__
        assert 'email' in result.__annotations__
        assert 'age' not in result.__annotations__


class TestOmit:
    """Test Omit type helper"""

    def test_omit_single_key(self):
        """Omit single key from class"""
        type OmitOne[T, K] = NewProtocol[*[
            Member[p.name, p.type]
            for p in Iter[Attrs[T]]
            if not IsAssignable[p.name, K]
        ]]

        result = eval_typing(OmitOne[User, Literal['age']])
        assert 'name' in result.__annotations__
        assert 'email' in result.__annotations__
        assert 'age' not in result.__annotations__


class TestPartial:
    """Test Partial type helper"""

    def test_partial_makes_optional(self):
        """Partial makes all fields optional"""
        type Partial[T] = NewProtocol[*[
            Member[p.name, p.type | None, p.quals]
            for p in Iter[Attrs[T]]
        ]]

        result = eval_typing(Partial[User])
        # All types should be | None
        assert 'name' in result.__annotations__
        assert 'email' in result.__annotations__
        assert 'age' in result.__annotations__
```

---

## Static Testing with mypy

### Using assert_type

```python
from typing import assert_type, Callable, Literal

# Helper to test
type ReturnType[T] = GetArg[T, Callable, Literal[1]]

def my_func() -> str:
    ...

# mypy will verify this is correct
result: ReturnType[my_func]
assert_type(result, str)  # Error if wrong!
```

### Using reveal_type for debugging

```python
from typing import reveal_type

type MyType = int | str

x: MyType = 1
reveal_type(x)  # mypy shows: Revealed type is "int | str"
```

---

## Testing Edge Cases

### Empty Result

```python
def test_pick_no_keys(self):
    """Pick with no matching keys returns empty"""
    type PickNone[T, K] = NewProtocol[*[
        Member[p.name, p.type]
        for p in Iter[Attrs[T]]
        if IsAssignable[p.name, K]
    ]]

    result = eval_typing(PickNone[User, Literal['nonexistent']])
    # Should be empty or have no attrs
```

### All Keys

```python
def test_pick_all_keys(self):
    """Pick with all keys returns original"""
    result = eval_typing(Pick[User, Literal['name', 'email', 'age']])
    # Should have all three fields
```

### Union Keys

```python
def test_pick_with_union(self):
    """Pick works with union of keys"""
    Keys = Literal['name'] | Literal['email']
    result = eval_typing(Pick[User, Keys])
    # Should work
```

---

## Test Helpers Reference

### Common Fixtures

```python
# tests/conftest.py
import pytest

class SimpleClass:
    name: str
    age: int


class ClassWithMethods:
    name: str

    def greet(self) -> str:
        return f"Hello {self.name}"


class ClassWithDefaults:
    name: str = "unknown"
    age: int = 0


class ClassWithOptional:
    name: str | None
    age: int | None
```

### Import Reference

```python
# Standard imports for testing
from typemap.type_eval import eval_typing, EvalContext

# Type operators
from typemap import (
    Attrs, Members, Iter, GetMember, GetMemberType,
    NewProtocol, UpdateClass, Member, Param,
    IsAssignable, IsEquivalent, Bool,
    StrConcat, Uppercase, Lowercase, Capitalize,
    GetArg, GetArgs, GetAnnotations, DropAnnotations,
    Length, Slice,
)

# Extensions
from typemap_extensions import (
    GetDefault, GetFieldItem,
    Attrs, Members, Iter, GetMemberType,
    NewProtocol, Member,
)
```

---

## Running Tests

### Run all tests

```bash
uv run pytest tests/
```

### Run specific test file

```bash
pytest tests/test_helpers.py -v
```

### Run with coverage

```bash
uv run pytest tests/ --cov=typemap --cov-report=html
```

### Type check

```bash
uv run mypy typemap/ tests/
```

---

## Troubleshooting

### Issue: StuckException

```python
# This happens with unresolved TypeVars
type Stuck[T] = T  # Can't evaluate without concrete T

# Solution: Provide concrete types in tests
result = eval_typing(Stuck[int])  # Works!
```

### Issue: Runtime type differs from static type

```python
# Runtime evaluation may produce different results
# than static type checking

# Always verify with both: runtime + mypy
```

---

## References

- `tests/test_fastapilike_1.py` - Working examples
- `tests/test_type_eval.py` - Core operator tests
- `docs/testing_types.md` - General testing documentation
