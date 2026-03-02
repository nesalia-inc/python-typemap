# typemap DX - Multi-Level Type Manipulation

This document describes the different levels of control for the typemap developer experience, from simple to expert level, based on PEP 827 features.

---

## Philosophy

Different users need different levels of control:

| Level | User | Use Case |
|-------|------|----------|
| **Level 1** | Most users | Quick, declarative patterns |
| **Level 2** | Advanced users | Customization, specific needs |
| **Level 3** | Experts / Library authors | Full control, new patterns |

---

## Level 1: High-Level API (Simplest)

The simplest way to use typemap - pre-built utilities that just work.

**Note:** These are the same utility types that exist in TypeScript.

### Pre-built Type Utilities

```python
from typemap import (
    # Selection (same as TypeScript)
    Pick,           # Pick[T, 'field1' | 'field2']
    Omit,           # Omit[T, 'password']

    # Transformation (same as TypeScript)
    Partial,        # Make all fields optional
    Required,       # Make all fields required
    Record,         # Record[K, T]

    # Introspection (same as TypeScript)
    KeyOf,          # Get all keys as union
)

# NOT included (framework-specific, not TypeScript native):
# - Create[T]    # Built with typemap, provided by FastAPI/Pydantic
# - Public[T]    # Built with typemap, provided by FastAPI/Pydantic
# - Update[T]    # Built with typemap, provided by FastAPI/Pydantic
```

### Basic Usage

```python
from typemap import Pick, Omit, Partial, Required, KeyOf, Record

# Define your model
class User:
    id: int
    name: str
    email: str
    password: str
    created_at: datetime

# Type transformations (same as TypeScript)
type UserBrief = Pick[User, 'id' | 'name'>      # Only id and name
type UserPrivate = Omit[User, 'password'>        # Excludes password
type OptionalUser = Partial[User]                # All optional
type RequiredUser = Required[User]               # All required
type UserKeys = KeyOf[User]                     # 'id' | 'name' | 'email' | ...
```

### What TypeScript Has (And typemap Matches)

| TypeScript | typemap | Description |
|------------|---------|-------------|
| `Pick<T, K>` | ✅ `Pick[T, K]` | Select properties |
| `Omit<T, K>` | ✅ `Omit[T, K]` | Exclude properties |
| `Partial<T>` | ✅ `Partial[T]` | Make optional |
| `Required<T>` | ✅ `Required[T]` | Make required |
| `Record<K, T>` | ✅ `Record[K, T]` | Key-value type |
| `Exclude<T, U>` | ❌ (not implemented) | Exclude from union |
| `Extract<T, U>` | ❌ (not implemented) | Extract from union |
| `ReturnType<T>` | ❌ (not implemented) | Function return type |
| `Parameters<T>` | ❌ (not implemented) | Function parameters |

---

## Level 2: Medium-Level API (Customizable)

For users who need to customize behavior with field options.

### Field Options

```python
from typemap import Field

class User(Model):
    # Primary key - excluded from Create
    id: int = Field(primary_key=True)

    # Private - excluded from Public
    password: str = Field(private=True)

    # Hidden - excluded from everything
    internal_id: str = Field(hidden=True)

    # Read-only - excluded from Update
    created_at: datetime = Field(readonly=True)

    # With default - preserved in Create
    status: str = Field(default="active")

    # Custom validation
    email: EmailStr = Field(validate=True)
```

### Framework-Built Types (Not TypeScript Native)

These types would be **built with typemap** and provided by frameworks like FastAPI/Pydantic:

```python
# These come from fastapi/typemap integration, not typemap core
from fastapi_typemap import Create, Public, Update

# Include/Exclude specific fields
type UserPublic = Public[User, exclude={'password'}>
type UserBrief = Public[User, include={'id', 'name'}]

# With defaults
type UserCreate = Create[User, include_defaults=True]
type UserUpdate = Update[User, set_defaults=False]

# Validation
type StrictUser = Create[User, validate=True]
```

