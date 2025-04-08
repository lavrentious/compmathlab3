from typing import Any

import sympy as sp  # type: ignore

from config import PRECISION


def is_float(s: Any) -> bool:
    if type(s) == float:
        return True
    if type(s) == str:
        s = s.replace(",", ".")
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_int(s: Any) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False


def to_float(s: Any) -> float:
    if type(s) == float:
        return s
    if type(s) == str:
        s = s.replace(",", ".")
    return float(s)


def to_sp_float(s: Any) -> sp.Float:
    if type(s) == sp.Float:
        return s
    if type(s) == str:
        s = s.replace(",", ".")
    return sp.Float(s, PRECISION)
