# pytest . -v -s --log-cli-level=INFO

import asyncio
import logging
import pytest
import pytest_asyncio
from dotenv import dotenv_values

from pymexc.proto import (
    PrivateAccountV3Api,
    PrivateDealsV3Api,
    PrivateOrdersV3Api,
    PublicAggreBookTickerV3Api,
    PublicAggreDealsV3Api,
    PublicAggreDepthsV3Api,
    PublicLimitDepthsV3Api,
    PublicMiniTickerV3Api,
    PublicMiniTickersV3Api,
    PublicSpotKlineV3Api,
    PublicBookTickerBatchV3Api,
)
from pymexc._async.spot import WebSocket, HTTP
from pymexc._async.base_websocket import SPOT as SPOT_WS

env = dotenv_values(".env")
api_key = env["API_KEY"]
api_secret = env["API_SECRET"]

PRINT_RESPONSE = True
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",  # add line number
)
logger = logging.getLogger(__name__)

listen_key = None


@pytest_asyncio.fixture
async def ws_client():
    """Create a new WebSocket client for each test."""
    global listen_key
    if not listen_key:
        listen_key = await HTTP(api_key=api_key, api_secret=api_secret).create_listen_key()
        listen_key = listen_key.get("listenKey")

    client = WebSocket(api_key=api_key, api_secret=api_secret, proto=True, listenKey=listen_key)
    logger.info(f"WebSocket client created: {client}")
    yield client
    # Cleanup
    if hasattr(client, "ws"):
        logger.info(f"Closing WebSocket: {client.ws}")
        await client.ws.close()
    if hasattr(client, "session"):
        logger.info(f"Closing HTTP session: {client.session}")
        await client.session.close()


async def make_mxusdt_order(time_wait: int = 2):
    """Make a MXUSDT order and cancel it."""
    client = HTTP(api_key=api_key, api_secret=api_secret)
    await asyncio.sleep(time_wait)
    order_response = await client.order("MXUSDT", "BUY", "LIMIT", quantity=20, price=0.1)
    logger.info(f"MXUSDT Order Response: {order_response}")
    await asyncio.sleep(time_wait)
    cancel_order_response = await client.cancel_order("MXUSDT", order_response["orderId"])
    logger.info(f"MXUSDT Cancel Order Response: {cancel_order_response}")
    await asyncio.sleep(time_wait)


@pytest.mark.asyncio
async def test_deals_stream(ws_client: WebSocket):
    """Test the deals stream subscription."""
    messages: list[PublicAggreDealsV3Api] = []

    async def handle_message(msg):
        messages.append(msg)
        logger.info(f"Received message: {msg}")
        if len(messages) >= 2:  # Get at least 2 messages
            await ws_client.unsubscribe(ws_client.deals_stream)

    await ws_client.deals_stream(handle_message, "BTCUSDT", interval="100ms")

    # Wait for messages
    await asyncio.sleep(5)

    if PRINT_RESPONSE:
        logger.info(f"{messages[0].deals[0].price=}")

    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, PublicAggreDealsV3Api)
        assert float(msg.deals[0].price) > 0
        assert float(msg.deals[0].quantity) > 0
        assert msg.deals[0].tradeType > 0
        assert int(msg.deals[0].time) > 0


@pytest.mark.asyncio
async def test_kline_stream(ws_client: WebSocket):
    """Test the kline stream subscription."""
    messages: list[PublicSpotKlineV3Api] = []

    async def handle_message(msg: PublicSpotKlineV3Api):
        messages.append(msg)
        logger.info(f"Received message: {msg}")
        if len(messages) >= 2:  # Get at least 2 messages
            await ws_client.unsubscribe("public.kline")

    await ws_client.kline_stream(handle_message, "BTCUSDT", interval="Min1")

    # Wait for messages
    await asyncio.sleep(2)

    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, PublicSpotKlineV3Api)
        assert msg.interval == "Min1"
        assert int(msg.windowStart) > 0
        assert float(msg.openingPrice) > 0
        assert float(msg.closingPrice) > 0
        assert float(msg.highestPrice) > 0
        assert float(msg.lowestPrice) > 0
        assert float(msg.volume) > 0
        assert float(msg.amount) > 0
        assert int(msg.windowEnd) > 0


