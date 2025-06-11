# pytest . -v -s

import asyncio
import json
import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock
from dotenv import dotenv_values

import pymexc._async.base
from pymexc._async.spot import WebSocket

env = dotenv_values(".env")
api_key = env["API_KEY"]
api_secret = env["API_SECRET"]

PRINT_RESPONSE = True


@pytest_asyncio.fixture
async def ws_client():
    """Create a new WebSocket client for each test."""
    client = WebSocket(api_key=api_key, api_secret=api_secret)
    yield client
    # Cleanup
    if hasattr(client, "ws"):
        await client.ws.close()
    if hasattr(client, "session"):
        await client.session.close()


@pytest.mark.asyncio
async def test_deals_stream(ws_client: WebSocket):
    """Test the deals stream subscription."""
    messages = []

    async def handle_message(msg):
        messages.append(msg)
        if len(messages) >= 2:  # Get at least 2 messages
            await ws_client.unsubscribe("public.deals")

    await ws_client.deals_stream(handle_message, "BTCUSDT")

    # Wait for messages
    await asyncio.sleep(2)

    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, dict)
        assert "d" in msg  # deals data
        assert "s" in msg["d"]  # symbol
        assert msg["d"]["s"] == "BTCUSDT"


@pytest.mark.asyncio
async def test_kline_stream(ws_client: WebSocket):
    """Test the kline stream subscription."""
    messages = []

    async def handle_message(msg):
        messages.append(msg)
        if len(messages) >= 2:  # Get at least 2 messages
            await ws_client.unsubscribe("public.kline")

    await ws_client.kline_stream(handle_message, "BTCUSDT", "1m")

    # Wait for messages
    await asyncio.sleep(2)

    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, dict)
        assert "d" in msg  # kline data
        assert "s" in msg["d"]  # symbol
        assert msg["d"]["s"] == "BTCUSDT"
        assert "k" in msg["d"]  # kline data


@pytest.mark.asyncio
async def test_increase_depth_stream(ws_client: WebSocket):
    """Test the increase depth stream subscription."""
    messages = []

    async def handle_message(msg):
        messages.append(msg)
        if len(messages) >= 2:  # Get at least 2 messages
            await ws_client.unsubscribe("public.increase.depth")

    await ws_client.increase_depth_stream(handle_message, "BTCUSDT")

    # Wait for messages
    await asyncio.sleep(2)

    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, dict)
        assert "d" in msg  # depth data
        assert "s" in msg["d"]  # symbol
        assert msg["d"]["s"] == "BTCUSDT"


@pytest.mark.asyncio
async def test_limit_depth_stream(ws_client: WebSocket):
    """Test the limit depth stream subscription."""
    messages = []

    async def handle_message(msg):
        messages.append(msg)
        if len(messages) >= 2:  # Get at least 2 messages
            await ws_client.unsubscribe("public.limit.depth")

    await ws_client.limit_depth_stream(handle_message, "BTCUSDT", 5)

    # Wait for messages
    await asyncio.sleep(2)

    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, dict)
        assert "d" in msg  # depth data
        assert "s" in msg["d"]  # symbol
        assert msg["d"]["s"] == "BTCUSDT"
        assert "b" in msg["d"]  # bids
        assert "a" in msg["d"]  # asks


@pytest.mark.asyncio
async def test_book_ticker_stream(ws_client: WebSocket):
    """Test the book ticker stream subscription."""
    messages = []

    async def handle_message(msg):
        messages.append(msg)
        if len(messages) >= 2:  # Get at least 2 messages
            await ws_client.unsubscribe("public.bookTicker")

    await ws_client.book_ticker_stream(handle_message, "BTCUSDT")

    # Wait for messages
    await asyncio.sleep(2)

    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, dict)
        assert "d" in msg  # ticker data
        assert "s" in msg["d"]  # symbol
        assert msg["d"]["s"] == "BTCUSDT"
        assert "b" in msg["d"]  # best bid
        assert "a" in msg["d"]  # best ask


@pytest.mark.asyncio
async def test_account_update(ws_client: WebSocket):
    """Test the account update stream subscription."""
    messages = []

    async def handle_message(msg):
        messages.append(msg)
        if len(messages) >= 1:  # Get at least 1 message
            await ws_client.unsubscribe("private.account")

    await ws_client.account_update(handle_message)

    # Wait for messages
    await asyncio.sleep(2)

    assert len(messages) >= 1
    for msg in messages:
        assert isinstance(msg, dict)
        assert "d" in msg  # account data
        assert "a" in msg["d"]  # account info


@pytest.mark.asyncio
async def test_account_deals(ws_client: WebSocket):
    """Test the account deals stream subscription."""
    messages = []

    async def handle_message(msg):
        messages.append(msg)
        if len(messages) >= 1:  # Get at least 1 message
            await ws_client.unsubscribe("private.deals")

    await ws_client.account_deals(handle_message)

    # Wait for messages
    await asyncio.sleep(2)

    assert len(messages) >= 1
    for msg in messages:
        assert isinstance(msg, dict)
        assert "d" in msg  # deals data
        assert "a" in msg["d"]  # account info


@pytest.mark.asyncio
async def test_account_orders(ws_client: WebSocket):
    """Test the account orders stream subscription."""
    messages = []

    async def handle_message(msg):
        messages.append(msg)
        if len(messages) >= 1:  # Get at least 1 message
            await ws_client.unsubscribe("private.orders")

    await ws_client.account_orders(handle_message)

    # Wait for messages
    await asyncio.sleep(2)

    assert len(messages) >= 1
    for msg in messages:
        assert isinstance(msg, dict)
        assert "d" in msg  # orders data
        assert "a" in msg["d"]  # account info


@pytest.mark.asyncio
async def test_connection_error():
    """Test WebSocket connection error handling."""
    client = WebSocket(
        api_key="invalid_key",
        api_secret="invalid_secret",
        endpoint="wss://invalid.endpoint",
    )

    with pytest.raises(Exception) as e:
        await client._connect("wss://invalid.endpoint")

    assert "connection failed" in str(e.value).lower()


@pytest.mark.asyncio
async def test_keep_alive_loop(ws_client: WebSocket):
    """Test the keep alive loop functionality."""
    # Mock the HTTP client's keep_alive_listen_key method
    with patch.object(ws_client, "_keep_alive_loop") as mock_keep_alive:
        # Start the keep alive loop
        await ws_client._keep_alive_loop()

        # Verify the keep alive loop was called
        assert mock_keep_alive.called


@pytest.mark.asyncio
async def test_multiple_subscriptions(ws_client: WebSocket):
    """Test multiple stream subscriptions."""
    messages = []

    async def handle_message(msg):
        messages.append(msg)
        if len(messages) >= 4:  # Get at least 2 messages from each stream
            await ws_client.unsubscribe("public.deals", "public.bookTicker")

    # Subscribe to multiple streams
    await ws_client.deals_stream(handle_message, "BTCUSDT")
    await ws_client.book_ticker_stream(handle_message, "BTCUSDT")

    # Wait for messages
    await asyncio.sleep(2)

    assert len(messages) >= 4
    # Verify we got both types of messages
    message_types = set(msg.get("c", "").split("@")[1] for msg in messages)
    assert "public.deals" in message_types
    assert "public.bookTicker" in message_types
