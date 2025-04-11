import sympy as sp  # type: ignore

from logger import GlobalLogger
from solvers.base_solver import BaseSolver
from utils.integrals import IntegralExpr
from utils.validation import to_sp_float

logger = GlobalLogger()


class TrapSolver(BaseSolver):
    PRECISION_ORDER = 2  # k param

    def compute(self, integral_expr: IntegralExpr, interval_count: int) -> sp.Float:
        ans: sp.Float = to_sp_float(0)
        h = self.get_h(
            integral_expr.interval_l, integral_expr.interval_r, interval_count
        )
        f, interval_l = integral_expr.fn.compute, integral_expr.interval_l
        for i in range(interval_count):
            a, b = interval_l + h * i, interval_l + h * (i + 1)
            ans += to_sp_float("0.5") * (f(a) + f(b)) * h
        return ans
