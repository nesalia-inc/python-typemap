# Implementation Analysis - What Works and What's Unknown

This document captures the analysis of what has been tested and what remains to be validated for implementing type helpers like Pick, Omit, and Partial.

---

## Status: Work in Progress

Last updated: 2026-03-03

---

## 1. Tested and Working Helpers

The following helpers are already implemented and tested in the test suite:

### Public[T] - Keeps certain fields based on annotations

```python
# From tests/test_fastapilike_1.py
type Public[T] = NewProtocol[
    *[
        Member[p.name, FixPublicType[p.type], p.quals]
        for p in Iter[Attrs[T]]
        if not IsAssignable[Literal[PropQuals.HIDDEN], GetAnnotations[p.type]]
    ]
]
```

**Test:** `test_fastapi_like_1` ✅ Works

---

### Create[T] - Excludes primary key

```python
# From tests/test_fastapilike_1.py
type Create[T] = NewProtocol[
    *[
        Member[p.name, p.type, p.quals]
        for p in Iter[Attrs[T]]
        if not IsAssignable[Literal[PropQuals.PRIMARY], GetAnnotations[p.type]]
    ]
]
```

**Test:** `test_fastapi_like_2` ✅ Works

---

### Update[T] - Makes all fields optional with None defaults

```python
# From tests/test_fastapilike_1.py
type Update[T] = NewProtocol[
    *[
        Member[
            p.name,
            HasDefault[DropAnnotations[p.type] | None, None],
            p.quals,
        ]
        for p in Iter[Attrs[T]]
        if not IsAssignable[Literal[PropQuals.PRIMARY], GetAnnotations[p.type]]
    ]
]
```

**Test:** `test_fastapi_like_3` ✅ Works

---

### AddInit[T] - Adds __init__ method

```python
# From tests/test_fastapilike_1.py
type AddInit[T] = NewProtocol[
    InitFnType[T],
    *Members[T],
]
```

**Test:** `test_fastapi_like_4` ✅ Works

---

## 2. Base Filtering Pattern

The core pattern for filtering is:

```python
type Filtered[T] = NewProtocol[*[
    Member[p.name, p.type]
    for p in Iter[Attrs[T]]
    if <condition>
]]
```

### Available Conditions

#### Filter by annotation (TESTED - WORKS)

```python
if not IsAssignable[Literal[PropQuals.HIDDEN], GetAnnotations[p.type]]
if not IsAssignable[Literal[PropQuals.PRIMARY], GetAnnotations[p.type]]
```

#### Filter by type (TESTED - WORKS)

```python
# From test_fastapilike_1.py line 79
type NotOptional[T] = Union[
    *[x for x in Iter[FromUnion[T]] if not IsAssignable[x, None]]
]
```

#### Filter by key name (NOT TESTED - UNKNOWN)

```python
# THIS PATTERN IS NOT TESTED YET
type Pick[T, K] = NewProtocol[*[
    Member[p.name, p.type]
    for p in Iter[Attrs[T]]
    if IsAssignable[p.name, K]  # Can we filter by key name?
]]
```

---

## 3. Lifting Over Unions (PEP 785-810)

According to the PEP, operations are "lifted" over union types:

> When an operation is lifted over union types, we take the cross product of the union elements for each argument position, evaluate the operator for each tuple in the cross product, and then union all of the results together.

**Example from PEP:**

```python
Concat[Literal['a'] | Literal['b'], Literal['c'] | Literal['d']]
# =
Literal['ac'] | Literal['ad'] | Literal['bc'] | Literal['bd']
```

### Implication for Key Filtering

If `IsAssignable` is lifted over unions, then:

```python
IsAssignable[Literal['name'], Literal['name' | 'email']]
```

Should evaluate as:
- `IsAssignable[Literal['name'], Literal['name']]` → `True`
- `IsAssignable[Literal['name'], Literal['email']]` → `False`

Result: `True | False` → `True`

So theoretically, the pattern should work!

---

---

## 5. What's Working (TESTED - 2026-03-03)

