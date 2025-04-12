import json
import os
from enum import Enum
from io import TextIOWrapper
from typing import Any, List


from logger import GlobalLogger
from solvers.base_solver import Solution
from utils.integrals import IntegralExpr


logger = GlobalLogger()


class OutputFormat(Enum):
    JSON = "json"
    PLAIN = "plain"


class ResWriter:
    out_stream: TextIOWrapper | Any
    file_path: str | None = None

    def __init__(self, out_stream: TextIOWrapper | Any | str):
        if type(out_stream) == str:
            self.file_path = out_stream
            out_stream = self._get_out_stream(out_stream)
        self.out_stream = out_stream

    def _get_out_stream(self, file_path: str) -> TextIOWrapper | Any:
        if not file_path:
            raise ValueError("no file specified")
        if os.path.exists(file_path) and not os.access(
            os.path.dirname(file_path), os.W_OK
        ):
            raise PermissionError(f"no write permission for {file_path}")
        return open(file_path, "w")

    def write_solution(
        self,
        integral: IntegralExpr,
        result: Solution,
        format: OutputFormat = OutputFormat.PLAIN,
    ) -> None:
        res_writer: ResWriter
        if format == OutputFormat.JSON:
            res_writer = JsonWriter(self.out_stream)
        else:
            res_writer = PlainWriter(self.out_stream)
        logger.debug("using writer", res_writer.__class__.__name__)
        res_writer.write_solution(integral, result)

    def destroy(self) -> None:
        self.out_stream.close()


class PlainWriter(ResWriter):
    def write_solution(
        self,
        integral: IntegralExpr,
        result: Solution,
        format: OutputFormat = OutputFormat.PLAIN,
    ) -> None:
        self.out_stream.write(f"Function: {integral.fn.f_str()}\n")
        self.out_stream.write(
            f"Interval: [{integral.interval_l}, {integral.interval_r}]\n"
        )
        self.out_stream.write(f"Result: {result.value}\n")
        self.out_stream.write(f"Error: {result.error_rate}\n")
        self.out_stream.write(f"Iterations: {result.interval_count}\n")
        self.out_stream.flush()


class JsonWriter(ResWriter):
    def write_solution(
        self,
        integral: IntegralExpr,
        result: Solution,
        format: OutputFormat = OutputFormat.PLAIN,
    ) -> None:

        obj = {
            "function": integral.fn.f_str(),
            "interval_l": str(integral.interval_l),
            "interval_r": str(integral.interval_r),
            "result": str(result.value),
            "error": str(result.error_rate),
            "iterations": str(result.interval_count),
        }
        logger.debug("dumping json", obj)

        json.dump(
            obj,
            self.out_stream,
            indent=4,
        )
        self.out_stream.write("\n")
        self.out_stream.flush()
