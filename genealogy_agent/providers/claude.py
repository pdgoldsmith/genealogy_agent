from __future__ import annotations

from .base import LLMBackend


class ClaudeBackend(LLMBackend):
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        # TODO: wire to Anthropic SDK messages API.
        return (
            f"[Claude:{self.model}] System={system_prompt[:80]!r} "
            f"User={user_prompt[:120]!r}"
        )
