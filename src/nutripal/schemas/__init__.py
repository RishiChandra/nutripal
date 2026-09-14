"""Pydantic contracts for the photo->macro pipeline.

These lock the data shapes exchanged between the model passes and the deterministic layer.
Every field the JSON schemas in ``docs/photo_subagent_prompts.md`` define lives here.
"""
from __future__ import annotations

from .gate import Clarification, Driver, GateOutput, GateThresholds, Mode
from .nutrition import DbMatch, Macros, MealReport, ScaledItem
from .pass1 import Pass1Item, Pass1Output, Portion, Scene
from .pass2 import AddedItem, Conflict, Pass2Item, Pass2Output, Reconciliation

__all__ = [
    # pass 1
    "Portion",
    "Pass1Item",
    "Scene",
    "Pass1Output",
    # pass 2
    "Reconciliation",
    "Pass2Item",
    "AddedItem",
    "Conflict",
    "Pass2Output",
    # deterministic layer
    "Macros",
    "DbMatch",
    "ScaledItem",
    "MealReport",
    # gate
    "GateThresholds",
    "Driver",
    "Clarification",
    "GateOutput",
    "Mode",
]