### Pick[T, K] ✅ WORKS

```python
type Pick[T, K] = NewProtocol[*[
    Member[p.name, p.type]
    for p in Iter[Attrs[T]]
    if IsAssignable[p.name, K]
]]
```

**Verified:** `Pick[User, Literal['name', 'email']]` returns `{'name': str, 'email': str}`

---

### Omit[T, K] ✅ WORKS

```python
type Omit[T, K] = NewProtocol[*[
    Member[p.name, p.type]
    for p in Iter[Attrs[T]]
    if not IsAssignable[p.name, K]
]]
```

**Verified:** `Omit[User, Literal['age']]` returns `{'name': str, 'email': str}`

---

### Partial[T] ✅ WORKS

```python
type Partial[T] = NewProtocol[*[
    Member[p.name, p.type | None, p.quals]
    for p in Iter[Attrs[T]]
]]
```

**Verified:** `Partial[User]` returns `{'name': str | None, 'email': str | None, 'age': int | None}`

---

### DeepPartial[T] - ANALYSIS

#### What Works

We can detect if a type is complex using:

```python
type IsComplex[T] = not IsAssignable[Length[Attrs[T]], Literal[0]]

# Results:
IsComplex[str]     # → False (primitive!)
IsComplex[User]   # → True (has attributes!)
```

#### The Fundamental Limitation

Python **does not allow recursion** in type aliases:

```python
# This DOES NOT WORK:
type DeepPartial[T] = NewProtocol[*[
    Member[
        p.name,
        DeepPartial[p.type] | None if IsComplex[p.type]  # ← Cannot reference DeepPartial!
        else p.type | None
    ]
    for p in Iter[Attrs[T]]
]]
```

**Error:** `NameError: cannot reference 'DeepPartial' in its own definition`

#### Solutions

1. **Runtime function** (works - see `typemap_experiment/deeppartial.py`)
2. **Manual explicit recursion** (works but verbose)
3. **New DeepPartial operator** (requires modifying typemap core)

#### What We Can Build

| Helper | Status |
|--------|--------|
| `Partial[T]` | ✅ Works - top-level only |
| `Pick[T, K]` | ✅ Works |
| `Omit[T, K]` | ✅ Works |
| `IsComplex[T]` | ✅ Works (detection only) |
| `DeepPartial[T]` | ❌ Impossible as pure type alias |

#### Conclusion

DeepPartial as a pure type alias is **not possible** with current Python type system. This is a fundamental limitation of Python's type aliases, not a limitation of PEP 827 operators.

---

## Comprehensive Feature Analysis

### What WORKS with PEP 827 Primitives

| Feature | TypeScript | PEP 827 | Verified |
|---------|-----------|---------|---------|
| Recursive classes | `type List<T> = { value: T; next: List<T> }` | Via class definition | ✅ |
| Self/ThisType | `this` + `ThisType` | Standard Python `Self` | ✅ |
| Pick[T, K] | `Pick<T, 'name'>` | Works | ✅ |
| Omit[T, K] | `Omit<T, 'id'>` | Works | ✅ |
| Partial[T] | `Partial<T>` | Works | ✅ |
| GetMemberType | `T['key']` | `GetMemberType[T, 'key']` | ✅ |
| GetArg | infer keyword | `GetArg[T, Callable, 1]` | ✅ |
| String ops | `Uppercase<T>` | `StrConcat`, `Uppercase` | ✅ |
| Conditional | `T extends U ? X : Y` | `X if IsAssignable[T, U] else Y` | ✅ |
| IsComplex detection | Manual | `IsAssignable[Length[Attrs[T]], Literal[0]]` | ✅ |
| KeyOf | `keyof T` | `KeyOf[T]` | ✅ IMPLEMENTED! |

### What DOES NOT WORK

| Feature | TypeScript | PEP 827 | Reason |
|---------|-----------|---------|--------|
| DeepPartial | Auto recursive | ❌ | No recursion in type aliases |
| Template literal | `` `${T}` `` | ✅ | Works via typemap_experiment |

