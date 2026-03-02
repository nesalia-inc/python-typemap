# PEP 827 - Dataclasses-Style Method Generation

This document explains how to generate `__init__` methods automatically using PEP 827 type manipulation, similar to Python's `@dataclass` decorator but with full type control.

---

## Overview

PEP 827 enables automatic method generation using type-level programming:

```python
# Generate __init__ method type
type InitFnType[T] = typing.Member[
    Literal["__init__"],
    Callable[
        [
            typing.Param[Literal["self"], Self],
            *[
                typing.Param[
                    p.name,
                    p.type,
                    Literal["keyword"]
                    if typing.IsAssignable[GetDefault[p.init], Never]
                    else Literal["keyword", "default"],
                ]
                for p in typing.Iter[typing.Attrs[T]]
            ],
        ],
        None,
    ],
    Literal["ClassVar"],
]

# Add to class
type AddInit[T] = typing.NewProtocol[
    InitFnType[T],
    *[x for x in typing.Iter[typing.Members[T]]],
]

# Decorator
def dataclass_ish[T](cls: type[T]) -> typing.UpdateClass[InitFnType[T]]:
    pass
```

---

## Breaking Down the Components

### 1. GetDefault - Getting Default Values

First, we need a way to extract default values from class attributes:

```python
# Simplified version (from the PEP examples)
GetDefault: typing.TypeAlias = (
    # If init=False, no default
    Never
    if not p.init
    else (
        # If default is provided, use it
        p.default
        if p.default is not MISSING
        else (
            # If default_factory is provided
            p.default_factory
            if p.default_factory is not MISSING
            else Never
        )
    )
)
```

**Example Class:**

```python
class User:
    name: str                           # Required (no default)
    email: str = "unknown"              # Default: "unknown"
    age: int = 0                        # Default: 0
    active: bool = True                 # Default: True
    tags: list[str] = field(default_factory=list)  # default_factory

# Generated Output - GetDefault for each attribute:
GetDefault[User, 'name']     # → Never (required, no default)
GetDefault[User, 'email']   # → Literal["unknown"]
GetDefault[User, 'age']     # → Literal[0]
GetDefault[User, 'active']  # → Literal[True]
GetDefault[User, 'tags']    # → list[str] (from default_factory)
```

---

### 2. Attrs[T] - Get Class Attributes

```python
Attrs[User]
```

**Generated Output:**

```python
tuple[
    Member['name', str],
    Member['email', str],
    Member['age', int],
    Member['active', bool],
    Member['tags', list[str]],
]
```

Each `Member` contains:
- `name`: The attribute name (as `Literal`)
- `type`: The attribute type

### 2b. Members[T] vs Attrs[T] - What's the Difference?

```python
class User:
    name: str
    email: str = "unknown"
    age: int = 0

    def greet(self) -> str: ...
    def __str__(self) -> str: ...
```

**Attrs[User] - Only attributes (fields):**

```python
tuple[
    Member['name', str],
    Member['email', str],
    Member['age', int],
]
```

**Members[User] - All members (attributes + methods):**

```python
tuple[
    Member['name', str],
    Member['email', str],
    Member['age', int],
    Member['greet', Callable[[Self], str]],
    Member['__str__', Callable[[Self], str]],
]
```

**Key Difference:**
- `Attrs[T]` → Only instance attributes (fields with annotations)
- `Members[T]` → All members including methods, class variables, etc.

For `__init__` generation, we typically want `Attrs[T]` (only the data fields).

---

### 3. InitFnType - The __init__ Method Type

```python
type InitFnType[T] = typing.Member[
    Literal["__init__"],  # Method name
    Callable[...],         # Function signature
    Literal["ClassVar"],   # Class variable (not instance)
]
```

#### The Callable Signature

```python
Callable[
    [
        # First param: self
        typing.Param[Literal["self"], Self],

        # Rest params: one per attribute
        *[
            typing.Param[
                p.name,           # Attribute name
                p.type,           # Attribute type

                # Keyword-only, with or without default
                Literal["keyword"]
                if typing.IsAssignable[GetDefault[p.init], Never]
                else Literal["keyword", "default"],
            ]
            for p in typing.Iter[typing.Attrs[T]]
        ],
    ],
    None,  # Return type (None for __init__)
]
```

