# TypeScript Features vs typemap Implementation Status

This document outlines TypeScript's advanced type features and their current implementation status in the typemap project (PEP 827 reference implementation).

---

## 1. Basic Utility Types

| TypeScript | Description | typemap Status | Notes |
|------------|-------------|----------------|-------|
| `keyof T` | Get all keys of T as union | ❌ Not implemented | Issue #1 |
| `Pick<T, K>` | Select properties K from T | ❌ Not implemented | Issue #2 |
| `Omit<T, K>` | Exclude properties K from T | ❌ Not implemented | Issue #2 |
| `Partial<T>` | Make all properties optional | ❌ Not implemented | Issue #3 |
| `Required<T>` | Make all properties required | ❌ Not implemented | Issue #3 |
| `Readonly<T>` | Make all properties readonly | ❌ Not implemented | |
| `Record<K, T>` | Construct type with keys K and values T | ❌ Not implemented | |
| `Exclude<T, U>` | Exclude U from T | ❌ Not implemented | |
| `Extract<T, U>` | Extract U from T | ❌ Not implemented | |
| `NonNullable<T>` | Remove null and undefined | ❌ Not implemented | |
| `ReturnType<T>` | Get return type of function T | ❌ Not implemented | |
| `Parameters<T>` | Get parameters of function T as tuple | ❌ Not implemented | |
| `InstanceType<T>` | Get instance type of constructor T | ❌ Not implemented | |

---

## 2. Conditional Types

| TypeScript | Description | typemap Status | Notes |
|------------|-------------|----------------|-------|
| `T extends U ? X : Y` | Ternary conditional type | ⚠️ Partial | Uses `IsAssignable` but syntax differs |
| `infer` keyword | Type inference in conditionals | ❌ Not implemented | Major limitation |

> 📖 See detailed analysis: [docs/features/infer.md](./features/infer.md)

### Current Implementation

```python
# What we have (different syntax)
type FilterLinks[T] = Link[...] if IsAssignable[T, Link] else T

# What TypeScript looks like
type FilterLinks<T> = T extends Link ? Link[...] : T
```

### Missing: `infer` keyword

```typescript
// TypeScript
type ReturnType<T> = T extends (...args: infer A) => infer R ? R : never;
type First<T> = T extends [infer F, ...infer Rest] ? F : never;
```

Python has no equivalent to `infer` for type-level inference within conditional types.

---

## 3. Template Literal Types

| TypeScript | Description | typemap Status | Notes |
|------------|-------------|----------------|-------|
| `` `prefix${T}suffix` `` | String template types | ❌ Not implemented | See [docs/features/template_literals.md](./features/template_literals.md) |
| Uppercase/ Lowercase | Built-in string transforms | ✅ Implemented | `Uppercase`, `Lowercase`, `Capitalize`, etc. |

### Current Implementation

The string operations are implemented in `typemap/type_eval/_eval_operators.py`:

```python
_string_literal_op(Uppercase, op=str.upper)
_string_literal_op(Lowercase, op=str.lower)
_string_literal_op(Capitalize, op=str.capitalize)
_string_literal_op(StrConcat, op=lambda s, t: s + t)
```

### Missing: True Template Literals

```typescript
// TypeScript
type EventName = `on${Capitalize<string>}`;
type Path = `/users/${string}/${string}`;
```

Python cannot dynamically construct string types from other type expressions.

---

## 4. Mapped Types

| TypeScript | Description | typemap Status | Notes |
|------------|-------------|----------------|-------|
| `{ [K in keyof T]: T[K] }` | Basic mapping | ⚠️ Partial | Via `Iter[Attrs[T]]` but not native |
| `{ [K in keyof T]?: T[K] }` | Optional mapping | ❌ Not implemented | Requires `Partial` |
| `{ -readonly [K in keyof T]: T[K] }` | Remove readonly | ❌ Not implemented | |
| `{ +readonly [K in keyof T]: T[K] }` | Add readonly | ❌ Not implemented | |
| `{ [K in keyof T as F<K>]: T[K] }` | Key remapping | ❌ Not implemented | |

### Current Implementation

```python
# What we have - iterate over members
Iter[Attrs[MyClass]]  # Returns tuple of Member types
Members[MyClass]       # All members including methods
```

### Missing: Native Mapped Types

```typescript
// TypeScript - natural syntax
type Mapped<T> = { [K in keyof T]: T[K] };
type Optional<T> = { [K in keyof T]?: T[K] };
type Readonly<T> = { readonly [K in keyof T]: T[K] };
```

#### Ideal DX Proposal (No Grammar Change)

Use existing `Iter`, `Attrs`, and `NewProtocol`:

```python
# What we CAN build today:
type Mapped[T] = NewProtocol[
    *[
        Member[p.name, p.type, p.quals]
        for p in Iter[Attrs[T]]
    ]
]

# Optional (make fields None)
type Optional[T] = NewProtocol[
    *[
        Member[p.name, p.type | None, p.quals, None]
        for p in Iter[Attrs[T]]
    ]
]

# Key remapping (explicit)
type Prefixed[T] = NewProtocol[
    *[
        Member[
            StrConcat['prefix_', p.name],  # Need explicit naming
            p.type,
            p.quals,
        ]
        for p in Iter[Attrs[T]]
    ]
]
```