### Key Insights

1. **Most TypeScript utility types work**: Pick, Omit, Partial all work
2. **Recursion is the main limitation**: DeepPartial requires features Python doesn't have
3. **Detection works**: We can detect complex vs primitive types using `Length[Attrs[T]]`
4. **Runtime functions needed**: For automatic DeepPartial, use runtime function (see `typemap_experiment/deeppartial.py`)
5. **Template literals work**: Template[*Parts] concatenates string literals (see `typemap_experiment/template.py`)

---

## KeyOf Implementation (2026-03-03)

We implemented `KeyOf[T]` in typemap:

### Usage

```python
from typemap.typing import KeyOf
from typemap.type_eval import eval_typing

class User:
    name: str
    email: str
    age: int

# Get all keys as tuple of Literals
keys = eval_typing(KeyOf[User])
# Returns: (Literal['name'], Literal['email'], Literal['age'])
```

### Implementation

Added to:
- `typemap/typing.py` - KeyOf class definition
- `typemap/type_eval/_eval_operators.py` - _eval_KeyOf function

---

## Template Implementation (2026-03-03)

We implemented `Template[*Parts]` in typemap_experiment:

### Usage

```python
from typemap_experiment.template import Template
from typemap.type_eval import eval_typing
from typing import Literal
import typemap_experiment.template  # Register evaluator

# Simple concatenation
type Route = Template[Literal['/api/'], Literal['users']]
result = eval_typing(Route)
# Returns: Literal['/api/users']

# With type variables
Resource = Literal['posts']
type DynamicRoute = Template[Literal['/api/'], Resource]
result = eval_typing(DynamicRoute)
# Returns: Literal['/api/posts']
```

### Limitations

- Template parts must be string Literals or type aliases that evaluate to string Literals
- Does not work with `KeyOf[T]` because KeyOf returns a tuple of Literals, not a single string
- For dynamic use cases, use the runtime function `template()` from `typemap_experiment.template`

### Implementation

Added to:
- `typemap_experiment/typing.py` - Template class definition
- `typemap_experiment/template.py` - _eval_Template evaluator + runtime helper functions

### Files

- `typemap_experiment/template.py` - Contains both the evaluator and convenience runtime functions
- `typemap_experiment/typing.py` - Template class definition

---

## 6. What's Tested and Working

---

## 5. Next Steps

### To Validate

1. **Write a test** to verify key filtering works:
   ```python
   def test_pick_by_key_name():
       class User:
           name: str
           email: str
           age: int

       # This should only keep 'name' and 'email'
       type PickUserNameEmail = Pick[User, Literal['name', 'email']]
       result = eval_typing(PickUserNameEmail)
       # Verify it only has name and email
   ```

2. **If it works** → Implement Pick, Omit, Partial
3. **If it doesn't work** → Document limitation

---

## 6. Related Files

- `tests/test_fastapilike_1.py` - Working examples of Public, Create, Update, AddInit
- `tests/test_type_eval.py` - Core operator tests
- `pep.rst` - PEP 827 specification

---

## 7. Quick Reference

### Type Operators Used

| Operator | Purpose |
|----------|---------|
| `Attrs[T]` | Get attribute members of a class |
| `Members[T]` | Get all members including methods |
| `Iter[T]` | Iterate over a tuple type |
| `NewProtocol[*Ms]` | Create a new protocol type |
| `Member[N, T, Q, I, D]` | Define a member with name, type, qualifiers, init, definer |
| `IsAssignable[T, S]` | Check if T is assignable to S |
| `GetAnnotations[T]` | Get annotations from a type |
| `GetMemberType[T, 'name']` | Get type of a specific member |

### Filtering Conditions

```python
# Filter by annotation type
if not IsAssignable[Literal[HIDDEN], GetAnnotations[p.type]]

# Filter by member type
if not IsAssignable[p.type, None]

# Filter by key name (UNTESTED)
if IsAssignable[p.name, K]
```

---

*This document is a working analysis. Update as we learn more.*
