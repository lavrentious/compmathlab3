import sympy as sp  # type: ignore

from config import EPS
from utils.integrals import IntegralExpr
from utils.validation import to_sp_float


class Solution:
    value: sp.Float
    interval_count: int
    error_rate: sp.Float

    def __init__(self, value: sp.Float, interval_count: int, error_rate: sp.Float):
        self.value = value
        self.interval_count = interval_count
        self.error_rate = error_rate

    def __str__(self) -> str:
        value, interval_count, error_rate = (
            self.value,
            self.interval_count,
            self.error_rate,
        )
        return f"Solution({value=}, {interval_count=}, {error_rate=})"

    def __repr__(self) -> str:
        return self.__str__()


class BaseSolver:
    MAX_ITERATIONS = 100
    PRECISION_ORDER = 2

    def __init__(self) -> None:
        pass

    def get_h(self, interval_l: sp.Float, interval_r: sp.Float, interval_count: int) -> sp.Float:
        return (interval_r - interval_l) / interval_count

    def compute(self, integral_expr: IntegralExpr, interval_count: int) -> sp.Float:
        raise NotImplementedError

    def calculate_error(
        self, integral_expr: IntegralExpr, interval_count: int
    ) -> sp.Float:
        raise NotImplementedError

    def solve(
        self, integral_expr: IntegralExpr, interval_count: int, eps: sp.Float = EPS
    ) -> Solution:
        """
        default implementation
        uses Runge's method
        """
        ans = to_sp_float(0)
        for _ in range(self.MAX_ITERATIONS):
            ans = self.compute(integral_expr, interval_count * 2)
            if (abs(ans - self.compute(integral_expr, interval_count))) / (
                2**self.PRECISION_ORDER - 1
            ) < eps:
                return Solution(
                    self.compute(integral_expr, interval_count),
                    interval_count,
                    self.calculate_error(integral_expr, interval_count),
                )
            interval_count *= 2
        raise ValueError("max iterations exceeded")
