"""Pass 3 - Clarification gate (see docs/photo_subagent_prompts.md).

Impact is ``kcal_swing = (grams_high - grams_low) * kcal_per_g`` - portion uncertainty x
calorie density - NOT an item's share of the total. Two failure modes map to two question
types: PORTION (large swing) and IDENTITY (low recognition or weak DB match). The threshold
logic is simple enough to run as pure code; reserve the model for phrasing the questions.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Mode = Literal["portion", "identity"]


class GateThresholds(BaseModel):
    """Defaults from CLAUDE.md conventions; tune against Nutrition5k."""

    band_tolerance_kcal: float = 120
    item_swing_kcal: float = 60
    material_kcal: float = 40
    id_threshold: float = 0.6
    max_questions: int = 2


class Driver(BaseModel):
    item_id: str
    name: str
    mode: Mode
    kcal_point: float
    kcal_swing: float
    reason: str


class Clarification(BaseModel):
    item_id: str
    type: Mode
    question: str
    removes_kcal_swing: float


class GateOutput(BaseModel):
    gate: Literal["pass", "needs_clarification"]
    total_kcal_point: float
    total_kcal_swing: float
    finalize: bool
    drivers: list[Driver] = Field(default_factory=list)
    clarifications: list[Clarification] = Field(default_factory=list)
    notes_for_user_facing_report: str | None = None
