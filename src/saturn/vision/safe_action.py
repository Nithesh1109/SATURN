"""Safety boundary for vision-generated desktop actions."""

from __future__ import annotations

from dataclasses import dataclass

from saturn.tools.base import ToolContext, ToolResult
from saturn.tools.validator import ActionValidator


@dataclass(frozen=True)
class SafeVisionActionResult:
    allowed: bool
    result: ToolResult | None = None
    error: str | None = None


class SafeVisionActionExecutor:
    """Route vision-generated actions through the central validator and executor."""

    def __init__(self, executor, validator: ActionValidator | None = None) -> None:
        self._executor = executor
        self._validator = validator or ActionValidator()

    def execute(
        self,
        *,
        tool_name: str,
        arguments: dict[str, object],
        context: ToolContext,
    ) -> SafeVisionActionResult:
        validation = self._validator.validate(tool_name, arguments)
        if not validation.allowed:
            return SafeVisionActionResult(
                allowed=False,
                error=f"Vision action rejected: {validation.error}",
            )

        result = self._executor.execute(tool_name, arguments, context)
        return SafeVisionActionResult(allowed=True, result=result)