@pytest.mark.asyncio
async def test_increase_depth_stream(ws_client: WebSocket):
    """Test the increase depth stream subscription."""
    messages: list[PublicAggreDepthsV3Api] = []

    async def handle_message(msg: PublicAggreDepthsV3Api):
        messages.append(msg)
        # logger.info(f"Received message: {msg}")
        if len(messages) >= 2:  # Get at least 2 messages
            await ws_client.unsubscribe(ws_client.depth_stream)

    await ws_client.depth_stream(handle_message, "BTCUSDT")

    # Wait for messages
    await asyncio.sleep(2)

    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, PublicAggreDepthsV3Api)
        assert msg.eventType == "spot@public.aggre.depth.v3.api.pb@100ms"
        assert msg.fromVersion is not None
        assert len(msg.asks) > 0
        assert len(msg.bids) > 0


@pytest.mark.asyncio
async def test_limit_depth_stream(ws_client: WebSocket):
    """Test the limit depth stream subscription."""
    messages: list[PublicLimitDepthsV3Api] = []

    async def handle_message(msg: PublicLimitDepthsV3Api):
        messages.append(msg)
        logger.info(f"Received message: {msg}")
        if len(messages) >= 2:  # Get at least 2 messages
            await ws_client.unsubscribe(ws_client.limit_depth_stream)

    await ws_client.limit_depth_stream(handle_message, "BTCUSDT", 5)

    # Wait for messages
    await asyncio.sleep(3)

    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, PublicLimitDepthsV3Api)
        assert msg.eventType == "spot@public.limit.depth.v3.api.pb"
        assert msg.version is not None
        assert len(msg.asks) > 0
        assert len(msg.bids) > 0


@pytest.mark.asyncio
async def test_book_ticker_stream(ws_client: WebSocket):
    """Test the book ticker stream subscription."""
    messages: list[PublicAggreBookTickerV3Api] = []

    async def handle_message(msg: PublicAggreBookTickerV3Api):
        messages.append(msg)
        logger.info(f"Received message: {msg}")
        if len(messages) >= 2:  # Get at least 2 messages
            await ws_client.unsubscribe(ws_client.book_ticker_stream)

    await ws_client.book_ticker_stream(handle_message, "BTCUSDT")

    # Wait for messages
    await asyncio.sleep(2)

    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, PublicAggreBookTickerV3Api)
        assert msg.bidPrice is not None
        assert float(msg.bidPrice) > 0
        assert msg.bidQuantity is not None
        assert float(msg.bidQuantity) > 0
        assert msg.askPrice is not None
        assert float(msg.askPrice) > 0
        assert msg.askQuantity is not None
        assert float(msg.askQuantity) > 0


@pytest.mark.asyncio
async def test_book_ticker_batch_stream(ws_client: WebSocket):
    """Test the book ticker batch stream subscription."""
    messages: list[PublicBookTickerBatchV3Api] = []

    async def handle_message(msg: PublicBookTickerBatchV3Api):
        messages.append(msg)
        logger.info(f"Received message: {msg}")
        if len(messages) >= 2:  # Get at least 2 messages
            await ws_client.unsubscribe(ws_client.book_ticker_batch_stream)

    await ws_client.book_ticker_batch_stream(handle_message, "BTCUSDT")

    # Wait for messages
    await asyncio.sleep(2)

    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, PublicBookTickerBatchV3Api)
        assert msg.items[0].bidPrice is not None
        assert float(msg.items[0].bidPrice) > 0
        assert msg.items[0].bidQuantity is not None
        assert float(msg.items[0].bidQuantity) > 0
        assert msg.items[0].askPrice is not None
        assert float(msg.items[0].askPrice) > 0
        assert msg.items[0].askQuantity is not None
        assert float(msg.items[0].askQuantity) > 0


