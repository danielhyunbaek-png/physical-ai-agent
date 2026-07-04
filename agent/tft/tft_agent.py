"""TFT layer: semantic game actions, UI layout math, phase gating, prompt.

The end goal of the whole project: the physical agent plays Teamfight
Tactics. This module keeps ALL TFT knowledge in one place, layered on the
generic runtime:

  layout.json    where UI elements live (normalized coords -- calibrate!)
  set_data.json  editable set roster/traits/comps (update each rotation)
  TFTLayout      normalized coords -> screen pixels
  TFTTranslator  semantic actions ({"type":"tft_buy","slot":2}) -> primitives
                 (clicks/drags/hotkeys). Hotkeys D/F/E/W go through the
                 PHYSICAL keyboard -- Wave 1 hardware does most of the game;
                 only buy/place/move/augment need the robot mouse.
  phase hook     during combat the outcome is out of our hands -> skip LLM
                 calls entirely (the ~70% cost lever). Combat detection uses
                 a user-captured template (templates/combat_marker.png);
                 without one, every turn is treated as actionable (safe).
  system prompt  TFT economy/positioning strategy + the action vocabulary,
                 with the set data folded in.

Semantic actions the model emits (translated here, validated here):
  {"type": "tft_buy", "slot": 1..5}            click a shop card
  {"type": "tft_sell", "bench": 0..8}          hover bench + E
  {"type": "tft_place", "bench": 0..8, "row": 0..3, "col": 0..6}  drag
  {"type": "tft_move", "from_row":..,"from_col":..,"to_row":..,"to_col":..}
  {"type": "tft_bench", "row": 0..3, "col": 0..6}  hover board + W
  {"type": "tft_roll"}                          D
  {"type": "tft_level"}                         F
  {"type": "tft_lock"}                          click shop lock
  {"type": "tft_augment", "slot": 1..3}         click an augment card
Plus every generic primitive (click/drag/key/wait...) passes through.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions import validate_action  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SCREEN_W, SCREEN_H = 1920, 1080


def _load_json(name):
    with open(os.path.join(HERE, name)) as f:
        return json.load(f)


def load_layout():
    return _load_json("layout.json")


def load_set_data():
    return _load_json("set_data.json")


# ---- layout math -------------------------------------------------------------
class TFTLayout:
    """Turns layout.json's normalized coords into screen pixels."""

    def __init__(self, data=None, w=SCREEN_W, h=SCREEN_H):
        self.d = data or load_layout()
        self.w, self.h = w, h

    def _px(self, nx, ny):
        return int(nx * self.w), int(ny * self.h)

    def shop_px(self, slot):
        """slot 1..5"""
        s = self.d["shop_slots"]
        return self._px(s["x"][slot - 1], s["y"])

    def bench_px(self, i):
        """bench slot 0..8"""
        b = self.d["bench"]
        return self._px(b["x0"] + i * b["x_step"], b["y"])

    def hex_px(self, row, col):
        """player board hex: row 0 (back) .. 3 (front), col 0..6"""
        b = self.d["board"]
        x = 0.5 + (col - 3) * b["col_step"]
        if row % 2 == 1:
            x += b["odd_row_offset"]
        return self._px(x, b["row_y"][row])

    def button_px(self, name):
        return self._px(*self.d["buttons"][name])

    def augment_px(self, slot):
        """slot 1..3"""
        a = self.d["augments"]
        return self._px(a["x"][slot - 1], a["y"])

    def region(self, name):
        return tuple(self.d["regions"][name])

    def hotkey(self, name):
        return self.d["hotkeys"][name]


# ---- semantic -> primitive translation ----------------------------------------
def _rng(v, lo, hi, what):
    if not isinstance(v, int) or not (lo <= v <= hi):
        raise ValueError("{} must be an integer {}..{}".format(what, lo, hi))
    return v


