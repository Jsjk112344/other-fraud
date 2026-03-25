"""TinyFish async wrapper with timeout and thread isolation."""

from __future__ import annotations

import asyncio
import logging

try:
    from tinyfish import TinyFish, EventType, RunStatus
except ImportError:
    TinyFish = None
    EventType = None
    RunStatus = None

logger = logging.getLogger(__name__)

_client = None


def get_client() -> "TinyFish":
    """Lazily initialize TinyFish client (reads TINYFISH_API_KEY from env)."""
    global _client
    if _client is None:
        if TinyFish is None:
            raise RuntimeError("tinyfish package is not installed")
        _client = TinyFish()
    return _client


def _sync_extract(
    url: str,
    goal: str,
    stealth: bool = False,
    proxy_country: str | None = None,
) -> dict | None:
    """Synchronous TinyFish extraction -- runs in a thread for async compat."""
    kwargs: dict = {"url": url, "goal": goal}
    if stealth:
        kwargs["browser_profile"] = "stealth"
    if proxy_country:
        kwargs["proxy_config"] = {"enabled": True, "country_code": proxy_country}

    try:
        with get_client().agent.stream(**kwargs) as stream:
            for event in stream:
                if event.type == EventType.COMPLETE and event.status == RunStatus.COMPLETED:
                    return event.result_json
                if event.type == EventType.ERROR:
                    return None
    except Exception as e:
        logger.warning("TinyFish extraction failed for %s: %s", url, e)
        return None
    return None


async def tinyfish_extract(
    url: str,
    goal: str,
    stealth: bool = False,
    proxy_country: str | None = None,
    timeout: float = 15.0,
) -> dict | None:
    """Async TinyFish extraction with timeout. Returns None on failure."""
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(_sync_extract, url, goal, stealth, proxy_country),
            timeout=timeout,
        )
        return result
    except asyncio.TimeoutError:
        logger.warning("TinyFish extraction timed out for %s", url)
        return None
    except Exception as e:
        logger.warning("TinyFish extraction error for %s: %s", url, e)
        return None
