from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.orca.tools.geo import reverse_geocode
from app.orca.tools.marine import get_marine_conditions
from app.orca.tools.ocean import get_ocean_conditions
from app.orca.tools.pfz import get_pfz_advisory, get_pfz_service_status
from app.orca.tools.weather import get_weather_forecast


Tool = Callable[..., dict[str, Any]]


class ORCAToolRegistry:
    """Explicit allow-list of tools available to ORCA agents."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, tool: Tool) -> None:
        if not name or name in self._tools:
            raise ValueError(f"Tool '{name}' is already registered or invalid")
        self._tools[name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Unknown ORCA tool: {name}") from exc

    def names(self) -> list[str]:
        return sorted(self._tools)


tool_registry = ORCAToolRegistry()
tool_registry.register("get_weather_forecast", get_weather_forecast)
tool_registry.register("get_ocean_conditions", get_ocean_conditions)
tool_registry.register("get_marine_conditions", get_marine_conditions)
tool_registry.register("get_pfz_advisory", get_pfz_advisory)
tool_registry.register("get_pfz_service_status", get_pfz_service_status)
tool_registry.register("reverse_geocode", reverse_geocode)