class TFTTranslator:
    """Callable for Session(translate=...): expands tft_* actions into
    primitives and validates everything. Returns (primitives, errors)."""

    def __init__(self, layout=None):
        self.L = layout or TFTLayout()

    def expand(self, a):
        L = self.L
        kind = a.get("type")
        if kind == "tft_buy":
            x, y = L.shop_px(_rng(a.get("slot"), 1, 5, "slot"))
            return [{"type": "click", "x": x, "y": y}]
        if kind == "tft_sell":
            x, y = L.bench_px(_rng(a.get("bench"), 0, 8, "bench"))
            return [{"type": "mouse_move", "x": x, "y": y},
                    {"type": "key", "name": L.hotkey("sell_hovered")}]
        if kind == "tft_place":
            bx, by = L.bench_px(_rng(a.get("bench"), 0, 8, "bench"))
            hx, hy = L.hex_px(_rng(a.get("row"), 0, 3, "row"),
                              _rng(a.get("col"), 0, 6, "col"))
            return [{"type": "drag", "x1": bx, "y1": by, "x2": hx, "y2": hy}]
        if kind == "tft_move":
            x1, y1 = L.hex_px(_rng(a.get("from_row"), 0, 3, "from_row"),
                              _rng(a.get("from_col"), 0, 6, "from_col"))
            x2, y2 = L.hex_px(_rng(a.get("to_row"), 0, 3, "to_row"),
                              _rng(a.get("to_col"), 0, 6, "to_col"))
            return [{"type": "drag", "x1": x1, "y1": y1, "x2": x2, "y2": y2}]
        if kind == "tft_bench":
            x, y = L.hex_px(_rng(a.get("row"), 0, 3, "row"),
                            _rng(a.get("col"), 0, 6, "col"))
            return [{"type": "mouse_move", "x": x, "y": y},
                    {"type": "key", "name": L.hotkey("bench_hovered")}]
        if kind == "tft_roll":
            return [{"type": "key", "name": L.hotkey("reroll")}]
        if kind == "tft_level":
            return [{"type": "key", "name": L.hotkey("buy_xp")}]
        if kind == "tft_lock":
            x, y = L.button_px("lock")
            return [{"type": "click", "x": x, "y": y}]
        if kind == "tft_augment":
            x, y = L.augment_px(_rng(a.get("slot"), 1, 3, "slot"))
            return [{"type": "click", "x": x, "y": y}]
        return None                    # not a TFT action

    def __call__(self, actions):
        primitives, errors = [], []
        if not isinstance(actions, list):
            return [], ["actions must be a list"]
        for a in actions:
            if not isinstance(a, dict):
                errors.append("action must be a JSON object")
                continue
            try:
                expanded = self.expand(a)
            except ValueError as e:
                errors.append("{}: {}".format(a.get("type"), e))
                continue
            if expanded is None:       # generic primitive: validate as-is
                err = validate_action(a)
                if err:
                    errors.append(err)
                else:
                    primitives.append(a)
            else:
                primitives.extend(expanded)
        return primitives, errors


# ---- phase gating ---------------------------------------------------------------
def make_phase_hook(layout=None, template_path=None):
    """Session phase_hook: skip LLM calls during combat.

    Detection: template match on a user-captured combat marker (crop a
    distinctive combat-only UI element and save it as
    tft/templates/combat_marker.png). Falls back to 'always actionable'
    when no template exists -- correct, just not cost-optimal.
    Also OCRs the stage number into the per-turn context when possible.
    """
    L = layout or TFTLayout()
    tpl = template_path or os.path.join(HERE, "templates",
                                        "combat_marker.png")
    have_tpl = os.path.exists(tpl)

    def hook(vision, turn):
        out = {"phase": "planning"}
        if have_tpl:
            try:
                if vision.find(tpl, threshold=0.82):
                    return {"phase": "combat", "skip": True}
            except Exception:
                pass
        try:
            stage = vision.read_region_norm(L.region("stage"))
            if stage:
                out["extra"] = "Stage indicator reads: {!r}".format(stage)
        except Exception:
            pass                        # OCR is best-effort context
        return out

    return hook


