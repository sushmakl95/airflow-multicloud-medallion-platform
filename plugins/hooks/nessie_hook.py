"""Thin wrapper for the Nessie REST catalog API."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NessieReference:
    name: str
    hash: str | None = None
    type: str = "BRANCH"


def branch_url(base_url: str, ref: NessieReference) -> str:
    return f"{base_url.rstrip('/')}/api/v2/trees/{ref.type.lower()}/{ref.name}"


def commit_url(base_url: str, ref: NessieReference) -> str:
    suffix = f"@{ref.hash}" if ref.hash else ""
    return f"{base_url.rstrip('/')}/api/v2/trees/{ref.name}{suffix}/history"
