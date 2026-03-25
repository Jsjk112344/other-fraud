"""Tests for Google fallback and official price verification agents."""

import pytest
from unittest.mock import AsyncMock, patch


# --- Google Fallback Tests ---


@pytest.mark.asyncio
@patch("agents.google_fallback.tinyfish_extract", new_callable=AsyncMock)
async def test_google_search_returns_event_data(mock_extract):
    """google_event_search returns (dict, True) with expected keys when TinyFish succeeds."""
    from agents.google_fallback import google_event_search

    mock_extract.return_value = {
        "event_name": "F1 Singapore GP",
        "venue": "Marina Bay",
        "date": "2026-10-03",
        "face_value": 298,
        "source": "singaporegp.sg",
        "found": True,
    }

    result = await google_event_search("F1 Singapore GP")
    data, is_live = result

    assert is_live is True
    for key in ("event_name", "venue", "date", "face_value", "source", "found"):
        assert key in data
    assert data["found"] is True


@pytest.mark.asyncio
@patch("agents.google_fallback.tinyfish_extract", new_callable=AsyncMock)
async def test_google_search_event_not_found(mock_extract):
    """google_event_search returns found=False and unverified=True when event not in results."""
    from agents.google_fallback import google_event_search

    mock_extract.return_value = {"found": False}

    result = await google_event_search("Nonexistent Event")
    data, is_live = result

    assert data["found"] is False
    assert data["unverified"] is True
    assert is_live is True


@pytest.mark.asyncio
@patch("agents.google_fallback.tinyfish_extract", new_callable=AsyncMock)
async def test_google_search_tinyfish_failure(mock_extract):
    """google_event_search returns (None, False) when TinyFish returns None."""
    from agents.google_fallback import google_event_search

    mock_extract.return_value = None

    result = await google_event_search("F1 Singapore GP")
    data, is_live = result

    assert data is None
    assert is_live is False


def test_build_google_search_url():
    """build_google_search_url constructs proper Google search URL."""
    from agents.google_fallback import build_google_search_url

    result = build_google_search_url("F1 Singapore GP 2026")
    assert result.startswith("https://www.google.com/search?q=")
    assert "singapore+tickets+price" in result


def test_build_google_search_url_encodes_spaces():
    """build_google_search_url properly encodes spaces."""
    from agents.google_fallback import build_google_search_url

    result = build_google_search_url("Taylor Swift Eras Tour")
    assert "Taylor+Swift" in result or "Taylor%20Swift" in result
