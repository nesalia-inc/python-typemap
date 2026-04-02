# Type Operators

Type operators are classes that manipulate and transform types, inspired by TypeScript's utility types.

## Overview

Type operators in python-typemap are defined as special generic classes that:
- Accept type parameters via subscript syntax (e.g., `KeyOf[T]`)
- Are evaluated at runtime using `eval_typing()`
- Return transformed types

## Available Operators

### KeyOf[T]

Gets all keys/property names of a type as a tuple of Literals.

```python
import typemap_extensions as tm
from typemap import eval_typing

class User:
    name: str
    age: int

keys = eval_typing(tm.KeyOf[User])
# Result: tuple[Literal['name'], Literal['age']]
```

**Use cases:**
- Enum generation from data classes
- Dynamic form generation
- Generic key access utilities

---

### Partial[T]

Makes all fields of a type optional (each field becomes `T | None`).

```python
class User:
    name: str
    email: str

PartialUser = eval_typing(tm.Partial[User])
# Result: User with name: str | None, email: str | None
```

**Use cases:**
- Form inputs (all fields optional for creation)
- Update DTOs (only fields you want to update)
- PATCH API endpoints

---

### DeepPartial[T]

Recursively makes all nested fields optional.

```python
class Config:
    database: DatabaseConfig
    cache: CacheConfig

PartialConfig = eval_typing(tm.DeepPartial[Config])
# All fields at all levels become optional
```

---

### Pick[T, K]

Selects specific fields from a type.

```python
class User:
    name: str
    email: str
    password: str
    created_at: datetime

# Only public profile fields
PublicUser = eval_typing(tm.Pick[User, 'name' | 'email'])
```

**Use cases:**
- Public/private API responses
- Strip sensitive fields
- Create view models

---

### Omit[T, K]

Removes specific fields from a type.

```python
# Remove sensitive data
SafeUser = eval_typing(tm.Omit[User, 'password' | 'ssn'])
```

**Use cases:**
- Remove password from user responses
- Exclude internal fields from API output
- Sanitize data before logging

---

### Iter[T]

Iterates over type elements (e.g., union members, tuple elements, list items).

```python
type Status = 'pending' | 'active' | 'completed'

StatusType = eval_typing(tm.Iter[Status])
# Result: Literal['pending'] | Literal['active'] | Literal['completed']
```

**Use cases:**
- Union type iteration
- Tuple element access
- Generic sequence operations

---

### Attrs[T]

Gets type attributes as Member descriptors.

```python
class User:
    name: str
    age: int

attrs = eval_typing(tm.Attrs[User])
# Result: tuple[Member['name', str], Member['age', int]]
```

**Use cases:**
- ORM column introspection
- Form generation
- Schema extraction

---

### Param[T, N]

Gets the Nth parameter type of a callable.

```python
def greet(name: str, age: int) -> str:
    return f"Hello {name}"

FirstParam = eval_typing(tm.Param[greet, 0])
# Result: str

SecondParam = eval_typing(tm.Param[greet, 1])
# Result: int
```

---

### Return[T]

Gets the return type of a callable.

```python
ReturnType = eval_typing(tm.Return[greet])
# Result: str
```

---

### Required[T]

Makes all fields required (opposite of Partial).

```python
PartialUser = eval_typing(tm.Partial[User])
FullUser = eval_typing(tm.Required[PartialUser])
# Back to original User
```

---

### Readonly[T]

Makes all fields immutable.

```python
ImmutableUser = eval_typing(tm.Readonly[User])
# All fields become read-only
```

---

### NonOptional[T]

Removes None from optional fields.

```python
type MaybeUser = User | None

ConcreteUser = eval_typing(tm.NonOptional[MaybeUser])
# Result: User
```

---

### Flatten[T]

Flattens nested types.

```python
type Nested = int | tuple[int | tuple[int]]

Flat = eval_typing(tm.Flatten[Nested])
# Result: int
```

---

## Operator Composition

Operators can be composed for complex transformations:

```python
# Create a type with only non-sensitive, optional fields
PublicPartialUser = eval_typing(
    tm.Partial[
        tm.Omit[User, 'password' | 'ssn' | 'api_key']
    ]
)
```

## Custom Type Operators

You can create custom operators by extending the base classes:

```python
from typemap.typing import _TupleLikeOperator

class MyOperator[T](_TupleLikeOperator):
    """Custom type operator"""
    pass
```
