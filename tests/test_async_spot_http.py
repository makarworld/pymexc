# pytest . -v -s

import json
import time
from unittest.mock import patch

import curl_cffi.requests.exceptions
import pytest
import pytest_asyncio
from dotenv import dotenv_values

import pymexc._async.base
from pymexc._async.spot import HTTP

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
    assert await test_exchange_info(client) is None


@pytest.mark.asyncio
async def test_wrong_api_key():
    client = HTTP(api_key="wrong_api_key", api_secret="wrong_api_secret")
    with pytest.raises(pymexc._async.base.MexcAPIError):
        await client.exchange_info()


@pytest.mark.asyncio
async def test_proxy():
    # use invalid proxy
    client = HTTP(
        api_key=api_key,
        api_secret=api_secret,
        proxies={"http": "http://0.0.0.1:1234", "https": "http://0.0.0.1:1234"},
    )

    with pytest.raises(curl_cffi.requests.exceptions.ConnectionError):
        await client.ping()


@pytest.mark.asyncio
async def test_ping(http_client: HTTP):
    assert await http_client.ping() == {}


@pytest.mark.asyncio
async def test_time(http_client: HTTP):
    resp = await http_client.time()
    # {'serverTime': 1749076765439}

    if PRINT_RESPONSE:
        print(resp)

    assert isinstance(resp, dict)
    assert resp.get("serverTime") > 0
    assert isinstance(resp.get("serverTime"), int)


@pytest.mark.asyncio
async def test_default_symbols(http_client: HTTP):
    resp = await http_client.default_symbols()
    # {'data': ['SNTUSDT', 'CGPTUSDT', 'SHOOTUSDT', 'WEF

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert isinstance(resp.get("data"), list)
    assert "BNBUSDT" in resp.get("data")
    assert resp.get("msg") == "success"


@pytest.mark.asyncio
async def test_exchange_info(http_client: HTTP):
    resp = await http_client.exchange_info(symbol="BTCUSDT")
    # {'timezone': 'CST', 'serverTime': 1749076852582, '

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "BTCUSDT" in str(resp)


@pytest.mark.asyncio
async def test_order_book(http_client: HTTP):
    resp = await http_client.order_book(symbol="BTCUSDT", limit=1)
    # {'lastUpdateId': 42154878994, 'bids': [['104864.01

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "bids" in resp.keys()
    assert "asks" in resp.keys()
    assert len(resp.get("asks")) == 1
    assert resp.get("timestamp") > 0


@pytest.mark.asyncio
async def test_trades(http_client: HTTP):
    resp = await http_client.trades(symbol="BTCUSDT", limit=1)
    # [{'id': None, 'price': '104864.01', 'qty': '0.0001

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) == 1


@pytest.mark.asyncio
async def test_agg_trades(http_client: HTTP):
    resp = await http_client.agg_trades(symbol="BTCUSDT", limit=1)
    # [{'a': None, 'f': None, 'l': None, 'p': '104821.27

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) == 1
    assert resp[0].get("T") > 0


@pytest.mark.asyncio
async def test_klines(http_client: HTTP):
    resp = await http_client.klines(symbol="BTCUSDT", interval="1m", limit=1)
    # [[1749076800000, '104861.97', '104881.74', '104861

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) == 1
    assert resp[0][0] > 0


@pytest.mark.asyncio
async def test_avg_price(http_client: HTTP):
    resp = await http_client.avg_price(symbol="BTCUSDT")
    # {'mins': 5, 'price': '104848.56'}

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert isinstance(resp.get("mins"), int)
    assert isinstance(resp.get("price"), str)


@pytest.mark.asyncio
async def test_ticker_24h(http_client: HTTP):
    resp = await http_client.ticker_24h(symbol="BTCUSDT")
    # {'symbol': 'BTCUSDT', 'priceChange': '-965.92', 'p

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert resp.get("symbol") == "BTCUSDT"
    assert isinstance(resp.get("priceChange"), str)
    assert isinstance(resp.get("priceChangePercent"), str)


@pytest.mark.asyncio
async def test_ticker_price(http_client: HTTP):
    resp = await http_client.ticker_price(symbol="BTCUSDT")
    # {'symbol': 'BTCUSDT', 'price': '104873.06'}

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert resp.get("symbol") == "BTCUSDT"
    assert isinstance(resp.get("price"), str)


