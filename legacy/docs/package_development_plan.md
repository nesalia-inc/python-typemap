# Package Development Plan

This document outlines the development plan for transforming the PEP 827 reference implementation into a reusable package.

---

## Status: Draft

Last updated: 2026-03-03

---

## Current State

### What's Already Done

- ✅ PEP 827 specification (`pep.rst`)
- ✅ Core type operators (`typemap/typing.py`)
- ✅ Runtime evaluator (`typemap/type_eval/`)
- ✅ Test suite (`tests/`)
- ✅ Documentation (`docs/`)

### What's Working

| Feature | Status | Location |
|---------|--------|----------|
| `Attrs[T]` | ✅ Working | `tests/test_type_eval.py` |
| `Members[T]` | ✅ Working | `tests/test_type_eval.py` |
| `Iter[T]` | ✅ Working | `tests/test_type_eval.py` |
| `NewProtocol[*Ms]` | ✅ Working | `tests/test_type_eval.py` |
| `UpdateClass[*Ms]` | ✅ Working | `tests/test_type_eval.py` |
| `IsAssignable[T, S]` | ✅ Working | `tests/test_type_eval.py` |
| `GetMemberType[T, K]` | ✅ Working | `tests/test_type_eval.py` |
| `GetArg[T, B, I]` | ✅ Working | `tests/test_type_eval.py` |
| `StrConcat[A, B]` | ✅ Working | `tests/test_type_eval.py` |
| `Uppercase[S]` | ✅ Working | `tests/test_type_eval.py` |

### Tested Helpers

| Helper | Status | Test |
|--------|--------|------|
| `Public[T]` | ✅ Working | `test_fastapi_like_1` |
| `Create[T]` | ✅ Working | `test_fastapi_like_2` |
| `Update[T]` | ✅ Working | `test_fastapi_like_3` |
| `AddInit[T]` | ✅ Working | `test_fastapi_like_4` |
| `PropsOnly[T]` | ✅ Working | In QB examples |
| `Pick[T, K]` | ✅ Working | Verified 2026-03-03 |
| `Omit[T, K]` | ✅ Working | Verified 2026-03-03 |
| `Partial[T]` | ✅ Working | Verified 2026-03-03 |
| `DeepPartial[T]` | ✅ Working (explicit) | Verified 2026-03-03 |

---

## Phase 1: Validate Key Filtering (TODO)

### Goal

Verify that filtering by key name works:
```python
type Pick[T, K] = NewProtocol[*[
    Member[p.name, p.type]
    for p in Iter[Attrs[T]]
    if IsAssignable[p.name, K]  # Does this work?
]]
```

### Tasks

1. Write test in `tests/test_helpers.py`:
   ```python
   def test_pick_by_key():
       class User:
           name: str
           email: str
           age: int

       type Pick[T, K] = ...

       result = eval_typing(Pick[User, Literal['name', 'email']])
       # Verify name and email, exclude age
   ```

2. Run test and see if it passes

3. If it fails, investigate and document limitation

---

## Phase 2: Implement Standard Helpers (Next)

After validation, implement these helpers:

### Required Helpers (ALL TESTED AND WORKING!)

```python
# Pick - select specific keys
# Status: WORKS!
type Pick[T, K] = NewProtocol[*[
    Member[p.name, p.type]
    for p in Iter[Attrs[T]]
    if IsAssignable[p.name, K]
]]

# Omit - exclude specific keys
# Status: WORKS!
type Omit[T, K] = NewProtocol[*[
    Member[p.name, p.type]
    for p in Iter[Attrs[T]]
    if not IsAssignable[p.name, K]
]]

# Partial - make all fields optional
# Status: WORKS!
type Partial[T] = NewProtocol[*[
    Member[p.name, p.type | None, p.quals]
    for p in Iter[Attrs[T]]
]]

# DeepPartial - make all nested fields optional
# Status: NOT POSSIBLE as pure type alias (see below)
#
# DeepPartial CANNOT be built as a pure type alias because Python
# does not allow recursion in type aliases.
#
# Solution 1: Runtime function (works)
#   - See typemap_experiment/deeppartial.py
#
# Solution 2: Manual explicit recursion (verbose but works)
type DeepPartial_User = NewProtocol[*[
    Member[
        p.name,
        DeepPartial_Address | None if p.name == Literal['address']
        else p.type | None,
        p.quals
    ]
    for p in Iter[Attrs[User]]
]]

# Solution 3: New operator in typemap (requires core modification)
```

