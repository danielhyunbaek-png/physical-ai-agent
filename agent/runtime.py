"""Session runtime: the production observe -> decide -> act loop.

agent_loop.py (general goals) and tft/play_tft.py (TFT games) are thin CLIs
over this one class. What it adds over the campsite loop:

  - session logging: logs/session_<ts>/ gets session.jsonl (one record per
    turn: plan, actions, results, cost, latency), the frame each decision
    saw (turn_NNN.jpg), and summary.json -- every game is replayable for
    prompt tuning
  - budget guards: max turns, max $ (from llm metering), max minutes
  - stuck detection: N consecutive visually-identical frames -> warn the
    model; keep being stuck -> abort (or escalate once, see below)
  - escalation tier: pass escalate_to=LLM('anthropic') and the cheap brain
    can hand hard turns up -- plan {"escalate": true} or repeated stuck
  - validation feedback: malformed actions aren't executed; the errors are
    fed back to the model next turn so it self-corrects
  - phase hook: callable(vision, turn) -> {"skip": bool, "extra": str,
    "phase": str}. TFT uses this to NOT call the LLM during combat --
    the ~70% call reduction lever
  - clean shutdown on Ctrl-C: keys released, mouse released, log flushed

Zero-hardware end-to-end: dry-run drivers + Vision(still=...) + a scripted
brain. That exact combination is the test ladder (tests/run_tests.py).
"""

from __future__ import annotations

import base64
import json
import os
import time

import cv2

from actions import Actuators, validate_plan

SYSTEM = """You control a PHYSICAL robot: solenoids press keys on a real \
keyboard and a robot mouse moves a real cursor. You see the target computer's \
screen through a webcam photo. Work toward the user's goal one small step at \
a time.

Reply ONLY with JSON: {"done": bool, "reason": "...", "actions": [...]}
Each action is one of:
  {"type": "type", "text": "hello"}            -- type text (shift handled)
  {"type": "key", "name": "Enter"}             -- named key (Enter, Esc, Tab,
                                                  Bksp, F1..F12, Up/Down/etc)
  {"type": "chord", "keys": ["LCmd","Space"]}  -- modifier combo
  {"type": "mouse_move", "x": 960, "y": 540}   -- cursor to screen pixel
  {"type": "click", "x": 960, "y": 540}        -- click (button "L" or "R")
  {"type": "drag", "x1":..,"y1":..,"x2":..,"y2":..} -- press-move-release
  {"type": "wait", "seconds": 2}               -- wait for UI to settle
Screen coordinates are 1920x1080. The robot mouse is imprecise: after a move
or click, CHECK the next screenshot and correct rather than assuming success.
Use at most 3 actions per turn, then re-observe. Set done=true when the goal
is visibly complete in the screenshot. If you are truly unsure what to do,
add "escalate": true to ask a stronger model."""


def screenshot_b64(vision, max_px=1568, quality=80):
    """Rectified screen -> downscaled JPEG base64 (the cost lever: smaller
    images = cheaper vision calls)."""
    img = vision.screen()
    h, w = img.shape[:2]
    scale = min(1.0, max_px / max(h, w))
    if scale < 1.0:
        img = cv2.resize(img, None, fx=scale, fy=scale)
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return base64.b64encode(buf).decode()


