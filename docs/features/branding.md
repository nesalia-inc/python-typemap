# Branding and Type Widening - TypeScript vs PEP 827

This document explains type branding and widening in TypeScript and their status in PEP 827.

---

## What is Type Branding?

Type branding is a TypeScript pattern to create "nominal" types from structural types. It adds a unique identifier to a type to make it distinct from other types that have the same structure.

---

## TypeScript Branding

### Basic Branding

```typescript
// Create a branded type
type UserId = string & { __brand: 'UserId' };
type OrderId = string & { __brand: 'OrderId' };

// Now they're distinct!
function getUser(id: UserId) { }
function getOrder(id: OrderId) { }

const userId = 'abc' as UserId;
const orderId = 'abc' as OrderId;

getUser(userId);  // OK
getOrder(orderId); // OK
getUser(orderId); // Error! OrderId is not UserId
```

### Using Interface

```typescript
interface Brand<T, K> {
  __brand: K;
  __value: T;
}

type UserId = Brand<string, 'UserId'>;
type OrderId = Brand<string, 'OrderId'>;

function createUserId(id: string): UserId {
  return { __brand: 'UserId', __value: id };
}
```

### Using Namespace

```typescript
namespace Types {
  export type UserId = string & { readonly __userId: unique symbol };
  export type OrderId = string & { readonly __orderId: unique symbol };
}

function getUser(id: Types.UserId) { }
function getOrder(id: Types.OrderId) { }

const userId = 'abc' as Types.UserId;
getUser(userId); // OK
```

### Real-World Example

```typescript
// Prevent mixing up IDs
type Email = string & { readonly __email: unique symbol };
type Password = string & { readonly __password: unique symbol };
type Username = string & { readonly __username: unique symbol };

function sendEmail(to: Email, subject: string) { }
function login(password: Password) { }

const email = 'user@example.com' as Email;
const password = 'secret' as Password;

sendEmail(email, 'Hello'); // OK
sendEmail(password, 'Hi'); // Error! Password is not Email
```

---

## Type Widening

TypeScript widens les types literal vers leur type de base :

```typescript
// TypeScript automatically widens
type T1 = 'hello';  // Type is 'hello'
type T2 = string;   // Type widened to string

// With const
const name = 'hello';  // Type is 'hello' (narrow)
let name2 = 'hello';   // Type is string (widened)
```

### `as const`

```typescript
// Force narrow type
const config = {
  apiUrl: 'https://api.example.com',
  port: 8080,
} as const;
// Type is:
// { readonly apiUrl: 'https://api.example.com'; readonly port: 8080 }
```

---

## PEP 827 Equivalent

### Nominal Types via Protocol

PEP 827 can create nominal types using `NewProtocol`:

```python
# Cannot truly replicate branding
# But can create distinct protocol types

# This is NOT the same as branding
class UserId:
    pass

class OrderId:
    pass
```

### Why Branding Doesn't Work

1. **Intersection types** (`&`) are not supported in PEP 827
2. **Unique symbols** don't exist in Python
3. **Nominal typing** requires explicit class/protocol creation

---

## Comparison Table

| TypeScript | PEP 827 | Notes |
|------------|---------|-------|
| `string & { __brand: 'X' }` | ❌ | No intersection types |
| `interface Brand<T, K>` | ⚠️ | Partial via Protocol |
| Type widening | ⚠️ | Different model |
| `as const` | ❌ | Not applicable |
| Unique symbol | ❌ | Python doesn't have it |

---

## Workarounds in PEP 827

### Using NewProtocol

```python
# Create distinct types
class UserId:
    value: str

class OrderId:
    value: str

def get_user(id: UserId) -> None:
    pass

def get_order(id: OrderId) -> None:
    pass

# Usage
user_id = UserId(value='abc')
order_id = OrderId(value='abc')

get_user(user_id)  # OK
get_order(order_id) # OK
# get_user(order_id) # Would error at runtime
```

### Using Class Wrappers

```python
# Similar to branded types but more explicit
class Email:
    def __init__(self, value: str):
        if '@' not in value:
            raise ValueError("Invalid email")
        self.value = value

class Password:
    def __init__(self, value: str):
        if len(value) < 8:
            raise ValueError("Password too short")
        self.value = value
```

### Using Type Aliases (Limited)

```python
# Can't prevent mixing, but documents intent
type UserId = str  # These are the SAME type!
type OrderId = str # No real distinction

# Just documentation
def get_user(id: UserId) -> None: ...
def get_order(id: OrderId) -> None: ...
```

---

## Summary

| Feature | TypeScript | PEP 827 |
|---------|-----------|---------|
| Brand via intersection | ✅ | ❌ |
| Brand via interface | ✅ | ⚠️ |
| Type widening | ✅ | N/A |
| `as const` | ✅ | ❌ |
| Unique symbol | ✅ | ❌ |

**Conclusion:** Type branding is not possible in PEP 827 without significant changes to the type system.

---

## Ideal DX Proposal (No Grammar Change)

### Goal: Create distinct types using NewProtocol

Use existing `NewProtocol` to create branded nominal types.

### What We Can Build Today

```python
# 1. Create branded types using NewProtocol
class UserIdDef:
    value: str

class OrderIdDef:
    value: str

# These are now distinct types (protocols)
# You can't accidentally mix them

def get_user(id: UserIdDef) -> None: ...
def get_order(id: OrderIdDef) -> None: ...

# 2. Create a helper to build branded types
def brand_type(T, name: str):
    """Create a branded type at runtime"""
    return NewProtocol[Member['value', T]]

# 3. Using a base class pattern
class Brand(Protocol):
    value: str

class UserId(Brand):
    pass

class OrderId(Brand):
    pass

# These satisfy Brand but are distinct
```

### Practical DX

```python
# Helper to create branded types
def Brand[T](name: str) -> type:
    """Create a nominal type"""
    return NewProtocol[Member['value', T]]

# Usage
UserId = Brand[str]('UserId')
OrderId = Brand[str]('OrderId')

# At runtime, they're the same structure
# At type-check time, they're distinct if using distinct classes
```

### Validator Pattern

```python
# Add validation with Field
class ValidatedBrand(Protocol[T]):
    value: T

class Email:
    value: str

    def __init__(self, v: str):
        if '@' not in v:
            raise ValueError("Invalid email")
        self.value = v

# Usage
email = Email('user@example.com')
# Type checker sees: Email (not just str)
```

### Summary

| Approach | Type-Safe | Runtime Safe |
|----------|-----------|---------------|
| `NewProtocol[Member['value', T]]` | ✅ | ❌ |
| Classes with validation | ✅ | ✅ |
| Distinct classes | ✅ | ❌ |

The key insight: use **distinct Protocol classes** to create nominally distinct types.

---

## References

- [TypeScript Branding](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-aliases)
- [Unique Symbol](https://www.typescriptlang.org/docs/handbook/symbols.html#unique-symbol)

---

*Last updated: 2026-03-02*
