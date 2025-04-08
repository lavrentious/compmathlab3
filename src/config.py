from mpmath import mp  # type: ignore

from utils.meta import singleton

EPS = 0.0001
PRECISION = 69
DERIVATIVE_PRECISION = 0.0001


# ------- порошок уходи --------

mp.dps = PRECISION


@singleton
class GlobalConfig:
    def __init__(self) -> None:
        pass
