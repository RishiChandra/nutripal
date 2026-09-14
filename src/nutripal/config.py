"""Runtime configuration for Nutri Pal.

Secrets come from the environment or a local ``.env`` (never committed). Field names map to
upper-cased env vars, so ``anthropic_api_key`` reads ``ANTHROPIC_API_KEY`` - the same variable
the Anthropic SDK picks up natively.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- credentials ---
    usda_fdc_api_key: str | None = Field(default=None, description="USDA FoodData Central key (free).")
    anthropic_api_key: str | None = Field(default=None, description="Also read natively by the Anthropic SDK.")

    # --- model ---
    vision_model: str = Field(
        default="claude-sonnet-5",
        description="Multimodal model for Pass 1/2 vision and Pass 3 question phrasing.",
    )

    # --- deterministic layer ---
    cache_path: Path = Field(
        default=Path(".cache/nutrition.sqlite"),
        description="On-disk nutrition cache keyed on (db_query, state).",
    )
    swing_aggregation: Literal["linear", "quadrature"] = Field(
        default="linear",
        description="Linear = conservative worst case; switch to quadrature if the gate over-asks.",
    )


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton. Call ``get_settings.cache_clear()`` in tests to reload."""
    return Settings()
