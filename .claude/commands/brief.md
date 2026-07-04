Load a milestone brief and run the session from it.

Argument (optional): $ARGUMENTS — a brief number or keyword (e.g. "01", "solder", "cad", "wave2", "tft").

1. List `docs/briefs/` and pick the brief matching the argument; if no argument, show the table from `docs/briefs/README.md` and ask which one.
2. Read the chosen brief in full, plus `docs/PLAYBOOK.md` and the "Current state" section of `CLAUDE.md`.
3. If the brief contradicts CLAUDE.md, trust CLAUDE.md (it's newer) and fix the brief.
4. Restate the brief's goal and definition-of-done in 2–3 lines, confirm with Daniel, then execute the brief's order of operations, checking its failure-mode list whenever something misbehaves.
