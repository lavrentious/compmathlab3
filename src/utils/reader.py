import json
from io import TextIOWrapper
from typing import Any, List

import sympy as sp  # type: ignore

from logger import GlobalLogger
from utils.validation import to_sp_float

logger = GlobalLogger()


class Preset:
    name: str | None
    f_expr: str
    interval_l: sp.Float
    interval_r: sp.Float

    def __init__(
        self, name: str | None, f_expr: str, interval_l: sp.Float, interval_r: sp.Float
    ):
        self.name = name
        self.f_expr = f_expr
        self.interval_l = interval_l
        self.interval_r = interval_r

    def __str__(self) -> str:
        name, f_expr, interval_l, interval_r = (
            self.name,
            self.f_expr,
            self.interval_l,
            self.interval_r,
        )
        return f"Preset({name=}, {f_expr=}, {interval_l=}, {interval_r=})"

    def __repr__(self) -> str:
        return self.__str__()


class Reader:
    in_stream: TextIOWrapper | Any

    def __init__(self, in_stream: TextIOWrapper | Any | str):
        self.in_stream = in_stream

    def parse_preset(self) -> Preset:
        logger.info(f"parsing preset from {self.in_stream}")
        try:
            obj = json.load(self.in_stream)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON format") from e

        try:
            return self.obj_to_preset(obj)
        except ValueError as e:
            raise ValueError(f"invalid preset: {e}")

    def parse_presets(self) -> List[Preset]:
        logger.info(f"parsing presets from {self.in_stream}")
        try:
            data = json.load(self.in_stream)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON format") from e

        if not isinstance(data, list):
            raise ValueError("expected a list of presets")

        presets: List[Preset] = []
        for i, item in enumerate(data):
            try:
                preset = self.obj_to_preset(item)
                presets.append(preset)
            except ValueError as e:
                raise ValueError(f"preset at {i}: {e}")

        return presets

    def obj_to_preset(self, obj: Any) -> Preset:
        if not isinstance(obj, dict):
            raise ValueError(f"preset {obj} is not an object")

        name = obj.get("name")
        f_expr = obj.get("f_expr")
        interval_l = obj.get("interval_l")
        interval_r = obj.get("interval_r")

        if name is not None and not isinstance(name, str):
            raise ValueError(f"preset {obj}: 'name' must be a string or null")
        if not isinstance(f_expr, str):
            raise ValueError(f"preset {obj}: 'f_expr' is required and must be a string")
        if not isinstance(interval_l, (int, float)) and not isinstance(interval_l, str):
            raise ValueError(f"preset {obj}: 'interval_l' must be a number or string")
        if not isinstance(interval_r, (int, float)) and not isinstance(interval_r, str):
            raise ValueError(f"preset {obj}: 'interval_r' must be a number or string")

        return Preset(name, f_expr, to_sp_float(interval_l), to_sp_float(interval_r))

    def destroy(self) -> None:
        self.in_stream.close()