---

## 5. Type Guards and typeof

| TypeScript | Description | typemap Status | Notes |
|------------|-------------|----------------|-------|
| `typeof x` | Get type of value | ⚠️ Partial | `GetSpecialAttr` exists |
| `instanceof` | Instance check | ❌ Not implemented | |

### Current Implementation

```python
GetSpecialAttr[T, Literal["__name__"]]   # Get class name
GetSpecialAttr[T, Literal["__module__"]]  # Get module name
```

---

## 6. Indexed Access Types

| TypeScript | Description | typemap Status | Notes |
|------------|-------------|----------------|-------|
| `T['key']` | Access member type | ⚠️ Partial | Via `GetMemberType` |
| `T[K]` | Key access with union | ❌ Not implemented | See [docs/features/indexed_access.md](./features/indexed_access.md) |

---

## 7. Intersection & Union Operators

| TypeScript | Description | typemap Status | Notes |
|------------|-------------|----------------|-------|
| `T & U` | Intersection types | ❌ Not implemented | Not mentioned in PEP |
| `T \| U` | Union types | ✅ Native | Python's `\|` works |

### Missing: Intersection Types

```typescript
// TypeScript
type Combined = TypeA & TypeB;
interface A { a: string }
interface B { b: number }
type C = A & B;  // { a: string; b: number }
```

The PEP does not mention intersection types (`&`), which is a significant limitation compared to TypeScript.

#### Ideal DX Proposal (No Grammar Change)

Combine members using existing operators:

```python
# What we CAN build today:
# Combine two protocols into one

class A:
    a: str

class B:
    b: int

# Manual combination using NewProtocol
type C = NewProtocol[
    *[
        Member['a', str],
        Member['b', int],
    ]
]

# Or iterate and combine:
type UnionMembers[T, U] = NewProtocol[
    *[
        *[
            m for m in Iter[Attrs[T]]
        ],
        *[
            m for m in Iter[Attrs[U]]
        ],
    ]
]

# This is verbose but works!
```

---

---

## 8. Advanced Type Operators

| TypeScript | Description | typemap Status | Notes |
|------------|-------------|----------------|-------|
| `never` | Bottom type | ✅ Native | Python's `Never` |
| `unknown` | Top type | ⚠️ Partial | `typing.Any` |
| `any` | Dynamic type | ✅ Native | `typing.Any` |
| `void` | No return | ⚠️ Partial | `None` |
| `object` | Non-primitive | ❌ Not implemented | |

---

## 9. Type Assertions

| TypeScript | Description | typemap Status | Notes |
|------------|-------------|----------------|-------|
| `as` | Type assertion | ❌ Not implemented | |
| `<Type>` | Legacy assertion | ❌ Not implemented | |
| `infer` in constraints | Constrained inference | ❌ Not implemented | |

---

## 10. Numeric Literal Types

| TypeScript | Description | typemap Status | Notes |
|------------|-------------|----------------|-------|
| `0`, `1`, `2`, etc. | Numeric literals | ⚠️ Limited | Via `Literal[0]`, etc. |

---

## 11. Variadics

| TypeScript | Description | typemap Status | Notes |
|------------|-------------|----------------|-------|
| `...T` | Tuple spread | ✅ Implemented | Via `*Ts` syntax |
| `infer ...T` | Variadic inference | ❌ Not implemented | |

### Current Implementation

```python
# Works
class NewProtocol[*T]:
    pass
```

---

## Summary

### Implemented ✅

- String operations: `Uppercase`, `Lowercase`, `Capitalize`, `StrConcat`
- Type introspection: `Attrs`, `Members`, `GetMember`, `GetMemberType`
- Type checking: `IsAssignable`, `IsEquivalent`, `Bool`
- Type construction: `NewProtocol`, `UpdateClass`, `RaiseError`
- Annotations: `GetAnnotations`, `DropAnnotations`
- Tuple operations: `Length`, `Slice`
- Member types: `Member`, `Param` with qualifications

### Not Implemented ❌

**High Priority:**
- `KeyOf` - Get keys of type
- `Pick` / `Omit` - Property selection/exclusion
- `Partial` / `Required` - Optional/required modifiers
- `Record` - Key-value type construction
- `Exclude` / `Extract` - Union filtering
- `ReturnType` / `Parameters` - Function introspection
- `Readonly` - Make properties immutable

**Medium Priority:**
- True conditional types (`T extends U ? X : Y`)
- Mapped types with key remapping
- Intersection types (`&`)

**Low Priority:**
- Template literal types
- `infer` keyword for type inference
- Full `instanceof` support
- `NonNullable`, `InstanceType`

---

## References

- [TypeScript Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html)
- [TypeScript Conditional Types](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html)
- [TypeScript Mapped Types](https://www.typescriptlang.org/docs/handbook/2/mapped-types.html)
- [PEP 827 Draft](https://github.com/vercel/type-manipulation/blob/main/pep.rst)

---

*Last updated: 2026-03-02*
