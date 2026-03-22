"""Unified variable resolution and safe expression evaluation.

Variable syntax supported in script files:
  {varname}   Python f-string style  (preferred)
  $varname    shell-style            (still supported)
"""

import ast
import re
from typing import Any, Dict, Optional

from .measurement_store import MeasurementStore

# Combined pattern: matches either $varname or {varname}
_SUBST_RE = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)|\{([A-Za-z_][A-Za-z0-9_]*)\}")

# Legacy ${name} pattern kept for explicit backward-compat callers
_VAR_RE = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)")

# Identifiers that cannot be used as variable/label names
_RESERVED = frozenset({"last"})


def validate_name(name: str) -> Optional[str]:
    """Return an error message if *name* is not a valid variable/label identifier, else None."""
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return f"Invalid name '{name}': must be alphanumeric + underscore, starting with a letter or underscore."
    if name in _RESERVED:
        return f"'{name}' is a reserved keyword."
    return None


def substitute_vars(
    text: str,
    script_vars: Dict[str, str],
    measurements: Optional[MeasurementStore] = None,
) -> str:
    """Replace $name and {name} references in *text*.

    Both syntaxes are supported:
      {varname}  — Python f-string style (preferred)
      $varname   — shell-style (still supported)

    Resolution order: script_vars first, then measurement store labels.
    'last' resolves to the most recent measurement value.
    Unresolved tokens are left as-is.
    """

    def _replace(match: re.Match) -> str:
        # group(1) is from $name, group(2) is from {name}
        name = match.group(1) if match.group(1) is not None else match.group(2)
        # Script variables take priority
        if name in script_vars:
            return str(script_vars[name])
        # 'last' keyword -> most recent measurement value
        if name == "last" and measurements is not None:
            last = measurements.get_last()
            if last is not None:
                return str(last["value"])
        # Measurement store label lookup
        if measurements is not None:
            entry = measurements.get_by_label(name)
            if entry is not None:
                return str(entry["value"])
        # No match -- leave the original token so the user sees what wasn't resolved
        return match.group(0)

    return _SUBST_RE.sub(_replace, text)


def substitute_legacy(text: str, variables: Dict[str, str]) -> str:
    """Legacy ${name} substitution for backward compat during migration."""
    result = text
    for name, value in variables.items():
        result = result.replace(f"${{{name}}}", str(value))
    return result


def safe_eval(expr: str, names: Dict[str, Any]) -> Any:
    """Evaluate a math expression safely using AST walking.

    Supports: +, -, *, /, **, %, unary +/-, parentheses,
    numeric constants, named variables, subscript (dict[key]),
    and functions: abs, min, max, round.
    """
    allowed_funcs = {"abs": abs, "min": min, "max": max, "round": round}

    def _eval(node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Only numeric constants are allowed.")
        if isinstance(node, ast.Name):
            if node.id in names:
                return names[node.id]
            if node.id in allowed_funcs:
                return allowed_funcs[node.id]
            raise ValueError(f"Unknown name '{node.id}'.")
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            ops = {
                ast.Add: lambda a, b: a + b,
                ast.Sub: lambda a, b: a - b,
                ast.Mult: lambda a, b: a * b,
                ast.Div: lambda a, b: a / b,
                ast.Pow: lambda a, b: a**b,
                ast.Mod: lambda a, b: a % b,
            }
            op_func = ops.get(type(node.op))
            if op_func is None:
                raise ValueError("Operator not allowed.")
            return op_func(left, right)
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            raise ValueError("Unary operator not allowed.")
        if isinstance(node, ast.Subscript):
            value = _eval(node.value)
            if not isinstance(value, dict):
                raise ValueError("Subscript base must be a dict.")
            # Python 3.8 wraps slice in ast.Index; 3.9+ does not
            slice_node = node.slice
            if hasattr(ast, "Index") and isinstance(slice_node, ast.Index):
                slice_node = slice_node.value
            if isinstance(slice_node, ast.Constant):
                key = slice_node.value
            elif isinstance(slice_node, ast.Name):
                key = slice_node.id
            else:
                key = _eval(slice_node)
            return value[key]
        if isinstance(node, ast.Call):
            func = _eval(node.func)
            call_args = [_eval(a) for a in node.args]
            if func in allowed_funcs.values():
                return func(*call_args)
            raise ValueError("Function not allowed.")
        raise ValueError("Expression not allowed.")

    parsed = ast.parse(expr, mode="eval")
    return _eval(parsed)
