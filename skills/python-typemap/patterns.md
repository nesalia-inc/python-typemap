# Common Usage Patterns

This guide shows common patterns for using python-typemap effectively.

## Type Transformation Patterns

### 1. API Response Stripping

Remove sensitive fields from API responses:

```python
import typemap_extensions as tm
from typemap import eval_typing

class User:
    id: int
    email: str
    password_hash: str
    created_at: datetime

# For public API - no password!
PublicUser = eval_typing(tm.Omit[User, 'password_hash'])

# For admin API - no timestamps!
AdminUser = eval_typing(tm.Omit[User, 'created_at'])
```

### 2. Create/Update DTOs

Different types for different operations:

```python
# All fields optional for creation
class UserCreate:
    name: str | None = None
    email: str | None = None
    age: int | None = None

# With eval_typing on existing class
UserCreateDTO = eval_typing(tm.Partial[User])

# Only specific fields for profile update
UserUpdateDTO = eval_typing(
    tm.Partial[
        tm.Pick[User, 'name' | 'email']
    ]
)
```

### 3. Immutable Data Classes

Make data classes immutable after creation:

```python
from typing import Readonly

# Create an immutable version
ImmutableUser = eval_typing(tm.Readonly[User])

# Validate at runtime
def create_user(data: dict) -> ImmutableUser:
    return ImmutableUser(**data)
```

## Introspection Patterns

### 4. Dynamic Form Generation

```python
def generate_form_fields(cls: type) -> list[dict]:
    """Generate form configuration from class."""
    members = eval_typing(tm.Attrs[cls])
    fields = []

    for member in members:
        field = {
            'name': member.name,
            'type': get_html_input_type(member.type),
            'required': member.quals.required,
        }
        fields.append(field)

    return fields

# Usage
fields = generate_form_fields(User)
# [{'name': 'name', 'type': 'text', 'required': True}, ...]
```

### 5. JSON Schema Generation

```python
def to_json_schema(cls: type) -> dict:
    """Convert class to JSON Schema."""
    members = eval_typing(tm.Attrs[cls])
    properties = {}
    required = []

    for member in members:
        prop_type = member.type

        # Convert Python type to JSON Schema type
        if prop_type is str:
            json_type = "string"
        elif prop_type is int:
            json_type = "integer"
        elif prop_type is bool:
            json_type = "boolean"
        else:
            json_type = "object"

        properties[member.name] = {"type": json_type}

        if member.quals.required:
            required.append(member.name)

    return {
        "type": "object",
        "properties": properties,
        "required": required
    }
```

### 6. Database Model to Schema

```python
class UserModel:
    """SQLAlchemy-like model."""
    __tablename__ = 'users'

    id: int
    name: str
    email: str
    created_at: datetime

def extract_columns(model: type) -> list[Column]:
    """Extract column definitions from model."""
    members = eval_typing(tm.Attrs[model])
    columns = []

    for member in members:
        columns.append(Column(
            name=member.name,
            type=map_to_db_type(member.type),
            nullable=is_nullable(member.type),
            primary_key=(member.name == 'id')
        ))

    return columns
```

## Validation Patterns

### 7. Type-Safe Validation

```python
from typing import get_type_hints

def validate_dict(data: dict, cls: type) -> tuple[bool, list[str]]:
    """Validate dict against class type hints."""
    hints = get_type_hints(cls)
    errors = []

    for field, expected_type in hints.items():
        if field not in data:
            # Check if field is required
            members = eval_typing(tm.Attrs[cls])
            for m in members:
                if m.name == field and not m.quals.required:
                    continue
            errors.append(f"Missing required field: {field}")
        elif not isinstance(data[field], expected_type):
            errors.append(f"Invalid type for {field}")

    return len(errors) == 0, errors
```

### 8. Selective Update

```python
def partial_update(original: User, updates: dict) -> User:
    """Partially update a user, validating keys exist."""
    # Get allowed keys
    allowed_keys = eval_typing(tm.KeyOf[User])

    # Filter updates to only allowed keys
    valid_updates = {
        k: v for k, v in updates.items()
        if k in allowed_keys
    }

    return User(**{**asdict(original), **valid_updates})
```

## Composition Patterns

### 9. Complex Type Transformations

```python
# Chain transformations
type1 = tm.Omit[User, 'password']
type2 = tm.Partial[type1]
type3 = tm.Readonly[type2]

# Or inline
ComplexUser = eval_typing(
    tm.Readonly[
        tm.Partial[
            tm.Omit[User, 'password']
        ]
    ]
)
```

### 10. Conditional Types

```python
def conditional_pick(include_admin: bool, cls: type) -> type:
    """Pick fields based on condition."""
    if include_admin:
        return eval_typing(tm.Pick[cls, 'id' | 'name' | 'email' | 'role'])
    else:
        return eval_typing(tm.Pick[cls, 'id' | 'name' | 'email'])
```

## Performance Patterns

### 11. Caching Evaluations

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_partial_type(cls: type):
    """Cache Partial evaluations."""
    return eval_typing(tm.Partial[cls])

@lru_cache(maxsize=128)
def get_keys(cls: type):
    """Cache KeyOf evaluations."""
    return eval_typing(tm.KeyOf[cls])
```

### 12. Lazy Evaluation

```python
from typing import Generic, TypeVar

T = TypeVar('T')

class LazyType(Generic[T]):
    """Lazy type that evaluates on first access."""
    _evaluated: T | None = None

    def __init__(self, expr):
        self._expr = expr

    @property
    def value(self) -> T:
        if self._evaluated is None:
            self._evaluated = eval_typing(self._expr)
        return self._evaluated
```

## Anti-Patterns to Avoid

### Don't: Evaluate in Hot Loops

```python
# Bad - evaluates every iteration
for cls in classes:
    keys = eval_typing(tm.KeyOf[cls])  # Expensive!

# Good - evaluate once
key_cache = {cls: eval_typing(tm.KeyOf[cls]) for cls in classes}
for cls in classes:
    keys = key_cache[cls]
```

### Don't: Nest Too Deeply

```python
# Bad - hard to debug
Result = eval_typing(
    tm.Readonly[
        tm.Partial[
            tm.DeepPartial[
                tm.Omit[...]
            ]
        ]
    ]
)

# Good - intermediate variables
WithoutPassword = tm.Omit[User, 'password']
OptionalFields = tm.Partial[WithoutPassword]
ImmutableResult = tm.Readonly[OptionalFields]
```
