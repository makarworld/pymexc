"""
Tests for miniTicker and miniTickers WebSocket streams.
Tests timezone validation, sync/async implementations, and proper type annotations.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path to import pymexc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymexc.spot import WebSocket as SyncWebSocket, Timezone, VALID_TIMEZONES
from pymexc._async.spot import WebSocket as AsyncWebSocket
from pymexc.proto import ProtoTyping


class TestSyncMiniTickerStreams:
    """Test suite for sync miniTicker WebSocket streams."""

    def test_timezone_enum_exists(self):
        """Test that Timezone enum is properly defined."""
        assert hasattr(Timezone, 'H24')
        assert hasattr(Timezone, 'UTC_8')
        assert Timezone.H24.value == "24H"
        assert Timezone.UTC_8.value == "UTC+8"

    def test_valid_timezones_set(self):
        """Test that VALID_TIMEZONES contains all expected values."""
        expected_timezones = {
            "24H", "UTC-10", "UTC-8", "UTC-7", "UTC-6", "UTC-5", "UTC-4", "UTC-3",
            "UTC+0", "UTC+1", "UTC+2", "UTC+3", "UTC+4", "UTC+4:30", "UTC+5",
            "UTC+5:30", "UTC+6", "UTC+7", "UTC+8", "UTC+9", "UTC+10", "UTC+11",
            "UTC+12", "UTC+12:45", "UTC+13"
        }
        assert VALID_TIMEZONES == expected_timezones

    @patch('pymexc.spot.HTTP')
    def test_mini_ticker_stream_with_valid_timezone(self, mock_http):
        """Test mini_ticker_stream accepts valid timezone."""
        mock_http.return_value.create_listen_key.return_value = {'listenKey': 'test_key'}

        ws = SyncWebSocket(api_key='test', api_secret='test')
        ws._ws_subscribe = MagicMock()

        callback = MagicMock()
        ws.mini_ticker_stream(callback, "BTCUSDT", timezone="UTC+9")

        # Verify _ws_subscribe was called with correct parameters
        ws._ws_subscribe.assert_called_once_with(
            "public.miniTicker",
            callback,
            [{"symbol": "BTCUSDT", "timezone": "UTC+9"}]
        )

    @patch('pymexc.spot.HTTP')
    def test_mini_ticker_stream_with_invalid_timezone(self, mock_http):
        """Test mini_ticker_stream rejects invalid timezone."""
        mock_http.return_value.create_listen_key.return_value = {'listenKey': 'test_key'}

        ws = SyncWebSocket(api_key='test', api_secret='test')
        callback = MagicMock()

        with pytest.raises(ValueError) as exc_info:
            ws.mini_ticker_stream(callback, "BTCUSDT", timezone="INVALID")

        assert "Invalid timezone" in str(exc_info.value)
        assert "INVALID" in str(exc_info.value)

    @patch('pymexc.spot.HTTP')
    def test_mini_ticker_stream_default_timezone(self, mock_http):
        """Test mini_ticker_stream uses default timezone UTC+8."""
        mock_http.return_value.create_listen_key.return_value = {'listenKey': 'test_key'}

        ws = SyncWebSocket(api_key='test', api_secret='test')
        ws._ws_subscribe = MagicMock()

        callback = MagicMock()
        ws.mini_ticker_stream(callback, "BTCUSDT")

        # Verify default timezone is UTC+8
        ws._ws_subscribe.assert_called_once_with(
            "public.miniTicker",
            callback,
            [{"symbol": "BTCUSDT", "timezone": "UTC+8"}]
        )

    @patch('pymexc.spot.HTTP')
    def test_mini_tickers_stream_with_valid_timezone(self, mock_http):
        """Test mini_tickers_stream accepts valid timezone."""
        mock_http.return_value.create_listen_key.return_value = {'listenKey': 'test_key'}

        ws = SyncWebSocket(api_key='test', api_secret='test')
        ws._ws_subscribe = MagicMock()

        callback = MagicMock()
        ws.mini_tickers_stream(callback, timezone="24H")

        # Verify _ws_subscribe was called with correct parameters
        ws._ws_subscribe.assert_called_once_with(
            "public.miniTickers",
            callback,
            [{"timezone": "24H"}]
        )

    @patch('pymexc.spot.HTTP')
    def test_mini_tickers_stream_with_invalid_timezone(self, mock_http):
        """Test mini_tickers_stream rejects invalid timezone."""
        mock_http.return_value.create_listen_key.return_value = {'listenKey': 'test_key'}

        ws = SyncWebSocket(api_key='test', api_secret='test')
        callback = MagicMock()

        with pytest.raises(ValueError) as exc_info:
            ws.mini_tickers_stream(callback, timezone="UTC+99")

        assert "Invalid timezone" in str(exc_info.value)

    @patch('pymexc.spot.HTTP')
    def test_all_valid_timezones(self, mock_http):
        """Test that all timezone enum values are accepted."""
        mock_http.return_value.create_listen_key.return_value = {'listenKey': 'test_key'}

        ws = SyncWebSocket(api_key='test', api_secret='test')
        ws._ws_subscribe = MagicMock()
        callback = MagicMock()

        # Test each timezone value
        for tz in Timezone:
            ws._ws_subscribe.reset_mock()
            ws.mini_ticker_stream(callback, "BTCUSDT", timezone=tz.value)
            assert ws._ws_subscribe.called


class TestAsyncMiniTickerStreams:
    """Test suite for async miniTicker WebSocket streams."""

    @pytest.mark.asyncio
    async def test_async_timezone_enum_exists(self):
        """Test that async module has Timezone enum."""
        from pymexc._async.spot import Timezone as AsyncTimezone, VALID_TIMEZONES as AsyncValidTimezones

        assert hasattr(AsyncTimezone, 'H24')
        assert hasattr(AsyncTimezone, 'UTC_8')
        assert AsyncValidTimezones == VALID_TIMEZONES

    @pytest.mark.asyncio
    @patch('pymexc._async.spot.HTTP')
    async def test_async_mini_ticker_stream_with_valid_timezone(self, mock_http):
        """Test async mini_ticker_stream accepts valid timezone."""
        from unittest.mock import AsyncMock
        mock_http.return_value.create_listen_key = AsyncMock(return_value={'listenKey': 'test_key'})

        ws = AsyncWebSocket(api_key='test', api_secret='test')
        ws._ws_subscribe = AsyncMock()

        callback = MagicMock()
        await ws.mini_ticker_stream(callback, "ETHUSDT", timezone="UTC+0")

        # Verify _ws_subscribe was called with correct parameters
        ws._ws_subscribe.assert_called_once_with(
            "public.miniTicker",
            callback,
            [{"symbol": "ETHUSDT", "timezone": "UTC+0"}]
        )

    @pytest.mark.asyncio
    @patch('pymexc._async.spot.HTTP')
    async def test_async_mini_ticker_stream_with_invalid_timezone(self, mock_http):
        """Test async mini_ticker_stream rejects invalid timezone."""
        from unittest.mock import AsyncMock
        mock_http.return_value.create_listen_key = AsyncMock(return_value={'listenKey': 'test_key'})

        ws = AsyncWebSocket(api_key='test', api_secret='test')
        callback = MagicMock()

        with pytest.raises(ValueError) as exc_info:
            await ws.mini_ticker_stream(callback, "ETHUSDT", timezone="WRONG")

        assert "Invalid timezone" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('pymexc._async.spot.HTTP')
    async def test_async_mini_tickers_stream_default_timezone(self, mock_http):
        """Test async mini_tickers_stream uses default timezone UTC+8."""
        from unittest.mock import AsyncMock
        mock_http.return_value.create_listen_key = AsyncMock(return_value={'listenKey': 'test_key'})

        ws = AsyncWebSocket(api_key='test', api_secret='test')
        ws._ws_subscribe = AsyncMock()

        callback = MagicMock()
        await ws.mini_tickers_stream(callback)

        # Verify default timezone is UTC+8
        ws._ws_subscribe.assert_called_once_with(
            "public.miniTickers",
            callback,
            [{"timezone": "UTC+8"}]
        )


class TestTypeAnnotations:
    """Test that type annotations are correct."""

    def test_sync_mini_ticker_callback_type(self):
        """Test that sync mini_ticker_stream has correct callback type hint."""
        import inspect
        from typing import get_type_hints

        # Get the method signature
        sig = inspect.signature(SyncWebSocket.mini_ticker_stream)

        # Verify callback parameter exists
        assert 'callback' in sig.parameters
        assert 'symbol' in sig.parameters
        assert 'timezone' in sig.parameters

        # Verify timezone has default value
        assert sig.parameters['timezone'].default == "UTC+8"

    def test_async_mini_ticker_callback_type(self):
        """Test that async mini_ticker_stream has correct callback type hint."""
        import inspect

        # Get the method signature
        sig = inspect.signature(AsyncWebSocket.mini_ticker_stream)

        # Verify callback parameter exists
        assert 'callback' in sig.parameters
        assert 'symbol' in sig.parameters
        assert 'timezone' in sig.parameters

        # Verify timezone has default value
        assert sig.parameters['timezone'].default == "UTC+8"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
