"""Pass 2 - Reconcile the fixed visual estimate with user notes.

The Pass-1 estimate is the ANCHOR; notes only validate/refine it. Photos are NOT re-sent.
Agreement raises confidence and tightens the range; conflict lowers confidence but keeps the
visual estimate; unseen details (e.g. cooking oil) are appended via ``added_from_notes``.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from .pass1 import Portion


class Reconciliation(BaseModel):
    signal: str = Field(
        description="agrees | agrees_with_quantity | adds_unseen_detail | conflicts | irrelevant",
    )
    source_quote: str | None = None
    estimate_changed: bool | None = None
    confidence_delta: float | None = None
    action: str


class Pass2Item(BaseModel):
    """A Pass-1 item carried forward, plus an overall confidence and a reconciliation block."""

    id: str
    name: str
    state: str | None = None
    db_query: str
    portion: Portion
    recognition_confidence: float = Field(ge=0, le=1)
    portion_confidence: float = Field(ge=0, le=1)
    overall_confidence: float = Field(ge=0, le=1)
    cues_used: list[str] = Field(default_factory=list)
    limiting_factors: list[str] = Field(default_factory=list)
    reconciliation: Reconciliation


class AddedItem(BaseModel):
    """An item introduced from notes, not visible in the photo. ``id`` is assigned by code."""

    id: str | None = None
    name: str
    db_query: str
    state: str | None = None
    portion: Portion
    recognition_confidence: float = Field(default=0.0, ge=0, le=1)
    portion_confidence: float = Field(ge=0, le=1)
    overall_confidence: float = Field(ge=0, le=1)
    reconciliation: Reconciliation


class Conflict(BaseModel):
    """A note that disagrees with a clear visual finding - surfaced for the user to resolve."""

    item_id: str | None = None
    note_quote: str | None = None
    visual_finding: str | None = None
    detail: str | None = None


class Pass2Output(BaseModel):
    items: list[Pass2Item]
    added_from_notes: list[AddedItem] = Field(default_factory=list)
    conflicts: list[Conflict] = Field(default_factory=list)
    meal_confidence: float = Field(ge=0, le=1)
