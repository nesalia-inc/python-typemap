# Practical Examples

Real-world examples of using python-typemap.

## Example 1: REST API Layer

### Setup

```python
from dataclasses import dataclass
from datetime import datetime
from typemap import eval_typing
import typemap_extensions as tm

@dataclass
class User:
    id: int
    name: str
    email: str
    password_hash: str
    created_at: datetime
    updated_at: datetime
```

### API DTOs

```python
# Public user profile (no sensitive data)
PublicUser = eval_typing(
    tm.Omit[User, 'password_hash' | 'updated_at']
)

# User creation (all fields except id and timestamps)
UserCreate = eval_typing(
    tm.Partial[
        tm.Omit[User, 'id' | 'created_at' | 'updated_at']
    ]
)

# User update (all fields optional)
UserUpdate = eval_typing(
    tm.Partial[User]
)
```

### Usage

```python
# GET /users/:id - returns public data only
def get_user(user_id: int) -> PublicUser:
    user = db.get_user(user_id)
    # Type checker ensures no password_hash leaks
    return PublicUser(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at
    )

# PATCH /users/:id - any field can be updated
def update_user(user_id: int, data: UserUpdate) -> PublicUser:
    validated = validate_update(data)
    db.update_user(user_id, validated)
    return get_user(user_id)
```

---

## Example 2: Form Generation

### Model

```python
@dataclass
class ContactForm:
    name: str
    email: str
    subject: str
    message: str
    phone: str | None = None
```

### Form Generator

```python
def generate_form(cls: type) -> list[FormField]:
    """Generate HTML form fields from a class."""
    members = eval_typing(tm.Attrs[cls])
    fields = []

    type_map = {
        str: 'text',
        int: 'number',
        bool: 'checkbox',
        'email': 'email',
        'phone': 'tel',
    }

    for member in members:
        input_type = type_map.get(member.type, 'text')

        # Determine if required
        is_required = member.quals.required

        # Check for optional type
        is_optional = (
            isinstance(member.type, types.UnionType) and
            type(None) in types.get_args(member.type)
        )

        fields.append(FormField(
            name=member.name,
            input_type=input_type,
            required=is_required and not is_optional,
            label=humanize(member.name),
            placeholder=f"Enter {member.name}"
        ))

    return fields

# Usage
fields = generate_form(ContactForm)
# Returns FormField objects ready for template
```

---

## Example 3: Database Schema

### Model

```python
class Product:
    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
```

### Schema Extraction

```python
from typemap.type_eval import eval_typing
import typemap_extensions as tm

def extract_table_schema(cls: type) -> dict:
    """Extract database table schema from model."""
    members = eval_typing(tm.Attrs[cls])

    columns = []
    primary_key = None
    indexes = []

    for member in members:
        col = {
            'name': member.name,
            'type': sql_type(member.type),
            'nullable': is_nullable(member.type),
            'default': get_default(member),
        }

        columns.append(col)

        if member.name == 'id':
            primary_key = member.name
        elif member.name.endswith('_id'):
            indexes.append(member.name)

    return {
        'columns': columns,
        'primary_key': primary_key,
        'indexes': indexes
    }

# Output:
# {
#     'columns': [
#         {'name': 'id', 'type': 'INTEGER', 'nullable': False, 'default': None},
#         {'name': 'name', 'type': 'VARCHAR(255)', 'nullable': False, 'default': None},
#         ...
#     ],
#     'primary_key': 'id',
#     'indexes': []
# }
```

---

## Example 4: Validation Library

### Type Guard

```python
from typing import TypeGuard

def is_user(data: dict) -> TypeGuard[User]:
    """Check if dict matches User structure."""
    required_keys = eval_typing(tm.KeyOf[User])
    return all(key in data for key in required_keys)

def validate_user(data: dict) -> tuple[bool, User | None]:
    """Validate and convert dict to User."""
    if not is_user(data):
        return False, None

    try:
        return True, User(**data)
    except (TypeError, ValueError) as e:
        return False, None
```

### Partial Validation

```python
def validate_partial(data: dict, cls: type) -> tuple[bool, dict]:
    """Validate subset of fields."""
    partial_cls = eval_typing(tm.Partial[cls])
    keys = eval_typing(tm.KeyOf[partial_cls])

    errors = {}
    for key in keys:
        if key in data:
            if not isinstance(data[key], str):
                errors[key] = f"Expected str, got {type(data[key]).__name__}"

    return len(errors) == 0, errors
```

---

## Example 5: Plugin System

### Plugin Definition

```python
@dataclass
class PluginManifest:
    name: str
    version: str
    author: str
    dependencies: list[str]
    permissions: list[str]

@dataclass
class PluginConfig:
    manifest: PluginManifest
    enabled: bool
    settings: dict
```

### Schema Validation

```python
def register_plugin(config: dict) -> PluginConfig:
    """Register a plugin with validation."""
    # Get required plugin fields
    manifest_keys = eval_typing(tm.KeyOf[PluginManifest])

    # Validate manifest
    if 'manifest' not in config:
        raise PluginError("Missing manifest")

    manifest_data = config['manifest']
    missing = [k for k in manifest_keys if k not in manifest_data]

    if missing:
        raise PluginError(f"Missing manifest fields: {missing}")

    # Create validated config
    return PluginConfig(
        manifest=PluginManifest(**manifest_data),
        enabled=config.get('enabled', True),
        settings=config.get('settings', {})
    )
```

---

## Example 6: Event System

### Event Definition

```python
@dataclass
class UserEvent:
    user_id: int
    event_type: str
    timestamp: datetime
    data: dict

@dataclass
class OrderEvent:
    order_id: int
    event_type: str
    timestamp: datetime
    data: dict
```

### Unified Handler

```python
def create_event_handler(event: dict) -> UserEvent | OrderEvent:
    """Create appropriate event from dict."""
    event_type = event.get('type')

    if event_type in ('user.created', 'user.updated', 'user.deleted'):
        keys = eval_typing(tm.KeyOf[UserEvent])
        if all(k in event for k in keys):
            return UserEvent(**event)

    elif event_type in ('order.created', 'order.shipped', 'order.delivered'):
        keys = eval_typing(tm.KeyOf[OrderEvent])
        if all(k in event for k in keys):
            return OrderEvent(**event)

    raise ValueError(f"Unknown event type: {event_type}")
```

---

## Example 7: Testing

### Factory Pattern

```python
import typing

def make_factory(cls: type):
    """Create a factory that generates instances with defaults."""
    members = eval_typing(tm.Attrs[cls])

    def create(**overrides) -> cls:
        kwargs = {}

        for member in members:
            if member.name in overrides:
                kwargs[member.name] = overrides[member.name]
            elif has_default(cls, member.name):
                kwargs[member.name] = get_default(cls, member.name)
            else:
                # Use sensible defaults based on type
                kwargs[member.name] = get_fake_value(member.type)

        return cls(**kwargs)

    return create

# Usage
create_user = make_factory(User)
user = create_user(name="Test User")
```

### Property Testing

```python
from hypothesis import given, strategies as st

@given(st.dictionaries(st.text(), st.integers()))
def test_user_serialization(data: dict):
    """Test that partial user data can be validated."""
    PartialUser = eval_typing(tm.Partial[User])

    # Should not raise for partial data
    instance = PartialUser(**data)
    assert isinstance(instance, User)
```
