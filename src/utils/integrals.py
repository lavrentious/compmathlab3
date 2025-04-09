import sympy as sp  # type: ignore
import math
from config import PRECISION
from logger import GlobalLogger
from utils.math import Number, f_str_expr_to_sp_lambda
from utils.reader import Preset
from utils.validation import to_sp_float
import re

logger = GlobalLogger()


class FunctionExpr:
    f: sp.Lambda

    def __init__(
        self,
        f_str: str | None = None,
        f: sp.Lambda | None = None,
    ) -> None:
        """
        supported variants:
        1. FunctionExpr(f=)
        2. FunctionExpr(f_str=)
        """
        if f is not None:
            self.f = f
        elif f_str is not None:
            self.f = f_str_expr_to_sp_lambda(f_str)
        else:
            raise ValueError("f or f_str must be provided")

    def f_str(self) -> str:
        return str(self.f)

    def compute(self, x: Number) -> sp.Float:
        return self.f(to_sp_float(x)).subs({sp.symbols("x"): x}).evalf(PRECISION)

    def __str__(self) -> str:
        f = self.f
        return f"FunctionExpr({f=})"

    def __repr__(self) -> str:
        return self.__str__()


class IntegralExpr:
    fn: FunctionExpr
    interval_l: sp.Float
    interval_r: sp.Float

    def __init__(
        self,
        preset: Preset | None = None,
        interval_l: sp.Float | None = None,
        interval_r: sp.Float | None = None,
        f_str: str | None = None,
        f: sp.Lambda | None = None,
    ) -> None:
        """
        supported variants:
        1. IntegralExpr(preset=)
        2. IntegralExpr(interval_l=, interval_r=, f=)
        3. IntegralExpr(interval_r=, interval_r=, f_str=)
        """
        if preset is not None:
            self.interval_l = preset.interval_l
            self.interval_r = preset.interval_r
            self.fn = FunctionExpr(f_str=preset.f_expr)
        else:
            if interval_l is None:
                raise ValueError("interval_l is required")
            if interval_r is None:
                raise ValueError("interval_r is required")
            self.interval_l = interval_l
            self.interval_r = interval_r
            self.fn = FunctionExpr(f=f, f_str=f_str)
        
        if self.interval_l > self.interval_r:
            raise ValueError("interval left bound must be less than right bound")

    def __str__(self) -> str:
        fn, interval_l, interval_r = (
            self.fn,
            self.interval_l,
            self.interval_r,
        )
        return f"Integral({fn=}, {interval_l=}, {interval_r=})"

    def __repr__(self) -> str:
        return self.__str__()
