"""Provider-pluggable LLM brain for the agent.

One class, many brains. Everything except Anthropic speaks the OpenAI-style
API format, so we cover local (Ollama) and cheap cloud (DeepSeek, Qwen,
Gemini) with a single code path.

Cost tiers (July 2026 ballpark, per TFT game at ~700 turns):
    ollama    $0        local Qwen3-VL on the M4 Pro -- develop/debug here
    gemini    ~$0.1-0.4 Flash tier -- cheap real games
    deepseek  ~$0.1-0.4 V4 Flash tier (check vision support for your model)
    qwen      ~$0.1-0.5 DashScope qwen-vl tier
    anthropic ~$4-8     Sonnet -- reserve for hard decisions / tuning sessions

Production upgrades over the campsite version:
    - retries with backoff on transport errors (3 tries)
    - JSON-repair second ask when a reply won't parse (small models chat)
    - token + $ metering per call and per session (PRICES is editable --
      numbers drift; treat estimates as ballpark for the budget guard)
    - decide(..., extra=...) lets callers inject per-turn context (TFT phase,
      validation errors being fed back) without rebuilding the system prompt

Model names drift -- override with --model if a preset 404s.

API keys come from environment variables (never hardcode / never commit):
    export GEMINI_API_KEY=...      (aistudio.google.com)
    export DEEPSEEK_API_KEY=...    (platform.deepseek.com)
    export DASHSCOPE_API_KEY=...   (Alibaba DashScope, for qwen)
    export ANTHROPIC_API_KEY=...   (console.anthropic.com)
Ollama needs no key -- install and run locally:
    brew install ollama && ollama pull qwen3-vl:8b
"""

from __future__ import annotations

import json
import os
import time

PRESETS = {
    "anthropic": {"base_url": None,
                  "model": "claude-sonnet-5",
                  "key_env": "ANTHROPIC_API_KEY"},
    "ollama":    {"base_url": "http://localhost:11434/v1",
                  "model": "qwen3-vl:8b",
                  "key_env": None},
    "gemini":    {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
                  "model": "gemini-2.5-flash",       # check for newer flash tiers
                  "key_env": "GEMINI_API_KEY"},
    "deepseek":  {"base_url": "https://api.deepseek.com/v1",
                  "model": "deepseek-chat",          # confirm vision-capable model
                  "key_env": "DEEPSEEK_API_KEY"},
    "qwen":      {"base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
                  "model": "qwen-vl-plus",
                  "key_env": "DASHSCOPE_API_KEY"},
    "openai":    {"base_url": None,
                  "model": "gpt-4o-mini",
                  "key_env": "OPENAI_API_KEY"},
}

# $ per 1M tokens (input, output). EDITABLE -- prices drift; these only feed
# the session budget guard, so ballpark is fine. Unknown models cost 0.
PRICES = {
    "claude-sonnet-5":  (3.00, 15.00),
    "gemini-2.5-flash": (0.30, 2.50),
    "deepseek-chat":    (0.27, 1.10),
    "qwen-vl-plus":     (0.21, 0.63),
    "gpt-4o-mini":      (0.15, 0.60),
}

RETRIES = 3
BACKOFF_S = 2.0


