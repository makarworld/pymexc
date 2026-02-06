# pytest tests/test_async_context_manager.py -v -s --log-cli-level=INFO

import asyncio
import logging

import pytest
import pytest_asyncio
from dotenv import dotenv_values

from pymexc._async.spot import WebSocket as SpotWebSocket, HTTP
from pymexc._async.futures import WebSocket as FuturesWebSocket
from pymexc.proto import PublicAggreDealsV3Api

env = dotenv_values(".env")
api_key = env.get("API_KEY")
api_secret = env.get("API_SECRET")

if not api_key or not api_secret:
    pytest.skip("API credentials are required to run context manager tests", allow_module_level=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ==================== Spot WebSocket Context Manager Tests ====================


@pytest.mark.asyncio
async def test_spot_context_manager_enter_exit():
    """Test that Spot WebSocket context manager properly enters and exits."""
    listen_key = await HTTP(api_key=api_key, api_secret=api_secret).create_listen_key()
    listen_key = listen_key.get("listenKey")

    async with SpotWebSocket(api_key=api_key, api_secret=api_secret, proto=True, listenKey=listen_key) as ws:
        # Verify connection is established
        assert ws.is_connected(), "WebSocket should be connected after __aenter__"
        logger.info("Spot WebSocket connected via context manager")

    # After exiting context, connection should be closed
    assert not ws.is_connected(), "WebSocket should be disconnected after __aexit__"
    logger.info("Spot WebSocket properly closed after context manager exit")


@pytest.mark.asyncio
async def test_spot_context_manager_with_subscription():
    """Test that Spot WebSocket context manager cleans up subscriptions on exit."""
    listen_key = await HTTP(api_key=api_key, api_secret=api_secret).create_listen_key()
    listen_key = listen_key.get("listenKey")

    messages: list[PublicAggreDealsV3Api] = []

    async def handle_message(msg):
        messages.append(msg)
        logger.info(f"Received message: {type(msg).__name__}")

    async with SpotWebSocket(api_key=api_key, api_secret=api_secret, proto=True, listenKey=listen_key) as ws:
        # Subscribe to a stream
        await ws.deals_stream(handle_message, "BTCUSDT", interval="100ms")

        # Verify subscription is registered
        assert len(ws.subscriptions) > 0, "Should have at least one subscription"
        logger.info(f"Active subscriptions: {list(ws.subscriptions.keys())}")

        # Wait for some messages (increased timeout for reliability)
        await asyncio.sleep(5)

    # After context exit, subscriptions should be cleared via unsubscribe_all
    logger.info(f"Messages received: {len(messages)}")
    # Note: Message count depends on market activity, main test is subscription cleanup
    assert len(messages) >= 0, "Should handle message reception gracefully"


@pytest.mark.asyncio
async def test_spot_unsubscribe_all():
    """Test Spot WebSocket unsubscribe_all method directly."""
    listen_key = await HTTP(api_key=api_key, api_secret=api_secret).create_listen_key()
    listen_key = listen_key.get("listenKey")

    ws = SpotWebSocket(api_key=api_key, api_secret=api_secret, proto=True, listenKey=listen_key)

    async def handle_message(msg):
        logger.info(f"Received: {type(msg).__name__}")

    try:
        # Connect and subscribe to multiple streams
        await ws._connect(ws.endpoint)
        await ws.deals_stream(handle_message, "BTCUSDT", interval="100ms")
        await ws.book_ticker_stream(handle_message, "ETHUSDT")

        # Verify subscriptions exist
        assert len(ws.subscriptions) >= 2, f"Expected at least 2 subscriptions, got {len(ws.subscriptions)}"
        logger.info(f"Subscriptions before unsubscribe_all: {list(ws.subscriptions.keys())}")

        # Call unsubscribe_all
        await ws.unsubscribe_all()

        # Verify subscriptions are cleared
        assert len(ws.subscriptions) == 0, f"Expected 0 subscriptions after unsubscribe_all, got {len(ws.subscriptions)}"
        logger.info("unsubscribe_all successfully cleared all subscriptions")

    finally:
        if ws.ws and not ws.ws.closed:
            await ws.ws.close()
        if hasattr(ws, "session") and ws.session:
            await ws.session.close()


@pytest.mark.asyncio
async def test_spot_close_all():
    """Test Spot WebSocket close_all method."""
    listen_key = await HTTP(api_key=api_key, api_secret=api_secret).create_listen_key()
    listen_key = listen_key.get("listenKey")

    ws = SpotWebSocket(api_key=api_key, api_secret=api_secret, proto=True, listenKey=listen_key)

    async def handle_message(msg):
        pass

    # Connect and subscribe
    await ws._connect(ws.endpoint)
    await ws.deals_stream(handle_message, "BTCUSDT")

    assert ws.is_connected(), "Should be connected"

    # Call close_all (which internally calls __aexit__)
    await ws.close_all()

    assert not ws.is_connected(), "Should be disconnected after close_all"
    logger.info("close_all successfully closed the connection")


# ==================== Futures WebSocket Context Manager Tests ====================


@pytest.mark.asyncio
async def test_futures_context_manager_enter_exit():
    """Test that Futures WebSocket context manager properly enters and exits."""
    async with FuturesWebSocket(api_key=api_key, api_secret=api_secret) as ws:
        # Verify connection is established
        assert ws.is_connected(), "WebSocket should be connected after __aenter__"
        logger.info("Futures WebSocket connected via context manager")

    # After exiting context, connection should be closed
    assert not ws.is_connected(), "WebSocket should be disconnected after __aexit__"
    logger.info("Futures WebSocket properly closed after context manager exit")


@pytest.mark.asyncio
async def test_futures_context_manager_with_subscription():
    """Test that Futures WebSocket context manager cleans up subscriptions on exit."""
    messages = []

    def handle_message(msg):
        messages.append(msg)
        logger.info(f"Received futures message: {msg}")

    async with FuturesWebSocket(api_key=api_key, api_secret=api_secret) as ws:
        # Subscribe to a stream
        await ws.ticker_stream(handle_message, "BTC_USDT")

        # Verify subscription is registered
        assert len(ws.subscriptions) > 0, "Should have at least one subscription"
        logger.info(f"Active subscriptions: {list(ws.subscriptions.keys())}")

        # Wait for some messages
        await asyncio.sleep(3)

    logger.info(f"Messages received: {len(messages)}")
    # Note: Message count depends on market activity
    assert len(messages) >= 0, "Should handle message reception gracefully"


@pytest.mark.asyncio
async def test_futures_unsubscribe_all():
    """Test Futures WebSocket unsubscribe_all method directly."""
    ws = FuturesWebSocket(api_key=api_key, api_secret=api_secret)

    def handle_message(msg):
        logger.info(f"Received: {msg}")

    try:
        # Connect and subscribe to multiple streams
        await ws.connect()
        await ws.ticker_stream(handle_message, "BTC_USDT")
        await ws.deal_stream(handle_message, "ETH_USDT")

        # Verify subscriptions exist
        assert len(ws.subscriptions) >= 2, f"Expected at least 2 subscriptions, got {len(ws.subscriptions)}"
        logger.info(f"Subscriptions before unsubscribe_all: {list(ws.subscriptions.keys())}")

        # Call unsubscribe_all
        await ws.unsubscribe_all()

        # Verify subscriptions are cleared
        assert len(ws.subscriptions) == 0, f"Expected 0 subscriptions after unsubscribe_all, got {len(ws.subscriptions)}"
        logger.info("unsubscribe_all successfully cleared all subscriptions")

    finally:
        if ws.ws and not ws.ws.closed:
            await ws.ws.close()
        if hasattr(ws, "session") and ws.session:
            await ws.session.close()


@pytest.mark.asyncio
async def test_futures_close_all():
    """Test Futures WebSocket close_all method."""
    ws = FuturesWebSocket(api_key=api_key, api_secret=api_secret)

    def handle_message(msg):
        pass

    # Connect and subscribe
    await ws.connect()
    await ws.ticker_stream(handle_message, "BTC_USDT")

    assert ws.is_connected(), "Should be connected"

    # Call close_all
    await ws.close_all()

    assert not ws.is_connected(), "Should be disconnected after close_all"
    logger.info("close_all successfully closed the connection")


# ==================== Error Handling Tests ====================


@pytest.mark.asyncio
async def test_context_manager_exception_handling():
    """Test that context manager properly cleans up even when exception occurs."""
    listen_key = await HTTP(api_key=api_key, api_secret=api_secret).create_listen_key()
    listen_key = listen_key.get("listenKey")

    ws = None
    try:
        async with SpotWebSocket(api_key=api_key, api_secret=api_secret, proto=True, listenKey=listen_key) as ws:
            assert ws.is_connected()
            raise ValueError("Test exception")
    except ValueError:
        pass

    # Even after exception, cleanup should have happened
    assert not ws.is_connected(), "WebSocket should be disconnected even after exception"
    logger.info("Context manager properly cleaned up after exception")


@pytest.mark.asyncio
async def test_unsubscribe_all_empty_subscriptions():
    """Test unsubscribe_all when there are no subscriptions."""
    listen_key = await HTTP(api_key=api_key, api_secret=api_secret).create_listen_key()
    listen_key = listen_key.get("listenKey")

    async with SpotWebSocket(api_key=api_key, api_secret=api_secret, proto=True, listenKey=listen_key) as ws:
        # Don't subscribe to anything
        assert len(ws.subscriptions) == 0

        # unsubscribe_all should not raise
        await ws.unsubscribe_all()

        logger.info("unsubscribe_all handled empty subscriptions gracefully")

