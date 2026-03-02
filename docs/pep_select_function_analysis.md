# PEP 827 Type Manipulation - Select Function Deep Dive

This document provides an in-depth analysis of the `select` function example from PEP 827, explaining how advanced type manipulation works together.

---

## Overview

The `select` function demonstrates complex type-level programming using PEP 827's type manipulation features:

```python
def select[ModelT, K: typing.BaseTypedDict](
    typ: type[ModelT],
    /,
    **kwargs: Unpack[K],
) -> list[
    typing.NewProtocol[
        *[
            typing.Member[
                c.name,
                ConvertField[typing.GetMemberType[ModelT, c.name]],
            ]
            for c in typing.Iter[typing.Attrs[K]]
        ]
    ]
]:
    raise NotImplementedError
```

---

## Breaking Down the Components

### 1. Function Signature

```python
def select[ModelT, K: typing.BaseTypedDict](
    typ: type[ModelT],
    /,
    **kwargs: Unpack[K],
) -> ...
```

- **`ModelT`**: Generic type parameter for the model class
- **`K: typing.BaseTypedDict`**: Constrained type parameter that must be a TypedDict
- **`typ: type[ModelT]`**: The model class itself (passed as parameter)
- **`**kwargs: Unpack[K]`**: Keyword arguments that must conform to TypedDict K
- **`/`**: Positional-only parameter (typ must be positional)

### 2. What Does `Unpack[K]` Do?

`Unpack` comes from PEP 646 (Variadic Generics) and allows unpacking a TypedDict into keyword arguments:

```python
class User(TypedDict):
    name: str
    email: str

# These are equivalent:
def foo(**kwargs: Unpack[User]): ...
def foo(*, name: str, email: str): ...
```

---

## The Return Type Analysis

### Step 1: `typing.Iter[typing.Attrs[K]]`

```python
for c in typing.Iter[typing.Attrs[K]]
```

- **`Attrs[K]`**: Gets all attributes/members of the TypedDict K as a tuple of `Member` types
- **`Iter[...]`**: Allows iteration over the tuple at type level

**Example:**
```python
class User(TypedDict):
    name: str
    email: str

# Attrs[User] returns:
# tuple[Member['name', str], Member['email', str]]

# Iter[Attrs[User]] allows iterating over each Member
```

### Step 2: `typing.GetMemberType[ModelT, c.name]`

```python
typing.GetMemberType[ModelT, c.name]
```

- Gets the type of a specific member from `ModelT` by its name
- This is a **key feature** - it allows dynamic type lookup at type-checking time

**Example:**
```python
class User:
    name: str
    email: str

GetMemberType[User, 'name']  # Returns: str
GetMemberType[User, 'email']  # Returns: str
```

### Step 3: `ConvertField[...]`

```python
ConvertField[typing.GetMemberType[ModelT, c.name]]
```

`ConvertField` is a type alias (not a built-in) defined in the PEP for field type transformation:

```python
# From PEP 827 (lines ~920-930)
ConvertField: typing.TypeAlias = (
    PointerArg | AdjustLink | PropsOnly
)
```

It applies one of three transformations to a field type:
- **`PointerArg`**: Convert to pointer/argument type
- **`AdjustLink`**: Adjust link types
- **`PropsOnly`**: Keep only properties

### Step 4: Building the Member List

```python
[
    typing.Member[
        c.name,
        ConvertField[typing.GetMemberType[ModelT, c.name]],
    ]
    for c in typing.Iter[typing.Attrs[K]]
]
```

This list comprehension at the type level:
1. Iterates over each member `c` in the TypedDict K
2. For each member, creates a new `Member` type with:
   - **`c.name`**: The original member name
   - **Transformed type**: `ConvertField[...]` applied to the original type

### Step 5: `typing.NewProtocol`

```python
typing.NewProtocol[
    *[
        typing.Member[...],
        typing.Member[...],
        ...
    ]
]
```

- **`NewProtocol`**: Creates a new protocol type at runtime/type-check time
- The `*` unpacks the list into variadic type parameters
- Each `Member` defines a name-type pair

**Result:** A protocol with the transformed members

---

## The Complete Transformation Flow

Let's trace through a complete example:

```python
class UserModel:
    id: int
    name: str
    email: str
    password: str  # Sensitive - should be pointer
    links: list[Link]  # Should be adjusted

class UserView(TypedDict):
    name: str
    email: str

# Call:
select(UserModel, name=True, email=True)

# Return type analysis:
# 1. K = UserView
# 2. Attrs[UserView] = tuple[Member['name', str], Member['email', str]]
# 3. For each member:
#    - name: GetMemberType[UserModel, 'name'] = str
#    - email: GetMemberType[UserModel, 'email'] = str
# 4. Apply ConvertField to each type
# 5. Build NewProtocol with transformed members

# Result: list[Protocol with name: str, email: str]
```

