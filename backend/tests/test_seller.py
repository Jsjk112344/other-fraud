"""Tests for Carousell seller investigation agent."""

import pytest
from unittest.mock import AsyncMock, patch


# --- Carousell seller tests ---


@pytest.mark.asyncio
async def test_seller_profile_fields():
    """investigate_carousell_seller returns correct fields when TinyFish succeeds."""
    mock_raw = {
        "account_age": "2 years",
        "total_listings": "15",
        "listing_categories": ["Tickets", "Electronics"],
        "overall_rating": 4.5,
        "reviews": [
            {"reviewer": "buyer1", "rating": 5, "text": "great seller", "date": "2026-01-10"},
            {"reviewer": "buyer2", "rating": 1, "text": "scam never delivered", "date": "2026-02-15"},
        ],
    }
    with patch("agents.seller.tinyfish_extract", new_callable=AsyncMock, return_value=mock_raw):
        from agents.seller import investigate_carousell_seller

        result, is_live = await investigate_carousell_seller("testuser")

    assert is_live is True
    assert "account_age" in result
    assert "total_listings" in result
    assert "listing_categories" in result
    assert "review_count" in result
    assert "reviews" in result
    assert "review_sentiment" in result
    assert "platform" in result
    assert result["platform"] == "carousell"


@pytest.mark.asyncio
async def test_seller_profile_fallback():
    """investigate_carousell_seller falls back to mock data when TinyFish returns None."""
    with patch("agents.seller.tinyfish_extract", new_callable=AsyncMock, return_value=None):
        from agents.seller import investigate_carousell_seller

        result, is_live = await investigate_carousell_seller("testuser")

    assert is_live is False
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_seller_profile_url():
    """build_seller_profile_url constructs correct Carousell URL."""
    from agents.seller import build_seller_profile_url

    url = build_seller_profile_url("ticketseller123")
    assert url == "https://www.carousell.sg/u/ticketseller123/"


@pytest.mark.asyncio
async def test_seller_uses_stealth():
    """investigate_carousell_seller calls tinyfish_extract with stealth=True and proxy_country='SG'."""
    mock_extract = AsyncMock(return_value={"account_age": "1 year", "reviews": []})
    with patch("agents.seller.tinyfish_extract", mock_extract):
        from agents.seller import investigate_carousell_seller

        await investigate_carousell_seller("testuser")

    mock_extract.assert_called_once()
    call_kwargs = mock_extract.call_args
    assert call_kwargs.kwargs.get("stealth") is True or call_kwargs[1].get("stealth") is True
    assert call_kwargs.kwargs.get("proxy_country") == "SG" or call_kwargs[1].get("proxy_country") == "SG"
    assert "/u/testuser/" in (call_kwargs.kwargs.get("url") or call_kwargs[1].get("url") or call_kwargs[0][0])


def test_normalize_seller_profile():
    """normalize_seller_profile maps raw response to standard schema."""
    from agents.seller import normalize_seller_profile

    raw = {
        "account_age": "2 years",
        "total_listings": "15",
        "listing_categories": ["Tickets"],
        "reviews": [{"text": "great seller", "rating": 5}],
    }
    result = normalize_seller_profile(raw)
    assert result["review_count"] == 1
    assert result["total_listings"] == 15
    assert result["platform"] == "carousell"


def test_analyze_review_sentiment_positive():
    """analyze_review_sentiment detects positive reviews."""
    from agents.seller import analyze_review_sentiment

    result = analyze_review_sentiment([{"text": "great seller"}, {"text": "fast delivery"}])
    assert "2 positive" in result


def test_analyze_review_sentiment_negative():
    """analyze_review_sentiment detects negative reviews."""
    from agents.seller import analyze_review_sentiment

    result = analyze_review_sentiment([{"text": "scam artist never delivered"}])
    assert "1 negative" in result


def test_analyze_review_sentiment_mixed():
    """analyze_review_sentiment handles mixed reviews."""
    from agents.seller import analyze_review_sentiment

    result = analyze_review_sentiment([
        {"text": "great"},
        {"text": "scam"},
        {"text": "okay i guess"},
    ])
    assert "1 positive" in result
    assert "1 negative" in result
    assert "1 neutral" in result
