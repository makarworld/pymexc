"""
Verification script for miniTicker and miniTickers WebSocket streams (Sync version)
Tests that the new functions can receive real data from MEXC.
"""

import logging
from pymexc import spot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def handle_mini_ticker(message):
    """Handle individual miniTicker messages"""
    logger.info(f"[miniTicker] Received data for symbol")
    print(f"miniTicker: {message}")
    print("-" * 80)


def handle_mini_tickers(message):
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


def main():
    logger.info("Starting miniTicker/miniTickers verification (Sync)")

    # Initialize WebSocket client (no auth needed for public streams)
    ws_client = spot.WebSocket()

    logger.info("Subscribing to miniTicker stream for BTCUSDT (UTC+8)")
    ws_client.mini_ticker_stream(handle_mini_ticker, "BTCUSDT", timezone="UTC+8")

    logger.info("Subscribing to miniTickers stream for all pairs (UTC+8)")
    ws_client.mini_tickers_stream(handle_mini_tickers, timezone="UTC+8")

    logger.info("WebSocket connections established. Waiting for data...")
    logger.info("Press Ctrl+C to stop")

    # Keep connection alive
    try:
        while True:
            ...
    except KeyboardInterrupt:
        logger.info("Stopping...")


if __name__ == "__main__":
    main()