@pytest.mark.asyncio
async def test_ticker_book_price(http_client: HTTP):
    resp = await http_client.ticker_book_price(symbol="BTCUSDT")
    # {'symbol': 'BTCUSDT', 'bidPrice': '104867.06', 'bi

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert resp.get("symbol") == "BTCUSDT"
    assert isinstance(resp.get("bidPrice"), str)
    assert isinstance(resp.get("bidQty"), str)
    assert isinstance(resp.get("askPrice"), str)
    assert isinstance(resp.get("askQty"), str)


@pytest.mark.asyncio
async def test_create_sub_account(http_client: HTTP):
    resp = await http_client.create_sub_account("test_subaccount", "test_note")
    error = {
        "code": "730601",
        "msg": "Sub-account name must be a combination of 8-32 letters and numbers",
    }

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert resp == error


@pytest.mark.asyncio
async def test_sub_account_list(http_client: HTTP):
    resp = await http_client.sub_account_list()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert isinstance(resp.get("subAccounts"), list)


@pytest.mark.asyncio
async def test_create_sub_account_api_key(http_client: HTTP):
    resp = await http_client.create_sub_account_api_key(
        sub_account="test_subaccount",
        note="test_note",
        permissions="SPOT_ACCOUNT_READ",
    )
    error = {"code": "730002", "msg": "Parameter error"}

    if PRINT_RESPONSE:
        print(str(resp))

    assert isinstance(resp, dict)
    assert resp == error


@pytest.mark.asyncio
async def test_query_sub_account_api_key(http_client: HTTP):
    resp = await http_client.query_sub_account_api_key(
        sub_account="test_subaccount",
    )
    error = {"code": "730002", "msg": "Parameter error"}

    if PRINT_RESPONSE:
        print(str(resp))

    assert isinstance(resp, dict)
    assert resp == error


@pytest.mark.asyncio
async def test_delete_sub_account_api_key(http_client: HTTP):
    resp = await http_client.delete_sub_account_api_key(
        sub_account="test_subaccount",
        api_key="test_api_key",
    )
    error = {"code": "730706", "msg": "API KEY information does not exist"}

    if PRINT_RESPONSE:
        print(str(resp))

    assert isinstance(resp, dict)
    assert resp == error


@pytest.mark.asyncio
async def test_universal_transfer(http_client: HTTP):
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.universal_transfer(
            from_account_type="SPOT",
            to_account_type="SPOT",
            asset="USDT",
            amount=0.01,
        )

    assert str(e.value) == "(code=700007): No permission to access the endpoint."


@pytest.mark.asyncio
async def test_query_universal_transfer_history(http_client: HTTP):
    resp = await http_client.query_universal_transfer_history(
        from_account_type="SPOT",
        to_account_type="SPOT",
    )

    assert isinstance(resp, dict)
    assert isinstance(resp.get("result"), list)
    assert isinstance(resp.get("totalCount"), int)


@pytest.mark.asyncio
async def test_sub_account_asset(http_client: HTTP):
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.sub_account_asset(
            sub_account="test_subaccount",
            account_type="SPOT",
        )

    assert str(e.value) == "(code=700004): subAccount not exist"


@pytest.mark.asyncio
async def test_get_kyc_status(http_client: HTTP):
    resp = await http_client.get_kyc_status()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert isinstance(resp.get("status"), str)


@pytest.mark.asyncio
async def test_get_default_symbols(http_client: HTTP):
    resp = await http_client.get_default_symbols()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert isinstance(resp.get("data"), list)
    assert "BNBUSDT" in resp.get("data")
    assert resp.get("msg") == "success"


@pytest.mark.asyncio
async def test_test_order(http_client: HTTP):
    # Test LIMIT order
    resp = await http_client.test_order(
        symbol="MXUSDT",
        side="BUY",
        order_type="LIMIT",
        quantity=50,
        price=0.1,
    )

    if PRINT_RESPONSE:
        print("Test LIMIT order response:", str(resp)[:50])

    assert isinstance(resp, dict)
    assert resp == {}

    # Test MARKET order
    resp = await http_client.test_order(
        symbol="MXUSDT",
        side="SELL",
        order_type="MARKET",
        quantity=50,
    )

    if PRINT_RESPONSE:
        print("Test MARKET order response:", str(resp)[:50])

    assert isinstance(resp, dict)
    assert resp == {}

    # Test error case - missing required parameters
    with pytest.raises(ValueError) as e:
        await http_client.test_order(
            symbol="MXUSDT",
            side="BUY",
            order_type="LIMIT",
        )
    assert "LIMIT orders require both quantity and price" in str(e.value)

    with pytest.raises(ValueError) as e:
        await http_client.test_order(
            symbol="MXUSDT",
            side="BUY",
            order_type="MARKET",
        )
    assert "MARKET orders require either quantity or quoteOrderQty" in str(e.value)