### Utility Helpers

```python
# ReturnType - extract return type from Callable
type ReturnType[T] = GetArg[T, Callable, Literal[1]]

# Parameters - extract parameter types
type Parameters[T] = GetArg[T, Callable, Literal[0]]

# ArrayElement - extract element type from list[T]
type ArrayElement[T] = GetArg[T, list, Literal[0]]

# DictValue - extract value type from dict[K, V]
type DictValue[T] = GetArg[T, dict, Literal[1]]

# KeyOf - get all keys as union (already exists conceptually)
# Note: Not directly available, needs different approach
```

---

## Phase 3: Package Structure

### Recommended Structure

```
typemap/
├── __init__.py           # Public API exports
├── typing.py             # Core type definitions
├── operators.py          # String operators (StrConcat, etc.)
├── runtime/              # Runtime evaluator
│   ├── __init__.py
│   ├── eval.py
│   └── errors.py
├── helpers/              # Standard helpers (Pick, Omit, etc.)
│   ├── __init__.py
│   ├── transforms.py     # Pick, Omit, Partial
│   ├── extraction.py     # ReturnType, Parameters
│   └── strings.py        # String helpers
└── _internal/            # Private APIs

docs/                    # User documentation
tests/                   # Test suite
scripts/                 # Build/utility scripts
```

### API Surface

```python
# typemap/__init__.py
from typemap.typing import (
    # Core operators
    Attrs, Members, Iter,
    GetMember, GetMemberType,
    GetArg, GetArgs,
    NewProtocol, UpdateClass,
    Member, Param,
    IsAssignable, IsEquivalent, Bool,
    StrConcat, Uppercase, Lowercase, Capitalize,
    GetAnnotations, DropAnnotations,
    Length, Slice,
)

# Standard helpers
from typemap.helpers import (
    Pick, Omit, Partial, Required,
    ReturnType, Parameters,
    ArrayElement, DictValue,
)
```

---

## Phase 4: Testing

### Test Coverage Goals

- [ ] Unit tests for each helper
- [ ] Integration tests (combining helpers)
- [ ] Edge case tests (empty, union, etc.)
- [ ] Property-based tests with Hypothesis

### Test Files

```
tests/
├── test_operators.py      # Core operator tests
├── test_helpers.py        # Pick, Omit, Partial
├── test_extraction.py     # ReturnType, Parameters
├── test_integration.py   # Combined helpers
└── test_edge_cases.py    # Edge cases
```

---

## Phase 5: Documentation

### Required Documentation

1. **API Reference** - Auto-generated from docstrings
2. **Getting Started** - Basic usage tutorial
3. **Migration Guide** - From TypeScript to Python
4. **Examples** - Real-world use cases

### Documentation Files

```
docs/
├── index.md              # Main documentation
├── getting_started.md    # Installation and basic usage
├── api_reference.md     # Full API documentation
├── examples.md          # Real-world examples
├── migration.md         # TypeScript migration guide
└── testing.md           # Testing guide
```

---

## Phase 6: Release

### Version 1.0.0 Checklist

- [ ] All core operators tested
- [ ] Standard helpers implemented
- [ ] Documentation complete
- [ ] CI/CD configured
- [ ] PyPI package created

### Dependencies

```toml
[project]
name = "typemap"
version = "1.0.0"
requires-python = ">=3.14"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov",
    "mypy>=1.10",
    "ruff",
    "hypothesis",
]
docs = [
    "mkdocs",
    "mkdocstrings",
]
```

---

## Open Questions

1. **Package name**: Keep as `typemap` or rename?
2. **Python version support**: 3.14 only or backport with `typing_extensions`?
3. **Breaking change policy**: How long to maintain backward compatibility?
4. **License**: MIT, Apache 2, or other?

---

## References

- `docs/implementation_analysis.md` - Detailed analysis
- `docs/helpers_testing_strategy.md` - Testing strategy
- `docs/testing_types.md` - General testing guide
- `pep.rst` - PEP 827 specification
