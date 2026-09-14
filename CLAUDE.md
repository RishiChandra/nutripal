# Nutri Pal - Project Context

Audio-first health/nutrition assistant. This is **one agent** in a larger system: an
orchestrator routes to specialized subagents ("let me talk to my Nutri Pal"). Primary surface
is voice; a companion app handles photo upload and settings.

Scope of this agent: track food eaten per day and estimate macros from **text and/or photos**,
and track physical/mental health from user descriptions. Macros are the priority output;
fiber/vitamins/minerals are nice-to-haves. Room to add sleep/exercise later, not now.

## Current focus: the photo -> macro subagent

We fully designed the subagent that estimates macros from meal photos. It is built as **one
multimodal model run in three prompted passes, with deterministic code between them.**

```
Photos (primary) -> Pass 1 Blind vision -> [code] resolve+enrich -> Pass 2 Reconcile <- user notes (secondary)
                                                                          |
                                    [code] rescale+aggregate -> Pass 3 Gate -> Report | Ask user -+
                                                                                          +- answer loops back to Pass 2
```

### Key design decisions (do not regress these)

- **Portion size is the dominant error source**, not food identification. Design around it.
  (Grounded in Google's Nutrition5k work - single-RGB portion estimation is the hard part.)
- **Two-pass, blind-first.** Pass 1 sees the photo ONLY, so the user's text can't anchor the
  visual estimate. Pass 2 treats the visual estimate as the anchor and uses notes only to
  validate / adjust confidence (agree -> raise + tighten; conflict -> lower, don't overwrite;
  unseen detail like cooking oil -> add).
- **Macros come from a nutrition DB, never the model.** The model emits `db_query` + grams;
  deterministic code looks up USDA FoodData Central (Nutritionix/Edamam for branded) and does
  all arithmetic. This kills macro hallucination.
- **Uncertainty is expressed two ways:** a 0-1 confidence AND a `grams_low/high` range.
- **The clarification gate ranks by calorie SWING, not share of total.**
  `kcal_swing = (grams_high - grams_low) * kcal_per_g`. This captures portion uncertainty x
  calorie density, so it asks about a small blob of oil (dense, uncertain) but never about
  parsley. Two failure modes -> two question types: portion (large swing) and identity (low
  recognition or weak DB match -> density itself is wrong). Cap questions; phrase for one-breath
  voice answers; the answer re-enters at Pass 2. Metric generalizes to any tracked macro.

### Design artifacts in this repo

- `docs/photo_subagent_prompts.md` - the three prompts (blind / reconcile / evaluate) with
  system+user templates and output schemas, the deterministic between-pass layer as
  pseudo-Python (`resolve_food`, `enrich`, `scale`, `aggregate`), and a workflow diagram.
- `docs/photo_subagent_design.html` - rendered flow diagram of the subagent.

## Open / next tasks

1. **Deterministic layer -> real code.** Turn the pseudo-Python into an actual module against a
   chosen nutrition DB (USDA FoodData Central API is free; get an API key). Include the swing
   math and caching keyed on `(db_query, state)`.
2. **Nutrition5k benchmark harness.** Wire up the Nutrition5k test set and measure two things:
   portion MAE, and whether `portion_confidence` actually correlates with gram error (if not,
   the gate is cosmetic - re-tune Pass 1 scale anchors).
3. **Compiler agent.** Merges the photo subagent's report with any text-only logging into one
   final per-meal answer with totals + confidence.
4. **Orchestrator + voice loop.** Turn `clarifications[]` into spoken questions and feed the
   answer back into Pass 2.

## Conventions

- Keep all macro numbers and arithmetic in deterministic code; the model only supplies
  `db_query` and grams.
- Round only at output edges; keep full precision internally.
- Start the swing aggregation with a linear sum (conservative); switch to quadrature if the
  gate interrupts too often.

## Repo layout (Phase 0 scaffolding)

Python project, `src/` layout. Package `nutripal`:

- `src/nutripal/config.py` - `Settings` (API keys via `.env`, model id, cache path, swing mode).
- `src/nutripal/schemas/` - Pydantic contracts for every pass; they lock the data shapes the
  rest of the code depends on:
  - `pass1.py` - `Pass1Output` (blind vision: items, portion range, confidences, scene).
  - `pass2.py` - `Pass2Output` (reconciled items, `added_from_notes`, conflicts).
  - `nutrition.py` - `DbMatch`, `ScaledItem`, `MealReport` (deterministic layer + gate input).
    Note: `ScaledItem` carries BOTH `recognition_confidence` and `match_confidence` so the gate
    can raise an identity question from a weak DB match, not just a weak visual ID.
  - `gate.py` - `GateThresholds`, `GateOutput` (Pass 3 clarification gate).
- `tests/` - schema round-trip tests against the examples in `docs/photo_subagent_prompts.md`.

Tooling: Python >=3.11, Pydantic v2, `pytest`, `ruff`. Env managed with `uv` (or venv + pip).
Copy `.env.example` -> `.env` and fill `USDA_FDC_API_KEY` and `ANTHROPIC_API_KEY`.

Next up: **Phase 1** - implement the deterministic layer under `src/nutripal/nutrition/`.