class LLM:
    """llm = LLM('ollama'); plan = llm.decide(system, goal, img_b64, history)"""

    def __init__(self, provider="anthropic", model=None):
        if provider not in PRESETS:
            raise ValueError("provider must be one of {}".format(list(PRESETS)))
        self.provider = provider
        p = PRESETS[provider]
        self.model = model or p["model"]
        self.calls = 0
        self.tokens_in = 0
        self.tokens_out = 0
        self.total_cost = 0.0

        key = os.environ.get(p["key_env"]) if p["key_env"] else "ollama"
        if p["key_env"] and not key:
            raise RuntimeError("set {0} in your environment first "
                               "(export {0}=...)".format(p["key_env"]))

        if provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic()
        else:
            from openai import OpenAI          # pip install openai
            self.client = OpenAI(base_url=p["base_url"], api_key=key)

    # ---- metering -----------------------------------------------------------
    def _meter(self, tin, tout):
        self.calls += 1
        self.tokens_in += tin
        self.tokens_out += tout
        pin, pout = PRICES.get(self.model, (0.0, 0.0))
        cost = tin / 1e6 * pin + tout / 1e6 * pout
        self.total_cost += cost
        return cost

    # ---- raw call (one image + text turn) -----------------------------------
    def _call(self, system, user_text, img_b64, history):
        if self.provider == "anthropic":
            content = []
            if img_b64:
                content.append({"type": "image", "source": {
                    "type": "base64", "media_type": "image/jpeg",
                    "data": img_b64}})
            content.append({"type": "text", "text": user_text})
            msg = self.client.messages.create(
                model=self.model, max_tokens=700, system=system,
                messages=history + [{"role": "user", "content": content}],
            )
            u = getattr(msg, "usage", None)
            self._meter(getattr(u, "input_tokens", 0) if u else 0,
                        getattr(u, "output_tokens", 0) if u else 0)
            return msg.content[0].text
        content = []
        if img_b64:
            content.append({"type": "image_url", "image_url": {
                "url": "data:image/jpeg;base64," + img_b64}})
        content.append({"type": "text", "text": user_text})
        resp = self.client.chat.completions.create(
            model=self.model, max_tokens=700,
            messages=[{"role": "system", "content": system}]
            + history + [{"role": "user", "content": content}],
        )
        u = getattr(resp, "usage", None)
        self._meter(getattr(u, "prompt_tokens", 0) if u else 0,
                    getattr(u, "completion_tokens", 0) if u else 0)
        return resp.choices[0].message.content

    def _call_retrying(self, system, user_text, img_b64, history):
        last = None
        for attempt in range(RETRIES):
            try:
                return self._call(system, user_text, img_b64, history)
            except Exception as e:                       # transport/rate errors
                last = e
                wait = BACKOFF_S * (2 ** attempt)
                print("[llm] call failed ({}); retry in {:.0f}s".format(e, wait))
                time.sleep(wait)
        raise RuntimeError("LLM unreachable after {} tries: {}".format(
            RETRIES, last))

    # ---- public -------------------------------------------------------------
    def decide(self, system, goal, img_b64, history, extra=None):
        """One observe->decide turn. Returns the parsed JSON plan dict.

        extra: optional per-turn string appended to the user text (phase
        hints, validation errors fed back). On unparseable output, asks once
        more for bare JSON before giving up.
        """
        user_text = "Goal: {}\nWhat next?".format(goal)
        if extra:
            user_text += "\n" + extra
        text = self._call_retrying(system, user_text, img_b64, history)
        try:
            return extract_json(text)
        except ValueError:
            print("[llm] unparseable reply; asking for bare JSON once")
            repair = (user_text + "\nYour last reply was not valid JSON. "
                      "Reply with ONLY the JSON object, nothing else.")
            text = self._call_retrying(system, repair, img_b64, history)
            return extract_json(text)      # second failure raises to caller

    def stats(self):
        return {"provider": self.provider, "model": self.model,
                "calls": self.calls, "tokens_in": self.tokens_in,
                "tokens_out": self.tokens_out,
                "cost_usd": round(self.total_cost, 4)}


def extract_json(text):
    """Pull the first balanced {...} block out of a model reply (models love
    to chat around their JSON, especially small local ones; some fence it)."""
    if text is None:
        raise ValueError("empty model reply")
    start = text.find("{")
    if start < 0:
        raise ValueError("no JSON in model reply: {!r}".format(text[:200]))
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        c = text[i]
        if esc:
            esc = False
            continue
        if c == "\\" and in_str:
            esc = True
        elif c == '"':
            in_str = not in_str
        elif not in_str:
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(text[start:i + 1])
    # fall back to greedy (old behavior) for truncated-but-parseable replies
    end = text.rfind("}") + 1
    return json.loads(text[start:end])