@pytest.mark.asyncio
async def test_order(http_client: HTTP):
    # Test LIMIT order
    resp = await http_client.order(
        symbol="MXUSDT",
        side="BUY",
        order_type="LIMIT",
        quantity=50,
        price=0.1,
    )

    if PRINT_RESPONSE:
        print("LIMIT order response:", str(resp)[:50])

    assert isinstance(resp, dict)
    assert "orderId" in resp
    assert "symbol" in resp
    assert resp["symbol"] == "MXUSDT"
    assert resp["side"] == "BUY"
    assert resp["type"] == "LIMIT"

    # Test error case - missing required parameters
    with pytest.raises(ValueError) as e:
        await http_client.order(
            symbol="MXUSDT",
            side="BUY",
            order_type="LIMIT",
        )
    assert "LIMIT orders require both quantity and price" in str(e.value)

    with pytest.raises(ValueError) as e:
        await http_client.order(
            symbol="MXUSDT",
            side="BUY",
            order_type="MARKET",
        )
    assert "MARKET orders require either quantity or quoteOrderQty" in str(e.value)


@pytest.mark.asyncio
async def test_cancel_order(http_client: HTTP):
    # First create an order
    order = await http_client.order(
        symbol="MXUSDT",
        side="BUY",
        order_type="LIMIT",
        quantity=50,
        price=0.1,
    )

    if PRINT_RESPONSE:
        print("Created order:", str(order)[:50])

    # Then cancel it
    resp = await http_client.cancel_order(symbol="MXUSDT", order_id=order["orderId"])

    if PRINT_RESPONSE:
        print("Cancel order response:", str(resp)[:50])

    assert isinstance(resp, dict)
    assert "orderId" in resp
    # Status could be NEW or CANCELED depending on timing
    assert resp["status"] in ["NEW", "CANCELED"]

    # Test error case - invalid order ID
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.cancel_order(symbol="MXUSDT", order_id="invalid_order_id")
    assert "code" in str(e.value)
    assert "Unknown order id" in str(e.value)


@pytest.mark.asyncio
async def test_cancel_all_open_orders(http_client: HTTP):
    # First create a buy order
    order = await http_client.order(
        symbol="MXUSDT",
        side="BUY",
        order_type="LIMIT",
        quantity=50,
        price=0.1,
    )

    if PRINT_RESPONSE:
        print("Created order:", str(order)[:50])

    # Then cancel all
    resp = await http_client.cancel_all_open_orders(symbol="MXUSDT")

    if PRINT_RESPONSE:
        print("Cancel all orders response:", str(resp)[:50])

    assert isinstance(resp, list)
    assert all(isinstance(order, dict) for order in resp)
    for order in resp:
        assert "orderId" in order
        assert "status" in order
        assert order["status"] in ["NEW", "CANCELED"]


@pytest.mark.asyncio
async def test_query_order(http_client: HTTP):
    # First create an order
    order = await http_client.order(
        symbol="MXUSDT",
        side="BUY",
        order_type="LIMIT",
        quantity=50,
        price=0.1,
    )

    if PRINT_RESPONSE:
        print("Created order:", str(order)[:50])

    # Then query it
    resp = await http_client.query_order(symbol="MXUSDT", order_id=order["orderId"])

    if PRINT_RESPONSE:
        print("Query order response:", str(resp)[:50])

    assert isinstance(resp, dict)
    assert "orderId" in resp
    assert resp["symbol"] == "MXUSDT"
    assert resp["side"] == "BUY"
    assert resp["type"] == "LIMIT"

    # Test error case - invalid order ID
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.query_order(symbol="MXUSDT", order_id="invalid_order_id")
    assert "code" in str(e.value)
    assert "Order does not exist" in str(e.value)


