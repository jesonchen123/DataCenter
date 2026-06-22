from dataclasses import dataclass
from time import perf_counter
from typing import Callable

from app.core.config import Settings, settings as default_settings


class LLMClientError(RuntimeError):
    pass


@dataclass(frozen=True)
class LLMChatResult:
    content: str
    request_payload: dict
    response_payload: dict
    latency_ms: int


def is_llm_configured(settings: Settings = default_settings) -> bool:
    api_key = (settings.llm_api_key or "").strip()
    return bool(api_key and api_key not in {"your_api_key", "change_me"})


class OpenAICompatibleLLMClient:
    def __init__(
        self,
        settings: Settings = default_settings,
        post: Callable | None = None,
    ) -> None:
        self.settings = settings
        self._post = post or _resolve_post()

    def chat(
        self,
        messages: list[dict],
        response_format: dict | None = None,
    ) -> LLMChatResult:
        if not is_llm_configured(self.settings):
            raise LLMClientError("LLM API key is not configured.")

        payload = {
            "model": self.settings.llm_model_name,
            "messages": messages,
            "temperature": self.settings.llm_temperature,
            "max_tokens": self.settings.llm_max_tokens,
        }
        if response_format is not None:
            payload["response_format"] = response_format

        headers = {
            "Authorization": f"Bearer {self.settings.llm_api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.settings.llm_api_base_url.rstrip('/')}/chat/completions"

        started_at = perf_counter()
        try:
            response = self._post(
                url,
                headers=headers,
                json=payload,
                timeout=self.settings.llm_timeout,
            )
            response.raise_for_status()
            response_payload = response.json()
            content = response_payload["choices"][0]["message"]["content"]
        except Exception as exc:
            raise LLMClientError(str(exc)) from exc

        latency_ms = int((perf_counter() - started_at) * 1000)
        return LLMChatResult(
            content=content,
            request_payload=payload,
            response_payload=response_payload,
            latency_ms=latency_ms,
        )


def _resolve_post() -> Callable:
    try:
        import httpx
    except ImportError as exc:
        raise LLMClientError("httpx is required for real LLM calls.") from exc
    return httpx.post
