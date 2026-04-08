from __future__ import annotations

from .base import LLMBackend


class OpenAIBackend(LLMBackend):
    def __init__(self, model: str = "gpt-4.1") -> None:
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        # TODO: wire to OpenAI SDK responses API.
        return (
            f"[OpenAI:{self.model}] System={system_prompt[:80]!r} "
            f"User={user_prompt[:120]!r}"
        )
