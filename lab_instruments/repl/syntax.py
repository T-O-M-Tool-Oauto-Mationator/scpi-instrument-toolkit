"""Unified variable resolution and safe expression evaluation.

Variable syntax: {varname}  (Python f-string style)
"""

import ast
import re
from typing import Any

from .measurement_store import MeasurementStore

# Pattern: matches {varname}
_SUBST_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_.]*)\}")

# Identifiers that cannot be used as variable/label names
_RESERVED = frozenset({"last"})


def strip_inline_comment(text: str) -> str:
    """Remove a trailing ``# comment`` from *text*, respecting quoted strings.

    Examples::

        strip_inline_comment('x += 1  # bump')      -> 'x += 1'
        strip_inline_comment('name = "a # b"')       -> 'name = "a # b"'
        strip_inline_comment('count++')               -> 'count++'
    """
    in_sq = in_dq = False
    for i, ch in enumerate(text):
        if ch == '"' and not in_sq:
            in_dq = not in_dq
        elif ch == "'" and not in_dq:
            in_sq = not in_sq
        elif ch == "#" and not in_sq and not in_dq:
            return text[:i].rstrip()
    return text


def validate_name(name: str) -> str | None:
    """Return an error message if *name* is not a valid variable/label identifier, else None."""
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return f"Invalid name '{name}': must be alphanumeric + underscore, starting with a letter or underscore."
    if name in _RESERVED:
        return f"'{name}' is a reserved keyword."
    return None


def substitute_vars(
    text: str,
    script_vars: dict[str, Any],
    measurements: MeasurementStore | None = None,
) -> str:
    """Replace {name} references in *text*.

    Resolution order: script_vars first, then measurement store labels.
    'last' resolves to the most recent measurement value.
    Unresolved tokens are left as-is.
    """

    def _replace(match: re.Match) -> str:
        name = match.group(1)
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


def substitute_expand(text: str, variables: dict[str, Any]) -> str:
    """Replace {name} references from a variables dict during script expansion."""

    def _replace(match: re.Match) -> str:
        name = match.group(1)
        if name in variables:
            return str(variables[name])
        return match.group(0)

    return _SUBST_RE.sub(_replace, text)


