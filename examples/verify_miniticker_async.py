"""
Verification script for miniTicker and miniTickers WebSocket streams (Async version)
Tests that the new functions can receive real data from MEXC.
"""

import asyncio
import logging
from pymexc import spot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def handle_mini_ticker(message):
    """Handle individual miniTicker messages"""
    logger.info(f"[miniTicker] Received data for symbol")
    print(f"miniTicker: {message}")
    print("-" * 80)


async def handle_mini_tickers(message):
    """Handle batch miniTickers messages"""
    logger.info(f"[miniTickers] Received batch data")
    if hasattr(message, 'items'):
        print(f"miniTickers: Received {len(message.items)} tickers")
        # Print first ticker as sample
        if message.items:
            print(f"Sample ticker: {message.items[0]}")
    else:
        print(f"miniTickers: {message}")
    print("-" * 80)


async def main():
    logger.info("Starting miniTicker/miniTickers verification (Async)")

    # Initialize WebSocket client (no auth needed for public streams)
    ws_client = spot.AsyncWebSocket()

    logger.info("Subscribing to miniTicker stream for BTCUSDT (UTC+8)")
    await ws_client.mini_ticker_stream(handle_mini_ticker, "BTCUSDT", timezone="UTC+8")

    logger.info("Subscribing to miniTickers stream for all pairs (24H)")
    await ws_client.mini_tickers_stream(handle_mini_tickers, timezone="24H")

    logger.info("WebSocket connections established. Waiting for data...")
    logger.info("Press Ctrl+C to stop")

    # Keep connection alive
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        logger.info("Stopping...")
        await ws_client.close_all()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
