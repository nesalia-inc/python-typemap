# DeepPartial helper for typemap
# This adds DeepPartial functionality on top of existing typemap operators
# No modification to core typemap needed!

from typemap.type_eval import eval_typing
from typemap_extensions import (
    Attrs, Iter, NewProtocol, Member, IsAssignable, Length
)
from typing import Literal, get_args

# ============================================================================
# DeepPartial - Makes all nested fields optional recursively
# ============================================================================

# Key insight: We can detect if a type is primitive using Length[Attrs[T]]
# - If Length[Attrs[T]] == 0, it's a primitive (str, int, etc.)
# - If Length[Attrs[T]] > 0, it's a complex type (class with attributes)


def _get_members_from_attrs(attrs_result):
    """Extract Member objects from Attrs result"""
    # attrs_result is a GenericAlias, we need to get the tuple inside
    # The structure is: tuple[Member[...], Member[...], ...]

    # Convert to tuple to see what's inside
    # The result might be wrapped in an unpacking

    # Try to get args first
    if hasattr(attrs_result, '__args__'):
        args = get_args(attrs_result)
        # If the first arg is a tuple, that's our members
        if args and isinstance(args[0], tuple):
            # Handle the *tuple case
            if len(args[0]) > 0:
                return args[0]
        return args

    return attrs_result


def make_deeppartial_class(T):
    """
    Create a DeepPartial version of a class at runtime.

    This function:
    1. Gets all attributes of T
    2. For each attribute:
       - If it's a primitive (int, str, etc.), makes it optional
       - If it's a complex type, recursively applies DeepPartial
    3. Returns a new class with all fields optional

    Usage:
        DeepPartialUser = make_deeppartial_class(User)
    """
    # Get the original attributes
    attrs_result = eval_typing(Attrs[T])

    # Extract members
    members = _get_members_from_attrs(attrs_result)

    new_annotations = {}

    for member in members:
        # member is a Member type with associated types
        # We can access .name and .type using GetMemberType

        # Get the name
        name_literal = member.name
        name = eval_typing(name_literal)
        # If it's a Literal, extract the actual string value
        if hasattr(name, '__args__'):
            name = name.__args__[0]

        # Get the type
        field_type = eval_typing(member.type)

        # Check if this is a complex type
        # We check if Attrs[field_type] has any members
        try:
            nested_attrs_result = eval_typing(Attrs[field_type])
            nested_members = _get_members_from_attrs(nested_attrs_result)
            has_nested = len(nested_members) > 0
        except:
            has_nested = False

        if has_nested:
            # It's a complex type - recursively apply DeepPartial
            nested_dp = make_deeppartial_class(field_type)
            new_annotations[name] = nested_dp | None
        else:
            # It's a primitive - just make optional
            new_annotations[name] = field_type | None

    # Create the new class
    class_name = f"DeepPartial_{T.__name__}"
    new_class = type(class_name, (), {"__annotations__": new_annotations})

    return new_class


def DeepPartial(T):
    """
    Type alias helper for DeepPartial.

    At runtime, this creates a new class with all nested fields optional.

    Usage:
        DeepPartialUser = DeepPartial(User)
    """
    return make_deeppartial_class(T)


# Example usage in type alias context:
# Since we can't do true recursion in type aliases,
# we provide this as a runtime helper

__all__ = ['make_deeppartial_class', 'DeepPartial']
