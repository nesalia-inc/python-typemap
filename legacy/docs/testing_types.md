# Testing Typemap Types

This document describes the strategies and tools available for testing types in typemap.

---

## Overview

Testing types in typemap involves two different approaches:

1. **Runtime Evaluation** - Testing that type computations produce expected results at runtime
2. **Static Type Checking** - Testing that type annotations are correct using mypy/pyright

---

## 1. Runtime Evaluation

### Using `eval_typing`

The main tool for runtime type evaluation is `eval_typing`:

```python
from typemap.type_eval import eval_typing
from typemap import Attrs, Iter, Member, NewProtocol

# Define a type alias
type MyType = int | str

# Evaluate it at runtime
result = eval_typing(MyType)
# Returns: union of int and str
```

### Complete Example

```python
from typemap.type_eval import eval_typing
from typemap import Attrs, Member, NewProtocol

# Define a class
class User:
    name: str
    age: int
    email: str = "unknown"

# Evaluate Attrs[User]
attrs_result = eval_typing(Attrs[User])
# Returns tuple of Member types

# Evaluate a derived type
type PublicUser = NewProtocol[
    *[Member[p.name, p.type] for p in eval_typing(Attrs[User])]
]

public_result = eval_typing(PublicUser)
```

### Available Test Utilities

```python
from typemap.type_eval import eval_typing, EvalContext
from typemap_extensions import (
    Attrs, Members, Iter, GetMemberType,
    NewProtocol, Member, GetArg, StrConcat,
)
```

---

## 2. Static Type Checking

### Using mypy

The project uses mypy for static type checking:

```bash
# Run mypy
uv run mypy typemap/ tests/

# Run with specific options
uv run mypy --strict typemap/
```

### Type Testing Pattern

To test that a type produces the expected result, use `assert_type` (Python 3.11+):

```python
from typing import assert_type

type MyPick[T, K] = ...

class User:
    name: str
    age: int

# This will be checked by mypy
result: MyPick[User, 'name']
assert_type(result, ???)  # Should be what MyPick produces
```

---

## 3. Test Structure

### Unit Tests

```python
# tests/test_my_types.py
from __future__ import annotations

import pytest
from typemap.type_eval import eval_typing
from typemap import Attrs, Members, Iter, Member, NewProtocol
from typemap_extensions import GetMemberType, GetArg, StrConcat

class TestAttrs:
    def test_attrs_basic_class(self):
        class User:
            name: str
            age: int

        result = eval_typing(Attrs[User])
        # Check result structure
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_attrs_with_methods(self):
        class User:
            name: str

            def greet(self) -> str:
                return f"Hello {self.name}"

        # Attrs should only return attributes, not methods
        result = eval_typing(Attrs[User])
        assert len(result) == 1


class TestGetMemberType:
    def test_get_member_type(self):
        class User:
            name: str

        result = eval_typing(GetMemberType[User, Literal['name']])
        assert result == str


class TestStrConcat:
    def test_concat(self):
        result = eval_typing(StrConcat['hello', 'world'])
        assert result == 'helloworld'

    def test_concat_uppercase(self):
        from typemap_extensions import Uppercase, Capitalize

        result = eval_typing(StrConcat['hello', Uppercase['world']])
        assert result == 'helloWORLD'
```

### Integration Tests

```python
# tests/test_fastapilike.py
from __future__ import annotations

from typemap import Attrs, Iter, Member, NewProtocol
from typemap_extensions import GetDefault, GetFieldItem, IsAssignable
from typing import Literal, Field

def test_create_type():
    """Test that Create type excludes primary_key"""
    class User:
        id: int = Field(primary_key=True)
        name: str
        email: str = "unknown"

    # Evaluate Create[User]
    # Should exclude 'id' and keep 'name', 'email'
    result = eval_typing(Create[User])
    # Verify structure
```

---

## 4. Testing Patterns

### Pattern 1: Direct Evaluation

```python
def test_type_evaluation():
    """Test that a type alias evaluates correctly"""
    type MyUnion = int | str

    result = eval_typing(MyUnion)
    assert result == int | str
```

### Pattern 2: Class Member Testing

```python
def test_class_members():
    """Test Attrs and Members operators"""
    class User:
        name: str
        age: int

        def greet(self) -> str: ...

    # Attrs - only instance attributes
    attrs = eval_typing(Attrs[User])
    assert len(attrs) == 2  # name, age

    # Members - all members including methods
    members = eval_typing(Members[User])
    assert len(members) == 3  # name, age, greet
```

### Pattern 3: Protocol Construction

```python
def test_new_protocol():
    """Test NewProtocol creates expected structure"""
    type SimpleProtocol = NewProtocol[
        Member['name', str],
        Member['age', int],
    ]

    result = eval_typing(SimpleProtocol)
    # Verify it's a Protocol with expected members
```

### Pattern 4: Conditional Types