**Generated Output for User class:**

```python
InitFnType[User] = Member[
    "__init__",
    Callable[
        [
            # self parameter
            Param["self", Self],

            # name: required (keyword-only, no default)
            Param["name", str, "keyword"],

            # email: optional (keyword-only, with default)
            Param["email", str, "keyword", "default"],

            # age: optional
            Param["age", int, "keyword", "default"],

            # active: optional
            Param["active", bool, "keyword", "default"],

            # tags: optional (from default_factory)
            Param["tags", list[str], "keyword", "default"],
        ],
        None,  # Return type: None
    ],
    "ClassVar",  # It's a class variable (method)
]
```

**Detailed breakdown:**

| Component | Purpose |
|----------|---------|
| `typing.Param` | Defines a function parameter |
| `Literal["self"]` | Parameter name is "self" |
| `Self` | Type refers to the class instance |
| `Literal["keyword"]` | Keyword-only argument (no positional) |
| `Literal["keyword", "default"]` | Keyword argument with default value |
| `typing.IsAssignable[GetDefault[p.init], Never]` | Check if default exists |

---

### 4. AddInit - Protocol with __init__

```python
type AddInit[T] = typing.NewProtocol[
    InitFnType[T],                        # Add the __init__ member
    *[x for x in typing.Iter[typing.Members[T]]],  # Keep existing members
]
```

**Generated Output for User class:**

```python
AddInit[User] = NewProtocol[
    # The generated __init__ method
    Member[
        "__init__",
        Callable[
            [
                Param["self", Self],
                Param["name", str, "keyword"],
                Param["email", str, "keyword", "default"],
                Param["age", int, "keyword", "default"],
                Param["active", bool, "keyword", "default"],
                Param["tags", list[str], "keyword", "default"],
            ],
            None,
        ],
        "ClassVar",
    ],

    # Original members from Members[User]
    Member['name', str],
    Member['email', str],
    Member['age', int],
    Member['active', bool],
    Member['tags', list[str]],
]
```

This creates a new protocol that:
1. Includes the generated `__init__` method
2. Preserves all existing class members (attributes, methods)

---

### 5. UpdateClass - Runtime Class Modification

```python
def dataclass_ish[T](
    cls: type[T],
) -> typing.UpdateClass[InitFnType[T]]:
    pass
```

**Runtime Behavior:**

When `@dataclass_ish` is applied to a class:

```python
@dataclass_ish
class User:
    name: str
    email: str = "unknown"
    age: int = 0
```

The decorator generates and adds the `__init__` method at runtime:

```python
# Runtime class after UpdateClass applied:
class User:
    name: str
    email: str = "unknown"
    age: int = 0

    def __init__(
        self,
        *,
        name: str,
        email: str = "unknown",
        age: int = 0,
    ) -> None:
        self.name = name
        self.email = email
        self.age = age
```

`UpdateClass` is the runtime counterpart to `NewProtocol`:

| Feature | Purpose |
|---------|---------|
| `NewProtocol` | Create type at type-checking time |
| `UpdateClass` | Modify class at runtime |

---

## Complete Example

### Before: Manual User Class

```python
class User:
    name: str
    email: str = "unknown"
    age: int = 0
    active: bool = True

    def __init__(
        self,
        *,
        name: str,
        email: str = "unknown",
        age: int = 0,
        active: bool = True,
    ) -> None:
        self.name = name
        self.email = email
        self.age = age
        self.active = active
```

### After: With Type-Generated __init__

```python
# Define the model
class User:
    name: str
    email: str = "unknown"
    age: int = 0
    active: bool = True

# Apply decorator
@dataclass_ish
class User:
    name: str
    email: str = "unknown"
    age: int = 0
    active: bool = True

# Usage
user = User(name="John", email="john@example.com")
# Or with defaults
user = User(name="Jane")  # email="unknown", age=0, active=True
```

