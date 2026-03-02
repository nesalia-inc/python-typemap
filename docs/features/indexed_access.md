# Indexed Access Types - TypeScript vs PEP 827

This document explains Indexed Access types in TypeScript and their status in PEP 827.

---

## What are Indexed Access Types?

Indexed access types allow you to access types using a key, similar to how you access values in an object or array.

---

## TypeScript Indexed Access

### Basic Usage

```typescript
type Person = { name: string; age: number };

// Access a specific key
type Name = Person['name'];  // → string
type Age = Person['age'];    // → number

// Access with union
type PersonKeys = Person['name' | 'age'];  // → string | number

// Access all keys with keyof
type AllKeys = Person[keyof Person];  // → string | number
```

### Nested Access

```typescript
type Nested = {
  user: {
    name: string;
    address: {
      city: string;
    };
  }
};

type City = Nested['user']['address']['city'];  // → string
```

### Array/ tuple Access

```typescript
type Array = string[];

// First element
type First = Array[0];  // → string

// Number key
type NumKey = Array[number];  // → string

type Tuple = [string, number, boolean];
type First = Tuple[0];   // → string
type Last = Tuple[2];    // → boolean
```

### With Conditional Types

```typescript
type Mapped = { a: 1; b: 2; c: 3 };
type Picked = Mapped['a' | 'b'];  // → 1 | 2
```

---

## PEP 827 Equivalent

### GetMemberType

PEP 827 provides `GetMemberType` for accessing member types:

```python
# TypeScript
type Name = Person['name']

# PEP 827
type Name = GetMemberType[Person, Literal['name']]
```

### GetArg for Generic Types

For generic types like arrays:

```python
# TypeScript
type First = Array[0]

# PEP 827 - No direct equivalent
# Could use GetArg with list base
# But indexing by literal number not directly supported
```

---

## Comparison Table

| TypeScript | PEP 827 | Notes |
|------------|---------|-------|
| `T['key']` | `GetMemberType[T, 'key']` | ✅ For class members |
| `T[K]` (union) | Not supported | ⚠️ Limited |
| `T[number]` | Not supported | Array element access |
| `T[0]` | Not supported | Tuple index |
| Nested access | Multiple GetMemberType | `T['a']['b']['c']` |

---

## Workarounds

### For Class Members

```python
# TypeScript
type Name = User['name']

# PEP 827
type Name = GetMemberType[User, Literal['name']]
```

### For Nested Types

```python
# TypeScript
type City = Nested['user']['address']['city']

# PEP 827 - Chain GetMemberType
type City = GetMemberType[
    GetMemberType[
        GetMemberType[Nested, Literal['user']],
        Literal['address']
    ],
    Literal['city']
]
```

---

## Missing Features

| Feature | PEP 827 Status |
|---------|----------------|
| `T['key']` | ⚠️ Use GetMemberType |
| `T[K]` with union | ❌ Not supported |
| `T[number]` | ❌ Not supported |
| `T[0]` tuple index | ❌ Not supported |

---

## Ideal DX Proposal (New Operators Allowed)

### Goal: Ergonomic member access

Create helper operators that make access cleaner.

### Proposed New Operators

```python
# 1. Type alias for cleaner access
type Attr[T, K] = GetMemberType[T, K]

# 2. Batch access
class MemberTypes[T]:
    """All member types as a dict"""
    # Returns dict of name -> type

class MemberNames[T]:
    """All member names as union"""
    # Returns union of literal names

# 3. Nested access helper
type NestedGet[T, Path] = ...  # e.g., NestedGet[User, 'profile.address.city']

# 4. Optional member access
type OptionalMember[T, K] = GetMemberType[T, K] | None
```

### Usage

```python
# Simple access - cleaner than GetMemberType
type Name = Attr[User, 'name']  # Uses string literal directly
type Email = Attr[User, 'email']

# All names as union
type UserKeys = MemberNames[User]  # → 'name' | 'email' | ...

# All types as dict
type UserTypes = MemberTypes[User]  # → {'name': str, 'email': str}

# Nested access (proposed)
type City = NestedGet[User, 'profile.address.city']
```

### Implementation with Current Operators

```python
# These CAN be implemented today!

# Simple accessor
type Attr[T, K] = GetMemberType[T, K]

# All names (KeyOf equivalent)
type MemberNames[T] = KeyOf[T]  # Already exists!

# All types
type MemberTypes[T] = NewProtocol[
    *[
        Member[p.name, p.type]
        for p in Iter[Attrs[T]]
    ]
]

# Nested access - chain GetMemberType
type NestedGet[T, K1, K2] = GetMemberType[
    GetMemberType[T, K1],
    K2
]
```

### Advanced Operators

```python
# Filtered members
class FilteredMembers[T, Qual]:
    """Get members with specific qualifier"""
    # Uses IsAssignable on .quals

class MethodsOnly[T]:
    """Only method members"""
    # Filters to ClassVar qualifiers

class PropertiesOnly[T]:
    """Only property/attribute members"""
    # Excludes ClassVar

# Usage
type UserMethods = MethodsOnly[User]
type UserProps = PropertiesOnly[User]
```

---

## References

- [TypeScript Indexed Access Types](https://www.typescriptlang.org/docs/handbook/2/indexed-access-types.html)

---

*Last updated: 2026-03-02*
