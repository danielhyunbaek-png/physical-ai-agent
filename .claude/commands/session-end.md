Close out the current working session.

1. Append a dated session record to `CLAUDE.md` covering: decisions made (with rationale), things built/changed (files + what they do), corrections to earlier facts (write "was X, now Y" — never silently overwrite), anything left UNVERIFIED, and the agreed next steps. Match the style of the existing session records.
2. If any locked parameter or design fact changed, update it in place in the relevant CLAUDE.md section too (not just the session record), and check whether `2x2_Prototype_Dimensions.md` or a `docs/briefs/` file also needs the fix.
3. Stage and commit with a descriptive message (look at `git log --oneline` for the house style: terse, content-first).
4. **Remind Daniel to `git push`** — hard project rule at milestones; the repo has drifted ahead of origin before.
5. End with a 3-line summary: what changed, what's unverified, what's next.
