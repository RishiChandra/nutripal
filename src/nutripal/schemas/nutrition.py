"""Deterministic-layer contracts: DB match, per-gram densities, scaled items, meal report.

All macro numbers and arithmetic live in code (never the model). ``per_g`` holds per-gram
densities; scaling multiplies by grams. This module also defines the report handed to Pass 3.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

# Nutrient map keyed by name. Well-known keys: kcal, protein, carb, fat, fiber (extensible).
Macros = dict[str, float]


class DbMatch(BaseModel):
    fdc_id: str | int | None = None
    description: str
    match_confidence: float = Field(ge=0, le=1, description="How well db_query matched the DB entry.")


class ScaledItem(BaseModel):
    """One item after enrich + scale, carrying everything the Pass-3 gate needs.

    Design call-out: BOTH ``recognition_confidence`` and ``match_confidence`` are carried
    through, so the gate can raise an identity question from either a weak visual ID or a weak
    DB match (a bad match means ``kcal_per_g`` itself is wrong - which the portion range cannot
    capture).
    """

    id: str
    name: str
    db_match: DbMatch | None = None
    per_g: Macros = Field(default_factory=dict)
    macros: Macros = Field(default_factory=dict)
    macros_low: Macros = Field(default_factory=dict)
    macros_high: Macros = Field(default_factory=dict)
    kcal_point: float
    kcal_low: float
    kcal_high: float
    kcal_swing: float = Field(description="kcal_high - kcal_low; this item's calorie uncertainty.")
    kcal_share: float | None = Field(default=None, description="Display-only share of total calories.")
    recognition_confidence: float = Field(ge=0, le=1)
    match_confidence: float | None = Field(default=None, ge=0, le=1)
    source: str = Field(default="photo", description="'photo' or 'notes' - item origin.")


class MealReport(BaseModel):
    """Aggregate report and the input document to the Pass-3 gate."""

    items: list[ScaledItem]
    totals: Macros = Field(default_factory=dict)
    total_kcal_point: float
    total_kcal_swing: float
    kcal_band: tuple[float, float] = Field(description="Asymmetric [low, high] calorie band.")
