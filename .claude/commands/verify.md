Run the project's verification ladder and report results.

1. Agent stack: `cd agent && source .venv/bin/activate && python tests/run_tests.py` — all 20 tests must pass with zero hardware/network/keys. The venv is Python 3.9 — if anything fails on syntax, check for 3.10+ features first.
2. If firmware changed: mock-compile the touched `.ino` with `-Wall -Wextra` (host-side, the way `keyboard_v1` was validated) and re-read its header rules (power-on order: USB first, THEN 12V; CASCADE_REVERSED flag).
3. If any Python file changed: verify 3.9 compatibility via `python -c "import ast; ast.parse(open(F).read(), feature_version=(3,9))"` for each changed file.
4. If CAD/dimensions changed: cross-check every value against `2x2_Prototype_Dimensions.md` and the locked parameters in `CLAUDE.md` / `docs/briefs/03_84key_plate_cad.md`; flag any contradiction rather than picking one.
5. Report pass/fail per rung, shortest possible. If everything passes, say so in one line.
