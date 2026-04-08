from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Citation:
    source_id: str
    locator: str
    note: str = ""


@dataclass(slots=True)
class Discovery:
    summary: str
    confidence: float
    citations: list[Citation] = field(default_factory=list)
    requires_human_review: bool = False
    status: str = "hypothesis"


@dataclass(slots=True)
class ResourceExamined:
    resource_id: str
    resource_type: str
    accessed_at: datetime
    notes: str = ""


@dataclass(slots=True)
class ResearchLogEntry:
    timestamp: datetime
    action: str
    detail: str
    citations: list[Citation] = field(default_factory=list)