class Session:
    def __init__(self, brain, kb, vision, goal, mouse=None, system=SYSTEM,
                 max_turns=15, budget_usd=None, max_minutes=None,
                 escalate_to=None, translate=None, phase_hook=None,
                 log_root=None, save_frames=True, turn_delay_s=1.0,
                 stuck_after=3, history_keep=6):
        self.brain = brain
        self.escalate_to = escalate_to
        self.actuators = Actuators(kb, mouse)
        self.vision = vision
        self.goal = goal
        self.system = system
        self.max_turns = max_turns
        self.budget_usd = budget_usd
        self.max_minutes = max_minutes
        self.translate = translate or (lambda acts: validate_plan(
            {"actions": acts}))
        self.phase_hook = phase_hook
        self.save_frames = save_frames
        self.turn_delay_s = turn_delay_s
        self.stuck_after = stuck_after
        self.history_keep = history_keep

        root = log_root or os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "logs")
        self.log_dir = os.path.join(
            root, "session_" + time.strftime("%Y%m%d_%H%M%S"))
        os.makedirs(self.log_dir, exist_ok=True)
        self._log_f = open(os.path.join(self.log_dir, "session.jsonl"), "a")

    # ---- logging ----------------------------------------------------------------
    def _log(self, record):
        record["ts"] = round(time.time(), 3)
        self._log_f.write(json.dumps(record) + "\n")
        self._log_f.flush()

    def _save_frame(self, turn):
        if not self.save_frames:
            return None
        path = os.path.join(self.log_dir, "turn_{:03d}.jpg".format(turn))
        try:
            cv2.imwrite(path, self.vision.screen())
            return path
        except Exception:
            return None

    def _total_cost(self):
        c = self.brain.total_cost
        if self.escalate_to is not None:
            c += self.escalate_to.total_cost
        return c

    # ---- the loop -----------------------------------------------------------------
    def run(self):
        start = time.time()
        history = []
        feedback = None            # validation errors fed back next turn
        stuck_run = 0              # consecutive unchanged-screen turns
        escalated_for_stuck = False
        prev_hash = None
        stop = "max_turns"
        turn = 0

        print("[session] goal: {}".format(self.goal))
        print("[session] brain: {} / {}  log: {}".format(
            self.brain.provider, self.brain.model, self.log_dir))

        try:
            while turn < self.max_turns:
                # -- guards ------------------------------------------------------
                if self.budget_usd and self._total_cost() >= self.budget_usd:
                    stop = "budget ${:.2f} reached".format(self.budget_usd)
                    break
                if self.max_minutes and \
                        (time.time() - start) / 60 >= self.max_minutes:
                    stop = "time limit {}min reached".format(self.max_minutes)
                    break

                # -- observe ------------------------------------------------------
                self.vision.wait_settle()
                extra_parts = []
                if self.phase_hook is not None:
                    ph = self.phase_hook(self.vision, turn) or {}
                    if ph.get("skip"):     # e.g. TFT combat: no LLM call
                        self._log({"turn": turn, "phase": ph.get("phase"),
                                   "skipped": True})
                        time.sleep(self.turn_delay_s)
                        continue
                    if ph.get("extra"):
                        extra_parts.append(ph["extra"])

                cur_hash = None
                try:
                    cur_hash = self.vision.screen_hash()
                except Exception:
                    pass
                if cur_hash is not None and prev_hash is not None and \
                        self.vision.hash_distance(prev_hash, cur_hash) <= 5:
                    stuck_run += 1
                else:
                    stuck_run = 0
                prev_hash = cur_hash

                if stuck_run >= 2 * self.stuck_after:
                    stop = "stuck: screen unchanged {} turns".format(stuck_run)
                    break
                if stuck_run >= self.stuck_after:
                    extra_parts.append(
                        "NOTE: the screen has not changed for {} turns. Your "
                        "recent actions are not working -- try a different "
                        "approach.".format(stuck_run))

                if feedback:
                    extra_parts.append(feedback)
                    feedback = None

                img_b64 = screenshot_b64(self.vision)
                frame_path = self._save_frame(turn)

                # -- decide -------------------------------------------------------
                use_escalation = (self.escalate_to is not None and
                                  stuck_run >= self.stuck_after and
                                  not escalated_for_stuck)
                brain = self.brain
                t0 = time.time()
                try:
                    plan = brain.decide(self.system, self.goal, img_b64,
                                        history,
                                        extra="\n".join(extra_parts) or None)
                except Exception as e:
                    stop = "brain failure: {}".format(e)
                    break
                if (plan.get("escalate") or use_escalation) and \
                        self.escalate_to is not None:
                    print("[session] escalating turn {} to {}".format(
                        turn, self.escalate_to.model))
                    escalated_for_stuck = escalated_for_stuck or use_escalation
                    plan = self.escalate_to.decide(
                        self.system, self.goal, img_b64, history,
                        extra="\n".join(extra_parts) or None)
                latency = round(time.time() - t0, 2)

                # -- act -----------------------------------------------------------
                actions, errors = self.translate(plan.get("actions", []))
                if errors:
                    feedback = ("Your previous actions had errors and were "
                                "skipped: " + "; ".join(errors))
                results = self.actuators.run(actions)

                self._log({"turn": turn, "frame": frame_path,
                           "plan": plan, "executed": actions,
                           "results": results, "errors": errors,
                           "latency_s": latency,
                           "cost_usd": round(self._total_cost(), 4)})
                print("[session] turn {}: {} (+{} actions, {:.1f}s, "
                      "${:.3f} total)".format(
                          turn, plan.get("reason", "")[:80], len(actions),
                          latency, self._total_cost()))

                if plan.get("done"):
                    stop = "done: " + str(plan.get("reason", ""))[:120]
                    break

                history.append({"role": "user", "content":
                                "(turn {} executed: {})".format(
                                    turn, json.dumps(actions))})
                history.append({"role": "assistant",
                                "content": json.dumps(plan)})
                history = history[-self.history_keep:]
                turn += 1
                time.sleep(self.turn_delay_s)
        except KeyboardInterrupt:
            stop = "interrupted (Ctrl-C)"
        finally:
            self.actuators.shutdown()

        summary = {"goal": self.goal, "stop": stop, "turns": turn + 1,
                   "minutes": round((time.time() - start) / 60, 2),
                   "brain": self.brain.stats(),
                   "escalation": (self.escalate_to.stats()
                                  if self.escalate_to else None),
                   "log_dir": self.log_dir}
        with open(os.path.join(self.log_dir, "summary.json"), "w") as f:
            json.dump(summary, f, indent=2)
        self._log_f.close()
        print("[session] STOP: {}  ({} turns, {} min, ${:.3f})".format(
            stop, summary["turns"], summary["minutes"],
            self._total_cost()))
        return summary