```python
def test_conditional():
    """Test conditional type evaluation"""
    type Maybe[T] = T if IsAssignable[T, str] else str

    # When T = str
    result_str = eval_typing(Maybe[str])
    assert result_str == str

    # When T = int (not assignable to str)
    result_int = eval_typing(Maybe[int])
    assert result_int == str
```

---

## 5. Mypy Integration

### Using `reveal_type`

For debugging type inference, use `reveal_type`:

```python
from typing import reveal_type

type MyType = int | str
x: MyType = 1
reveal_type(x)  # mypy will show: Revealed type is "int | str"
```

### Using `assert_type`

Verify type checker understanding:

```python
from typing import assert_type

type PickTwo[T] = ...  # Pick first two fields

class User:
    name: str
    age: int
    email: str

result = PickTwo[User, 'name' | 'age']
assert_type(result, ???)  # Should be { name: str, age: int }
```

### Custom Mypy Plugins

For advanced type testing, you may need custom mypy plugins. See the mypy documentation for plugin development.

---

## 6. Test Utilities Reference

### Evaluation Functions

```python
# Core evaluation
from typemap.type_eval import eval_typing, EvalContext

# With context
ctx = EvalContext()
result = eval_typing(MyType, ctx=ctx)
```

### Test Helpers

```python
# Common imports for testing
from typemap import (
    Attrs, Members, Iter, GetMember, GetMemberType,
    NewProtocol, NewTypedDict, UpdateClass,
    Member, Param,
    IsAssignable, IsEquivalent, Bool,
)

from typemap_extensions import (
    GetArg, GetArgs, GetDefault, GetFieldItem,
    StrConcat, Uppercase, Lowercase, Capitalize,
    GetAnnotations, DropAnnotations,
    Length, Slice,
)
```

---

## 7. Running Tests

### Run All Tests

```bash
# Using uv
uv run pytest tests/

# Using pytest directly
pytest tests/
```

### Run Specific Test File

```bash
pytest tests/test_type_eval.py -v
```

### Run with Coverage

```bash
uv run pytest tests/ --cov=typemap --cov-report=html
```

### Type Check

```bash
# Full type checking
uv run mypy typemap/ tests/

# Strict mode
uv run mypy --strict typemap/
```

---

## 8. Best Practices

### DO

1. **Test runtime evaluation first** - Use `eval_typing` to verify computed types
2. **Test edge cases** - Empty types, unions, nested types
3. **Use clear assertions** - Verify exact structure of results
4. **Test both success and failure cases**

### DON'T

1. **Don't assume mypy will catch everything** - Runtime evaluation catches bugs
2. **Don't skip integration tests** - Test how types work together
3. **Don't forget to test updates** - When changing type operators

---

## 9. Example: Full Test

```python
# tests/test_example.py
from __future__ import annotations

import pytest
from typemap.type_eval import eval_typing
from typemap import Attrs, Member, NewProtocol
from typemap_extensions import StrConcat, Uppercase, Capitalize


class TestStringOperations:
    """Test string type operations"""

    def test_str_concat(self):
        """Test basic string concatenation"""
        result = eval_typing(StrConcat['hello', 'world'])
        assert result == 'helloworld'

    def test_str_concat_uppercase(self):
        """Test concatenation with uppercase"""
        result = eval_typing(StrConcat['hello', Uppercase['world']])
        assert result == 'helloWORLD'

    def test_str_concat_capitalize(self):
        """Test concatenation with capitalize"""
        result = eval_typing(StrConcat[Capitalize['hello'], 'world'])
        assert result == 'Helloworld'


class TestProtocolConstruction:
    """Test NewProtocol"""

    def test_simple_protocol(self):
        """Test creating a simple protocol"""
        type Simple = NewProtocol[
            Member['name', str],
            Member['age', int],
        ]

        result = eval_typing(Simple)
        # Verify it's a protocol-like structure
        assert result is not None


class TestAttrs:
    """Test Attrs operator"""

    def test_simple_class(self):
        """Test Attrs on a simple class"""
        class User:
            name: str
            age: int

        result = eval_typing(Attrs[User])
        assert isinstance(result, tuple)
        assert len(result) == 2
```

---

## 10. Troubleshooting

### Common Issues

**Issue: `StuckException` during evaluation**

```python
# This happens with unresolved TypeVars
# Solution: Provide concrete types in tests

type Stuck[T] = T  # Can't evaluate without concrete T

# Test with concrete type
result = eval_typing(Stuck[int])  # Works!
```

**Issue: Runtime type differs from static type**

```python
# Runtime evaluation may produce different results
# than static type checking

# Always verify with both: runtime + mypy
```

---

## References

- [Python typing module documentation](https://docs.python.org/3/library/typing.html)
- [mypy documentation](https://mypy.readthedocs.io/)
- [pytest documentation](https://docs.pytest.org/)

---

*Last updated: 2026-03-02*
