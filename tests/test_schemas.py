"""Round-trip the example payloads from docs/photo_subagent_prompts.md through the schemas."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from nutripal.schemas import (
    GateOutput,
    GateThresholds,
    MealReport,
    Pass1Output,
    Pass2Output,
)

PASS1_EXAMPLE = {
    "items": [
        {
            "id": "item_1",
            "name": "grilled chicken breast",
            "state": "grilled, skinless",
            "db_query": "chicken breast grilled skinless",
            "portion": {
                "grams": 140,
                "grams_low": 110,
                "grams_high": 185,
                "description": "one palm-sized piece",
            },
            "recognition_confidence": 0.9,
            "portion_confidence": 0.5,
            "cues_used": ["dinner fork for scale", "plate ~27cm"],
            "limiting_factors": ["partially occluded by rice"],
        }
    ],
    "scene": {
        "reference_objects": ["fork"],
        "plate_diameter_cm_est": 27,
        "occlusion": "moderate",
        "photo_count": 1,
        "single_angle": True,
    },
    "overall_notes": "Standard dinner plate, one overhead shot.",
}

PASS2_EXAMPLE = {
    "items": [
        {
            "id": "item_1",
            "name": "grilled chicken breast",
            "db_query": "chicken breast grilled skinless",
            "portion": {"grams": 170, "grams_low": 150, "grams_high": 190, "description": "~6 oz, user-stated"},
            "recognition_confidence": 0.95,
            "portion_confidence": 0.85,
            "overall_confidence": 0.88,
            "reconciliation": {
                "signal": "agrees_with_quantity",
                "source_quote": "about 6oz chicken",
                "estimate_changed": True,
                "confidence_delta": 0.35,
                "action": "Moved grams 140->170 to match stated 6oz; tightened range.",
            },
        }
    ],
    "added_from_notes": [
        {
            "name": "olive oil",
            "db_query": "olive oil",
            "portion": {"grams": 10, "grams_low": 5, "grams_high": 15},
            "recognition_confidence": 0.0,
            "portion_confidence": 0.4,
            "overall_confidence": 0.4,
            "reconciliation": {
                "signal": "adds_unseen_detail",
                "source_quote": "cooked in olive oil",
                "action": "Added cooking oil not visible in photo; est. 1 tbsp.",
            },
        }
    ],
    "conflicts": [],
    "meal_confidence": 0.82,
}

GATE_EXAMPLE = {
    "gate": "needs_clarification",
    "total_kcal_point": 640,
    "total_kcal_swing": 185,
    "finalize": False,
    "drivers": [
        {"item_id": "item_3", "name": "olive oil", "mode": "portion",
         "kcal_point": 90, "kcal_swing": 90, "reason": "5-15g at ~9 kcal/g."},
        {"item_id": "item_2", "name": "white rice", "mode": "portion",
         "kcal_point": 270, "kcal_swing": 95, "reason": "1-2 cups; dense, wide range."},
    ],
    "clarifications": [
        {"item_id": "item_2", "type": "portion",
         "question": "Was the rice about a cup, or closer to two?", "removes_kcal_swing": 95},
        {"item_id": "item_3", "type": "portion",
         "question": "Was there about a tablespoon of oil, or closer to two?", "removes_kcal_swing": 90},
    ],
    "notes_for_user_facing_report": "Calorie range 560-745 pending rice and oil portions.",
}


def test_pass1_round_trips():
    out = Pass1Output.model_validate(PASS1_EXAMPLE)
    item = out.items[0]
    assert item.portion.grams_low <= item.portion.grams <= item.portion.grams_high
    assert 0 <= item.recognition_confidence <= 1
    assert out.scene.plate_diameter_cm_est == 27


def test_pass2_round_trips():
    out = Pass2Output.model_validate(PASS2_EXAMPLE)
    assert out.added_from_notes[0].name == "olive oil"
    assert out.items[0].reconciliation.signal == "agrees_with_quantity"
    assert out.meal_confidence == 0.82


def test_gate_round_trips():
    out = GateOutput.model_validate(GATE_EXAMPLE)
    assert out.finalize is False
    assert {c.type for c in out.clarifications} <= {"portion", "identity"}


def test_gate_threshold_defaults():
    t = GateThresholds()
    assert (
        t.band_tolerance_kcal,
        t.item_swing_kcal,
        t.material_kcal,
        t.id_threshold,
        t.max_questions,
    ) == (120, 60, 40, 0.6, 2)


def test_inverted_portion_range_rejected():
    bad_item = {**PASS1_EXAMPLE["items"][0],
                "portion": {"grams": 100, "grams_low": 200, "grams_high": 50}}
    bad = {**PASS1_EXAMPLE, "items": [bad_item]}
    with pytest.raises(ValidationError):
        Pass1Output.model_validate(bad)


def test_meal_report_constructs():
    report = MealReport(
        items=[],
        totals={"kcal": 0.0},
        total_kcal_point=0.0,
        total_kcal_swing=0.0,
        kcal_band=(0.0, 0.0),
    )
    assert report.kcal_band == (0.0, 0.0)