### What the Generated Type Looks Like

For the `User` class above, `InitFnType[User]` produces:

```python
Member[
    "__init__",
    Callable[
        [
            Param["self", Self],
            Param["name", str, "keyword"],           # No default
            Param["email", str, "keyword", "default"],  # Has default
            Param["age", int, "keyword", "default"],
            Param["active", bool, "keyword", "default"],
        ],
        None,
    ],
    "ClassVar",
]
```

---

## Base Class Pattern (Pydantic-Style)

Instead of a decorator, use `__init_subclass__` for automatic generation:

```python
class Model:
    def __init_subclass__[T](
        cls: type[T],
    ) -> typing.UpdateClass[InitFnType[T]]:
        super().__init_subclass__()

# Now all subclasses automatically get __init__
class User(Model):
    name: str
    email: str = "unknown"

class Product(Model):
    name: str
    price: float = 0.0

# Both automatically have generated __init__
user = User(name="John")  # Works!
product = Product(name="Widget", price=9.99)  # Works!
```

---

## Comparison with Python's dataclass

| Feature | @dataclass | PEP 827 Method |
|---------|------------|----------------|
| Syntax | Decorator | Decorator or base class |
| Type generation | Runtime `__init__` | Type-level + runtime |
| IDE support | Limited | Full autocomplete |
| Type safety | Runtime only | Type-checking time |
| Customization | `field()` | Type manipulation |
| Init parameters | `__init__`/`__new__` | Configurable |

### Key Advantages of PEP 827 Approach

1. **Full IDE Support**: Type checkers understand the generated signature
2. **Type Safety**: Errors caught at type-checking time
3. **Composable**: Can combine with other type operations
4. **Flexible**: Different init styles possible

---

## Advanced: Customizing the Init

### Exclude Certain Fields

```python
type PublicInit[T] = typing.Member[
    "__init__",
    Callable[
        [
            typing.Param[Literal["self"], Self],
            *[
                typing.Param[p.name, p.type, ...]
                for p in typing.Iter[typing.Attrs[T]]
                if p.name not in ("password", "secret")  # Exclude
            ],
        ],
        None,
    ],
    Literal["ClassVar"],
]
```

**Generated Output for User with password:**

```python
# Input: User { name, email, password, age }
# Excludes: password, secret

PublicInit[User] = Member[
    "__init__",
    Callable[
        [
            Param["self", Self],
            Param["name", str, "keyword"],              # Included
            Param["email", str, "keyword", "default"],  # Included
            # password: EXCLUDED
            Param["age", int, "keyword", "default"],   # Included
        ],
        None,
    ],
    "ClassVar",
]
```

### Rename Parameters

```python
type SnakeToCamel[T] = typing.Member[
    "__init__",
    Callable[
        [
            typing.Param[Literal["self"], Self],
            *[
                typing.Param[
                    snake_to_camel(p.name),  # Transform name
                    p.type,
                    ...
                ]
                for p in typing.Iter[typing.Attrs[T]]
            ],
        ],
        None,
    ],
    Literal["ClassVar"],
]
```

**Generated Output:**

```python
# Input: User { first_name, last_name, email_address }
# Transformed to camelCase

SnakeToCamel[User] = Member[
    "__init__",
    Callable[
        [
            Param["self", Self],
            Param["firstName", str, "keyword"],        # first_name → firstName
            Param["lastName", str, "keyword"],         # last_name → lastName
            Param["emailAddress", str, "keyword"],     # email_address → emailAddress
        ],
        None,
    ],
    "ClassVar",
]
```

### Add Validation

```python
type ValidatedInit[T] = typing.Member[
    "__init__",
    Callable[
        [
            typing.Param[Literal["self"], Self],
            *[
                typing.Param[
                    p.name,
                    validate(p.type),  # Add validation
                    ...
                ]
                for p in typing.Iter[typing.Attrs[T])
            ],
        ],
        None,
    ],
    Literal["ClassVar"],
]
```

