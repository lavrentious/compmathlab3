import enum

import sympy as sp  # type: ignore

from config import EPS
from logger import GlobalLogger
from solvers.base_solver import BaseSolver, Solution
from utils.integrals import IntegralExpr
from utils.math import d2f, max_in_interval
from utils.validation import to_sp_float

logger = GlobalLogger()


class TrapSolver(BaseSolver):
    PRECISION_ORDER = 2  # k param

    def compute(self, integral_expr: IntegralExpr, interval_count: int) -> sp.Float:
        ans: sp.Float = to_sp_float(0)
        h = self.get_h(integral_expr.interval_l, integral_expr.interval_r, interval_count)
        f, interval_l = integral_expr.fn.compute, integral_expr.interval_l
        for i in range(interval_count):
            a, b = interval_l + h * i, interval_l + h * (i + 1)
            ans += to_sp_float("0.5") * (f(a) + f(b)) * h
        return ans

    def calculate_error(
        self, integral_expr: IntegralExpr, interval_count: int
    ) -> sp.Float:
        fn, a, b = (
            integral_expr.fn.compute,
            integral_expr.interval_l,
            integral_expr.interval_r,
        )
        return max_in_interval(lambda x: abs(d2f(fn, x)), a, b) * (
            ((b - a) ** 3) / (12 * interval_count**2)
        )