@pytest.mark.asyncio
async def test_current_open_orders(http_client: HTTP):
    # First create a buy order
    order = await http_client.order(
        symbol="MXUSDT",
        side="BUY",
        order_type="LIMIT",
        quantity=50,
        price=0.1,
    )

    if PRINT_RESPONSE:
        print("Created order:", str(order)[:50])

    resp = await http_client.current_open_orders(symbol="MXUSDT")

    if PRINT_RESPONSE:
        print("Current open orders response:", str(resp)[:50])

    assert isinstance(resp, list)
    assert all(isinstance(order, dict) for order in resp)
    for order in resp:
        assert "orderId" in order
        assert "symbol" in order
        assert "side" in order
        assert "type" in order
        assert "status" in order


@pytest.mark.asyncio
async def test_all_orders(http_client: HTTP):
    resp = await http_client.all_orders(symbol="MXUSDT", limit=10)

    if PRINT_RESPONSE:
        print("All orders response:", str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) <= 10
    assert all(isinstance(order, dict) for order in resp)
    for order in resp:
        assert "orderId" in order
        assert "symbol" in order
        assert "side" in order
        assert "type" in order
        assert "status" in order


@pytest.mark.asyncio
async def test_account_information(http_client: HTTP):
    resp = await http_client.account_information()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "balances" in resp
    assert isinstance(resp["balances"], list)


@pytest.mark.asyncio
async def test_account_trade_list(http_client: HTTP):
    resp = await http_client.account_trade_list(symbol="MXUSDT", limit=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) <= 10
    assert all(isinstance(trade, dict) for trade in resp)


@pytest.mark.asyncio
async def test_enable_mx_deduct(http_client: HTTP):
    # Test with invalid data
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.enable_mx_deduct(mx_deduct_enable=True)

    assert e.errisinstance(pymexc._async.base.MexcAPIError)
    # Check for either code or msg in error message
    error_str = str(e.value)
    assert any(key in error_str for key in ["code", "msg"])


@pytest.mark.asyncio
async def test_query_mx_deduct_status(http_client: HTTP):
    resp = await http_client.query_mx_deduct_status()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert "mxDeductEnable" in resp["data"]


