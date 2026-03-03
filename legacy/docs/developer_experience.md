# typemap Developer Experience - Final Vision

This document describes the ideal developer experience for using typemap, focusing on the public API and usage patterns. No implementation details are included.

---

## Philosophy

The typemap package should feel:

1. **Natural** - Uses familiar Python typing syntax
2. **Minimal** - Simple imports, clean API
3. **Powerful** - Enable TypeScript-like type manipulation
4. **Safe** - Clear errors, predictable behavior

---

## Installation

```bash
pip install typemap
```

---

## Basic Usage

### Imports

```python
from typemap import (
    # Type utilities
    Pick,
    Omit,
    Partial,
    Required,
    KeyOf,

    # Type introspection
    Attrs,
    Members,
    GetMemberType,

    # Type evaluation
    eval_typing,
)
```

---

## Type Utilities

### KeyOf - Extract Keys from a Type

```python
from typemap import KeyOf

class User:
    name: str
    email: str
    age: int

# Get all keys as a union of literals
type UserKeys = KeyOf[User]
# Equivalent to: Literal['name', 'email', 'age']
```

### Pick - Select Properties

```python
from typemap import Pick

class User:
    name: str
    email: str
    age: int

# Select only specific properties
type UserNameAndEmail = Pick[User, 'name' | 'email']
# Equivalent to: { name: str; email: str }
```

### Omit - Exclude Properties

```python
from typemap import Omit

class User:
    id: int
    name: str
    email: str
    password: str

# Exclude sensitive fields
type PublicUser = Omit[User, 'id' | 'password']
# Equivalent to: { name: str; email: str }
```

### Partial - Make All Properties Optional

```python
from typemap import Partial

class User:
    name: str
    email: str
    age: int

# All properties become optional
type PartialUser = Partial[User]
# Equivalent to: { name?: str | None; email?: str | None; age?: int | None }
```

### Required - Make All Properties Required

```python
from typemap import Required, Partial

# Inverse of Partial
type RequiredUser = Required[Partial[User]]
# All None | optional types become required
```

---

## TypedDict Support

typemap works seamlessly with Python's native `TypedDict` from the `typing` module. All TypedDict features are supported out of the box.

### Basic TypedDict

```python
from typing import TypedDict  # Native Python

class User(TypedDict):
    name: str
    email: str
    age: int
```

### Required and NotRequired

```python
from typing import TypedDict, Required, NotRequired  # Native Python

class User(TypedDict):
    name: str                    # required by default
    email: Required[str]         # explicitly required
    age: NotRequired[int]        # optional field
    bio: NotRequired[str]        # optional field
```

### total=False (All Optional)

```python
from typing import TypedDict  # Native Python

class PartialUser(TypedDict, total=False):
    name: str
    email: str
    age: int
```

### ReadOnly Fields

```python
from typing import TypedDict, ReadOnly  # Native Python

class User(TypedDict):
    id: ReadOnly[int]            # Cannot be modified
    name: str
    email: str
```

### Closed TypedDict (No Extra Keys)

```python
from typing import TypedDict  # Native Python (3.13+)

class StrictUser(TypedDict, closed=True):
    name: str
```

### Extra Items

```python
from typing import TypedDict, ReadOnly  # Native Python (3.13+)

class FlexibleUser(TypedDict, extra_items=str):
    name: str

class FlexibleReadOnlyUser(TypedDict, extra_items=ReadOnly[int]):
    name: str
```

### Generic TypedDict

```python
from typing import TypedDict, Generic, TypeVar  # Native Python

T = TypeVar('T')

class Response(TypedDict, Generic[T]):
    status: int
    payload: T
```

---

## Using typemap with TypedDict

typemap utilities work seamlessly with native TypedDict:

### Pick and Omit with TypedDict

```python
from typing import TypedDict
from typemap import Pick, Omit

class User(TypedDict):
    id: int
    name: str
    email: str
    password: str

# Works with TypedDict
type UserCreate = Omit[User, 'id']  # Exclude id
type PublicUser = Pick[User, 'id' | 'name' | 'email']  # Select public fields
type SensitiveUser = Omit[User, 'password'>  # Remove sensitive data
```

### KeyOf with TypedDict

```python
from typing import TypedDict
from typemap import KeyOf

class User(TypedDict):
    name: str
    email: str
    age: int

# Get all keys as union
type UserKeys = KeyOf[User]
# Equivalent to: Literal['name', 'email', 'age']
```

### Partial with TypedDict

```python
from typing import TypedDict
from typemap import Partial

class User(TypedDict):
    name: str
    email: str

# Make all fields optional
type PartialUser = Partial[User]
# { name?: str | None; email?: str | None }
```

### Combined Patterns

```python
from typing import TypedDict
from typemap import Pick, Omit, Partial

class User(TypedDict):
    id: int
    name: str
    email: str
    password: str
    created_at: str

# API response types
type UserResponse = Pick[User, 'id' | 'name' | 'email'>

# Creation type (no id, no timestamps)
type UserCreate = Omit[User, 'id' | 'created_at'>

# Update type (all optional)
type UserUpdate = Partial[User]

# Public profile (no sensitive data)
type PublicProfile = Omit[User, 'password' | 'created_at'>
```

---

## Type Introspection

### TypedDict with Inheritance

```python
from typemap import TypedDict

class BaseUser(TypedDict):
    name: str
    email: str

class ExtendedUser(BaseUser):
    age: int
    # Inherits 'name' and 'email'
```

### Generic TypedDict

