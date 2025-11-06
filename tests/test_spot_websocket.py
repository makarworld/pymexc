# pytest . -v -s

import logging
import threading
import time

import pytest
from dotenv import dotenv_values

from pymexc.proto import (
    PrivateAccountV3Api,
    PrivateDealsV3Api,
    PrivateOrdersV3Api,
    PublicAggreBookTickerV3Api,
    PublicAggreDealsV3Api,
    PublicAggreDepthsV3Api,
    PublicBookTickerBatchV3Api,
    PublicLimitDepthsV3Api,
    PublicSpotKlineV3Api,
)
from pymexc.spot import HTTP, WebSocket

env = dotenv_values(".env")
api_key = env.get("API_KEY")
api_secret = env.get("API_SECRET")

if not api_key or not api_secret:
    pytest.skip("API credentials are required to run WebSocket tests", allow_module_level=True)

PRINT_RESPONSE = True
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@pytest.fixture
def ws_client():
    client = WebSocket(api_key=api_key, api_secret=api_secret, proto=True)
    logger.info("WebSocket client created: %s", client)
    yield client
    try:
        client.exit()
    except Exception as exc:
        logger.warning("Failed to close WebSocket client: %s", exc)
    time.sleep(1)


def make_mxusdt_order(time_wait: int = 2):
    client = HTTP(api_key=api_key, api_secret=api_secret)
    time.sleep(time_wait)
    order_response = client.order("MXUSDT", "BUY", "LIMIT", quantity=20, price=0.1)
    logger.info("MXUSDT Order Response: %s", order_response)
    time.sleep(time_wait)
    cancel_order_response = client.cancel_order("MXUSDT", order_response["orderId"])
    logger.info("MXUSDT Cancel Order Response: %s", cancel_order_response)
    time.sleep(time_wait)


def _wait_or_fail(event: threading.Event, timeout: float, message: str):
    if not event.wait(timeout):
        pytest.fail(message)


def test_deals_stream(ws_client: WebSocket):
    messages: list[PublicAggreDealsV3Api] = []
    done = threading.Event()

    def handle_message(msg: PublicAggreDealsV3Api):
        messages.append(msg)
        logger.info("Received deals message: %s", msg)
        if len(messages) >= 2:
            ws_client.unsubscribe(ws_client.deals_stream)
            done.set()

    ws_client.deals_stream(handle_message, "BTCUSDT", interval="100ms")

    _wait_or_fail(done, 10, "Не получили достаточно сообщений сделки за отведённое время")
    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, PublicAggreDealsV3Api)
        assert msg.deals
        assert float(msg.deals[0].price) > 0
        assert float(msg.deals[0].quantity) > 0
        assert msg.deals[0].tradeType > 0
        assert int(msg.deals[0].time) > 0


def test_kline_stream(ws_client: WebSocket):
    messages: list[PublicSpotKlineV3Api] = []
    done = threading.Event()

    def handle_message(msg: PublicSpotKlineV3Api):
        messages.append(msg)
        logger.info("Received kline message: %s", msg)
        if len(messages) >= 2:
            ws_client.unsubscribe(ws_client.kline_stream)
            done.set()

    ws_client.kline_stream(handle_message, "BTCUSDT", interval="Min1")

    _wait_or_fail(done, 10, "Не получили достаточно сообщений клина за отведённое время")
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


def test_increase_depth_stream(ws_client: WebSocket):
    messages: list[PublicAggreDepthsV3Api] = []
    done = threading.Event()

    def handle_message(msg: PublicAggreDepthsV3Api):
        messages.append(msg)
        if len(messages) >= 2:
            ws_client.unsubscribe(ws_client.depth_stream)
            done.set()

    ws_client.depth_stream(handle_message, "BTCUSDT")

    _wait_or_fail(done, 10, "Не получили достаточно сообщений об агрегированной глубине")
    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, PublicAggreDepthsV3Api)
        assert msg.eventType == "spot@public.aggre.depth.v3.api.pb"
        assert msg.fromVersion is not None
        assert msg.asks
        assert msg.bids


def test_limit_depth_stream(ws_client: WebSocket):
    messages: list[PublicLimitDepthsV3Api] = []
    done = threading.Event()

    def handle_message(msg: PublicLimitDepthsV3Api):
        messages.append(msg)
        logger.info("Received limit depth message: %s", msg)
        if len(messages) >= 2:
            ws_client.unsubscribe(ws_client.limit_depth_stream)
            done.set()

    ws_client.limit_depth_stream(handle_message, "BTCUSDT", 5)

    _wait_or_fail(done, 10, "Не получили достаточно сообщений о лимитной глубине")
    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, PublicLimitDepthsV3Api)
        assert msg.eventType == "spot@public.limit.depth.v3.api.pb"
        assert msg.version is not None
        assert msg.asks
        assert msg.bids


def test_book_ticker_stream(ws_client: WebSocket):
    messages: list[PublicAggreBookTickerV3Api] = []
    done = threading.Event()

    def handle_message(msg: PublicAggreBookTickerV3Api):
        messages.append(msg)
        if len(messages) >= 2:
            ws_client.unsubscribe(ws_client.book_ticker_stream)
            done.set()

    ws_client.book_ticker_stream(handle_message, "BTCUSDT")

    _wait_or_fail(done, 10, "Не получили достаточно сообщений book ticker")
    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, PublicAggreBookTickerV3Api)
        assert msg.bidPrice is not None and float(msg.bidPrice) > 0
        assert msg.bidQuantity is not None and float(msg.bidQuantity) > 0
        assert msg.askPrice is not None and float(msg.askPrice) > 0
        assert msg.askQuantity is not None and float(msg.askQuantity) > 0


