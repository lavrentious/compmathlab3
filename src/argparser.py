import argparse
import enum
import sys
from argparse import Namespace
from io import TextIOWrapper
from typing import Any, List

import sympy as sp  # type: ignore

from logger import GlobalLogger, LogLevel
from solvers.rect_solver import RectStrategy
from utils.reader import Preset, Reader

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
            type=sp.Float,
            help="specify interval left bound",
        )
        self.parser.add_argument(
            "--interval-r",
            action="store",
            type=sp.Float,
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

        if self.args.preset:
            try:
                self.preset = self.find_preset(self.args.preset)
            except ValueError as e:
                logger.error(e)
                self.print_presets()
                exit(1)
            logger.debug(f"preset selected with --preset: {self.preset}")
        elif self.args.input_file is not None:
            self.in_stream = self.args.input_file

        if not self.preset:
            if self.args.input_file:
                logger.debug(f'loading preset from "{self.in_stream.name}"')
                reader = Reader(self.in_stream)
                self.preset = reader.parse_preset()
            else:
                logger.debug(f"loading manually from args")
                self.preset = self._validate_manual(
                    self.args.f_expr, self.args.interval_l, self.args.interval_r
                )

        self.method = SolutionMethod(self.args.method)
        self.rect_strategy = RectStrategy(self.args.rect_strategy)

        return 0

    def _validate_manual(
        self, f_expr: str, interval_l: float, interval_r: float
    ) -> Preset:
        logger.debug(
            f'validating manual preset "{f_expr}" [{interval_l} ; {interval_r}]'
        )
        if not f_expr:
            raise ValueError("function expression is required")
        if not interval_l:
            raise ValueError("interval left bound is required")
        if not interval_r:
            raise ValueError("interval right bound is required")
        return Preset(None, f_expr, interval_l, interval_r)

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
