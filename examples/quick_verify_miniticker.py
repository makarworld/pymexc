"""
Quick verification script for miniTicker WebSocket stream
Connects, receives a few messages, then exits.
"""

import logging
import time
import threading
from pymexc import spot
from pymexc.proto import ProtoTyping

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Counter for received messages
message_count = 0
max_messages = 2

# Event to signal when to stop
stop_event = threading.Event()


def handle_mini_ticker(message: ProtoTyping.PublicMiniTickerV3Api):
    """Handle miniTicker messages"""
    global message_count
    message_count += 1

    logger.info(f"✅ [{message_count}/{max_messages}] miniTicker received!")

    # Print message details
    try:
        if hasattr(message, 'symbol'):
            print(f"  Symbol: {message.symbol}")
            print(f"  Price: {message.price}")
            print(f"  24h High: {message.high}")
            print(f"  24h Low: {message.low}")
            print(f"  Volume: {message.volume}")
            print(f"  Rate: {message.rate}")
        else:
            print(f"  Message type: {type(message)}")
            print(f"  Raw data: {message}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        print(f"  Raw message: {message}")

    # Stop after receiving max_messages
    if message_count >= max_messages:
        logger.info("✅ Received target number of messages. Test PASSED!")
        stop_event.set()


def main():
    logger.info("=" * 60)
    logger.info("miniTicker Quick Verification Test")
    logger.info("=" * 60)
    logger.info(f"Testing: miniTicker stream for BTCUSDT")
    logger.info(f"Timezone: UTC+8")
    logger.info(f"Target messages: {max_messages}")
    logger.info(f"Note: miniTicker updates every 3 seconds")
    logger.info("")

    # Initialize WebSocket client with proto=True
    logger.info("Initializing WebSocket with proto=True...")
    ws_client = spot.WebSocket(proto=True)

    # Subscribe to miniTicker stream
    logger.info("Subscribing to miniTicker stream...")
    ws_client.mini_ticker_stream(handle_mini_ticker, "BTCUSDT", timezone="UTC+8")

    logger.info("Waiting for messages (timeout: 45 seconds)...")
    logger.info("(This may take a few seconds as updates are pushed every 3s)")
    logger.info("")

    # Wait for messages or timeout
    if stop_event.wait(timeout=45):
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ SUCCESS: miniTicker stream is working correctly!")
        logger.info(f"✅ Received {message_count} messages from MEXC")
        logger.info("=" * 60)
        return True
    else:
        logger.error("")
        logger.error("=" * 60)
        logger.error("❌ TIMEOUT: No messages received within 45 seconds")
        logger.error("This might indicate:")
        logger.error("  - Connection issue with MEXC")
        logger.error("  - Symbol not available")
        logger.error("  - Network connectivity problem")
        logger.error("=" * 60)
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
