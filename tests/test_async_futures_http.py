# pytest . -v -s

import time

import curl_cffi.requests.exceptions
import pytest
import pytest_asyncio
from dotenv import dotenv_values

import pymexc._async.base
from pymexc._async.futures import HTTP

env = dotenv_values(".env")

api_key = env["API_KEY"]
api_secret = env["API_SECRET"]

PRINT_RESPONSE = True


@pytest_asyncio.fixture
async def http_client():
    """Create a new HTTP client for each test."""
    client = HTTP(api_key=api_key, api_secret=api_secret)
    yield client
    # Cleanup
    if hasattr(client, "session"):
        await client.session.close()


@pytest.mark.asyncio
async def test_no_auth():
    client = HTTP()
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await client.assets()

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
    assert "code=400" in str(e.value) or "api key required" in str(e.value)


@pytest.mark.asyncio
async def test_wrong_api_key():
    http = HTTP(api_key="wrong_api_key", api_secret="wrong_api_secret")
    with pytest.raises(pymexc._async.base.MexcAPIError):
        await http.assets()


@pytest.mark.asyncio
async def test_proxy():
    # use invalid proxy
    http_proxy = HTTP(
        api_key=api_key,
        api_secret=api_secret,
        proxies={"http": "http://0.0.0.1:1234", "https": "http://0.0.0.1:1234"},
    )

    with pytest.raises(curl_cffi.requests.exceptions.ConnectionError):
        await http_proxy.ping()


@pytest.mark.asyncio
async def test_ping(http_client: HTTP):
    resp = await http_client.ping()
    # {}

    if PRINT_RESPONSE:
        print(resp)

    assert isinstance(resp, dict)


