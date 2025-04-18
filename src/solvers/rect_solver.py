import enum

import sympy as sp  # type: ignore

from logger import GlobalLogger
from solvers.base_solver import BaseSolver
from utils.integrals import IntegralExpr
from utils.validation import to_sp_float

logger = GlobalLogger()


class RectStrategy(enum.Enum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class RectSolver(BaseSolver):
    PRECISION_ORDER = 1  # k param
    strategy: RectStrategy = RectStrategy.LEFT

    def compute(self, integral_expr: IntegralExpr, interval_count: int) -> sp.Float:
        ans: sp.Float = to_sp_float(0)
        h = self.get_h(
            integral_expr.interval_l, integral_expr.interval_r, interval_count
        )
        if self.strategy == RectStrategy.LEFT:
            x = integral_expr.interval_l
        elif self.strategy == RectStrategy.RIGHT:
            x = integral_expr.interval_l + h
        elif self.strategy == RectStrategy.CENTER:
            x = integral_expr.interval_l + h / 2
        for i in range(interval_count):
            x += h
            y = integral_expr.fn.compute(x)
            ans += h * y
        return ans

    def set_strategy(self, strategy: RectStrategy) -> None:
        self.strategy = strategy
