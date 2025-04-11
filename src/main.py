from typing import List

from argparser import ArgParser, SolutionMethod
from logger import GlobalLogger, LogLevel
from solvers.base_solver import BaseSolver
from solvers.rect_solver import RectSolver
from solvers.simpson_solver import SimpsonSolver
from solvers.trap_solver import TrapSolver
from utils.integrals import IntegralExpr
from utils.meta import colorful_error_trace
from utils.reader import Preset, Reader

if __name__ != "__main__":
    exit(0)


def _parse_presets() -> List[Preset]:
    presets_reader = Reader(open("src/presets.json", "r"))
    presets = presets_reader.parse_presets()
    presets_reader.destroy()
    return presets


def _get_solver(parser: ArgParser) -> BaseSolver:
    method = parser.method
    if method == SolutionMethod.RECT:
        solver = RectSolver()
        solver.set_strategy(parser.rect_strategy)
        return solver
    if method == SolutionMethod.TRAP:
        return TrapSolver()
    if method == SolutionMethod.SIMPSON:
        return SimpsonSolver()
    return BaseSolver()


def run() -> None:
    parser = ArgParser(_parse_presets())
    logger = GlobalLogger()
    try:
        parser.parse_and_validate_args()
    except Exception as e:
        logger.error(e)
        exit(1)
    GlobalLogger().set_min_level(LogLevel.DEBUG if parser.verbose else LogLevel.INFO)
    GlobalLogger().debug("Verbose mode:", parser.verbose)

    try:
        integral = IntegralExpr(preset=parser.preset)
    except Exception as e:
        logger.error(e)
        exit(1)
    logger.debug("solving integral", integral)

    solver = _get_solver(parser)
    try:
        ans = solver.solve(integral, 4)
    except Exception as e:
        logger.error(e)
        logger.debug(colorful_error_trace(e))
        exit(1)

    print("================")
    print("result:", ans.value)
    print("interval count:", ans.interval_count)
    print("error rate:", ans.error_rate)


run()
