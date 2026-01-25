"""Minimal schema helpers.

No external dependencies. Only validates required top-level keys and schema_version.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class ValidationError(Exception):
    message: str

    def __str__(self) -> str:
        return self.message


def require_keys(obj: Dict[str, Any], keys: Iterable[str], context: str = "") -> None:
    missing: List[str] = [k for k in keys if k not in obj]
    if missing:
        prefix = f"{context}: " if context else ""
        raise ValidationError(prefix + f"Missing keys: {', '.join(missing)}")


def require_schema(obj: Dict[str, Any], expected_prefix: str, context: str = "") -> None:
    v = obj.get("schema_version")
    if not isinstance(v, str) or not v.startswith(expected_prefix):
        prefix = f"{context}: " if context else ""
        raise ValidationError(prefix + f"Invalid schema_version: {v!r} (expected prefix {expected_prefix!r})")
