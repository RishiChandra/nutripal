# Nutri Pal

Audio-first nutrition assistant. This repo houses the **photo -> macro subagent**: it estimates
a meal's macros from photo(s) (+ optional notes) using one multimodal model run in three
prompted passes, with deterministic nutrition-DB lookups and arithmetic **between** the passes.

See [`CLAUDE.md`](CLAUDE.md) for design context and
[`docs/photo_subagent_prompts.md`](docs/photo_subagent_prompts.md) for the full pass-by-pass spec.

## Layout

```
src/nutripal/
  config.py            # settings + API keys
  schemas/             # Pydantic contracts for each pass + the internal report
docs/                  # design spec + rendered diagram
tests/                 # schema round-trip tests
```

## Setup

Requires Python >= 3.11.

With [uv](https://docs.astral.sh/uv/):

```bash
uv sync --extra dev
cp .env.example .env    # then fill in the two API keys
uv run pytest
```

Or with venv + pip:

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
pytest
```

## Status

- **Phase 0 - scaffolding + schemas** (done)
- Phase 1 - deterministic layer (`nutrition/`: FDC client, resolve/enrich/scale/aggregate, swing, cache)
- Phase 2 - the three model passes + pipeline
- Phase 3 - Nutrition5k benchmark harness
- Phase 4 - compiler agent
- Phase 5 - orchestrator + voice loop
