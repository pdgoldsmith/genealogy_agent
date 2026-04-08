from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class GedcomRecord:
    level: int
    pointer: str | None
    tag: str
    value: str
    children: list["GedcomRecord"] = field(default_factory=list)


def parse_gedcom(text: str) -> list[GedcomRecord]:
    """Parse GEDCOM text into a simple tree representation."""
    roots: list[GedcomRecord] = []
    stack: list[GedcomRecord] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split(" ", 2)
        if len(parts) < 2:
            continue

        level = int(parts[0])

        pointer: str | None = None
        tag: str
        value = ""

        if len(parts) == 2:
            tag = parts[1]
        else:
            if parts[1].startswith("@") and parts[1].endswith("@"):
                pointer = parts[1]
                tail = parts[2].split(" ", 1)
                tag = tail[0]
                value = tail[1] if len(tail) > 1 else ""
            else:
                tag = parts[1]
                value = parts[2]

        record = GedcomRecord(level=level, pointer=pointer, tag=tag, value=value)

        while stack and stack[-1].level >= level:
            stack.pop()

        if stack:
            stack[-1].children.append(record)
        else:
            roots.append(record)

        stack.append(record)

    return roots
