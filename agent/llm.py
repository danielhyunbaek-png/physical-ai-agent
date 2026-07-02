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

Model names drift -- override with --model if a preset 404s.

API keys come from environment variables (never hardcode / never commit):
    export GEMINI_API_KEY=...      (aistudio.google.com)
    export DEEPSEEK_API_KEY=...    (platform.deepseek.com)
    export DASHSCOPE_API_KEY=...   (Alibaba DashScope, for qwen)
    export ANTHROPIC_API_KEY=...   (console.anthropic.com)
Ollama needs no key -- install and run locally:
    brew install ollama && ollama pull qwen3-vl:8b
"""

import json
import os

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


class LLM:
    """llm = LLM('ollama'); plan = llm.decide(system, goal, img_b64, history)"""

    def __init__(self, provider="anthropic", model=None):
        if provider not in PRESETS:
            raise ValueError(f"provider must be one of {list(PRESETS)}")
        self.provider = provider
        p = PRESETS[provider]
        self.model = model or p["model"]

        key = os.environ.get(p["key_env"]) if p["key_env"] else "ollama"
        if p["key_env"] and not key:
            raise RuntimeError(f"set {p['key_env']} in your environment first "
                               f"(export {p['key_env']}=...)")

        if provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic()
        else:
            from openai import OpenAI          # pip install openai
            self.client = OpenAI(base_url=p["base_url"], api_key=key)

    def decide(self, system, goal, img_b64, history):
        """One observe->decide turn. Returns the parsed JSON plan dict."""
        user_text = f"Goal: {goal}\nWhat next?"
        if self.provider == "anthropic":
            msg = self.client.messages.create(
                model=self.model, max_tokens=500, system=system,
                messages=history + [{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {
                            "type": "base64", "media_type": "image/jpeg",
                            "data": img_b64}},
                        {"type": "text", "text": user_text},
                    ]}],
            )
            text = msg.content[0].text
        else:
            resp = self.client.chat.completions.create(
                model=self.model, max_tokens=500,
                messages=[{"role": "system", "content": system}]
                + history + [{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{img_b64}"}},
                        {"type": "text", "text": user_text},
                    ]}],
            )
            text = resp.choices[0].message.content
        return extract_json(text)


def extract_json(text):
    """Pull the first {...} block out of a model reply (models love to chat
    around their JSON, especially small local ones)."""
    start = text.find("{")
    end = text.rfind("}") + 1
    if start < 0 or end <= start:
        raise ValueError(f"no JSON in model reply: {text[:200]!r}")
    return json.loads(text[start:end])
