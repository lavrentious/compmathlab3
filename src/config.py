import sympy as sp  # type: ignore
from mpmath import mp  # type: ignore

from utils.meta import singleton

PRECISION = 32
EPS = sp.Float("0.01", PRECISION)
INF_EPS = sp.Float("0.0001", PRECISION)
DERIVATIVE_PRECISION = 0.0001
SAMPLES_COUNT = 1000
RUNGE_ERROR_THRESHOLD = sp.Float("1e6")
MAX_STARTING_SUBDIVISIONS = int(2**14)


# ------- порошок уходи --------

mp.dps = PRECISION


@singleton
class GlobalConfig:
    def __init__(self) -> None:
        pass
