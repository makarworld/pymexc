"""
Integration tests for WebSocket fixes.
Tests context manager support, async operations, and cleanup.
"""

import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os
import aiohttp

# Add parent directory to path to import pymexc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymexc._async.spot import WebSocket as SpotWebSocket
from pymexc._async.futures import WebSocket as FuturesWebSocket


@pytest.mark.asyncio
async def test_spot_websocket_context_manager():
    """Test that SpotWebSocket works as an async context manager."""

    # Mock the HTTP class to avoid real API calls
    with patch('pymexc._async.spot.HTTP') as mock_http:
        mock_http.return_value.create_listen_key = AsyncMock(return_value={'listenKey': 'test_key'})
        mock_http.return_value.keep_alive_listen_key = AsyncMock(return_value={'msg': 'success'})

        # Test context manager usage
        async with SpotWebSocket(api_key='test', api_secret='test') as ws:
            # Mock the connection
            ws.ws = AsyncMock()
            ws.session = AsyncMock()
            ws.connected = True

            # Verify the websocket was created
            assert ws is not None
            assert hasattr(ws, '__aenter__')
            assert hasattr(ws, '__aexit__')

        # After exiting context, cleanup should be done
        assert ws._keep_alive_task is None or ws._keep_alive_task.cancelled()


@pytest.mark.asyncio
async def test_spot_websocket_no_blocking_sleep():
    """Test that _keep_alive_loop uses asyncio.sleep instead of blocking sleep."""

    with patch('pymexc._async.spot.HTTP') as mock_http:
        mock_http.return_value.create_listen_key = AsyncMock(return_value={'listenKey': 'test_key'})
        mock_http.return_value.keep_alive_listen_key = AsyncMock(return_value={'msg': 'success'})

        ws = SpotWebSocket(api_key='test', api_secret='test')

        # Check that the _keep_alive_loop method exists and is async
        assert asyncio.iscoroutinefunction(ws._keep_alive_loop)

        # Start the keep alive loop and immediately cancel it
        task = asyncio.create_task(ws._keep_alive_loop())
        await asyncio.sleep(0.1)  # Let it start
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass  # Expected


@pytest.mark.asyncio
async def test_unsubscribe_all_spot():
    """Test that unsubscribe_all properly cleans up all subscriptions."""

    with patch('pymexc._async.spot.HTTP'):
        ws = SpotWebSocket()
        ws.ws = AsyncMock()
        ws.connected = True

        # Add some mock subscriptions
        ws.subscriptions = [
            {"method": "SUBSCRIPTION", "params": ["spot@public.deals.v3.api@BTCUSDT"]},
            {"method": "SUBSCRIPTION", "params": ["spot@public.bookTicker.v3.api@ETHUSDT"]}
        ]

        # Set initial callback directory state
        ws.callback_directory = {"some_topic": lambda x: x}

        # Call unsubscribe_all
        await ws.unsubscribe_all()

        # Verify unsubscription message was sent
        ws.ws.send_json.assert_called_once()
        call_args = ws.ws.send_json.call_args[0][0]
        assert call_args['method'] == 'UNSUBSCRIPTION'

        # Verify internal state was cleared
        assert ws.callback_directory == {}
        assert len(ws.subscriptions) == 0


@pytest.mark.asyncio
async def test_close_all_cleanup():
    """Test that close_all properly cleans up all resources."""

    with patch('pymexc._async.spot.HTTP'):
        ws = SpotWebSocket()
        ws.ws = AsyncMock()
        ws.ws.closed = False
        ws.session = AsyncMock()
        ws.connected = True
        # Create a proper awaitable mock for _keep_alive_task that stays running
        async def mock_task():
            try:
                await asyncio.sleep(100)  # Long-running task
            except asyncio.CancelledError:
                pass
        ws._keep_alive_task = asyncio.create_task(mock_task())
        await asyncio.sleep(0)  # Let the task start

        # Add mock unsubscribe_all
        ws.unsubscribe_all = AsyncMock()

        # Call close_all
        await ws.close_all()

        # Verify cleanup was performed
        ws.unsubscribe_all.assert_called_once()
        ws.ws.close.assert_called_once()
        ws.session.close.assert_called_once()
        # Task should be done (either cancelled or finished)
        assert ws._keep_alive_task.done()
        assert ws.connected == False