**Generated Output:**

```python
# Input: User { name: str, email: str, age: int }
# Output: email wrapped with validation

ValidatedInit[User] = Member[
    "__init__",
    Callable[
        [
            Param["self", Self],
            Param["name", str, "keyword"],
            Param["email", ValidatedEmail, "keyword"],  # Wrapped with validation
            Param["age", int, "keyword", "default"],
        ],
        None,
    ],
    "ClassVar",
]
```

---

## Implementation Roadmap

### Phase 1: Basic Infrastructure
1. ✅ `Attrs[T]` - Get class attributes
2. ✅ `Members[T]` - Get all members
3. ✅ `Iter[T]` - Type-level iteration
4. ✅ `GetMemberType[T, K]` - Get member type

### Phase 2: Parameter Types
5. Implement `Param[N, T, ...]` - Parameter definition
6. Implement `Self` - Self type reference
7. Implement `Callable[[...], R]` - Function types

### Phase 3: Default Values
8. Implement `GetDefault` - Extract default values
9. Implement `MISSING` sentinel
10. Handle `default_factory`

### Phase 4: Class Modification
11. Implement `NewProtocol` - Type creation
12. Implement `UpdateClass` - Runtime class modification
13. Implement decorator and base class patterns

---

## Comparison with TypeScript

### TypeScript

```typescript
// TypeScript doesn't have runtime class transformation
// But similar patterns exist with decorators

class User {
  constructor(
    public name: string,
    public email: string = "unknown",
    public age: number = 0
  ) {}
}
```

### Python with PEP 827

```python
class User:
    name: str
    email: str = "unknown"
    age: int = 0

@dataclass_ish
class User:
    name: str
    email: str = "unknown"
    age: int = 0

# Same result, but:
# - Type is generated from class definition
# - Works with any existing class
# - No runtime decorator needed for type info
```

---

## Real-World Use Cases

### 1. Pydantic-Style Models

```python
class User(Model):
    name: str
    email: EmailStr  # Custom type with validation
    age: int = 0

user = User(name="John", email="john@example.com")
```

### 2. ORM Models

```python
class User(Model):
    id: int
    name: str
    created_at: datetime

user = User(name="Test")  # id auto-generated, created_at set
```

### 3. API Request/Response

```python
class CreateUserRequest(Model):
    name: str
    email: str
    password: str  # Never returned

class UserResponse(Model):
    id: int
    name: str
    email: str
```

### 4. FastAPI CRUD Models

A powerful use case is automatically deriving FastAPI/Pydantic CRUD models from a single database model:

```python
from typing import Field

class User(Model):
    id: int = Field(primary_key=True)
    name: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime
```

#### GetDefault - Extract Default Values

```python
# Extract the default type from an Init field.
# If it is a Field, pull out the "default" field,
# otherwise return the type itself.
type GetDefault[Init] = (
    GetFieldItem[Init, Literal["default"]]
    if typing.IsAssignable[Init, Field]
    else Init
)
```

**Generated Output:**

```python
# For: id: int = Field(primary_key=True)
GetDefault[Field[int, primary_key=True]]  # → Never (no default)

# For: name: str (no default)
GetDefault[str]  # → str

# For: email: str = "user@example.com"
GetDefault[str]  # → str (not a Field)
```

**GetFieldItem - Extract items from Field**

```python
# GetFieldItem extracts a specific item from a Field type
# Used to check metadata like primary_key, private, default, etc.

GetFieldItem[Field[int, primary_key=True], Literal["primary_key"]]  # → True
GetFieldItem[Field[str, private=True], Literal["private"]]          # → True
GetFieldItem[Field[str, default="foo"], Literal["default"]]         # → "foo"
```

---

#### Create[T] - Create Model (excludes PK, preserves defaults)

```python
# Create takes everything but the primary key and preserves defaults
type Create[T] = typing.NewProtocol[
    *[
        typing.Member[
            p.name,
            p.type,
            p.quals,
            GetDefault[p.init],
        ]
        for p in typing.Iter[typing.Attrs[T]]
        if not typing.IsAssignable[
            Literal[True],
            GetFieldItem[p.init, Literal["primary_key"]],
        ]
    ]
]
```

