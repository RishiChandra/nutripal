"""Pass 1 - Blind Vision Extraction (see docs/photo_subagent_prompts.md).

The model sees the photo(s) ONLY here; user notes are withheld so the visual estimate is not
anchored by text. The model emits identity + a portion gram range + confidences - never macros.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class Portion(BaseModel):
    grams: float = Field(ge=0, description="Best-estimate edible portion, grams.")
    grams_low: float = Field(ge=0, description="Low end of the visual uncertainty range.")
    grams_high: float = Field(ge=0, description="High end of the visual uncertainty range.")
    description: str | None = Field(default=None, description="Human anchor, e.g. 'one palm-sized piece'.")

    @model_validator(mode="after")
    def _range_ordered(self) -> "Portion":
        if self.grams_low > self.grams_high:
            raise ValueError(f"grams_low ({self.grams_low}) must be <= grams_high ({self.grams_high})")
        return self


class Pass1Item(BaseModel):
    id: str
    name: str
    state: str = Field(description="Preparation: raw, grilled, fried, ... (drives DB density).")
    db_query: str = Field(description="Short, DB-friendly search query.")
    portion: Portion
    recognition_confidence: float = Field(ge=0, le=1)
    portion_confidence: float = Field(ge=0, le=1)
    cues_used: list[str] = Field(default_factory=list)
    limiting_factors: list[str] = Field(default_factory=list)


class Scene(BaseModel):
    reference_objects: list[str] = Field(default_factory=list)
    plate_diameter_cm_est: float | None = None
    occlusion: str | None = Field(default=None, description="Free text, e.g. none|light|moderate|heavy.")
    photo_count: int = Field(default=1, ge=0)
    single_angle: bool = True


class Pass1Output(BaseModel):
    items: list[Pass1Item]
    scene: Scene
    overall_notes: str | None = None
