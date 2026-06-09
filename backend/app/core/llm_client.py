"""
LLM Client — OpenAI-compatible async client for agent inference.
Supports any provider with an OpenAI-compatible API (OpenAI, Azure, Groq, Ollama, etc.).

Configure via environment:
  LLM_API_KEY        — required
  LLM_BASE_URL       — defaults to https://api.openai.com/v1
  LLM_MODEL           — defaults to gpt-4o-mini
  LLM_TEMPERATURE     — defaults to 0.3

Usage:
  from app.core.llm_client import llm

  result = await llm.chat(
      system_prompt="You are a governance agent...",
      user_prompt="Analyze the following data assets...",
      response_format={"type": "json_object"},
  )
  # result = {"content": "...", "parsed": {...}, "model": "gpt-4o-mini",
  #            "tokens": {"prompt": 150, "completion": 80, "total": 230},
  #            "cost_cents": 0.05, "duration_ms": 450}
"""

import json
import time
import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

# ── Cost per 1M tokens (USD) ──
_MODEL_PRICING: dict[str, tuple[float, float]] = {
    # (prompt_per_1M, completion_per_1M)
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4-turbo": (10.00, 30.00),
    "gpt-3.5-turbo": (0.50, 1.50),
    "claude-3-5-sonnet": (3.00, 15.00),
    "claude-3-haiku": (0.25, 1.25),
    "deepseek-chat": (0.27, 1.10),
    "llama-3.1-70b": (0.59, 0.79),
}


class LLMClient:
    """Async OpenAI-compatible LLM client."""

    def __init__(self):
        self._http: Optional[object] = None  # httpx.AsyncClient

    async def _get_client(self):
        """Lazy-init httpx client."""
        if self._http is None:
            try:
                import httpx
            except ImportError:
                raise RuntimeError(
                    "httpx is required for LLM calls. Install with: pip install httpx"
                )
            self._http = httpx.AsyncClient(
                base_url=settings.llm_base_url,
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=120.0,
            )
        return self._http

    @property
    def is_configured(self) -> bool:
        """Check if the LLM client has the minimum required configuration."""
        return bool(settings.llm_api_key)

    async def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict | None = None,
        temperature: float | None = None,
        max_tokens: int = 2000,
    ) -> dict:
        """
        Send a chat completion request.

        Returns:
            {
                "content": str,          # Raw response text
                "parsed": dict | None,   # Parsed JSON if response_format is json_object
                "model": str,            # Model used
                "tokens": {"prompt": int, "completion": int, "total": int},
                "cost_cents": float,     # Estimated cost in cents
                "duration_ms": int,      # Wall-clock time
            }
        """
        if not self.is_configured:
            raise RuntimeError(
                "LLM_API_KEY not set. Set it in .env or environment variables."
            )

        client = await self._get_client()
        temp = temperature if temperature is not None else settings.llm_temperature
        model = settings.llm_model

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temp,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        start = time.monotonic()

        try:
            resp = await client.post("/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.error(f"[LLM] API call failed: {e}")
            raise

        duration_ms = int((time.monotonic() - start) * 1000)

        choice = data["choices"][0]
        content = choice["message"]["content"]
        usage = data.get("usage", {})

        tokens = {
            "prompt": usage.get("prompt_tokens", 0),
            "completion": usage.get("completion_tokens", 0),
            "total": usage.get("total_tokens", 0),
        }

        # Parse JSON if response_format was json_object
        parsed = None
        if response_format and response_format.get("type") == "json_object":
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                logger.warning("[LLM] Failed to parse JSON response, using raw content")
                parsed = {"raw": content}

        # Estimate cost
        prompt_price, completion_price = _MODEL_PRICING.get(model, (0.15, 0.60))
        cost_usd = (tokens["prompt"] / 1_000_000) * prompt_price + \
                   (tokens["completion"] / 1_000_000) * completion_price
        cost_cents = round(cost_usd * 100, 2)

        return {
            "content": content,
            "parsed": parsed,
            "model": data.get("model", model),
            "tokens": tokens,
            "cost_cents": cost_cents,
            "duration_ms": duration_ms,
        }


# Singleton
llm = LLMClient()
