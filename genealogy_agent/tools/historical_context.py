from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class HistoricalContext:
    topic: str
    place: str
    period: str
    summary: str
    sources: list[str]


class MCPClient(Protocol):
    def get_context(self, topic: str, place: str, period: str) -> HistoricalContext:
        ...


class DictMCPClient:
    """Simple MCP-like adapter backed by a dictionary for local/offline use."""

    def __init__(self, records: dict[tuple[str, str, str], HistoricalContext]) -> None:
        self.records = records

    def get_context(self, topic: str, place: str, period: str) -> HistoricalContext:
        return self.records.get(
            (topic, place, period),
            HistoricalContext(topic=topic, place=place, period=period, summary="No context found", sources=[]),
        )