@pytest.mark.asyncio
async def test_query_symbol_commission(http_client: HTTP):
    resp = await http_client.query_symbol_commission(symbol="MXUSDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert "makerCommission" in resp["data"]
    assert "takerCommission" in resp["data"]


@pytest.mark.asyncio
async def test_get_currency_info(http_client: HTTP):
    resp = await http_client.get_currency_info()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert all(isinstance(currency, dict) for currency in resp)


@pytest.mark.asyncio
async def test_withdraw(http_client: HTTP):
    # Test with invalid data
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.withdraw(
            coin="INVALID_COIN", address="invalid_address", amount=-1
        )

    assert e.errisinstance(pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_cancel_withdraw(http_client: HTTP):
    # Test with invalid data
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.cancel_withdraw(id="invalid_id")

    assert e.errisinstance(pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_deposit_history(http_client: HTTP):
    resp = await http_client.deposit_history(limit=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) <= 10
    assert all(isinstance(deposit, dict) for deposit in resp)


@pytest.mark.asyncio
async def test_withdraw_history(http_client: HTTP):
    resp = await http_client.withdraw_history(limit=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) <= 10
    assert all(isinstance(withdraw, dict) for withdraw in resp)


@pytest.mark.asyncio
async def test_generate_deposit_address(http_client: HTTP):
    # Test with invalid data
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.generate_deposit_address(
            coin="INVALID_COIN", network="INVALID_NETWORK"
        )

    assert e.errisinstance(pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_deposit_address(http_client: HTTP):
    resp = await http_client.deposit_address(coin="USDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert all(isinstance(address, dict) for address in resp)


@pytest.mark.asyncio
async def test_withdraw_address(http_client: HTTP):
    resp = await http_client.withdraw_address(coin="USDT", limit=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert isinstance(resp["data"], list)
    assert len(resp["data"]) <= 10


@pytest.mark.asyncio
async def test_user_universal_transfer(http_client: HTTP):
    # Test with invalid data
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.user_universal_transfer(
            from_account_type="INVALID",
            to_account_type="INVALID",
            asset="INVALID",
            amount=-1,
        )

    assert e.errisinstance(pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_user_universal_transfer_history(http_client: HTTP):
    resp = await http_client.user_universal_transfer_history(
        from_account_type="SPOT", to_account_type="SPOT", page=1, size=10
    )

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "rows" in resp
    assert isinstance(resp["rows"], list)


@pytest.mark.asyncio
async def test_user_universal_transfer_history_by_tranid(http_client: HTTP):
    # Test with invalid data
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.user_universal_transfer_history_by_tranid(
            tran_id="invalid_tran_id"
        )

    assert e.errisinstance(pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_get_assets_convert_into_mx(http_client: HTTP):
    resp = await http_client.get_assets_convert_into_mx()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert all(isinstance(asset, dict) for asset in resp)


@pytest.mark.asyncio
async def test_dust_transfer(http_client: HTTP):
    resp = await http_client.dust_transfer(asset="USDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "convertFee" in resp
    assert "failedList" in resp
    assert "successList" in resp


@pytest.mark.asyncio
async def test_dustlog(http_client: HTTP):
    resp = await http_client.dustlog(limit=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert isinstance(resp["data"], list)
    assert len(resp["data"]) <= 10


@pytest.mark.asyncio
async def test_internal_transfer(http_client: HTTP):
    # Test with invalid data
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.internal_transfer(
            to_account_type="INVALID",
            to_account="invalid_account",
            asset="INVALID",
            amount=-1,
        )

    assert e.errisinstance(pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_internal_transfer_history(http_client: HTTP):
    current_time = int(time.time() * 1000)
    one_day_ago = current_time - (24 * 60 * 60 * 1000)

    resp = await http_client.internal_transfer_history(
        start_time=one_day_ago, end_time=current_time
    )

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert isinstance(resp["data"], list)


@pytest.mark.asyncio
async def test_get_etf_info(http_client: HTTP):
    with pytest.raises(json.decoder.JSONDecodeError) as e:
        resp = await http_client.get_etf_info(symbol="ANY_SYMBOL")
        if PRINT_RESPONSE:
            print("ETF info response:", resp)

    assert "Expecting value: line 1 column 1 (char 0)" in str(e.value)


@pytest.mark.asyncio
async def test_create_listen_key(http_client: HTTP):
    resp = await http_client.create_listen_key()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "listenKey" in resp


@pytest.mark.asyncio
async def test_keep_alive_listen_key(http_client: HTTP):
    # First create a listen key
    listen_key_response = await http_client.create_listen_key()
    listen_key = listen_key_response["listenKey"]

    # Then keep it alive
    resp = await http_client.keep_alive_listen_key(listen_key=listen_key)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "listenKey" in resp
    assert resp["listenKey"] == listen_key


@pytest.mark.asyncio
async def test_get_listen_keys(http_client: HTTP):
    # First create a listen key
    listen_key_response = await http_client.create_listen_key()
    listen_key = listen_key_response["listenKey"]

    # Then get it
    resp = await http_client.get_listen_keys()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "listenKey" in resp
    assert isinstance(resp["listenKey"], list)
    assert listen_key in resp["listenKey"]


@pytest.mark.asyncio
async def test_close_listen_key(http_client: HTTP):
    # First create a listen key
    listen_key_response = await http_client.create_listen_key()
    listen_key = listen_key_response["listenKey"]

    # Then close it
    resp = await http_client.close_listen_key(listen_key)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "listenKey" in resp
    assert resp["listenKey"] == listen_key


@pytest.mark.asyncio
async def test_get_rebate_history_records(http_client: HTTP):
    resp = await http_client.get_rebate_history_records(page=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert isinstance(resp["data"], list)


@pytest.mark.asyncio
async def test_get_rebate_records_detail(http_client: HTTP):
    resp = await http_client.get_rebate_records_detail(page=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert isinstance(resp["data"], list)


@pytest.mark.asyncio
async def test_get_self_rebate_records_detail(http_client: HTTP):
    resp = await http_client.get_self_rebate_records_detail(page=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert isinstance(resp["data"], list)


@pytest.mark.asyncio
async def test_query_refercode(http_client: HTTP):
    resp = await http_client.query_refercode()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "referCode" in resp


@pytest.mark.asyncio
async def test_affiliate_commission_record(http_client: HTTP):
    resp = await http_client.affiliate_commission_record(page=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    # Data could be None if no records
    assert resp["data"] is None or isinstance(resp["data"], list)


@pytest.mark.asyncio
async def test_affiliate_withdraw_record(http_client: HTTP):
    resp = await http_client.affiliate_withdraw_record(page=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    # Data could be None if no records
    assert resp["data"] is None or isinstance(resp["data"], list)


@pytest.mark.asyncio
async def test_affiliate_commission_detail_record(http_client: HTTP):
    resp = await http_client.affiliate_commission_detail_record(page=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    # Data could be None if no records
    assert resp["data"] is None or isinstance(resp["data"], list)
