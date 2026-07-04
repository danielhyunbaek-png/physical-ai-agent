"""Hardware-free test ladder for the whole agent stack.

    cd agent && python tests/run_tests.py        (or: python -m unittest ...)

ZERO hardware, ZERO network, ZERO API keys: fake keyboard, dry-run mouse,
fake gantry transport, synthetic frames, scripted brain. If this passes on
the MacBook, the plumbing is sound end-to-end -- what's left to trust is
physics (solenoids, steppers) and model quality (prompt tuning).

Needs numpy + opencv (already in requirements.txt / the venv).
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from actions import Actuators, validate_action, validate_plan
from llm import LLM, extract_json
from mouse_driver import (DryRunMouse, GantryMouse, MouseKeysMouse,
                          apply_affine, fit_affine)
from runtime import Session, screenshot_b64
from tft.tft_agent import (TFTLayout, TFTTranslator, build_system_prompt,
                           make_phase_hook)
from vision import Vision


# ---- fakes -------------------------------------------------------------------
class FakeKB:
    """Records every driver call; stands in for KeyboardDriver."""

    def __init__(self):
        self.dry_run = True
        self.calls = []

    def type_text(self, text, lead_ms=0):
        self.calls.append(("type", text))

    def key(self, name):
        self.calls.append(("key", name))

    def chord(self, *names):
        self.calls.append(("chord",) + names)

    def hold(self, name):
        self.calls.append(("hold", name))

    def release(self, name="ALL"):
        self.calls.append(("release", name))

    def close(self):
        pass


class FakeSerial:
    """Answers every gantry command with OK; records the wire traffic."""

    def __init__(self):
        self.sent = []

    def write(self, b):
        self.sent.append(b.decode().strip())

    def readline(self):
        return b"OK\n"

    def close(self):
        pass


class FakeBrain:
    """Scripted LLM: returns queued plans; meters fake cost per call."""

    provider, model = "fake", "fake-1"

    def __init__(self, plans, cost_per_call=0.0):
        self.plans = list(plans)
        self.cost_per_call = cost_per_call
        self.calls = 0
        self.total_cost = 0.0

    def decide(self, system, goal, img_b64, history, extra=None):
        self.calls += 1
        self.total_cost += self.cost_per_call
        self.last_extra = extra
        return self.plans.pop(0) if self.plans else {"done": True,
                                                     "reason": "out of plans"}

    def stats(self):
        return {"provider": self.provider, "model": self.model,
                "calls": self.calls, "cost_usd": self.total_cost}


def synth_frame(seed=0):
    """A deterministic 1080p 'screenshot' with some structure."""
    rng = np.random.RandomState(seed)
    img = np.full((1080, 1920, 3), 40, np.uint8)
    for i in range(12):
        x, y = rng.randint(0, 1800), rng.randint(0, 1000)
        img[y:y + 60, x:x + 100] = rng.randint(60, 255, 3)
    return img


# ---- actions -------------------------------------------------------------------
class TestActions(unittest.TestCase):
    def test_validation(self):
        self.assertIsNone(validate_action({"type": "type", "text": "hi"}))
        self.assertIsNone(validate_action(
            {"type": "drag", "x1": 1, "y1": 2, "x2": 3, "y2": 4}))
        self.assertIn("missing", validate_action({"type": "drag", "x1": 1}))
        self.assertIn("unknown", validate_action({"type": "sudo"}))
        self.assertIn("wrong type", validate_action(
            {"type": "type", "text": 42}))
        ok, errs = validate_plan({"actions": [{"type": "key", "name": "A"},
                                              {"type": "nope"}]})
        self.assertEqual((len(ok), len(errs)), (1, 1))

    def test_dispatch_and_mouse_skip(self):
        kb = FakeKB()
        acts = Actuators(kb, None)
        res = acts.run([{"type": "key", "name": "Enter"},
                        {"type": "click", "x": 5, "y": 5}])
        self.assertEqual(res[0], "ok")
        self.assertIn("SKIP", res[1])
        self.assertIn(("key", "Enter"), kb.calls)

    def test_mousekeys_coexistence(self):
        kb = FakeKB()
        m = MouseKeysMouse(kb, {"est_px_s": 1000, "tap_px": 1})
        acts = Actuators(kb, m)
        acts.run([{"type": "click", "x": 960, "y": 540},   # enables MK
                  {"type": "type", "text": "hello"}])      # must disable MK
        self.assertFalse(m.enabled)
        # 5x LOpt toggles happened at least twice (on, then off)
        opts = [c for c in kb.calls if c == ("key", "LOpt")]
        self.assertGreaterEqual(len(opts), 10)


# ---- mouse drivers ---------------------------------------------------------------
class TestMouse(unittest.TestCase):
    def test_dryrun_drag(self):
        m = DryRunMouse()
        m.drag(10, 20, 30, 40)
        s = " ".join(m.log)
        self.assertIn("BTN L DOWN", s)
        self.assertIn("(30, 40)", s)
        self.assertIn("BTN L UP", s)
        self.assertLess(s.index("DOWN"), s.index("(30, 40)"))

    def test_mousekeys_moves(self):
        kb = FakeKB()
        m = MouseKeysMouse(kb, {"est_px_s": 500, "tap_px": 1, "fine_px": 40})
        m.enable()
        kb.calls = []
        m.move_to(m.pos[0] + 10, m.pos[1])          # fine: 10 taps of O
        taps = [c for c in kb.calls if c == ("key", "O")]
        self.assertEqual(len(taps), 10)
        kb.calls = []
        m.move_to(m.pos[0] + 300, m.pos[1])         # coarse: hold O
        self.assertIn(("hold", "O"), kb.calls)
        self.assertIn(("release", "O"), kb.calls)

    def test_gantry_protocol_and_affine(self):
        t = FakeSerial()
        g = GantryMouse(transport=t, calib={
            "pad_mm": [300, 200],
            "affine": [[300.0 / 1920, 0, 0], [0, 200.0 / 1080, 0]]})
        g.click("L", 960, 540)
        joined = " | ".join(t.sent)
        self.assertIn("HOME", joined)
        self.assertIn("MOVE 150.00 100.00", joined)
        self.assertIn("CLICK L", joined)

    def test_affine_fit_roundtrip(self):
        src = [(0, 0), (1920, 0), (960, 1080), (100, 900)]
        dst = [(0, 0), (300, 0), (150, 200), (15.625, 166.67)]
        A = fit_affine(src, dst)
        x, y = apply_affine(A, 1920, 0)
        self.assertAlmostEqual(x, 300, places=1)
        self.assertAlmostEqual(y, 0, places=1)


# ---- llm helpers ---------------------------------------------------------------
class TestLLM(unittest.TestCase):
    def test_extract_json(self):
        self.assertEqual(extract_json('{"a": 1}'), {"a": 1})
        self.assertEqual(extract_json('Sure! Here:\n```json\n{"a": {"b": 2}}'
                                      '\n```\nHope that helps!'),
                         {"a": {"b": 2}})
        self.assertEqual(extract_json('x {"s": "brace } in string"} y'),
                         {"s": "brace } in string"})
        with self.assertRaises(ValueError):
            extract_json("no json here")

    def test_metering(self):
        llm = LLM.__new__(LLM)               # no client, no key needed
        llm.model = "claude-sonnet-5"
        llm.calls = llm.tokens_in = llm.tokens_out = 0
        llm.total_cost = 0.0
        cost = llm._meter(1_000_000, 100_000)
        self.assertAlmostEqual(cost, 3.00 + 1.50, places=6)
        self.assertEqual(llm.calls, 1)


# ---- vision ----------------------------------------------------------------------
class TestVision(unittest.TestCase):
    def test_still_mode_and_hash(self):
        v = Vision(still=synth_frame(1))
        self.assertEqual(v.frame().shape, (1080, 1920, 3))
        h1 = v.screen_hash()
        self.assertEqual(Vision.hash_distance(h1, v.screen_hash()), 0)
        h2 = Vision.frame_hash(synth_frame(2))
        self.assertGreater(Vision.hash_distance(h1, h2), 5)
        self.assertTrue(v.wait_settle())      # still mode: instant True
        v.close()

    def test_crop_norm(self):
        img = synth_frame(3)
        crop = Vision.crop_norm(img, (0.5, 0.5, 0.25, 0.25))
        self.assertEqual(crop.shape[:2], (270, 480))

    def test_screen_calibration_roundtrip(self):
        v = Vision(still=synth_frame(4))
        v.calibrate_screen([(10, 10), (1900, 15), (1890, 1070), (5, 1060)])
        d = tempfile.mkdtemp()
        try:
            p = v.save_screen_calibration(os.path.join(d, "q.json"))
            v2 = Vision(still=synth_frame(4), calib_path=p)
            self.assertEqual(v2.screen().shape, (1080, 1920, 3))
        finally:
            shutil.rmtree(d)
        v.close()

    def test_screenshot_b64_downscales(self):
        v = Vision(still=synth_frame(5))
        b64 = screenshot_b64(v, max_px=800)
        self.assertLess(len(b64), 400_000)
        self.assertTrue(b64)
        v.close()


# ---- tft layer ---------------------------------------------------------------------
class TestTFT(unittest.TestCase):
    def setUp(self):
        self.L = TFTLayout()
        self.tr = TFTTranslator(self.L)

    def test_layout_math(self):
        for i in range(1, 6):
            x, y = self.L.shop_px(i)
            self.assertTrue(0 < x < 1920 and 0 < y < 1080)
        x0, _ = self.L.hex_px(0, 0)
        x1, _ = self.L.hex_px(1, 0)
        self.assertGreater(x1, x0)            # odd rows offset right

    def test_translator(self):
        prims, errs = self.tr([
            {"type": "tft_buy", "slot": 3},
            {"type": "tft_place", "bench": 0, "row": 3, "col": 2},
            {"type": "tft_roll"},
            {"type": "tft_sell", "bench": 4},
            {"type": "wait", "seconds": 1},
            {"type": "tft_buy", "slot": 9},           # out of range
            {"type": "mystery"},                      # unknown
        ])
        self.assertEqual(len(errs), 2)
        kinds = [p["type"] for p in prims]
        self.assertEqual(kinds, ["click", "drag", "key", "mouse_move",
                                 "key", "wait"])
        self.assertEqual(prims[2]["name"], "D")       # roll hotkey
        self.assertEqual(prims[4]["name"], "E")       # sell hotkey

    def test_prompt_and_phase_hook(self):
        p = build_system_prompt()
        self.assertIn("tft_buy", p)
        self.assertIn("interest", p.lower())
        hook = make_phase_hook(self.L)
        out = hook(Vision(still=synth_frame(6)), 0)
        self.assertEqual(out.get("phase"), "planning")
        self.assertFalse(out.get("skip", False))


# ---- runtime end-to-end ----------------------------------------------------------
class TestRuntime(unittest.TestCase):
    def _session(self, brain, **kw):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        kb = FakeKB()
        v = Vision(still=synth_frame(7))
        defaults = dict(mouse=DryRunMouse(), log_root=d, save_frames=False,
                        turn_delay_s=0, max_turns=10)
        defaults.update(kw)
        return Session(brain, kb, v, "test goal", **defaults), kb

    def test_full_session_done(self):
        brain = FakeBrain([
            {"done": False, "reason": "typing",
             "actions": [{"type": "type", "text": "hi"},
                         {"type": "bogus"}]},          # -> validation error
            {"done": True, "reason": "finished", "actions": []},
        ])
        s, kb = self._session(brain)
        summary = s.run()
        self.assertTrue(summary["stop"].startswith("done"))
        self.assertIn(("type", "hi"), kb.calls)
        self.assertIn("skipped", brain.last_extra)     # error was fed back
        log = os.path.join(summary["log_dir"], "session.jsonl")
        with open(log) as f:
            records = [json.loads(line) for line in f]
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["errors"],
                         ["unknown action type: 'bogus'"])
        self.assertTrue(os.path.exists(
            os.path.join(summary["log_dir"], "summary.json")))

    def test_budget_stop(self):
        brain = FakeBrain([{"done": False, "reason": "r", "actions": []}] * 50,
                          cost_per_call=0.30)
        s, _ = self._session(brain, budget_usd=1.0, max_turns=50,
                             stuck_after=99)
        summary = s.run()
        self.assertIn("budget", summary["stop"])
        self.assertLessEqual(brain.calls, 5)

    def test_stuck_abort_on_frozen_screen(self):
        brain = FakeBrain([{"done": False, "reason": "r", "actions": []}] * 50)
        s, _ = self._session(brain, max_turns=50, stuck_after=2)
        summary = s.run()                      # still image never changes
        self.assertIn("stuck", summary["stop"])

    def test_tft_translated_session(self):
        brain = FakeBrain([
            {"done": False, "reason": "buy + place",
             "actions": [{"type": "tft_buy", "slot": 1},
                         {"type": "tft_place", "bench": 0, "row": 3,
                          "col": 3}]},
            {"done": True, "reason": "ok", "actions": []},
        ])
        mouse = DryRunMouse()
        s, _ = self._session(brain, mouse=mouse,
                             translate=TFTTranslator(TFTLayout()))
        summary = s.run()
        self.assertTrue(summary["stop"].startswith("done"))
        joined = " ".join(mouse.log)
        self.assertIn("BTN L DOWN", joined)    # the drag happened


if __name__ == "__main__":
    unittest.main(verbosity=2)