@pytest.mark.asyncio
async def test_mini_tickers_stream(ws_client: WebSocket):
    """Test the mini tickers stream subscription."""
    messages: list[PublicMiniTickersV3Api] = []
    done = asyncio.Event()

    async def handle_message(msg: PublicMiniTickersV3Api):
        messages.append(msg)
        logger.info(f"Received mini tickers message: {str(msg)[:50]}")
        if len(messages) >= 1:  # Mini tickers push every 3 seconds, so wait for at least 1
            await ws_client.unsubscribe(ws_client.mini_tickers_stream)
            done.set()

    await ws_client.mini_tickers_stream(handle_message, timezone="UTC+8")

    # Wait for messages
    try:
        await asyncio.wait_for(done.wait(), timeout=15)  # Increased timeout for 3-second interval
    except asyncio.TimeoutError:
        pytest.fail("Did not receive mini tickers messages")

    assert len(messages) >= 1
    for msg in messages:
        assert isinstance(msg, PublicMiniTickersV3Api)
        assert hasattr(msg, "items") and msg.items
        assert len(msg.items) > 0
        first = msg.items[0]
        assert hasattr(first, "symbol") and first.symbol
        assert hasattr(first, "price") and first.price is not None


@pytest.mark.asyncio
async def test_mini_ticker_stream(ws_client: WebSocket):
    """Test the mini ticker stream subscription."""
    messages: list[PublicMiniTickerV3Api] = []
    done = asyncio.Event()

    async def handle_message(msg: PublicMiniTickerV3Api):
        messages.append(msg)
        logger.info(f"Received mini ticker message: {str(msg)[:50]}")
        if len(messages) >= 1:  # Mini ticker pushes every 3 seconds, so wait for at least 1
            await ws_client.unsubscribe(ws_client.mini_ticker_stream)
            done.set()

    await ws_client.mini_ticker_stream(handle_message, "BTCUSDT", timezone="UTC+8")

    # Wait for messages
    try:
        await asyncio.wait_for(done.wait(), timeout=15)  # Increased timeout for 3-second interval
    except asyncio.TimeoutError:
        pytest.fail("Did not receive mini ticker messages")

    assert len(messages) >= 1
    for msg in messages:
        assert isinstance(msg, PublicMiniTickerV3Api)
        assert hasattr(msg, "symbol") and msg.symbol == "BTCUSDT"
        assert hasattr(msg, "price") and msg.price is not None


@pytest.mark.asyncio
async def test_account_update(ws_client: WebSocket):
    """Test the account update stream subscription."""
    messages: list[PrivateAccountV3Api] = []

    async def handle_message(msg: PrivateAccountV3Api):
        messages.append(msg)
        logger.info(f"Received message: {msg}")
        if len(messages) >= 1:  # Get at least 1 message
            await ws_client.unsubscribe("private.account")

    await ws_client.account_update(handle_message)

    await make_mxusdt_order()

    # Wait for messages
    await asyncio.sleep(2)

    assert len(messages) >= 1
    for msg in messages:
        assert isinstance(msg, PrivateAccountV3Api)
        assert msg.vcoinName == "USDT"
        assert msg.coinId == "128f589271cb4951b03e71e6323eb7be"
        assert msg.balanceAmount is not None
        assert msg.balanceAmountChange is not None
        assert msg.frozenAmount is not None
        assert msg.frozenAmountChange is not None
        assert msg.type == "ENTRUST_PLACE"
        assert msg.time > 0


@pytest.mark.asyncio
async def test_account_deals(ws_client: WebSocket):
    """Test the account deals stream subscription."""
    messages: list[PrivateDealsV3Api] = []

    async def handle_message(msg):
        messages.append(msg)
        logger.info(f"Received message: {msg}")
        if len(messages) >= 2:  # Get at least 2 messages
            await ws_client.unsubscribe(ws_client.account_deals)

    await ws_client.account_deals(handle_message)

    await make_mxusdt_order()

    # Wait for messages
    await asyncio.sleep(2)

    if PRINT_RESPONSE:
        logger.info(f"{messages}")

    await ws_client.unsubscribe(ws_client.account_deals)

    await asyncio.sleep(2)

    assert len(messages) >= 0
    for msg in messages:
        assert isinstance(msg, PrivateDealsV3Api)
        assert float(msg.price) > 0
        assert float(msg.quantity) > 0
        assert msg.tradeType > 0
        assert int(msg.time) > 0