@pytest.mark.asyncio
async def test_detail(http_client: HTTP):
    resp = await http_client.detail(symbol="BTC_USDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "BTC_USDT" in str(resp)


@pytest.mark.asyncio
async def test_support_currencies(http_client: HTTP):
    resp = await http_client.support_currencies()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert isinstance(resp.get("data"), list)


@pytest.mark.asyncio
async def test_get_depth(http_client: HTTP):
    resp = await http_client.get_depth(symbol="BTC_USDT", limit=5)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "bids" in resp.keys()
    assert "asks" in resp.keys()


@pytest.mark.asyncio
async def test_index_price(http_client: HTTP):
    resp = await http_client.index_price(symbol="BTC_USDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "price" in resp or "indexPrice" in resp


@pytest.mark.asyncio
async def test_fair_price(http_client: HTTP):
    resp = await http_client.fair_price(symbol="BTC_USDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "price" in resp or "fairPrice" in resp


@pytest.mark.asyncio
async def test_funding_rate(http_client: HTTP):
    resp = await http_client.funding_rate(symbol="BTC_USDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "fundingRate" in resp or "rate" in resp


@pytest.mark.asyncio
async def test_kline(http_client: HTTP):
    resp = await http_client.kline(symbol="BTC_USDT", interval="Min1")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or isinstance(resp.get("data"), list)


@pytest.mark.asyncio
async def test_deals(http_client: HTTP):
    resp = await http_client.deals(symbol="BTC_USDT", limit=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or isinstance(resp.get("data"), list)


@pytest.mark.asyncio
async def test_ticker(http_client: HTTP):
    resp = await http_client.ticker(symbol="BTC_USDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "symbol" in resp or "contractName" in resp


@pytest.mark.asyncio
async def test_risk_reverse(http_client: HTTP):
    resp = await http_client.risk_reverse(symbol="BTC_USDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)


@pytest.mark.asyncio
async def test_risk_reverse_history(http_client: HTTP):
    resp = await http_client.risk_reverse_history(symbol="BTC_USDT", page_num=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


@pytest.mark.asyncio
async def test_funding_rate_history(http_client: HTTP):
    resp = await http_client.funding_rate_history(symbol="BTC_USDT", page_num=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


@pytest.mark.asyncio
async def test_assets(http_client: HTTP):
    resp = await http_client.assets()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or isinstance(resp.get("data"), list)


@pytest.mark.asyncio
async def test_asset(http_client: HTTP):
    resp = await http_client.asset(currency="USDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "currency" in resp or "asset" in resp


@pytest.mark.asyncio
async def test_transfer_record(http_client: HTTP):
    resp = await http_client.transfer_record(page_num=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


@pytest.mark.asyncio
async def test_open_positions(http_client: HTTP):
    resp = await http_client.open_positions()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or isinstance(resp.get("data"), list)


@pytest.mark.asyncio
async def test_history_positions(http_client: HTTP):
    resp = await http_client.history_positions(page_num=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


@pytest.mark.asyncio
async def test_funding_records(http_client: HTTP):
    current_time = int(time.time() * 1000)
    one_day_ago = current_time - (24 * 60 * 60 * 1000)

    resp = await http_client.funding_records(
        position_type=1,
        start_time=one_day_ago,
        end_time=current_time,
        page_num=1,
        page_size=10,
    )

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


@pytest.mark.asyncio
async def test_open_orders(http_client: HTTP):
    resp = await http_client.open_orders(page_num=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


@pytest.mark.asyncio
async def test_history_orders(http_client: HTTP):
    resp = await http_client.history_orders(page_num=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


@pytest.mark.asyncio
async def test_get_order(http_client: HTTP):
    # Test with invalid order ID
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.get_order(order_id="invalid_order_id")

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_batch_query(http_client: HTTP):
    # Test with invalid order IDs
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.batch_query(order_ids="invalid_order_id")

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_order_deals(http_client: HTTP):
    resp = await http_client.order_deals(symbol="BTC_USDT", page_num=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


@pytest.mark.asyncio
async def test_get_trigger_orders(http_client: HTTP):
    resp = await http_client.get_trigger_orders(page_num=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


@pytest.mark.asyncio
async def test_get_stop_limit_orders(http_client: HTTP):
    resp = await http_client.get_stop_limit_orders(page_num=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


@pytest.mark.asyncio
async def test_risk_limit(http_client: HTTP):
    resp = await http_client.risk_limit()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or isinstance(resp.get("data"), list)


@pytest.mark.asyncio
async def test_tiered_fee_rate(http_client: HTTP):
    resp = await http_client.tiered_fee_rate()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or isinstance(resp.get("data"), dict)


@pytest.mark.asyncio
async def test_get_leverage(http_client: HTTP):
    resp = await http_client.get_leverage(symbol="BTC_USDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or isinstance(resp.get("data"), dict)


@pytest.mark.asyncio
async def test_get_position_mode(http_client: HTTP):
    resp = await http_client.get_position_mode()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "positionMode" in resp


@pytest.mark.asyncio
async def test_change_leverage(http_client: HTTP):
    # Test with invalid data
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.change_leverage(leverage=1000, symbol="BTC_USDT")

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_change_position_mode(http_client: HTTP):
    # Test with invalid data - method is under maintenance
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.change_position_mode(position_mode=1)

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_order(http_client: HTTP):
    # Test with invalid data - method is under maintenance
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.order(
            symbol="BTC_USDT",
            price=100000,
            vol=0.001,
            side=1,
            type=1,
            open_type=1,
        )

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_cancel_order(http_client: HTTP):
    # Test with invalid order ID
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.cancel_order(symbol="BTC_USDT", order_id="invalid_order_id")

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_cancel_all_orders(http_client: HTTP):
    # Test with invalid symbol
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.cancel_all_orders(symbol="INVALID_SYMBOL")

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_cancel_plan_order(http_client: HTTP):
    # Test with invalid order ID
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.cancel_plan_order(symbol="BTC_USDT", order_id="invalid_order_id")

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_cancel_stop_order(http_client: HTTP):
    # Test with invalid order ID
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.cancel_stop_order(symbol="BTC_USDT", order_id="invalid_order_id")

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)
