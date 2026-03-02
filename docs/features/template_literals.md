# Advanced Template Literal Types - TypeScript vs PEP 827

This document explains advanced template literal types in TypeScript and their status in PEP 827.

---

## What are Template Literal Types?

Template literal types build on string literal types, and have the ability to expand into many strings via unions.

---

## TypeScript Template Literals

### Basic Usage

```typescript
// Basic string concatenation
type Greeting = `hello, ${string}`;  // Any string starting with "hello, "

// With literal types
type EventName = `on${string}`;  // Any string starting with "on"
type HTTPMethod = `GET` | `POST` | `PUT` | `DELETE`;

// With specific types
type Name = `Mr. ${string}` | `Mrs. ${string}`;
```

### Built-in String Manipulation

```typescript
// Uppercase
type Upper = Uppercase<'hello'>;  // → 'HELLO'

// Lowercase
type Lower = Lowercase<'HELLO'>;  // → 'hello'

// Capitalize
type Cap = Capitalize<'hello'>;  // → 'Hello'

// Uncapitalize
type Uncap = Uncapitalize<'Hello'>;  → 'hello'
```

### Advanced: Key Remapping

```typescript
type Mapped = {
  foo: string;
  bar: number;
};

// Transform keys
type Transformed = {
  [K in keyof Mapped as `get${Capitalize<K>}`]: Mapped[K];
};
// → { getFoo: string; getBar: number }
```

### Complex Examples

```typescript
// API path building
type Route = `/${string}`;

// Method names
type Setter<T> = `set${Capitalize<T>}`;
type Getter<T> = `get${Capitalize<T>}`;

type UserSetters = Setter<'name' | 'email'>;
// → 'setName' | 'setEmail'

// CSS properties
type CSSProp = `${'width' | 'height'}: ${number}px`;
// → 'width: numberpx' | 'height: numberpx'
```

---

## PEP 827 Status

### String Operations (Partial Support)

```python
# These ARE implemented in typemap:
Uppercase['hello']    # → 'HELLO'
Lowercase['HELLO']    # → 'hello'
Capitalize['hello']   # → 'Hello'
StrConcat['a', 'b']   # → 'ab'
```

### Missing: True Template Literals

```typescript
// TypeScript - Full template literals
type Prefix = 'get';
type Name = `${Prefix}${Capitalize<string>}`;  // Dynamic construction

// PEP 827 - NOT supported
# Cannot dynamically construct string types from other type expressions
```

---

## Comparison Table

| TypeScript | PEP 827 | Status |
|------------|---------|--------|
| `` `${string}` `` | ❌ | Not supported |
| `` `${T}` `` | ❌ | Not supported |
| `` `${Prefix}${T}` `` | ❌ | Not supported |
| `Uppercase[T]` | ✅ | Implemented |
| `Lowercase[T]` | ✅ | Implemented |
| `Capitalize[T]` | ✅ | Implemented |
| `StrConcat[T, U]` | ✅ | Implemented |

---

## Why Template Literals Are Limited in PEP 827

### 1. Dynamic String Construction

TypeScript template literals can construct strings from **any** string type:

```typescript
type T = string;
type Result = `prefix${T}suffix`;  // Works in TS
```

PEP 827 would need to:
- Track string variable contents
- Handle string concatenation at type level
- This requires significant additional machinery

### 2. Key Remapping with Template Literals

```typescript
// TypeScript - powerful key transformation
type Transformed = {
  [K in keyof T as `get${Capitalize<K>}`]: T[K]
};
```

PEP 827 has no equivalent for key remapping in mapped types.

---

## Workarounds

### Using String Unions

```python
# Instead of dynamic template literals
# Define all possible values explicitly

type HTTPMethods = 'GET' | 'POST' | 'PUT' | 'DELETE'
type EventNames = 'onClick' | 'onHover' | 'onFocus'
```

### Using String Operations

```python
# Partial workaround with Uppercase, Lowercase, Capitalize
type EventPrefix = 'on'
type EventBase = 'click' | 'hover' | 'focus'

# Can't combine dynamically, but can define manually
type Events = 'onClick' | 'onHover' | 'onFocus'
```

---

## Summary

| Feature | TypeScript | PEP 827 |
|---------|-----------|---------|
| Static concatenation | ✅ | ✅ (StrConcat) |
| `Uppercase` | ✅ | ✅ |
| `Lowercase` | ✅ | ✅ |
| `Capitalize` | ✅ | ✅ |
| Dynamic `${T}` | ✅ | ❌ |
| Key remapping | ✅ | ❌ |
| Pattern matching | ✅ | ❌ |

---

## Ideal DX Proposal (New Operators Allowed)

### Goal: Ergonomic string type utilities

Create helper classes for common string manipulations.

### Proposed New Operators

```python
# 1. Pre-defined builder helpers
class Prefix[T]:
    """Add prefix to string literal"""
    type result = StrConcat[T, ...]  # Would need new operator

# 2. Join helper
class Join[Parts, Sep]:
    """Join string parts with separator"""
    # StrJoin['a', 'b', 'c'], '_'] → 'a_b_c'

# 3. Split helper
class Split[T, Sep]:
    """Split string into tuple"""
    # Split['a_b_c', '_'] → ['a', 'b', 'c']

# 4. Replace helper
class Replace[T, Old, New]:
    """Replace substring"""
    # Replace['hello', 'lo', 'ya'] → 'hya'

# 5. Match helper
class Matches[T, Pattern]:
    """Check if matches pattern"""
    # Returns True/False
```

### What We CAN Build Today

```python
# 1. Pre-defined string unions (most common)
type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'DELETE'
type EventName = 'onClick' | 'onHover' | 'onFocus'

# 2. Using StrConcat
type MethodGet = StrConcat['G', 'E', 'T']  # → 'GET'
type EventHandler = StrConcat['on', Capitalize['click']]  # → 'onClick'

# 3. Builder for method names from fields
type MethodNames[T] = NewProtocol[
    *[
        Member[
            StrConcat['get', Capitalize[p.name]],
            Callable[[Self], p.type],
        ]
        for p in Iter[Attrs[T]]
    ]
]

# Usage
class User:
    name: str
    email: str

type UserMethods = MethodNames[User]
# → { getName: (Self) -> str, getEmail: (Self) -> str }
```

### Additional Proposed Helpers

```python
# Snake/Camel case converters
type SnakeToCamel[S] = ...  # Convert snake_case to camelCase
type CamelToSnake[S] = ...  # Convert camelCase to snake_case

# Pluralizer
type Pluralize[S] = ...  # 'user' → 'users'

# URL builders
type RouteBuilder[Resource] = StrConcat['/', Resource]
type RouteList[Resource] = StrConcat[Resource, 's']

# Usage
type UsersRoute = RouteBuilder['users']  # → '/users'
type UserRoutes = RouteList['user']  # → 'users'
```

### Key Insight

Most useful string operations in practice are:
1. **Pre-defined unions** - Just list all variants
2. **Static concatenation** - Use `StrConcat`
3. **Case conversion** - Need new helpers
4. **Key remapping** - Use iteration + StrConcat

---

## References

- [TypeScript Template Literal Types](https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html)

---

*Last updated: 2026-03-02*