**Generated Output for User:**

```python
# Input: User { id, name, email, password, created_at, updated_at }
# Output: Create model (excludes primary_key, includes defaults)

Create[User] = NewProtocol[
    Member['name', str, ...],
    Member['email', str, ...],
    Member['password', str, ...],
    Member['created_at', datetime, ..., datetime],  # with default
    Member['updated_at', datetime, ..., datetime],  # with default
]
# Note: id is excluded (primary_key=True)
```

---

#### Public[T] - Public Response Model (excludes sensitive fields)

```python
type Public[T] = typing.NewProtocol[
    *[
        typing.Member[
            p.name,
            p.type,
            p.quals,
        ]
        for p in typing.Iter[typing.Attrs[T]]
        if not typing.IsAssignable[
            Literal[True],
            GetFieldItem[p.init, Literal["private"]],
        ]
    ]
]
```

**Generated Output for User:**

```python
# Input: User { id, name, email, password, created_at, updated_at }
# Output: Public model (excludes password and private fields)

Public[User] = NewProtocol[
    Member['id', int, ...],
    Member['name', str, ...],
    Member['email', str, ...],
    Member['created_at', datetime, ...],
    Member['updated_at', datetime, ...],
]
# Note: password is excluded (private=True)
```

---

#### Update[T] - Update Model (all fields optional)

```python
type Update[T] = typing.NewProtocol[
    *[
        typing.Member[
            p.name,
            p.type | None,  # Make optional
            p.quals,
            None,  # Default is None for updates
        ]
        for p in typing.Iter[typing.Attrs[T]]
    ]
]
```

**Generated Output for User:**

```python
# Input: User { id, name, email, password }
# Output: All fields become optional (T | None)

Update[User] = NewProtocol[
    Member['id', int | None, ..., None],
    Member['name', str | None, ..., None],
    Member['email', str | None, ..., None],
    Member['password', str | None, ..., None],
    Member['created_at', datetime | None, ..., None],
    Member['updated_at', datetime | None, ..., None],
]
```

---

#### Putting It All Together

```python
# Database model
class User(Model):
    id: int = Field(primary_key=True)
    name: str
    email: str
    password: str = Field(private=True)
    created_at: datetime
    updated_at: datetime

# Auto-derived types
type UserCreate = Create[User]      # For POST /users
type UserUpdate = Update[User]      # For PATCH /users
type UserPublic = Public[User]     # For GET /users
type UserResponse = Public[User]   # Same as Public
```

**FastAPI Usage:**

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

# POST /users - Create a new user
@app.post("/users", response_model=UserPublic)
async def create_user(user: UserCreate):
    # user has: name, email, password, created_at, updated_at
    # user does NOT have: id (auto-generated)
    db_user = db.create(user)
    return db_user  # Returns Public (no password)

# GET /users/{id} - Get user (public fields only)
@app.get("/users/{id}", response_model=UserPublic)
async def get_user(id: int):
    user = db.get(User, id)
    if not user:
        raise HTTPException(404)
    return user  # password excluded automatically

# PATCH /users/{id} - Update user
@app.patch("/users/{id}", response_model=UserPublic)
async def update_user(id: int, update: UserUpdate):
    # All fields are optional
    user = db.update(User, id, update)
    return user
```

---

## Summary

PEP 827 enables powerful method generation:

1. **Type-level iteration** over class attributes
2. **Dynamic parameter generation** based on attributes
3. **Default value handling** at the type level
4. **Runtime class modification** via `UpdateClass`
5. **Decorator or base class** patterns

This mirrors what tools like Pydantic, dataclasses, and attrs do at runtime, but adds full type safety and IDE support.

---

## References

- PEP 557: Data Classes
- PEP 827: Type Manipulation (Draft)
- Python `typing` module
- Pydantic library

---

*Last updated: 2026-03-02*
