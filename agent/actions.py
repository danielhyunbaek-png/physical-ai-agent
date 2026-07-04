"""One action vocabulary for the whole agent.

The LLM emits JSON actions; this module is the single place that defines,
validates, and executes them. The general loop and the TFT layer both route
through Actuators, so a new action type is added HERE once and works
everywhere. Semantic TFT actions (tft_buy, tft_place...) are expanded into
these primitives by tft/tft_agent.py before execution.

Primitives:
  keyboard  {"type":"type","text":"hi"}            physical typing
            {"type":"key","name":"Enter"}          one named key
            {"type":"chord","keys":["LCmd","Space"]}
            {"type":"hold","name":"LShift"} / {"type":"release","name":"ALL"}
  mouse     {"type":"mouse_move","x":960,"y":540}
            {"type":"click","x":960,"y":540,"button":"L"}   (x/y optional)
            {"type":"drag","x1":..,"y1":..,"x2":..,"y2":..}
  control   {"type":"wait","seconds":2}

Validation is strict on shape but forgiving on extras -- models decorate.
"""

from __future__ import annotations

import time

# type -> (required fields, {field: python types})
SPECS = {
    "type":       (("text",), {"text": str}),
    "key":        (("name",), {"name": str}),
    "chord":      (("keys",), {"keys": list}),
    "hold":       (("name",), {"name": str}),
    "release":    ((), {"name": str}),
    "wait":       ((), {"seconds": (int, float)}),
    "mouse_move": (("x", "y"), {"x": (int, float), "y": (int, float)}),
    "click":      ((), {"x": (int, float), "y": (int, float), "button": str}),
    "drag":       (("x1", "y1", "x2", "y2"),
                   {"x1": (int, float), "y1": (int, float),
                    "x2": (int, float), "y2": (int, float), "button": str}),
}

MOUSE_ACTIONS = ("mouse_move", "click", "drag")
KEYBOARD_ACTIONS = ("type", "key", "chord", "hold", "release")


def validate_action(a):
    """Return None if valid, else a short error string (fed back to the LLM)."""
    if not isinstance(a, dict):
        return "action must be a JSON object"
    kind = a.get("type")
    if kind not in SPECS:
        return "unknown action type: {!r}".format(kind)
    required, types = SPECS[kind]
    for f in required:
        if f not in a:
            return "{}: missing field {!r}".format(kind, f)
    for f, t in types.items():
        if f in a and not isinstance(a[f], t):
            return "{}: field {!r} has wrong type".format(kind, f)
    if kind == "chord" and not all(isinstance(k, str) for k in a["keys"]):
        return "chord: keys must be strings"
    return None


def validate_plan(plan):
    """Validate a whole {"done":..,"reason":..,"actions":[..]} plan.
    Returns (ok_actions, errors)."""
    ok, errors = [], []
    if not isinstance(plan, dict):
        return [], ["plan must be a JSON object"]
    actions = plan.get("actions", [])
    if not isinstance(actions, list):
        return [], ["actions must be a list"]
    for a in actions:
        err = validate_action(a)
        if err:
            errors.append(err)
        else:
            ok.append(a)
    return ok, errors


class Actuators:
    """Owns the keyboard + mouse and executes validated actions.

    Handles the Mouse Keys coexistence problem: before any keyboard action it
    calls mouse.suspend() (Mouse Keys OFF so letters type), and mouse actions
    resume() it internally. Backends that don't care have no-op hooks.
    """

    def __init__(self, kb, mouse=None):
        self.kb = kb
        self.mouse = mouse

    def execute(self, a):
        """Execute one action. Returns a result string for the session log."""
        kind = a["type"]
        if kind in MOUSE_ACTIONS and self.mouse is None:
            return "SKIP: no mouse backend (--mouse) configured"

        if kind in KEYBOARD_ACTIONS and self.mouse is not None:
            self.mouse.suspend()

        if kind == "type":
            self.kb.type_text(a["text"])
        elif kind == "key":
            self.kb.key(a["name"])
        elif kind == "chord":
            self.kb.chord(*a["keys"])
        elif kind == "hold":
            self.kb.hold(a["name"])
        elif kind == "release":
            self.kb.release(a.get("name", "ALL"))
        elif kind == "wait":
            time.sleep(min(float(a.get("seconds", 1)), 15.0))
        elif kind == "mouse_move":
            self.mouse.move_to(a["x"], a["y"])
        elif kind == "click":
            self.mouse.click(a.get("button", "L"), a.get("x"), a.get("y"))
        elif kind == "drag":
            self.mouse.drag(a["x1"], a["y1"], a["x2"], a["y2"],
                            a.get("button", "L"))
        return "ok"

    def run(self, actions):
        """Execute a validated action list; returns per-action results."""
        results = []
        for a in actions:
            try:
                results.append(self.execute(a))
            except Exception as e:                       # keep the loop alive
                results.append("ERROR: {}".format(e))
        return results

    def shutdown(self):
        """Best-effort safe state: everything released, Mouse Keys off."""
        try:
            self.kb.release("ALL")
        except Exception:
            pass
        if self.mouse is not None:
            try:
                self.mouse.release("L")
                self.mouse.close()
            except Exception:
                pass


if __name__ == "__main__":
    good = {"type": "drag", "x1": 1, "y1": 2, "x2": 3, "y2": 4}
    bad = {"type": "drag", "x1": 1}
    assert validate_action(good) is None
    assert validate_action(bad) is not None
    print("[actions] validation smoke test done")
