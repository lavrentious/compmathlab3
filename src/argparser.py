import argparse
import enum
import sys
from argparse import Namespace
from io import TextIOWrapper
from typing import Any, List

import sympy as sp  # type: ignore

from config import MAX_STARTING_SUBDIVISIONS
from logger import GlobalLogger, LogLevel
from solvers.rect_solver import RectStrategy
from utils.math import f_str_expr_to_sp_lambda
from utils.reader import Preset, Reader
from utils.validation import to_sp_float

logger = GlobalLogger()


class SolutionMethod(enum.Enum):
    RECT = "rect"
    TRAP = "trap"
    SIMPSON = "simpson"


class ArgParser:
    parser: argparse.ArgumentParser
    in_stream: TextIOWrapper | Any = sys.stdin
    out_stream: None | TextIOWrapper | Any = sys.stdout
    args: Namespace

    presets: List[Preset]

    preset: Preset | None = None
    method: SolutionMethod
    rect_strategy: RectStrategy
    subdivisions: int

    # args
    verbose: bool = False

    def _register_args(self) -> None:
        self.parser.add_argument("-h", "--help", action="store_true", help="shows help")
        self.parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="set verbose mode",
        )
        self.parser.add_argument(
            "--list-presets", action="store_true", help="list available presets"
        )
        self.parser.add_argument(
            "--preset",
            action="store",
            type=str,
            help="select preset by name or index (see --list-presets)",
        )
        self.parser.add_argument(
            "--f-expr",
            action="store",
            type=str,
            help="specify function expression",
        )
        self.parser.add_argument(
            "--interval-l",
            action="store",
            type=str,
            help="specify interval left bound",
        )
        self.parser.add_argument(
            "--interval-r",
            action="store",
            type=str,
            help="specify interval right bound",
        )
        self.parser.add_argument(
            "--method",
            action="store",
            choices=[item.value for item in SolutionMethod],
            default=SolutionMethod.RECT.value,
            help="specify solution method",
        )
        self.parser.add_argument(
            "--rect-strategy",
            action="store",
            choices=[item.value for item in RectStrategy],
            default=RectStrategy.LEFT.value,
            help="specify strategy for rect method",
        )
        self.parser.add_argument(
            "-n",
            "--subdivisions",
            action="store",
            type=int,
            default=4,
            help="starting number of subdivisions",
        )
        self.parser.add_argument(
            "input_file",
            nargs="?",
            help="file to read from (preset format)",
            type=argparse.FileType("r"),
        )

    def __init__(self, presets: List[Preset]) -> None:
        self.parser = argparse.ArgumentParser(add_help=False)
        self._register_args()
        self.presets = presets

    def parse_and_validate_args(self) -> int:
        self.args = self.parser.parse_args()

        self.verbose = self.args.verbose or False
        if self.args.verbose:
            logger.set_min_level(LogLevel.DEBUG)
        if self.args.help:
            self.print_help()
            exit(0)
        if self.args.list_presets:
            self.print_presets()
            exit(0)

        if self.args.input_file is not None:
            self.in_stream = self.args.input_file
        self.preset = self._get_preset()
        print("using preset:", self.preset)

        self.method = SolutionMethod(self.args.method)
        self.rect_strategy = RectStrategy(self.args.rect_strategy)

        self.subdivisions = self.args.subdivisions
        if self.subdivisions <= 0:
            logger.error("subdivisions must be greater than 0")
            exit(1)
        if self.subdivisions > MAX_STARTING_SUBDIVISIONS:
            logger.error(f"subdivisions must be less than {MAX_STARTING_SUBDIVISIONS}")
            exit(1)

        return 0

    def _get_preset(self) -> Preset:
        preset: Preset | None = None
        f_expr_str: str | None = self.args.f_expr
        interval_l_str: str | None = self.args.interval_l
        interval_r_str: str | None = self.args.interval_r

        f_expr: str | None = None
        interval_l: sp.Float | None = None
        interval_r: sp.Float | None = None

        if self.args.preset:
            try:
                res = self.find_preset(self.args.preset)
                preset = Preset(
                    name=res.name,
                    f_expr=res.f_expr,
                    interval_l=res.interval_l,
                    interval_r=res.interval_r,
                )
            except ValueError as e:
                logger.error(e)
                self.print_presets()
                exit(1)
            logger.debug(f"preset selected with --preset: {preset}")
        elif self.args.input_file is not None:
            self.in_stream = self.args.input_file

        if not self.preset and self.args.input_file:
            logger.debug(f'loading preset from "{self.in_stream.name}"')
            reader = Reader(self.in_stream)
            preset = reader.parse_preset()
        if f_expr_str is not None:
            f_expr = self._validate_f_expr(f_expr_str)
        if interval_l_str is not None:
            interval_l = self._validate_interval_bound(interval_l_str, "left")
        if interval_r_str is not None:
            interval_r = self._validate_interval_bound(interval_r_str, "right")
        if preset is None:
            logger.debug(f"loading preset from cmd line args")
            if f_expr is None:
                raise ValueError("function expression is required (--f-expr <expr>)")
            if interval_l is None:
                raise ValueError(
                    "interval left bound is required (--interval-l <float>)"
                )
            if interval_r is None:
                raise ValueError(
                    "interval right bound is required (--interval-r <float>)"
                )
            if interval_l > interval_r:
                raise ValueError("left bound must be less than right bound")
            preset = Preset(None, f_expr, interval_l, interval_r)
        else:
            if f_expr is not None:
                logger.warning(
                    f"preset's f_expr={preset.f_expr} is overriden by --f-expr={f_expr}"
                )
                preset.f_expr = f_expr
            if interval_l is not None:
                logger.warning(
                    f"preset's interval_l={preset.interval_l} is overriden by --interval-l={interval_l}"
                )
                preset.interval_l = interval_l
            if interval_r is not None:
                logger.warning(
                    f"preset's interval_r={preset.interval_r} is overriden by --interval-r={interval_r}"
                )
                preset.interval_r = interval_r

        return preset

    def _validate_f_expr(self, f_expr: str) -> str:
        try:
            f_str_expr_to_sp_lambda(f_expr)
        except ValueError as e:
            raise ValueError(f"invalid function expression: {e}")
        return f_expr

    def _validate_interval_bound(self, bound: str, name: str) -> sp.Float:
        try:
            return to_sp_float(bound)
        except ValueError as e:
            raise ValueError(f"invalid {name} bound: {e}")

    def print_help(self) -> None:
        self.parser.print_help()
        print("variants (descending priority)")
        print("\t1. specify --preset <name/index>")
        print("\t2. specify <input_file.json>")
        print(
            "\t3. specify manually --f-expr <expr> --interval-l <float> --interval-r <float>"
        )

    def print_presets(self) -> None:
        print("available presets (use --preset <name/index>):")
        for i, preset in enumerate(self.presets):
            print(
                f"{i+1:>2} {preset.name or '':<15} {preset.f_expr:<45} [{preset.interval_l:>7.2f} ; {preset.interval_r:<7.2f}]"
            )

    def find_preset(self, query: str) -> Preset:
        by_name = [p for p in self.presets if p.name == query]
        if len(by_name) > 1:
            logger.warning(f"found {len(by_name)} presets with name {query}")
        if len(by_name) > 0:
            return by_name[0]
        if query.isdigit():
            index = int(query) - 1
            if 0 <= index < len(self.presets):
                return self.presets[index]
            raise ValueError(f"index {query} is out of range (1-{len(self.presets)})")
        raise ValueError(f'preset "{query}" not found')
