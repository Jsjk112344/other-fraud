"""Tests for TinyFish base agent wrapper."""

import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from agents.base import tinyfish_extract


class TestTinyFishExtract:
    """TinyFish base wrapper handles timeout, success, and error cases."""

    @pytest.mark.asyncio
    async def test_tinyfish_extract_returns_none_on_timeout(self):
        """tinyfish_extract returns None when the call times out."""
        async def slow_thread(*args, **kwargs):
            raise asyncio.TimeoutError()

        with patch("agents.base.asyncio") as mock_asyncio:
            mock_asyncio.TimeoutError = asyncio.TimeoutError
            mock_asyncio.to_thread = AsyncMock(return_value={"title": "test"})
            mock_asyncio.wait_for = AsyncMock(side_effect=asyncio.TimeoutError())
            result = await tinyfish_extract(url="https://example.com", goal="test")
        assert result is None

    @pytest.mark.asyncio
    async def test_tinyfish_extract_returns_result_on_success(self):
        """tinyfish_extract returns result dict when TinyFish call succeeds."""
        expected = {"title": "test"}
        with patch("agents.base._sync_extract", return_value=expected):
            result = await tinyfish_extract(url="https://example.com", goal="test")
        assert result == expected

    @pytest.mark.asyncio
    async def test_tinyfish_extract_returns_none_on_exception(self):
        """tinyfish_extract returns None when TinyFish call raises any exception."""
        with patch("agents.base._sync_extract", side_effect=RuntimeError("fail")):
            result = await tinyfish_extract(url="https://example.com", goal="test")
        assert result is None