def safe_eval(expr: str, names: dict[str, Any], *, strict: bool = True) -> Any:
    """Evaluate an expression safely using AST walking (no exec/eval).

    Operators: ``+ - * / // ** % ^ | & << >>``
    Unary: ``+ - not ~``
    Comparisons: ``== != < <= > >=``
    Boolean: ``and or not``
    Ternary: ``a if cond else b``
    Containers: ``[list]`` ``(tuple)`` subscript ``x[i]``
    Constants: ``pi e inf nan True False`` and string/number literals
    Functions: ``abs min max sum round pow divmod len``
               ``int float str bool hex bin oct ord chr``
               ``sqrt log log2 log10 exp ceil floor hypot``
               ``sin cos tan asin acos atan atan2 degrees radians``

    Errors (Python-style):
      * ``NameError`` -- unknown identifier (strict mode).
      * ``ZeroDivisionError`` -- ``/ // %`` by zero.
      * ``TypeError`` -- incompatible operand types or unsupported literal.
      * ``IndexError`` / ``KeyError`` -- bad subscript.

    When ``strict=False`` (legacy), unknown identifiers fall back to their
    bare name as a string so that expressions like ``status == passed``
    work without the labels being declared. Default is ``strict=True``.
    """
    import math

    allowed_funcs: dict[str, Any] = {
        # Type conversions
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
        "hex": hex,
        "bin": bin,
        "oct": oct,
        "ord": ord,
        "chr": chr,
        # Math basics
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "pow": pow,
        "divmod": divmod,
        "len": len,
        # Math module
        "sqrt": math.sqrt,
        "log": math.log,
        "log2": math.log2,
        "log10": math.log10,
        "exp": math.exp,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "atan2": math.atan2,
        "degrees": math.degrees,
        "radians": math.radians,
        "ceil": math.ceil,
        "floor": math.floor,
        "hypot": math.hypot,
        # NaN / Inf checks
        "is_nan": math.isnan,
        "is_inf": math.isinf,
        "is_finite": math.isfinite,
        # Constants
        "pi": math.pi,
        "e": math.e,
        "inf": math.inf,
        "nan": math.nan,
        "true": True,
        "True": True,
        "false": False,
        "False": False,
    }

    # Rewrite || and && to Python boolean operators
    expr = expr.replace("||", " or ").replace("&&", " and ")
    # Rewrite ^ to ** so users can write 2^3 to mean 2**3
    expr = expr.replace("^", "**")

    def _eval(node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float, str, bool)):
                return node.value
            raise TypeError(f"constant type not allowed: {type(node.value).__name__}")
        if isinstance(node, ast.Name):
            if node.id in names:
                return names[node.id]
            if node.id in allowed_funcs:
                return allowed_funcs[node.id]
            if strict:
                raise NameError(f"name '{node.id}' is not defined")
            return node.id
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            ops = {
                ast.Add: lambda a, b: a + b,
                ast.Sub: lambda a, b: a - b,
                ast.Mult: lambda a, b: a * b,
                ast.Div: lambda a, b: a / b,
                ast.FloorDiv: lambda a, b: a // b,
                ast.Pow: lambda a, b: a**b,
                ast.Mod: lambda a, b: a % b,
                ast.BitOr: lambda a, b: int(a) | int(b),
                ast.BitAnd: lambda a, b: int(a) & int(b),
                ast.BitXor: lambda a, b: int(a) ^ int(b),
                ast.LShift: lambda a, b: int(a) << int(b),
                ast.RShift: lambda a, b: int(a) >> int(b),
            }
            op_func = ops.get(type(node.op))
            if op_func is None:
                raise TypeError(f"operator not allowed: {type(node.op).__name__}")
            return op_func(left, right)
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            if isinstance(node.op, ast.Not):
                return not operand
            if isinstance(node.op, ast.Invert):
                return ~int(operand)
            raise ValueError("Unary operator not allowed.")
        if isinstance(node, ast.Compare):
            left = _eval(node.left)
            for op, comparator in zip(node.ops, node.comparators, strict=False):
                right = _eval(comparator)
                cmp_ops = {
                    ast.Eq: lambda a, b: a == b,
                    ast.NotEq: lambda a, b: a != b,
                    ast.Lt: lambda a, b: a < b,
                    ast.LtE: lambda a, b: a <= b,
                    ast.Gt: lambda a, b: a > b,
                    ast.GtE: lambda a, b: a >= b,
                }
                cmp_func = cmp_ops.get(type(op))
                if cmp_func is None:
                    raise ValueError("Comparison not allowed.")
                if not cmp_func(left, right):
                    return False
                left = right
            return True
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                result = True
                for v in node.values:
                    result = _eval(v)
                    if not result:
                        return result
                return result
            if isinstance(node.op, ast.Or):
                result = False
                for v in node.values:
                    result = _eval(v)
                    if result:
                        return result
                return result
            raise ValueError("Boolean operator not allowed.")
        if isinstance(node, ast.IfExp):
            return _eval(node.body) if _eval(node.test) else _eval(node.orelse)
        if isinstance(node, ast.List):
            return [_eval(el) for el in node.elts]
        if isinstance(node, ast.Tuple):
            return tuple(_eval(el) for el in node.elts)
        if isinstance(node, ast.Subscript):
            value = _eval(node.value)
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
            # Handle keyword arguments (e.g. round(3.14, ndigits=2))
            call_kwargs = {}
            for kw in node.keywords:
                call_kwargs[kw.arg] = _eval(kw.value)
            if callable(func) and (func in allowed_funcs.values() or func in (True, False)):
                return func(*call_args, **call_kwargs)
            raise ValueError("Function not allowed.")
        if isinstance(node, ast.Attribute):
            # Allow method calls on results, e.g. str methods
            raise ValueError("Attribute access not allowed in expressions.")
        raise ValueError(f"Expression node not allowed: {type(node).__name__}")

    parsed = ast.parse(expr, mode="eval")
    return _eval(parsed)
