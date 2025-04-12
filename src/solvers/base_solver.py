from typing import List
import sympy as sp  # type: ignore

from config import EPS, INF_EPS, RUNGE_ERROR_THRESHOLD
from logger import GlobalLogger
from utils.integrals import IntegralExpr
from utils.validation import to_sp_float

logger = GlobalLogger()


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
    MAX_ITERATIONS = 15
    PRECISION_ORDER = 2

    def __init__(self) -> None:
        pass

    def get_h(
        self, interval_l: sp.Float, interval_r: sp.Float, interval_count: int
    ) -> sp.Float:
        return (interval_r - interval_l) / interval_count

    def compute(self, integral_expr: IntegralExpr, interval_count: int) -> sp.Float:
        raise NotImplementedError

    def solve(
        self, integral_expr: IntegralExpr, interval_count: int, eps: sp.Float = EPS
    ) -> Solution:
        singularities = integral_expr.get_inf_singularities_in_interval()
        if len(singularities) == 0:
            return self._solve(integral_expr, interval_count, eps)

        last_x = integral_expr.interval_l
        solutions: List[Solution] = []
        logger.debug("singularities in interval detected")
        for s in sorted(singularities):
            logger.debug(f"computing integral on interval [{last_x}, {s}]")
            solutions.append(
                self._solve(
                    IntegralExpr(
                        interval_l=last_x,
                        interval_r=s,
                        fn=integral_expr.fn,
                    ),
                    interval_count,
                    eps,
                )
            )
            last_x = s
        logger.debug(
            f"computing integral on interval [{last_x}, {integral_expr.interval_r}]"
        )
        solutions.append(
            self._solve(
                IntegralExpr(
                    interval_l=last_x,
                    interval_r=integral_expr.interval_r,
                    fn=integral_expr.fn,
                ),
                interval_count,
                eps,
            )
        )
        return Solution(
            value=sum(s.value for s in solutions),
            interval_count=sum(s.interval_count for s in solutions),
            error_rate=max(s.error_rate for s in solutions),
        )

    def _solve(
        self, integral_expr: IntegralExpr, interval_count: int, eps: sp.Float = EPS
    ) -> Solution:
        """
        default implementation
        - checks convergence and raises ValueError if not convergent
        - uses Runge's method
        """
        if not integral_expr.is_convergent():
            # only checks that the interval is not infinite
            raise ValueError(f"integral {integral_expr} does not converge")

        if integral_expr.interval_l == integral_expr.interval_r:
            return Solution(
                value=to_sp_float(0),
                interval_count=0,
                error_rate=to_sp_float(0),
            )

        if abs(integral_expr.fn.limit(integral_expr.interval_l, dir="+")) == sp.oo:
            integral_expr = IntegralExpr(
                interval_l=integral_expr.interval_l + INF_EPS,
                interval_r=integral_expr.interval_r,
                fn=integral_expr.fn,
            )
            logger.warning(
                f"left limit is infinite; interval_l={integral_expr.interval_l}"
            )
        if abs(integral_expr.fn.limit(integral_expr.interval_r, dir="-")) == sp.oo:
            integral_expr = IntegralExpr(
                interval_l=integral_expr.interval_l,
                interval_r=integral_expr.interval_r - INF_EPS,
                fn=integral_expr.fn,
            )
            logger.warning(
                f"right limit is infinite; interval_r={integral_expr.interval_r}"
            )

        prev = self.compute(integral_expr, interval_count)
        for i in range(self.MAX_ITERATIONS):
            interval_count *= 2
            current = self.compute(integral_expr, interval_count)
            error = abs(current - prev) / (2**self.PRECISION_ORDER - 1)
            logger.debug(f"iteration {i+1}: value={current}, error={error}")
            # if error > RUNGE_ERROR_THRESHOLD:
            #     logger.warning(
            #         f"error={error} > RUNGE_ERROR_THRESHOLD={RUNGE_ERROR_THRESHOLD}; assuming divergent "
            #     )
            #     break
            if error < eps:
                return Solution(
                    current,
                    interval_count,
                    error,
                )
            prev = current
        raise ValueError("integral diverges")
