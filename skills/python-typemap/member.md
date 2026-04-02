# Member Type Descriptor

`Member` is the fundamental type descriptor in python-typemap, representing a named type field with optional qualifiers.

## Definition

```python
class Member[N: str, T, Q: MemberQuals = typing.Never, ...]:
    type name = N
    type type = T
    type quals = Q
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `N` | `str` | The member name (literal string) |
| `T` | `Any` | The member type |
| `Q` | `MemberQuals` | Optional qualifiers (readonly, required, etc.) |

## MemberQuals

Qualifiers modify member behavior:

```python
class MemberQuals(typing.Protocol):
    """Qualifiers for a Member type."""
    readonly: bool
    required: bool
    deprecated: bool
```

### Built-in Qualifiers

| Qualifier | Effect |
|------------|--------|
| `readonly` | Field cannot be modified |
| `required` | Field must be provided |
| `deprecated` | Field is deprecated |

## Creating Members

### From Class Attributes

```python
import typemap_extensions as tm
from typemap import eval_typing

class User:
    name: str
    email: str

# Get all members as Member descriptors
members = eval_typing(tm.Attrs[User])
# Result: tuple[Member['name', str], Member['email', str]]
```

### From Type Annotations

```python
from typemap.typing import Member

# Explicit Member creation
NameMember = Member['name', str]
EmailMember = Member['email', str, {"readonly": True}]
```

## Accessing Member Properties

```python
member: Member['name', str] = ...

name = member.name   # 'name' (literal)
t = member.type      # str
quals = member.quals # MemberQuals instance
```

## Use Cases

### 1. Field Introspection

```python
def inspect_fields(cls: type) -> list[str]:
    """Get all field names of a class."""
    members = eval_typing(tm.Attrs[cls])
    return [m.name for m in members]
```

### 2. Schema Generation

```python
def generate_schema(cls: type) -> dict:
    """Generate JSON schema from class."""
    members = eval_typing(tm.Attrs[cls])
    properties = {}
    required = []

    for member in members:
        properties[member.name] = {
            "type": get_json_type(member.type)
        }
        if member.quals.required:
            required.append(member.name)

    return {"properties": properties, "required": required}
```

### 3. Form Generation

```python
def generate_form(cls: type) -> list[FormField]:
    """Generate form fields from class."""
    members = eval_typing(tm.Attrs[cls])
    fields = []

    for member in members:
        fields.append(FormField(
            name=member.name,
            type=get_form_type(member.type),
            required=member.quals.required,
            readonly=member.quals.readonly
        ))

    return fields
```

## Member with Qualifiers

### Readonly Fields

```python
class Config:
    id: str  # Regular
    api_key: str  # readonly

# Access qualifiers
members = eval_typing(tm.Attrs[Config])
for m in members:
    if m.quals.readonly:
        print(f"{m.name} is readonly")
```

### Required Fields

```python
@dataclass
class User:
    name: str           # required by default
    email: str | None = None  # optional

# Check what's required
members = eval_typing(tm.Attrs[User])
required = [m.name for m in members if m.quals.required]
# ['name']
```

## Advanced: Custom Qualifiers

```python
from typemap.typing import MemberQuals

class MyQuals(MemberQuals):
    """Custom qualifier for validation rules."""
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None

# Use custom qualifier
ValidatedField = Member['username', str, {"min_length": 3, "max_length": 20}]
```

## Member vs Attrs

| Aspect | `Member` | `Attrs` |
|--------|----------|---------|
| What | Single field descriptor | All fields of a type |
| Returns | One `Member` instance | Tuple of `Member` instances |
| Use | When you need one field | When you need all fields |
