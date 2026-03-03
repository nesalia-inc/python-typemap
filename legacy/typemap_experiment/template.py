# Template helper for typemap
# This adds Template literal string functionality as a type operator

from typemap.type_eval import eval_typing, register_evaluator, _ensure_context
from typemap.type_eval._eval_typing import _eval_types
from typemap.type_eval import _typing_inspect
from typemap.type_eval._eval_operators import _lift_over_unions
from typemap_experiment.typing import Template
from typing import Literal, get_args


def _from_literal(val):
    """Extract value from a Literal type."""
    if _typing_inspect.is_literal(val):
        args = get_args(val)
        if len(args) == 1:
            return args[0]
        return args
    raise AssertionError(f"expected a literal type, got {val!r}")


@register_evaluator(Template)
@_lift_over_unions
def _eval_Template(*parts, ctx):
    """Evaluate Template literal.

    Template[*Parts] concatenates all parts into a single string literal.
    Each part can be:
    - A string Literal -> use the value directly
    - A type that evaluates to a string -> use its literal value

    Example:
        Template['/', Resource, '/id']
        # For Resource = Literal['users'], returns: Literal['/users/id']
    """
    result_parts = []
    for part in parts:
        evaluated = _eval_types(part, ctx)
        lit_val = _from_literal(evaluated)
        if not isinstance(lit_val, str):
            raise TypeError(
                f"Template part must be a string literal, got {lit_val!r}"
            )
        result_parts.append(lit_val)

    return Literal[''.join(result_parts)]


# Also provide convenience runtime functions
def template(*parts):
    """
    Simple template literal string builder.

    Usage:
        template('hello', 'world')  # Literal['helloworld']
        template('/', 'users', '/id')  # Literal['/users/id']
    """
    return Literal[''.join(parts)]


__all__ = ['Template', 'template']
