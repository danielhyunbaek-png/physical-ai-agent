# selfwrite: the keyboard writes its own software

From the 698-like comment: *"Now let Claude control it and write its own software."*

`gen0.py` (written by a human) asks Claude to write `gen1.py`. **The solenoids type gen1 into Terminal**, then type `python3 gen1.py &`. gen1 now controls the keyboard: it asks Claude for gen2, types it and launches it. **gen3 is the last one** and says goodbye. Each generation gets a GOAL from its parent and has to do one new visible thing.

Safety rails live in `selfwrite.py`, which Claude can't edit:
- Hard stop at gen 3.
- Generated code can only import `selfwrite`, with no os, files or network.
- Code is syntax-checked before it's typed.
- Every typed file is **read back from disk and compared** before it runs.

## 0. One-time setup (~5 min)
```bash
cd ~/"Documents/Claude/Projects/Physical AI Agent/agent" && source .venv/bin/activate
python3 -c "import serial; print('pyserial ok')"
export ANTHROPIC_API_KEY=sk-ant-...     # console.anthropic.com -> API keys
cd ../tools/selfwrite
python3 selfwrite.py preview            # NO typing: prints the gen1 Claude would write
```
If `preview` prints Python code, the API key works.

## 1. Map the keys Python needs (~30–45 min, PSU on only while testing)
```bash
python3 selfwrite.py check              # lists mapped keys + what's missing
```
**Must have:** `Enter LShift 9 0 ; = ' . , -`. All of these are needed for `( ) : = " ' . , _`.
**Should have:** `1–8`, `[ ]`, `/`. Claude is told which characters exist and will avoid the rest.
To map a key: Serial Monitor, `FIRE <ch>`, watch which key moves, then `MAP <ch> <Name>` and `SAVE`. Run `check` again when you're done.
Then a smoke test: open a blank Terminal and type `python3 -c "print('hi')"` with `TYPE` and `KEY Enter`.

## 2. Film
1. Close Serial Monitor and the Monkeytype Chrome tab. They hold the USB port.
2. Use a clean Terminal window with a big font (Cmd +), in `tools/selfwrite` with the venv active. Run `rm -f gen1.py gen2.py gen3.py`.
3. Type yourself: `python3 gen0.py &` and press Enter. **Then hands off.** Keep the Terminal window focused the whole run.
4. Each generation takes about 1–2 min of typing plus 10–20 s for Claude. Total is roughly 5–7 min, so speed it up in the edit.

**If it stops:** `[selfwrite] ... differs` means a key was missed, usually from plate sag. It retries once, then stops. If the shell is stuck in `heredoc>`, press Ctrl-C by hand. For the shot list, the `gen1.py`–`gen3.py` files are the evidence. Open them at the end of the video.

## Env knobs
`CLAUDE_MODEL` (default `claude-sonnet-5-5`) · `KB_PULSE` (50) · `KB_PORT` · `SELFWRITE_MAX_GEN` (3) · `KB_DRY=1 SELFWRITE_FAKE=1 python3 gen0.py` runs the whole chain with no hardware and no API.
