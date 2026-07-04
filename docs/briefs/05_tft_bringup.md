# Brief 05 — TFT bring-up: first real game

**Goal:** the physical agent plays a TFT game end-to-end on a cheap brain within budget.

## Pre-game checklist (canonical order — also in `agent/README.md`)

1. `calibrate.py screen` — C920 on tripod, screen-quad rectification saved.
2. `calibrate.py tft` — overlay PNG check. **`tft/layout.json` coords are EYEBALLED DEFAULTS — verify every region against the overlay before trusting.**
3. **Fill `tft/set_data.json`** — it's a placeholder; populate with the live set's champions/traits/costs before any game.
4. Capture `tft/templates/combat_marker.png` — enables the combat-phase hook that skips LLM calls (~70% cost lever). Do not play a paid game without it.
5. `calibrate.py mousekeys` (or `gantry` if Wave 2 is built) — mouse backend calibration.
6. `cd agent && source .venv/bin/activate` — **every new Terminal** (#1 failure mode).

## Run strategy (cost discipline)

- Rehearse free: `--provider ollama` (qwen3-vl:8b local), `--dry-run`/`--still` first, then live keyboard with ollama.
- First paid game: cheap cloud (gemini/deepseek/qwen, ~$0.10–0.50/game), `--budget-usd` set, `--escalate-to anthropic` for augment choices only (or plan `"escalate": true`).
- `play_tft.py` defaults: ollama, 800 turns. Logs land in `agent/logs/` (gitignored) — keep them; they're the tuning corpus.
- Runtime guards already exist: budget/turn/minute stops, stuck detection (frame dHash), validation-error feedback. Use them, don't rebuild them.

## Semantic layer (already written — extend, don't bypass)

`tft_agent.py` maps tft_buy/sell/place/move/bench/roll/level/lock/augment → primitives. Hotkeys D/F/E/W go through the PHYSICAL keyboard; only buys/placements need the mouse. New actions belong in `agent/actions.py` (single vocabulary — add once, works everywhere).

## Debug ladder when something misbehaves

1. `python tests/run_tests.py` (20 tests, zero hardware) — if this fails, the problem is software, stop there.
2. `--dry-run --scripted` — plumbing without LLM or hardware.
3. `--still frame.png` — vision without the camera.
4. ollama live — full loop, $0.
5. Only then paid providers.

## Definition of done

One complete game, total spend logged and under budget, per-turn logs saved, prompt-tuning notes appended to CLAUDE.md; commit + **git push**. Film the first game — this is THE milestone.
