# pytest tests/test_spot_websocket_many_topics_async.py -v -s --log-cli-level=INFO

import asyncio
import logging

import pytest
import pytest_asyncio
from dotenv import dotenv_values

from pymexc.proto import (
    PublicAggreDealsV3Api,
)
from pymexc.spot import AsyncWebSocket

env = dotenv_values(".env")
api_key = env.get("API_KEY")
api_secret = env.get("API_SECRET")

if not api_key or not api_secret:
    pytest.skip("API credentials are required to run WebSocket tests", allow_module_level=True)

PRINT_RESPONSE = True
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def ws_client():
    client = AsyncWebSocket(api_key=api_key, api_secret=api_secret, proto=True)
    logger.info("WebSocket client created: %s", client)
    yield client
    try:
        await client.close()
    except Exception as exc:
        logger.warning("Failed to close WebSocket client: %s", exc)
    await asyncio.sleep(1)


@pytest.mark.asyncio
async def test_deals_stream(ws_client: AsyncWebSocket):
    messages_1: list[PublicAggreDealsV3Api] = []
    messages_2: list[PublicAggreDealsV3Api] = []
    topics: list[str] = []

    async def handle_message_1(msg: PublicAggreDealsV3Api):
        logger.info(f"[1] Received deals message: {str(msg)[:30]}")
        messages_1.append(msg)
        if len(messages_1) >= 6:
            logger.info(f"[1] Unsubscribing from deals stream")
            await ws_client.unsubscribe(topics[0])

    async def handle_message_2(msg: PublicAggreDealsV3Api):
        logger.info(f"[2] Received deals message: {str(msg)[:30]}")
        messages_2.append(msg)
        if len(messages_2) >= 12:
            logger.info(f"[2] Unsubscribing from deals stream")
            await ws_client.unsubscribe(topics[1])

    auth1 = await ws_client.deals_stream(handle_message_1, "BTCUSDT", interval="100ms")
    topics.append(auth1)

    await asyncio.sleep(2)

    auth2 = await ws_client.deals_stream(handle_message_2, "MXUSDT", interval="100ms")
    topics.append(auth2)

    await asyncio.sleep(100)

    assert len(messages_1) >= 1


if __name__ == "__main__":

    async def main():
        client = AsyncWebSocket(api_key=api_key, api_secret=api_secret, proto=True)
        try:
            await test_deals_stream(client)
        finally:
            await client.close()

    asyncio.run(main())
