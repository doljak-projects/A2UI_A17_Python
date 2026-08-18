"""Cache de estrutura A2UI derivada da DSL (issue #80)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.agui.dashboard_dsl import WeatherDashboardDsl, build_dashboard_components


@dataclass(frozen=True)
class CachedDashboardStructure:
    dsl: WeatherDashboardDsl
    components: list[dict[str, Any]]


class DashboardStructureCache:
    """Cache in-memory por hash da DSL — suficiente para a demo do tutorial."""

    def __init__(self) -> None:
        self._entries: dict[str, CachedDashboardStructure] = {}

    def get(self, request_hash: str) -> CachedDashboardStructure | None:
        return self._entries.get(request_hash)

    def put(self, request_hash: str, dsl: WeatherDashboardDsl, surface_id: str) -> CachedDashboardStructure:
        entry = CachedDashboardStructure(
            dsl=dsl,
            components=build_dashboard_components(surface_id, dsl),
        )
        self._entries[request_hash] = entry
        return entry

    def clear(self) -> None:
        self._entries.clear()


dashboard_structure_cache = DashboardStructureCache()