> **Note:** These are NOT TypeScript native types. They're examples of what frameworks can build ON TOP of typemap.

---

## Level 3: Low-Level API (Expert)

Full access to type manipulation primitives for building custom utilities.

### PEP 827 Core Features

#### Boolean Operators

```python
# Check type relationships at type level
IsAssignable[T, S]        # Is T assignable to S?
IsEquivalent[T, S]         # Are T and S equivalent?
Bool[T]                    # Convert to True/False
```

#### Object Introspection

```python
# Get class/TypedDict members
Members[T]                 # All members (attrs + methods)
Attrs[T]                   # Only attributes (fields)
GetMember[T, 'name']       # Get specific member
Iter[T]                    # Type-level iteration

# Member access
Member[N, T, Q, I, D]      # Full member: name, type, quals, init, definer
# Access: m.name, m.type, m.quals, m.init, m.definer
```

#### Type Operators

```python
# Extract information
GetMemberType[T, 'name']   # Get type of member
GetArg[T, Base, 0]         # Get type argument
GetSpecialAttr[T, '__name__']  # Get special attribute
Length[T]                  # Get tuple length
Slice[T, 0, 5]             # Slice tuple

# Union processing
FromUnion[T]               # Split union to tuple
Union[*Ts]                 # Create union
```

#### Type Construction

```python
# Create new types
NewProtocol[*Ms]           # Create protocol from Members
NewTypedDict[*Ms]          # Create TypedDict
UpdateClass[*Ms]           # Modify class at runtime

# Callable construction
Callable[[Param[...], ...], R]  # Function type
Param[N, T, Q]            # Parameter: name, type, qualifier
ParamQuals = Literal["*", "**", "default", "keyword", "positional"]
```

#### Field Operations

```python
# Handle Field(...) patterns
InitField[KwargDict]      # Wrapper for field defaults
GetFieldItem[F, 'default']  # Extract item from Field
GetDefault[Init]           # Extract default value
```

#### String Operations

```python
# String literal manipulation
Uppercase['hello']         # → 'HELLO'
Lowercase['HELLO']         # → 'hello'
Capitalize['hello']        # → 'Hello'
Concat['a', 'b']          # → 'ab'
Slice[S, 0, 3]            # Slice string literals
```

#### Error Handling

```python
# Generate type errors
RaiseError['Invalid type', T]  # Raise custom error message
```

---

## Building Blocks: From PEP 827

### The Complete Type System

