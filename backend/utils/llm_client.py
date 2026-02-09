"""DeepSeek LLM client wrapper."""
import asyncio
import json
from typing import Any, Dict, List, Optional

import httpx
from config import settings


class LLMClient:
    """Client for interacting with DeepSeek API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
    ):
        """Initialize the LLM client.

        Args:
            api_key: DeepSeek API key. Defaults to settings.DEEPSEEK_API_KEY.
            base_url: API base URL. Defaults to settings.DEEPSEEK_BASE_URL.
            model: Model name. Defaults to settings.DEEPSEEK_MODEL.
            temperature: Sampling temperature. Defaults to settings.TEMPERATURE.
            max_tokens: Max tokens in response. Defaults to settings.MAX_TOKENS.
            top_p: Nucleus sampling parameter. Defaults to settings.TOP_P.
        """
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.base_url = base_url or settings.DEEPSEEK_BASE_URL
        self.model = model or settings.DEEPSEEK_MODEL
        self.temperature = temperature if temperature is not None else settings.TEMPERATURE
        self.max_tokens = max_tokens if max_tokens is not None else settings.MAX_TOKENS
        self.top_p = top_p if top_p is not None else settings.TOP_P

        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=120.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
        retry_count: int = 3,
    ) -> str:
        """Generate a completion from the LLM.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt.
            temperature: Override default temperature.
            max_tokens: Override default max tokens.
            response_format: Optional response format (e.g., {"type": "json_object"}).
            retry_count: Number of retries on failure.

        Returns:
            The generated text response.
        """
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        for attempt in range(retry_count):
            try:
                response = await self._make_request(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                )
                return response
            except httpx.HTTPStatusError as e:
                if attempt == retry_count - 1:
                    raise RuntimeError(f"LLM request failed after {retry_count} attempts: {e}") from e
                await asyncio.sleep(2**attempt)  # Exponential backoff
            except Exception as e:
                if attempt == retry_count - 1:
                    raise RuntimeError(f"LLM request failed: {e}") from e
                await asyncio.sleep(2**attempt)

        raise RuntimeError("Unexpected error in LLM client")

    async def _make_request(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> str:
        """Make a request to the DeepSeek API.

        Args:
            messages: List of message dictionaries.
            temperature: Override default temperature.
            max_tokens: Override default max tokens.
            response_format: Optional response format specification.

        Returns:
            The generated text response.

        Raises:
            httpx.HTTPStatusError: If the API request fails.
        """
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
            "top_p": self.top_p,
        }

        if response_format:
            payload["response_format"] = response_format

        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Generate a JSON response from the LLM.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt.
            temperature: Override default temperature.

        Returns:
            The parsed JSON response as a dictionary.
        """
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            response_format={"type": "json_object"},
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {response}") from e

    def count_tokens(self, text: str) -> int:
        """Estimate token count for a text.

        This is a rough estimate assuming ~4 characters per token for Chinese text
        and ~4 characters per token for English text. For accurate counting,
        consider using tiktoken or similar library.

        Args:
            text: The text to count tokens for.

        Returns:
            Estimated token count.
        """
        # Simple heuristic: approximately 1 token per 3-4 characters
        # This varies by language and content, but works as a rough estimate
        return len(text) // 3


async def get_llm_client() -> LLMClient:
    """Get a shared LLM client instance.

    Returns:
        An LLMClient instance.
    """
    return LLMClient()
