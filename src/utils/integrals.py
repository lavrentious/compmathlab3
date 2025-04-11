from typing import Literal, Set

import sympy as sp  # type: ignore

from config import PRECISION, SAMPLES_COUNT
from logger import GlobalLogger
from utils.math import Number, f_str_expr_to_sp_lambda
from utils.reader import Preset
from utils.validation import to_sp_float

logger = GlobalLogger()


class FunctionExpr:
    symbol: sp.Symbol = sp.symbols("x")
    f: sp.Lambda

    singularities: Set[sp.Float]
    fixable_singularities: Set[sp.Float]
    inf_singularities: Set[sp.Float]

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

        self.singularities = self._find_singularities()
        self.inf_singularities = self._find_inf_singularities()
        self.fixable_singularities = self._find_fixable_singularities()

    def _find_singularities(self) -> Set[sp.Float]:
        return {to_sp_float(x) for x in sp.singularities(self.f.expr, self.symbol)}

    def _find_inf_singularities(self) -> Set[sp.Float]:
        return {
            s
            for s in self._find_singularities()
            if abs(self.limit(s, dir="+-")) == sp.oo
        }

    def _find_fixable_singularities(self) -> Set[sp.Float]:
        return {
            s
            for s in self._find_singularities()
            if abs(self.limit(s, dir="+-")) is not sp.oo
        }

    def f_str(self) -> str:
        return str(self.f)

    def compute(self, x: Number) -> sp.Float:
        x_sp_float = to_sp_float(x)
        if x_sp_float in self.fixable_singularities:
            logger.debug(
                f"fixable singularity at {x_sp_float}, computing limit={self.limit(x_sp_float, dir='+-')}"
            )
            return self.limit(x_sp_float, dir="+-")
        return self.f(x_sp_float).subs({sp.symbols("x"): x}).evalf(PRECISION)

    def limit(
        self, x: Number, dir: Literal["+"] | Literal["-"] | Literal["+-"] | None = None
    ) -> sp.Float:
        return sp.limit(self.f.expr, self.symbol, x, dir=dir).evalf(PRECISION)

    def continuous(self, l: Number, r: Number) -> bool:
        x = l
        d = (r - l) / SAMPLES_COUNT
        if d == 0:
            return True
        if d == sp.oo:
            return True
        while x <= r:
            try:
                y = self.compute(x)
                if (
                    not y.is_real
                    and not self.limit(x, dir="-").is_extended_real
                    and not self.limit(x, dir="+").is_extended_real
                ):
                    return False
            except Exception as e:
                logger.info(e)
                return False
            x += d
        return True

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
        fn: FunctionExpr | None = None,
    ) -> None:
        """
        supported variants:
        1. IntegralExpr(preset=)
        2. IntegralExpr(interval_l=, interval_r=, fn=)
        3. IntegralExpr(interval_l=, interval_r=, f=)
        4. IntegralExpr(interval_r=, interval_r=, f_str=)
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
            if fn:
                self.fn = fn
            else:
                self.fn = FunctionExpr(f=f, f_str=f_str)

        if self.interval_l > self.interval_r:
            raise ValueError("interval left bound must be less than right bound")

        # if abs(self.fn.limit(self.interval_l, dir="+")) == sp.oo:
        #     self.interval_l = self.interval_l + EPS
        # if abs(self.fn.limit(self.interval_r, dir="-")) == sp.oo:
        #     self.interval_r = self.interval_r - EPS

        if not self.fn.continuous(self.interval_l, self.interval_r):
            raise ValueError(
                f"function {self.fn} is not continuous on interval [{self.interval_l}, {self.interval_r}]"
            )

    def is_improper(self) -> Literal[1] | Literal[2] | None:
        """
        returns:
        - 1 for improper integral with infinite interval
        - 2 for improper integral with infinite fn
        - None for proper integral
        """
        a, b = self.interval_l, self.interval_r

        if a is -sp.oo or b == sp.oo:
            return 1

        if len(self.get_inf_singularities_in_interval()) > 0:
            return 2
        try:
            self.fn.limit(a, dir="+")
            self.fn.limit(b, dir="-")
        except Exception as e:
            logger.debug(e)
            return 2

        return None

    def is_convergent(self) -> bool:
        proper_order = self.is_improper()

        if proper_order is None:  # proper
            return True

        if proper_order == 1:
            logger.warning(
                f"{self} is a 1-st order improper integral (with infinite interval); assuming divergent"
            )
            return False

        if proper_order == 2:
            logger.debug(
                f"improper of 2-nd order with inf singularities ({self.get_inf_singularities_in_interval()}); assuming divergent"
            )
            return False
        # TODO
        # for each singularity approximate with polynomial approximation and determine convergence

        return True

    def get_inf_singularities_in_interval(self) -> Set[sp.Float]:
        return {
            x
            for x in self.fn.inf_singularities
            if self.interval_l < x < self.interval_r
        }

    def __str__(self) -> str:
        fn, interval_l, interval_r = (
            self.fn,
            self.interval_l,
            self.interval_r,
        )
        return f"Integral({fn=}, {interval_l=}, {interval_r=})"

    def __repr__(self) -> str:
        return self.__str__()
