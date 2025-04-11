from typing import List

import sympy as sp  # type: ignore

from logger import GlobalLogger
from solvers.base_solver import BaseSolver
from utils.integrals import IntegralExpr

logger = GlobalLogger()


class SimpsonSolver(BaseSolver):
    PRECISION_ORDER = 4  # k param

    def _generate_xs(
        self, interval_l: sp.Float, interval_r: sp.Float, interval_count: int
    ) -> List[sp.Float]:
        h = self.get_h(interval_l, interval_r, interval_count)
        ans: List[sp.Float] = []
        for i in range(interval_count):
            ans.append(interval_l + h * i)
        ans.append(interval_r)
        return ans

    def compute(self, integral_expr: IntegralExpr, interval_count: int) -> sp.Float:
        h = self.get_h(
            integral_expr.interval_l, integral_expr.interval_r, interval_count
        )
        f, interval_l = integral_expr.fn.compute, integral_expr.interval_l
        xs = self._generate_xs(interval_l, integral_expr.interval_r, interval_count)
        if len(xs) % 2 == 0:
            raise ValueError("interval_count must be even")
        x0 = xs[0]
        odd_xs = xs[1::2]
        even_xs = xs[2:-1:2]
        xn = xs[-1]

        y0 = f(x0)
        odd_ys = [f(x) for x in odd_xs]
        even_ys = [f(x) for x in even_xs]
        yn = f(xn)

        return h / 3 * (y0 + 4 * sum(odd_ys) + 2 * sum(even_ys) + yn)