```
┌─────────────────────────────────────────────────────────────┐
│                     PEP 827 Type System                     │
├─────────────────────────────────────────────────────────────┤
│  BOOLEAN OPERATORS                                          │
│  ├── IsAssignable[T, S]  - Subtype check                   │
│  ├── IsEquivalent[T, S] - Mutual assignability             │
│  └── Bool[T]             - To literal True/False           │
├─────────────────────────────────────────────────────────────┤
│  BASIC OPERATORS                                            │
│  ├── GetMemberType[T, K] - Get member type                  │
│  ├── GetArg[T, Base, I]  - Get type argument               │
│  ├── GetSpecialAttr[T, A] - Get __name__, __module__       │
│  ├── Length[T]            - Tuple/string length             │
│  └── Slice[T, S, E]       - Slice tuple/string             │
├─────────────────────────────────────────────────────────────┤
│  INTROSPECTION                                              │
│  ├── Members[T]           - All members (attrs + methods)  │
│  ├── Attrs[T]             - Only attributes                │
│  ├── GetMember[T, K]      - Specific member                │
│  ├── Iter[T]              - Type-level iteration          │
│  └── Member[N,T,Q,I,D]    - Member descriptor             │
├─────────────────────────────────────────────────────────────┤
│  CONSTRUCTION                                               │
│  ├── NewProtocol[*Ms]     - Create protocol type           │
│  ├── NewTypedDict[*Ms]    - Create TypedDict              │
│  ├── UpdateClass[*Ms]      - Modify class (runtime)        │
│  └── Callable[[...], R]    - Function type                │
├─────────────────────────────────────────────────────────────┤
│  CALLABLES                                                  │
│  ├── Param[N, T, Q]       - Parameter descriptor           │
│  ├── GenericCallable[V, λ] - Generic function              │
│  └── Overloaded[*Fs]      - Overloaded functions          │
├─────────────────────────────────────────────────────────────┤
│  FIELDS                                                     │
│  ├── InitField[KD]        - Field wrapper                 │
│  ├── GetFieldItem[F, K]   - Extract from Field            │
│  └── GetDefault[I]        - Get default value             │
├─────────────────────────────────────────────────────────────┤
│  STRINGS                                                    │
│  ├── Uppercase[S]         - UPPERCASE                      │
│  ├── Lowercase[S]         - lowercase                      │
│  ├── Capitalize[S]        - Capitalize                     │
│  ├── Concat[S1, S2]       - String concatenation          │
│  └── Slice[S, S, E]       - String slicing                │
├─────────────────────────────────────────────────────────────┤
│  UNION                                                      │
│  ├── FromUnion[T]         - Union → tuple                  │
│  └── Union[*Ts]           - Create union                   │
├─────────────────────────────────────────────────────────────┤
│  ANNOTATIONS (Future)                                       │
│  ├── GetAnnotations[T]    - Extract annotations            │
│  └── DropAnnotations[T]   - Remove annotations            │
└─────────────────────────────────────────────────────────────┘
```

---

## Real Examples from PEP 827

### Example 1: Prisma-style ORM

```python
# From PEP 827 - Query builder
def select[ModelT, K: BaseTypedDict](
    typ: type[ModelT],
    /,
    **kwargs: Unpack[K],
) -> list[
    NewProtocol[
        *[
            Member[
                c.name,
                ConvertField[GetMemberType[ModelT, c.name]],
            ]
            for c in Iter[Attrs[K]]
        ]
    ]
]:
    raise NotImplementedError
```

### Example 2: FastAPI CRUD

```python
# From PEP 827 - Create type
type Create[T] = NewProtocol[
    *[
        Member[
            p.name,
            p.type,
            p.quals,
            GetDefault[p.init],
        ]
        for p in Iter[Attrs[T]]
        if not IsAssignable[
            Literal[True],
            GetFieldItem[p.init, Literal['primary_key']],
        ]
    ]
]
```

### Example 3: Dataclass __init__

```python
# From PEP 827 - Generate __init__
type InitFnType[T] = Member[
    "__init__",
    Callable[
        [
            Param[Literal["self"], Self],
            *[
                Param[
                    p.name,
                    p.type,
                    Literal["keyword"]
                    if IsAssignable[GetDefault[p.init], Never]
                    else Literal["keyword", "default"],
                ]
                for p in Iter[Attrs[T]]
            ],
        ],
        None,
    ],
    Literal["ClassVar"],
]
```

### Example 4: NumPy Broadcasting

```python
# From PEP 827 - Type-level recursion
type MergeOne[T, S] = (
    T
    if IsEquivalent[T, S] or IsEquivalent[S, Literal[1]]
    else S
    if IsEquivalent[T, Literal[1]]
    else RaiseError[Literal["Broadcast mismatch"], T, S]
)

type Broadcast[T, S] = (
    S if Bool[Empty[T]]
    else T if Bool[Empty[S]]
    else tuple[
        *Broadcast[DropLast[T], DropLast[S]>,
        MergeOne[Last[T], Last[S]>,
    ]
)
```

---

## Comparison: Same Result, Different Levels

### Goal: Get public user type (without password)

**Level 1: Simplest**

```python
type UserPublic = Public[User]
```

**Level 2: With Options**

```python
type UserPublic = Public[User, exclude={'password'}]
```

**Level 3: Manual**

