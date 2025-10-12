"""Tests for the Giphy service."""

import asyncio
import os

import pytest
from dotenv import load_dotenv

from app.services.giphy import GiphyService


@pytest.fixture(autouse=True)
def setup_env():
    """Load environment variables before each test."""
    load_dotenv()


def test_giphy_service_with_key():
    """Test that GiphyService returns a URL when given a valid API key."""
    api_key = os.getenv("GIPHY_API_KEY") or ""
    giphy = GiphyService(api_key, rating="r")
    result = asyncio.run(giphy("laughter"))
    assert result is not None


def test_giphy_service_without_key():
    """Test that GiphyService returns None when given an empty API key."""
    giphy = GiphyService("", rating="r")
    result = asyncio.run(giphy("laughter"))
    assert result is None