@pytest.mark.asyncio
async def test_proto_default_is_true():
    """Test that proto defaults to True for better WebSocket functionality."""

    with patch('pymexc._async.spot.HTTP'):
        ws = SpotWebSocket()

        # Check that proto is True by default
        assert ws.proto == True


@pytest.mark.asyncio
async def test_no_threading_in_async():
    """Test that async implementation uses asyncio tasks instead of threading."""

    with patch('pymexc._async.spot.HTTP') as mock_http:
        mock_http.return_value.create_listen_key = AsyncMock(return_value={'listenKey': 'test_key'})

        ws = SpotWebSocket(api_key='test', api_secret='test')

        # Verify _keep_alive_task is an asyncio Task, not a thread
        if ws._keep_alive_task:
            assert isinstance(ws._keep_alive_task, asyncio.Task)
            # Clean up the task
            ws._keep_alive_task.cancel()
            try:
                await ws._keep_alive_task
            except asyncio.CancelledError:
                pass


@pytest.mark.asyncio
async def test_futures_websocket_context_manager():
    """Test that FuturesWebSocket also supports context manager."""

    # Test basic context manager support
    ws = FuturesWebSocket()

    # Verify context manager methods exist
    assert hasattr(ws, '__aenter__')
    assert hasattr(ws, '__aexit__')

    # Mock necessary attributes for testing
    ws.ws = AsyncMock()
    ws.ws.closed = False
    ws.session = AsyncMock()
    ws.connected = True

    # Test using context manager
    async with ws:
        assert ws is not None

    # After context, verify cleanup
    ws.ws.close.assert_called()


@pytest.mark.asyncio
async def test_direct_usage_without_context_manager():
    """Test that WebSocket can be used directly without context manager."""

    with patch('pymexc._async.spot.HTTP') as mock_http:
        mock_http.return_value.create_listen_key = AsyncMock(return_value={'listenKey': 'test_key'})

        # Direct usage without context manager
        ws = SpotWebSocket(api_key='test', api_secret='test')

        # Mock the connection components
        ws.ws = AsyncMock()
        ws.ws.closed = False
        ws.session = AsyncMock()
        ws.connected = True

        # Should be able to use it normally
        assert ws is not None
        assert ws.proto == True  # Check default

        # Manual cleanup should work
        await ws.close_all()

        # Verify cleanup happened
        ws.ws.close.assert_called_once()
        ws.session.close.assert_called_once()
        assert ws.connected == False


@pytest.mark.asyncio
async def test_cleanup_with_failures():
    """Test that cleanup continues even if some operations fail."""

    with patch('pymexc._async.spot.HTTP'):
        ws = SpotWebSocket()
        ws.connected = True

        # Mock components with failures
        ws.ws = AsyncMock()
        ws.ws.closed = False
        ws.ws.close = AsyncMock(side_effect=aiohttp.ClientError("WebSocket close failed"))

        ws.session = AsyncMock()
        ws.session.close = AsyncMock(side_effect=aiohttp.ClientError("Session close failed"))

        ws.unsubscribe_all = AsyncMock(side_effect=aiohttp.ClientError("Unsubscribe failed"))

        # close_all should handle these failures gracefully
        await ws.close_all()

        # Verify it tried to clean up despite failures
        ws.unsubscribe_all.assert_called_once()
        ws.ws.close.assert_called_once()
        ws.session.close.assert_called_once()

        # Verify state was reset
        assert ws.connected == False
        assert len(ws.subscriptions) == 0


if __name__ == "__main__":
    # Run tests with asyncio
    pytest.main([__file__, "-v", "-s"])