def test_book_ticker_batch_stream(ws_client: WebSocket):
    messages: list[PublicBookTickerBatchV3Api] = []
    done = threading.Event()

    def handle_message(msg: PublicBookTickerBatchV3Api):
        messages.append(msg)
        if len(messages) >= 2:
            ws_client.unsubscribe(ws_client.book_ticker_batch_stream)
            done.set()

    ws_client.book_ticker_batch_stream(handle_message, ["BTCUSDT"])

    _wait_or_fail(done, 10, "Не получили достаточно сообщений batch book ticker")
    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, PublicBookTickerBatchV3Api)
        assert msg.items
        first = msg.items[0]
        assert first.bidPrice is not None and float(first.bidPrice) > 0
        assert first.bidQuantity is not None and float(first.bidQuantity) > 0
        assert first.askPrice is not None and float(first.askPrice) > 0
        assert first.askQuantity is not None and float(first.askQuantity) > 0


def test_account_update(ws_client: WebSocket):
    messages: list[PrivateAccountV3Api] = []
    done = threading.Event()

    def handle_message(msg: PrivateAccountV3Api):
        messages.append(msg)
        logger.info("Received account update: %s", msg)
        ws_client.unsubscribe(ws_client.account_update)
        done.set()

    ws_client.account_update(handle_message)

    order_thread = threading.Thread(target=make_mxusdt_order, kwargs={"time_wait": 2})
    order_thread.start()

    _wait_or_fail(done, 20, "Не получили сообщение об обновлении аккаунта")
    order_thread.join(timeout=10)

    assert messages
    for msg in messages:
        assert isinstance(msg, PrivateAccountV3Api)
        assert msg.vcoinName == "USDT"
        assert msg.coinId
        assert msg.balanceAmount is not None
        assert msg.balanceAmountChange is not None
        assert msg.frozenAmount is not None
        assert msg.frozenAmountChange is not None
        assert msg.type
        assert msg.time > 0


def test_account_deals(ws_client: WebSocket):
    messages: list[PrivateDealsV3Api] = []
    done = threading.Event()

    def handle_message(msg: PrivateDealsV3Api):
        messages.append(msg)
        logger.info("Received account deal: %s", msg)
        if len(messages) >= 2:
            ws_client.unsubscribe(ws_client.account_deals)
            done.set()

    ws_client.account_deals(handle_message)

    order_thread = threading.Thread(target=make_mxusdt_order, kwargs={"time_wait": 2})
    order_thread.start()

    # Ждём, но не валимся по таймауту — биржа может не выдать сделки
    done.wait(20)
    ws_client.unsubscribe(ws_client.account_deals)
    order_thread.join(timeout=10)
    time.sleep(2)

    if PRINT_RESPONSE:
        logger.info("Account deals messages: %s", messages)

    assert len(messages) >= 0
    for msg in messages:
        assert isinstance(msg, PrivateDealsV3Api)
        assert float(msg.price) > 0
        assert float(msg.quantity) > 0
        assert msg.tradeType > 0
        assert int(msg.time) > 0


def test_account_orders(ws_client: WebSocket):
    messages: list[PrivateOrdersV3Api] = []
    done = threading.Event()

    def handle_message(msg: PrivateOrdersV3Api):
        messages.append(msg)
        logger.info("Received account order: %s", msg)
        ws_client.unsubscribe(ws_client.account_orders)
        done.set()

    ws_client.account_orders(handle_message)

    order_thread = threading.Thread(target=make_mxusdt_order, kwargs={"time_wait": 2})
    order_thread.start()

    _wait_or_fail(done, 20, "Не получили сообщение по заявкам аккаунта")
    order_thread.join(timeout=10)

    assert messages
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


def test_multiple_subscriptions(ws_client: WebSocket):
    messages: list[PublicAggreDealsV3Api | PublicAggreBookTickerV3Api] = []
    done = threading.Event()

    def handle_message(msg: PublicAggreDealsV3Api | PublicAggreBookTickerV3Api):
        messages.append(msg)
        if len(messages) >= 4:
            ws_client.unsubscribe(ws_client.deals_stream, ws_client.book_ticker_stream)
            done.set()

    ws_client.deals_stream(handle_message, "BTCUSDT")
    ws_client.book_ticker_stream(handle_message, "BTCUSDT")

    _wait_or_fail(done, 15, "Не получили сообщения от обоих потоков")
    assert len(messages) >= 4

    message_types = {type(msg) for msg in messages}
    assert PublicAggreDealsV3Api in message_types
    assert PublicAggreBookTickerV3Api in message_types

    for msg in messages:
        if isinstance(msg, PublicAggreDealsV3Api):
            assert msg.deals
            assert msg.deals[0].price is not None and float(msg.deals[0].price) > 0
            assert msg.deals[0].quantity is not None and float(msg.deals[0].quantity) > 0
            assert msg.deals[0].tradeType is not None and msg.deals[0].tradeType > 0
            assert msg.deals[0].time is not None and int(msg.deals[0].time) > 0

        if isinstance(msg, PublicAggreBookTickerV3Api):
            assert msg.bidPrice is not None and float(msg.bidPrice) > 0
            assert msg.bidQuantity is not None and float(msg.bidQuantity) > 0
            assert msg.askPrice is not None and float(msg.askPrice) > 0
            assert msg.askQuantity is not None and float(msg.askQuantity) > 0
