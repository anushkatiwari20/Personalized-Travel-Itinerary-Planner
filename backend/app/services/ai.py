"""AI Model Integration Services."""

import json
import logging
import re
from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import Any, Optional

import httpx

from app.config import get_settings
from app.utils.errors import AIGenerationError

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    name: str = "base"

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text using the LLM."""
        pass


class GroqProvider(LLMProvider):
    """Groq API provider."""

    name = "groq"

    def __init__(self, api_key: str, model: str):
        """Initialize Groq provider."""
        try:
            from groq import AsyncGroq

            self.client = AsyncGroq(api_key=api_key)
            self.model = model
            logger.info("Groq AsyncClient initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Groq: {str(e)}")
            raise AIGenerationError(f"Groq initialization failed: {str(e)}")

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=4096,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            raise AIGenerationError(f"Groq generation failed: {str(e)}")


class HuggingFaceProvider(LLMProvider):
    """Hugging Face Inference API provider."""

    name = "huggingface"

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.url = "https://router.huggingface.co/v1/chat/completions"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 4096,
            "temperature": 0.7,
        }
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.post(self.url, headers=headers, json=payload)
                r.raise_for_status()
                data = r.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"HuggingFace generation failed: {e}")
            raise AIGenerationError(f"HuggingFace generation failed: {str(e)}")


class OllamaProvider(LLMProvider):
    """Local Ollama provider (offline mode)."""

    name = "ollama"

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "format": "json",
        }
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                r = await client.post(f"{self.base_url}/api/chat", json=payload)
                r.raise_for_status()
                return r.json()["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise AIGenerationError(f"Ollama generation failed: {str(e)}")


class TemplateProvider(LLMProvider):
    """Offline fallback used when no AI key is configured.

    Produces a structured, deterministic itinerary so the whole app can be
    demoed and tested without any external API.
    """

    name = "template"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        dest = _extract(r"Create a detailed (.+?) itinerary", user_prompt, "your destination")
        start = _extract(r"from (\d{4}-\d{2}-\d{2})", user_prompt, str(date.today()))
        days = int(_extract(r"\((\d+) day\(s\)\)", user_prompt, "1"))
        budget = float(_extract(r"Budget: ₹(\d+)", user_prompt, "2000"))
        style = _extract(r"Travel style: (\w+)", user_prompt, "cultural")
        start_d = date.fromisoformat(start)
        itinerary_days = []
        for i in range(days):
            d = start_d + timedelta(days=i)
            itinerary_days.append(
                {
                    "day": i + 1,
                    "date": d.isoformat(),
                    "title": f"{style.title()} day {i + 1} in {dest}",
                    "morning": f"Old Town of {dest} - heritage walk and main landmark (Time: 150 minutes, Cost: ₹{int(budget*0.15)})",
                    "afternoon": f"Local museum & market district of {dest} (Time: 180 minutes, Cost: ₹{int(budget*0.2)})",
                    "evening": f"Sunset viewpoint and riverside / promenade in {dest} (Time: 120 minutes, Cost: ₹{int(budget*0.1)})",
                    "dining": [
                        {"name": "Local thali house", "description": "Regional vegetarian & non-veg thalis", "cost": f"₹{int(budget*0.08)}-₹{int(budget*0.12)} per meal"},
                        {"name": "Street food lane", "description": "Chaat, kebabs, sweets", "cost": f"₹{int(budget*0.03)}-₹{int(budget*0.06)} per meal"},
                        {"name": "Rooftop cafe", "description": "Coffee with a city view", "cost": f"₹{int(budget*0.05)}-₹{int(budget*0.1)} per meal"},
                    ],
                    "stay": f"Stay near the centre of {dest} for easy access to attractions and transport.",
                    "transit": "Use metro / auto-rickshaws (₹30-₹200 per ride) or ride-hailing apps; most stops today are within 5 km of each other.",
                    "daily_cost": round(budget * 0.9, 2),
                    "notes": "Set AI_PROVIDER and an API key in backend/.env to get a fully personalised AI itinerary.",
                }
            )
        return json.dumps(
            {
                "summary": f"A {days}-day {style} trip to {dest}, clustered by neighbourhood to minimise travel time and keep each day within ₹{int(budget)} per person.",
                "total_estimated_cost": round(budget * 0.9 * days, 2),
                "itinerary_days": itinerary_days,
            }
        )


def _extract(pattern: str, text: str, default: str) -> str:
    m = re.search(pattern, text)
    return m.group(1) if m else default


class AIOrchestrator:
    """Orchestration layer: picks a provider, calls it, parses JSON output."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    @property
    def provider_name(self) -> str:
        return self.provider.name

    async def generate_json(self, system_prompt: str, user_prompt: str, retries: int = 2) -> dict[str, Any]:
        last_error: Optional[Exception] = None
        for attempt in range(retries + 1):
            raw = await self.provider.generate(system_prompt, user_prompt)
            try:
                return parse_json_response(raw)
            except ValueError as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1}: could not parse model output as JSON: {e}")
                user_prompt = user_prompt + "\n\nIMPORTANT: Your previous answer was not valid JSON. Return ONLY the JSON object."
        raise AIGenerationError(f"Model did not return valid JSON: {last_error}")


def parse_json_response(raw: str) -> dict[str, Any]:
    """Robustly extract a JSON object from model output."""
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError("No JSON object found in model output")


_orchestrator: Optional[AIOrchestrator] = None


def _real(key) -> bool:
    """True only for a real key — ignores blank values and .env.example placeholders."""
    return bool(key) and not str(key).startswith(("your_", "gsk_your", "hf_your"))


def get_ai_orchestrator() -> AIOrchestrator:
    """Return a singleton orchestrator built from settings."""
    global _orchestrator
    if _orchestrator is not None:
        return _orchestrator

    s = get_settings()
    provider_name = (s.ai_provider or "groq").lower()
    provider: LLMProvider

    if provider_name == "groq" and _real(s.groq_api_key):
        provider = GroqProvider(s.groq_api_key, s.groq_model)
    elif provider_name == "huggingface" and _real(s.huggingface_api_key):
        provider = HuggingFaceProvider(s.huggingface_api_key, s.huggingface_model)
    elif provider_name == "ollama":
        provider = OllamaProvider(s.ollama_base_url, s.ollama_model)
    else:
        logger.warning(
            f"AI_PROVIDER='{provider_name}' but no API key configured — using offline template provider."
        )
        provider = TemplateProvider()

    logger.info(f"AI provider in use: {provider.name}")
    _orchestrator = AIOrchestrator(provider)
    return _orchestrator