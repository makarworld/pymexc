# pytest . -v -s

import time

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
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await client.account_information()

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
    assert "code=400" in str(e.value)
    assert "api key required" in str(e.value)


@pytest.mark.asyncio
async def test_wrong_api_key():
    http = HTTP(api_key="wrong_api_key", api_secret="wrong_api_secret")
    with pytest.raises(pymexc._async.base.MexcAPIError):
        await http.exchange_info()


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

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) == 1
    assert all(isinstance(trade, dict) for trade in resp)


@pytest.mark.asyncio
async def test_agg_trades(http_client: HTTP):
    resp = await http_client.agg_trades(symbol="BTCUSDT", limit=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) == 1
    assert all(isinstance(trade, dict) for trade in resp)


@pytest.mark.asyncio
async def test_klines(http_client: HTTP):
    resp = await http_client.klines(symbol="BTCUSDT", interval="1m", limit=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) == 1
    assert all(isinstance(kline, list) for kline in resp)


@pytest.mark.asyncio
async def test_avg_price(http_client: HTTP):
    resp = await http_client.avg_price(symbol="BTCUSDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "price" in resp
    assert "mins" in resp


@pytest.mark.asyncio
async def test_ticker_24h(http_client: HTTP):
    resp = await http_client.ticker_24h(symbol="BTCUSDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "symbol" in resp
    assert resp["symbol"] == "BTCUSDT"


@pytest.mark.asyncio
async def test_ticker_price(http_client: HTTP):
    resp = await http_client.ticker_price(symbol="BTCUSDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "symbol" in resp
    assert "price" in resp


@pytest.mark.asyncio
async def test_ticker_book_price(http_client: HTTP):
    resp = await http_client.ticker_book_price(symbol="BTCUSDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "symbol" in resp
    assert "bidPrice" in resp
    assert "askPrice" in resp


@pytest.mark.asyncio
async def test_create_sub_account(http_client: HTTP):
    # Test with invalid data
    res = await http_client.create_sub_account(sub_account="", note="")
    # {'code': '730600', 'msg': 'Sub-account name cannot be null'}

    if PRINT_RESPONSE:
        print(str(res)[:50])

    assert res["code"] == "730600"
    assert res["msg"] == "Sub-account name cannot be null"


@pytest.mark.asyncio
async def test_sub_account_list(http_client: HTTP):
    resp = await http_client.sub_account_list()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "subAccounts" in resp
    assert isinstance(resp["subAccounts"], list)


@pytest.mark.asyncio
async def test_create_sub_account_api_key(http_client: HTTP):
    # Test with invalid sub account
    res = await http_client.create_sub_account_api_key(
        sub_account="nonexistent",
        note="test",
        permissions=["SPOT_ACCOUNT_READ"],
    )

    if PRINT_RESPONSE:
        print(str(res)[:50])

    # {'code': '730002', 'msg': 'Parameter error'}
    assert isinstance(res, dict)
    assert res["code"] == "730002"
    assert res["msg"] == "Parameter error"


@pytest.mark.asyncio
async def test_get_kyc_status(http_client: HTTP):
    resp = await http_client.get_kyc_status()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert isinstance(resp.get("status"), str)


@pytest.mark.asyncio
async def test_get_uid(http_client: HTTP):
    resp = await http_client.get_uid()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "uid" in resp
    assert isinstance(resp.get("uid"), str)


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
    order = await http_client.order("MXUSDT", "BUY", "LIMIT", quantity=20, price=0.1)

    if PRINT_RESPONSE:
        print("Order response:", str(order)[:50])

    assert isinstance(order, dict)
    assert "orderId" in order

    # Cancel the order
    resp = await http_client.cancel_order("MXUSDT", order["orderId"])

    if PRINT_RESPONSE:
        print("Cancel order response:", str(resp)[:50])

    assert isinstance(resp, dict)
    assert "orderId" in resp
    assert resp["orderId"] == order["orderId"]


@pytest.mark.asyncio
async def test_query_order(http_client: HTTP):
    # First create an order
    order = await http_client.order("MXUSDT", "BUY", "LIMIT", quantity=20, price=0.1)

    if PRINT_RESPONSE:
        print("Order response:", str(order)[:50])

    assert isinstance(order, dict)
    assert "orderId" in order

    # Query the order
    resp = await http_client.query_order("MXUSDT", order_id=order["orderId"])

    if PRINT_RESPONSE:
        print("Query order response:", str(resp)[:50])

    assert isinstance(resp, dict)
    assert "orderId" in resp
    assert resp["orderId"] == order["orderId"]

    # Cancel the order
    await http_client.cancel_order("MXUSDT", order["orderId"])


@pytest.mark.asyncio
async def test_current_open_orders(http_client: HTTP):
    resp = await http_client.current_open_orders("MXUSDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert all(isinstance(order, dict) for order in resp)


@pytest.mark.asyncio
async def test_all_orders(http_client: HTTP):
    resp = await http_client.all_orders("MXUSDT", limit=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) <= 10
    assert all(isinstance(order, dict) for order in resp)


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

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
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
        await http_client.withdraw(coin="INVALID_COIN", address="invalid_address", amount=-1)

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_cancel_withdraw(http_client: HTTP):
    # Test with invalid data
    res = await http_client.cancel_withdraw(id="invalid_id")
    # {'id': 'invalid_id'}

    if PRINT_RESPONSE:
        print(str(res)[:50])

    assert isinstance(res, dict)
    assert res["id"] == "invalid_id"


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
        await http_client.generate_deposit_address(coin="INVALID_COIN", network="INVALID_NETWORK")

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_deposit_address(http_client: HTTP):
    resp = await http_client.deposit_address(coin="USDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert all(isinstance(addr, dict) for addr in resp)


@pytest.mark.asyncio
async def test_withdraw_address(http_client: HTTP):
    resp = await http_client.withdraw_address()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert isinstance(resp["data"], list)


@pytest.mark.asyncio
async def test_user_universal_transfer(http_client: HTTP):
    # Test with invalid data
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.user_universal_transfer(
            from_account_type="SPOT", to_account_type="FUTURES", asset="INVALID", amount=-1
        )

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_user_universal_transfer_history(http_client: HTTP):
    resp = await http_client.user_universal_transfer_history(
        from_account_type="SPOT", to_account_type="FUTURES", page=1, size=10
    )
    # {'rows': [], 'total': 0}

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert isinstance(resp["rows"], list)
    assert len(resp["rows"]) >= 0
    assert isinstance(resp["total"], int)
    assert resp["total"] >= 0


@pytest.mark.asyncio
async def test_user_universal_transfer_history_by_tranid(http_client: HTTP):
    # Test with invalid data
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.user_universal_transfer_history_by_tranid(tran_id="invalid_id")

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
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
    # Test with invalid data
    res = await http_client.dust_transfer(asset="INVALID_COIN")
    # {'successList': [], 'failedList': []}

    if PRINT_RESPONSE:
        print(str(res)[:50])

    assert isinstance(res, dict)
    assert "successList" in res
    assert "failedList" in res
    assert isinstance(res["successList"], list)
    assert isinstance(res["failedList"], list)
    assert len(res["successList"]) >= 0
    assert len(res["failedList"]) >= 0


@pytest.mark.asyncio
async def test_dustlog(http_client: HTTP):
    resp = await http_client.dustlog()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert isinstance(resp["data"], list)


@pytest.mark.asyncio
async def test_internal_transfer(http_client: HTTP):
    # Test with invalid data
    with pytest.raises(pymexc._async.base.MexcAPIError) as e:
        await http_client.internal_transfer(
            to_account_type="EMAIL", to_account="invalid@email.com", asset="INVALID", amount=-1
        )

    assert isinstance(e.value, pymexc._async.base.MexcAPIError)
    assert "code" in str(e.value)


@pytest.mark.asyncio
async def test_internal_transfer_history(http_client: HTTP):
    resp = await http_client.internal_transfer_history()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert isinstance(resp["data"], list)


@pytest.mark.asyncio
async def test_create_listen_key(http_client: HTTP):
    resp = await http_client.create_listen_key()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "listenKey" in resp
    assert isinstance(resp.get("listenKey"), str)


@pytest.mark.asyncio
async def test_get_listen_keys(http_client: HTTP):
    resp = await http_client.get_listen_keys()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "listenKey" in resp
    assert isinstance(resp["listenKey"], list)


@pytest.mark.asyncio
async def test_keep_alive_listen_key(http_client: HTTP):
    # First create a listen key
    listen_key_resp = await http_client.create_listen_key()
    listen_key = listen_key_resp.get("listenKey")

    if PRINT_RESPONSE:
        print(f"Created listen key: {listen_key}")

    assert listen_key is not None

    # Keep alive the listen key
    resp = await http_client.keep_alive_listen_key(listen_key)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)


@pytest.mark.asyncio
async def test_close_listen_key(http_client: HTTP):
    # First create a listen key
    listen_key_resp = await http_client.create_listen_key()
    listen_key = listen_key_resp.get("listenKey")

    if PRINT_RESPONSE:
        print(f"Created listen key: {listen_key}")

    assert listen_key is not None

    # Close the listen key
    resp = await http_client.close_listen_key(listen_key)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)


@pytest.mark.asyncio
async def test_get_rebate_history_records(http_client: HTTP):
    resp = await http_client.get_rebate_history_records(page=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    # Data could be None if no records
    assert resp["data"] is None or isinstance(resp["data"], list)


@pytest.mark.asyncio
async def test_get_rebate_records_detail(http_client: HTTP):
    resp = await http_client.get_rebate_records_detail(page=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    # Data could be None if no records
    assert resp["data"] is None or isinstance(resp["data"], list)


@pytest.mark.asyncio
async def test_get_self_rebate_records_detail(http_client: HTTP):
    resp = await http_client.get_self_rebate_records_detail(page=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    # Data could be None if no records
    assert resp["data"] is None or isinstance(resp["data"], list)


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
    assert resp["data"] is None or isinstance(resp["data"], dict)


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


@pytest.mark.asyncio
async def test_create_stp_strategy_group(http_client: HTTP):
    # Test creating STP strategy group
    group_name = f"test_group_{int(time.time())}"
    resp = await http_client.create_stp_strategy_group(trade_group_name=group_name)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "code" in resp
    # Cleanup - delete the group if created successfully
    if resp.get("code") == 200 and "data" in resp:
        trade_group_id = resp["data"].get("tradeGroupId")
        if trade_group_id:
            try:
                await http_client.delete_stp_strategy_group(trade_group_id=str(trade_group_id))
            except Exception:
                pass  # Ignore cleanup errors


@pytest.mark.asyncio
async def test_query_stp_strategy_group(http_client: HTTP):
    resp = await http_client.query_stp_strategy_group()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "code" in resp


@pytest.mark.asyncio
async def test_affiliate_campaign(http_client: HTTP):
    resp = await http_client.affiliate_campaign(page=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "code" in resp


@pytest.mark.asyncio
async def test_affiliate_referral(http_client: HTTP):
    resp = await http_client.affiliate_referral(page=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "code" in resp


@pytest.mark.asyncio
async def test_affiliate_subaffiliates(http_client: HTTP):
    resp = await http_client.affiliate_subaffiliates(page=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "code" in resp


async def __test_exchange_info(client: HTTP):
    try:
        resp = await client.exchange_info(symbol="BTCUSDT")
        if PRINT_RESPONSE:
            print(str(resp)[:50])
        return resp
    except Exception as e:
        if PRINT_RESPONSE:
            print(f"Error: {e}")
        return None
