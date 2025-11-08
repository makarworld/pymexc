# pytest . -v -s

import logging
import threading
import time

import pytest
from dotenv import dotenv_values

from pymexc.futures import HTTP, WebSocket

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
    client = WebSocket(api_key=api_key, api_secret=api_secret)
    logger.info("WebSocket client created: %s", client)
    yield client
    try:
        client.exit()
    except Exception as exc:
        logger.warning("Failed to close WebSocket client: %s", exc)
    time.sleep(1)


def _wait_or_fail(event: threading.Event, timeout: float, message: str):
    if not event.wait(timeout):
        pytest.fail(message)


def test_tickers_stream(ws_client: WebSocket):
    messages = []
    done = threading.Event()

    def handle_message(msg):
        messages.append(msg)
        logger.info("Received tickers message: %s", msg)
        if len(messages) >= 2:
            ws_client.unsubscribe("sub.tickers")
            done.set()

    ws_client.tickers_stream(handle_message)

    _wait_or_fail(done, 10, "Не получили достаточно сообщений tickers за отведённое время")
    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, dict)
        assert "data" in msg or "c" in msg or "p" in msg


def test_ticker_stream(ws_client: WebSocket):
    messages = []
    done = threading.Event()

    def handle_message(msg):
        messages.append(msg)
        logger.info("Received ticker message: %s", msg)
        if len(messages) >= 2:
            ws_client.unsubscribe("sub.ticker")
            done.set()

    ws_client.ticker_stream(handle_message, "BTC_USDT")

    _wait_or_fail(done, 10, "Не получили достаточно сообщений ticker за отведённое время")
    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, dict)
        assert "data" in msg or "c" in msg or "p" in msg


def test_deal_stream(ws_client: WebSocket):
    messages = []
    done = threading.Event()

    def handle_message(msg):
        messages.append(msg)
        logger.info("Received deal message: %s", msg)
        if len(messages) >= 2:
            ws_client.unsubscribe("sub.deal")
            done.set()

    ws_client.deal_stream(handle_message, "BTC_USDT")

    _wait_or_fail(done, 10, "Не получили достаточно сообщений deal за отведённое время")
    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, dict)
        assert "data" in msg or "p" in msg or "v" in msg


def test_depth_stream(ws_client: WebSocket):
    messages = []
    done = threading.Event()

    def handle_message(msg):
        messages.append(msg)
        logger.info("Received depth message: %s", msg)
        if len(messages) >= 2:
            ws_client.unsubscribe("sub.depth")
            done.set()

    ws_client.depth_stream(handle_message, "BTC_USDT")

    _wait_or_fail(done, 10, "Не получили достаточно сообщений depth за отведённое время")
    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, dict)
        assert "data" in msg or "bids" in msg or "asks" in msg


def test_depth_full_stream(ws_client: WebSocket):
    messages = []
    done = threading.Event()

    def handle_message(msg):
        messages.append(msg)
        logger.info("Received depth full message: %s", msg)
        if len(messages) >= 1:
            ws_client.unsubscribe("sub.depth.full")
            done.set()

    ws_client.depth_full_stream(handle_message, "BTC_USDT", limit=5)

    _wait_or_fail(done, 10, "Не получили сообщение depth full за отведённое время")
    assert len(messages) >= 1
    for msg in messages:
        assert isinstance(msg, dict)
        assert "data" in msg or "bids" in msg or "asks" in msg


def test_kline_stream(ws_client: WebSocket):
    messages = []
    done = threading.Event()

    def handle_message(msg):
        messages.append(msg)
        logger.info("Received kline message: %s", msg)
        if len(messages) >= 2:
            ws_client.unsubscribe("sub.kline")
            done.set()

    ws_client.kline_stream(handle_message, "BTC_USDT", interval="Min1")

    _wait_or_fail(done, 10, "Не получили достаточно сообщений kline за отведённое время")
    assert len(messages) >= 2
    for msg in messages:
        assert isinstance(msg, dict)
        assert "data" in msg or "c" in msg or "o" in msg


def test_funding_rate_stream(ws_client: WebSocket):
    messages = []
    done = threading.Event()

    def handle_message(msg):
        messages.append(msg)
        logger.info("Received funding rate message: %s", msg)
        if len(messages) >= 1:
            ws_client.unsubscribe("sub.funding.rate")
            done.set()

    ws_client.funding_rate_stream(handle_message, "BTC_USDT")

    _wait_or_fail(done, 10, "Не получили сообщение funding rate за отведённое время")
    assert len(messages) >= 1
    for msg in messages:
        assert isinstance(msg, dict)
        assert "data" in msg or "r" in msg or "fundingRate" in msg


def test_index_price_stream(ws_client: WebSocket):
    messages = []
    done = threading.Event()

    def handle_message(msg):
        messages.append(msg)
        logger.info("Received index price message: %s", msg)
        if len(messages) >= 1:
            ws_client.unsubscribe("sub.index.price")
            done.set()

    ws_client.index_price_stream(handle_message, "BTC_USDT")

    _wait_or_fail(done, 10, "Не получили сообщение index price за отведённое время")
    assert len(messages) >= 1
    for msg in messages:
        assert isinstance(msg, dict)
        assert "data" in msg or "p" in msg or "indexPrice" in msg


def test_fair_price_stream(ws_client: WebSocket):
    messages = []
    done = threading.Event()

    def handle_message(msg):
        messages.append(msg)
        logger.info("Received fair price message: %s", msg)
        if len(messages) >= 1:
            ws_client.unsubscribe("sub.fair.price")
            done.set()

    ws_client.fair_price_stream(handle_message, "BTC_USDT")

    _wait_or_fail(done, 10, "Не получили сообщение fair price за отведённое время")
    assert len(messages) >= 1
    for msg in messages:
        assert isinstance(msg, dict)
        assert "data" in msg or "p" in msg or "fairPrice" in msg


def test_personal_stream(ws_client: WebSocket):
    messages = []
    done = threading.Event()

    def handle_message(msg):
        messages.append(msg)
        logger.info("Received personal message: %s", msg)
        if len(messages) >= 1:
            ws_client.unsubscribe(ws_client.personal_stream)
            done.set()

    ws_client.personal_stream(handle_message)

    _wait_or_fail(done, 10, "Не получили сообщение personal stream за отведённое время")
    assert len(messages) >= 0  # May be empty if no account activity


def test_filter_stream(ws_client: WebSocket):
    messages = []
    done = threading.Event()

    def handle_message(msg):
        messages.append(msg)
        logger.info("Received filter message: %s", msg)
        if len(messages) >= 1:
            ws_client.unsubscribe("personal.filter")
            done.set()

    ws_client.filter_stream(handle_message, params={"filters": [{"filter": "asset"}]})

    _wait_or_fail(done, 10, "Не получили сообщение filter stream за отведённое время")
    assert len(messages) >= 0  # May be empty if no account activity


def test_multiple_subscriptions(ws_client: WebSocket):
    messages = []
    done = threading.Event()

    def handle_message(msg):
        messages.append(msg)
        logger.info(f"Received message type: {type(msg)}")
        if len(messages) >= 10:
            ws_client.unsubscribe("sub.ticker")
            ws_client.unsubscribe("sub.deal")
            done.set()

    ws_client.ticker_stream(handle_message, "BTC_USDT")
    ws_client.deal_stream(handle_message, "BTC_USDT")

    _wait_or_fail(done, 15, "Не получили сообщения от обоих потоков")
    assert len(messages) >= 10