# ---- the TFT brain prompt ---------------------------------------------------------
def _summarize_set(sd):
    champs = [c for c in sd.get("champions", [])
              if not c.get("_placeholder")]
    traits = [t for t in sd.get("traits", []) if not t.get("_placeholder")]
    comps = [c for c in sd.get("comps", []) if not c.get("_placeholder")]
    if not champs:
        return ("Set data file not filled in yet -- read champions, costs "
                "and traits from the screen.")
    lines = ["Set {} (patch {}):".format(sd.get("set"), sd.get("patch"))]
    lines.append("Champions: " + "; ".join(
        "{} ({}g: {})".format(c["name"], c["cost"], ",".join(c["traits"]))
        for c in champs))
    if traits:
        lines.append("Traits: " + "; ".join(
            "{} {}".format(t["name"], t["breakpoints"]) for t in traits))
    if comps:
        lines.append("Preferred comps: " + "; ".join(
            "{} (core: {})".format(c["name"], ",".join(c["core"]))
            for c in comps))
    return "\n".join(lines)


def build_system_prompt(set_data=None):
    sd = set_data or load_set_data()
    econ = sd.get("economy", {})
    return """You are playing Teamfight Tactics through a PHYSICAL robot: \
solenoids press real keys and a robot mouse moves a real cursor, watching \
the screen through a webcam. Screenshots are imperfect -- if a read is \
ambiguous, prefer safe actions and re-check next turn.

STRATEGY
- Economy first: interest pays 1 gold per {bp} held (max {mx}). Sit on \
breakpoints; don't roll below 50 unless your board is dying or you hit a \
power spike. Level with F at standard timings; roll-downs at 4-1 or when \
low HP forces it.
- Keep a frontline (rows 2-3) of tanks and a backline (row 0) of carries.
- Buy pairs toward 2-stars; sell strays that fit no trait.
- During carousel or when nothing useful is possible, wait.
- Augments matter: if unsure which augment to pick, add "escalate": true.

{setinfo}

Reply ONLY with JSON: {{"done": bool, "reason": "...", "actions": [...]}}
TFT actions (preferred -- the robot knows where the UI is):
  {{"type": "tft_buy", "slot": 1-5}}       buy a shop card
  {{"type": "tft_sell", "bench": 0-8}}     sell from bench
  {{"type": "tft_place", "bench": 0-8, "row": 0-3, "col": 0-6}}
  {{"type": "tft_move", "from_row":..,"from_col":..,"to_row":..,"to_col":..}}
  {{"type": "tft_bench", "row": 0-3, "col": 0-6}}
  {{"type": "tft_roll"}}  {{"type": "tft_level"}}  {{"type": "tft_lock"}}
  {{"type": "tft_augment", "slot": 1-3}}
  {{"type": "wait", "seconds": 2}}
Board rows: 0 = back line, 3 = front line. Bench slots count 0-8 from the
left. Shop slots count 1-5 from the left.
Generic actions also work: {{"type":"click","x":..,"y":..}}, "drag", "key".
Use at most 3 actions per turn, then re-observe. The robot mouse is slow and
imprecise -- verify each placement in the next screenshot and fix mistakes.
Set done=true only when the game is over.""".format(
        bp=econ.get("interest_breakpoints", [10, 20, 30, 40, 50])[0],
        mx=econ.get("max_interest", 5),
        setinfo=_summarize_set(sd))


if __name__ == "__main__":
    L = TFTLayout()
    tr = TFTTranslator(L)
    prims, errs = tr([{"type": "tft_buy", "slot": 3},
                      {"type": "tft_place", "bench": 0, "row": 3, "col": 2},
                      {"type": "tft_roll"},
                      {"type": "tft_buy", "slot": 9}])
    assert len(prims) == 3 and len(errs) == 1, (prims, errs)
    print("[tft] shop 3 ->", L.shop_px(3), " hex(3,2) ->", L.hex_px(3, 2))
    print("[tft] translator smoke test done; prompt is",
          len(build_system_prompt()), "chars")
