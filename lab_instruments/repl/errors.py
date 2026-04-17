"""Shared error classes that the REPL surfaces through ``ctx.report_error``.

Centralized so the command layer, shell, and any future consumer keep the
same surface. If this tuple ever gains or loses a class (e.g. adding
``OverflowError``), every handler updates in lock-step.
"""

EXPR_ERRORS: tuple[type[BaseException], ...] = (
    TypeError,
    NameError,
    ZeroDivisionError,
    ValueError,
    IndexError,
    KeyError,
    ArithmeticError,
    SyntaxError,
)