```python
from typemap import TypedDict, Generic, TypeVar

T = TypeVar('T')

class Response(TypedDict, Generic[T]):
    status: int
    payload: T
```

### Combining with Pick, Omit, Partial

```python
from typemap import TypedDict, Pick, Omit, Partial, Required

class User(TypedDict):
    id: int
    name: str
    email: str
    password: str

# Create different views
type UserCreate = Omit[User, 'id'>                # Exclude id
type UserResponse = Pick[User, 'id' | 'name' | 'email'>  # Public fields
type UserUpdate = Partial[User]                     # All optional
type PrivateUser = Omit[User, 'password'>          # Without password
```

---

## Type Introspection

### Attrs - Get Class Attributes

```python
from typemap import Attrs, Iter

class User:
    name: str
    email: str

# Get all attributes as Member types
type UserAttrs = Attrs[User]
# Returns: tuple[Member['name', str], Member['email', str]]

# Iterate over attributes
for attr in Iter[Attrs[User]]:
    print(attr.name, attr.type)
```

### Members - Get All Class Members

```python
from typemap import Members, Iter

class User:
    name: str

    def greet(self) -> str: ...

# Get all members (attributes + methods)
type UserMembers = Members[User]
```

### GetMemberType - Get Type of a Specific Member

```python
from typemap import GetMemberType

class User:
    name: str

# Get the type of a specific member
type NameType = GetMemberType[User, 'name']
# Equivalent to: str
```

---

## Runtime Type Evaluation

### eval_typing - Evaluate Type Expressions

```python
from typemap import eval_typing

# Evaluate a type alias at runtime
type MyType = Pick[User, 'name']
result = eval_typing(MyType)
```

---

## Advanced Patterns

### ORM-Style Query Builder

```python
from typemap import Pick, Omit, KeyOf

class User:
    id: int
    name: str
    email: str
    password: str

# Select specific fields for API response
def select_user_fields(**fields: bool) -> Pick[User, KeyOf[User]]:
    ...

# Usage
user = select_user_fields(name=True, email=True)
# Returns: { name: str; email: str }
```

### FastAPI Model Patterns

```python
from typemap import Pick, Omit, Partial, Required

class User(BaseModel):
    id: int
    name: str
    email: str
    password: str

# Create schemas automatically
type UserCreate = Omit[User, 'id'>
type UserResponse = Pick[User, 'id' | 'name' | 'email'>
type UserUpdate = Partial[User]
type UserPublic = Omit[User, 'password'>
```

### Validation Patterns

```python
from typemap import Pick, GetMemberType

class Field:
    name: str
    type: type

def validate_value(field: Field, value: GetMemberType[User, Field.name]):
    # Type-safe validation
    ...
```

---

## Custom Type Operators

### Creating Custom Type Utilities

```python
# Users can compose existing types
from typemap import Pick, Omit, KeyOf

# Create a utility type alias
type PublicFields = Pick[User, 'id' | 'name' | 'email'>
type PrivateFields = Omit[User, KeyOf[PublicFields]]

# Compose with existing types
type SafeUser = PublicFields | PrivateFields
```

---

## Error Handling

### Clear Type Errors

```python
from typemap import Pick

class User:
    name: str

# Invalid key - clear error message
type Invalid = Pick[User, 'nonexistent']
# Error: Key 'nonexistent' does not exist on User
# Available keys: 'name'
```

---

## Integration with IDEs

### Autocomplete Support

```python
from typemap import Pick

class User:
    name: str
    email: str
    age: int

# IDE autocomplete works for keys
type UserName = Pick[User, 'name' | 'email']
# IDE suggests: 'name', 'email', 'age'
```

### Hover Information

```python
# Hovering over Pick[User, 'name'] shows:
# Pick[User, 'name']
# Returns: { name: str }
```

---

## Testing Types

### Type Assertions

```python
from typemap import assert_type

# Runtime type checking
assert_type[Pick[User, 'name'], { name: str }]
```

### Type Equality

```python
from typemap import type_eq

# Check if two types are equal
assert type_eq(Pick[User, 'name'], { name: str })
```

---

## Compatibility

### Python Version

```python
# Requires Python 3.14+
import sys

if sys.version_info < (3, 14):
    raise ImportError("typemap requires Python 3.14+")
```

### Integration with mypy/pyright

```toml
# pyproject.toml
[tool.mypy]
plugins = ["typemap.mypy_plugin"]

[tool.pyright]
typeCheckingMode = "strict"
```

---

## Summary of Public API

```python
# Core type utilities
KeyOf[T]                           # Extract keys from type
Pick[T, K]                         # Select properties
Omit[T, K]                         # Exclude properties
Partial[T]                         # Make all optional
Required[T]                        # Make all required

# Introspection
Attrs[T]                           # Get attributes
Members[T]                         # Get all members
GetMemberType[T, K]               # Get specific member type
Iter[T]                           # Iterate over type

# Runtime
eval_typing[T]                    # Evaluate type at runtime

# Testing
assert_type[T, E]                 # Assert type equality
type_eq[T, E]                     # Check type equality
```

---

## Migration Guide

### From Python 3.13 to typemap

```python
# Before (no type manipulation)
def get_user_fields() -> dict[str, str]:
    return {'name': 'str', 'email': 'str'}

# After (with typemap)
def get_user_fields() -> Pick[User, 'name' | 'email']:
    ...
```

### From TypeScript to Python

```typescript
// TypeScript
type UserName = Pick<User, 'name'>;

// Python (typemap)
type UserName = Pick[User, 'name']
```

---

*Last updated: 2026-03-02*