```python
type UserPublic = NewProtocol[
    *[
        Member[p.name, p.type]
        for p in Iter[Attrs[User]]
        if p.name != 'password'
    ]
]
```

**All produce the same result:**

```python
# { id: int, name: str, email: str }
```

---

## Summary Table

| Level | Complexity | Flexibility | Typical Users |
|-------|------------|-------------|---------------|
| **1** | Low | Low | Most developers |
| **2** | Medium | Medium | Framework users |
| **3** | High | High | Library authors |

### Feature Matrix

| Feature | Level 1 | Level 2 | Level 3 |
|---------|:-------:|:-------:|:-------:|
| `Pick`, `Omit`, `Partial` | ✅ | ✅ | ✅ |
| `Record`, `Required` | ✅ | ✅ | ✅ |
| `KeyOf` | ✅ | ✅ | ✅ |
| Field options | - | ✅ | ✅ |
| Include/Exclude | - | ✅ | ✅ |
| `Attrs`, `Members`, `Iter` | - | - | ✅ |
| `NewProtocol`, `UpdateClass` | - | - | ✅ |
| `GetMemberType`, `GetArg` | - | - | ✅ |
| Boolean operators | - | - | ✅ |
| String operations | - | - | ✅ |
| Custom type aliases | - | - | ✅ |

---

## Migration Path

Users can start simple and graduate to lower levels as needed:

```
Level 1 → Level 2 → Level 3
   ↓         ↓
 Simple   Custom   Expert
```

### Example: Building a Custom Type

```python
# Start: Level 1 - Pre-built
type UserPublic = Public[User]

# Need custom exclusions? Move to Level 2
type UserPublic = Public[User, exclude={'password', 'internal_id'}]

# Need custom transformation? Move to Level 3
type CustomPublic[T] = NewProtocol[
    *[
        Member[p.name, Redacted[p.type]]
        if GetFieldItem[p.init, Literal['private']]
        else Member[p.name, p.type]
        for p in Iter[Attrs[T]]
    ]
]

type UserPublic = CustomPublic[User]
```

---

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| `Members`, `Attrs`, `Iter` | ✅ Implemented | Core introspection |
| `GetMemberType` | ✅ Implemented | Member access |
| `NewProtocol` | ✅ Implemented | Type creation |
| `UpdateClass` | ✅ Implemented | Runtime modification |
| `Pick`, `Omit`, `Partial` | ✅ Implemented | Utility types |
| `KeyOf` | ⚠️ Planned | Key extraction |
| `Create`, `Public`, `Update` | ⚠️ N/A | Framework-built | Not TypeScript native - built with typemap |
| `Exclude`, `Extract` | ❌ Not implemented | Future | TypeScript native |
| `Param`, `Callable` | ⚠️ Planned | Extended callables |
| String operations | ✅ Implemented | Uppercase, Lowercase, etc. |
| `GetAnnotations` | ✅ Implemented | Annotation handling |
| Runtime evaluator | ✅ Available | Third-party library |

---

## Reference

### Quick Lookup

```python
# Level 1 (TypeScript-equivalent)
from typemap import Pick, Omit, Partial, Required, KeyOf, Record

# Level 2
from typemap import Field

# Framework types (built with typemap, not in TypeScript)
# from fastapi_typemap import Create, Public, Update

# Level 3
from typemap import (
    # Introspection
    Members, Attrs, Iter, GetMember, GetMemberType,
    Member, MemberQuals,

    # Construction
    NewProtocol, NewTypedDict, UpdateClass,

    # Operators
    IsAssignable, IsEquivalent, Bool,

    # Callables
    Callable, Param, GenericCallable, Overloaded,

    # Fields
    InitField, GetFieldItem, GetDefault,

    # Strings
    Uppercase, Lowercase, Capitalize, Concat,

    # Union
    FromUnion, Union,

    # Misc
    RaiseError, GetSpecialAttr, Length, Slice,
)
```

---

*Last updated: 2026-03-02*
*Based on PEP 827 - Type Manipulation*