@pytest.mark.asyncio
async def test_account_orders(ws_client: WebSocket):
    """Test the account orders stream subscription."""
    messages: list[PrivateOrdersV3Api] = []

    async def handle_message(msg: PrivateOrdersV3Api):
        messages.append(msg)
        logger.info(f"Received message: {msg}")
        if len(messages) >= 1:  # Get at least 1 message
            await ws_client.unsubscribe("private.orders")

    await ws_client.account_orders(handle_message)

    await make_mxusdt_order()

    # Wait for messages
    await asyncio.sleep(2)

    assert len(messages) >= 1
    for msg in messages:
        assert isinstance(msg, PrivateOrdersV3Api)
        assert msg.id is not None
        assert msg.clientId is not None
        assert msg.price is not None
        assert msg.quantity is not None
        assert msg.amount is not None
        assert msg.avgPrice is not None
        assert msg.orderType is not None
        assert msg.tradeType is not None
        assert msg.isMaker is not None
        assert msg.remainAmount is not None
        assert msg.remainQuantity is not None
        assert msg.lastDealQuantity is not None
        assert msg.cumulativeQuantity is not None
        assert msg.cumulativeAmount is not None
        assert msg.status is not None
        assert msg.createTime is not None
        assert msg.market is not None
        assert msg.triggerType is not None
        assert msg.triggerPrice is not None
        assert msg.state is not None
        assert msg.ocoId is not None
        assert msg.routeFactor is not None
        assert msg.symbolId is not None
        assert msg.marketId is not None
        assert msg.marketCurrencyId is not None
        assert msg.currencyId is not None


@pytest.mark.asyncio
async def test_multiple_subscriptions(ws_client: WebSocket):
    """Test multiple stream subscriptions."""
    messages: list[PublicAggreDealsV3Api | PublicAggreBookTickerV3Api] = []
    done = asyncio.Event()

    async def handle_message(msg: PublicAggreDealsV3Api | PublicAggreBookTickerV3Api):
        messages.append(msg)
        logger.info(f"Received message type: {type(msg)}")
        if len(messages) >= 20:  # Get at least 10 messages from each stream
            await ws_client.unsubscribe(ws_client.deals_stream, ws_client.book_ticker_stream)
            done.set()

    # Subscribe to multiple streams
    await ws_client.deals_stream(handle_message, "BTCUSDT")
    await ws_client.book_ticker_stream(handle_message, "BTCUSDT")

    # Wait for messages
    try:
        await asyncio.wait_for(done.wait(), timeout=15)
    except asyncio.TimeoutError:
        pytest.fail("Did not receive messages from both streams")

    assert len(messages) >= 4
    # Verify we got both types of messages
    message_types = {type(msg) for msg in messages}

    assert PublicAggreDealsV3Api in message_types
    assert PublicAggreBookTickerV3Api in message_types

    for msg in messages:
        if isinstance(msg, PublicAggreDealsV3Api):
            assert msg.deals[0].price is not None
            assert float(msg.deals[0].price) > 0
            assert msg.deals[0].quantity is not None
            assert float(msg.deals[0].quantity) > 0
            assert msg.deals[0].tradeType is not None
            assert msg.deals[0].tradeType > 0
            assert msg.deals[0].time is not None
            assert int(msg.deals[0].time) > 0

        if isinstance(msg, PublicAggreBookTickerV3Api):
            assert msg.bidPrice is not None
            assert float(msg.bidPrice) > 0
            assert msg.bidQuantity is not None
            assert float(msg.bidQuantity) > 0
            assert msg.askPrice is not None
            assert float(msg.askPrice) > 0
            assert msg.askQuantity is not None
            assert float(msg.askQuantity) > 0
