from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Entry:
    term: int
    item: object