---

## Type Aliases Explained

### PointerArg

Converts certain types to pointer/reference types:

```python
PointerArg: typing.TypeAlias = (
    typing.Annotated[T, PointerArgAnnotation()]
    if typing.IsEquivalent[T, typing.Any]
    else T
)
```

Typically used for sensitive fields that shouldn't be serialized.

### AdjustLink

Adjusts link/reference types:

```python
AdjustLink: typing.TypeAlias = (
    typing.NewProtocol[
        typing.Member['href', str],
        typing.Member['rel', str],
    ]
    if typing.IsEquivalent[T, Link]
    else T
)
```

Transforms link types to a specific protocol shape.

### PropsOnly

Keeps only property fields, removing methods:

```python
PropsOnly: typing.TypeAlias = (
    T
    if typing.IsAssignable[T, typing.BaseTypedDict]
    else (
        typing.NewProtocol[
            *[
                typing.Member[
                    m.name,
                    m.type,
                ]
                for m in typing.Iter[typing.Attrs[T]]
                if typing.IsAssignable[
                    typing.GetSpecialAttr[m.type, typing.Literal['__qualname__']],
                    typing.Literal['property'],
                ]
            ]
        ]
    )
)
```

---

## Why This Is Powerful

### 1. Type-Safe Database Queries

The `select` function enables type-safe field selection:

```python
# Instead of:
def select(typ: type, fields: list[str]) -> list[dict]:
    ...

# You get:
select(UserModel, name=True, email=True)
# Return type: list[Protocol with name: str, email: str]
```

### 2. IDE Autocomplete

With proper mypy/pyright integration:

```python
# IDE knows exact return type
result = select(UserModel, name=True, email=True)
# Autocomplete shows: result[0].name, result[0].email
# Type checker validates: can't request non-existent fields
```

### 3. Runtime + Static Typing

- **Runtime**: The function raises `NotImplementedError` (for now)
- **Static**: Full type information available to IDE and type checkers

---

## Comparison with TypeScript

### Equivalent TypeScript

```typescript
type ConvertField<T> = PointerArg<T> | AdjustLink<T> | PropsOnly<T>;

function select<
  ModelT,
  K extends Record<string, any>
>(
  typ: new () => ModelT,
  kwargs: K
): Array<{
  [P in keyof K]: ModelT[P] extends Link
    ? AdjustLink<ModelT[P]>
    : ModelT[P]
}> {
  throw new Error("Not implemented");
}

// Usage
select(UserModel, { name: true, email: true });
// Returns: Array<{ name: string; email: string }>
```

### Key Differences

| Feature | TypeScript | PEP 827 (Python) |
|---------|------------|------------------|
| Syntax | `P in keyof K` | `for c in Iter[Attrs[K]]` |
| Type creation | Inline object | `NewProtocol` |
| Field transformation | Conditional type | `ConvertField` alias |
| Member definition | `{ name: type }` | `Member[name, type]` |

---

## Limitations and Considerations

### 1. Complexity

The type is very complex - requires understanding of:
- PEP 646 variadic generics
- PEP 647 protocol types
- PEP 827 type manipulation
- Type-level comprehensions

### 2. Runtime Behavior

Currently `raise NotImplementedError` - the function doesn't actually work at runtime. This is a **type-level demonstration only**.

### 3. Type Checker Support

Requires mypy/pyright plugin support for full functionality. Without plugins, type checkers may not understand:
- `NewProtocol` runtime creation
- `ConvertField` type alias resolution
- Type-level comprehensions

---

## Practical Implementation Roadmap

### Phase 1: Basic Building Blocks
1. Implement `Attrs[T]` - Get class/TypedDict members
2. Implement `Iter[T]` - Type-level iteration
3. Implement `GetMemberType[T, K]` - Get member by name
4. Implement `Member[N, T]` - Member type construction

### Phase 2: Type Construction
5. Implement `NewProtocol[*Ms]` - Protocol creation
6. Implement `Unpack[T]` - TypedDict unpacking

### Phase 3: Transformation
7. Implement `ConvertField` alias
8. Implement `PointerArg`, `AdjustLink`, `PropsOnly`

### Phase 4: Integration
9. Implement the `select` function
10. Add mypy/pyright plugin support

---

## References

- PEP 646: Variadic Generics
- PEP 647: User-Defined Protocol Types
- PEP 827: Type Manipulation (Draft)
- Python Typing docs: TypedDict, TypeAlias

---

*Last updated: 2026-03-02*
