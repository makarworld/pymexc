# pytest . -v -s

import json
import time

import curl_cffi.requests.exceptions
import pytest
from dotenv import dotenv_values

import pymexc.base
from pymexc.spot import HTTP

env = dotenv_values(".env")

api_key = env["API_KEY"]
api_secret = env["API_SECRET"]

http = HTTP(api_key=api_key, api_secret=api_secret)

PRINT_RESPONSE = True


def test_no_auth():
    assert test_exchange_info(HTTP()) is None


def test_wrong_api_key():
    http = HTTP(api_key="wrong_api_key", api_secret="wrong_api_secret")
    with pytest.raises(pymexc.base.MexcAPIError):
        http.exchange_info()


def test_proxy():
    # use invalid proxy
    http_proxy = HTTP(
        api_key=api_key,
        api_secret=api_secret,
        proxies={"http": "http://0.0.0.1:1234", "https": "http://0.0.0.1:1234"},
    )

    with pytest.raises(curl_cffi.requests.exceptions.ConnectionError):
        http_proxy.ping()


def test_ping():
    assert http.ping() == {}


def test_time():
    resp = http.time()
    # {'serverTime': 1749076765439}

    if PRINT_RESPONSE:
        print(resp)

    assert isinstance(resp, dict)
    assert resp.get("serverTime") > 0
    assert isinstance(resp.get("serverTime"), int)


def test_default_symbols():
    resp = http.default_symbols()
    # {'data': ['SNTUSDT', 'CGPTUSDT', 'SHOOTUSDT', 'WEF

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert isinstance(resp.get("data"), list)
    assert "BNBUSDT" in resp.get("data")
    assert resp.get("msg") == "success"


def test_exchange_info(http: HTTP = http):
    resp = http.exchange_info(symbol="BTCUSDT")
    # {'timezone': 'CST', 'serverTime': 1749076852582, '

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "BTCUSDT" in str(resp)


def test_order_book():
    resp = http.order_book(symbol="BTCUSDT", limit=1)
    # {'lastUpdateId': 42154878994, 'bids': [['104864.01

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "bids" in resp.keys()
    assert "asks" in resp.keys()
    assert len(resp.get("asks")) == 1
    assert resp.get("timestamp") > 0


def test_trades():
    resp = http.trades(symbol="BTCUSDT", limit=1)
    # [{'id': None, 'price': '104864.01', 'qty': '0.0001

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) == 1


def test_agg_trades():
    resp = http.agg_trades(symbol="BTCUSDT", limit=1)
    # [{'a': None, 'f': None, 'l': None, 'p': '104821.27

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) >= 0  # May be empty if no trades
    if len(resp) > 0:
        assert isinstance(resp[0], dict)


def test_klines():
    # Use client without auth for public endpoint
    public_client = HTTP()
    resp = public_client.klines(symbol="BTCUSDT", interval="1m", limit=1)
    # [[1749076800000, '104861.97', '104881.74', '104861

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) == 1
    assert resp[0][0] > 0


def test_avg_price():
    # Use client without auth for public endpoint
    public_client = HTTP()
    resp = public_client.avg_price(symbol="BTCUSDT")
    # {'mins': 5, 'price': '104848.56'}

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert isinstance(resp.get("mins"), int)
    assert isinstance(resp.get("price"), str)


def test_ticker_24h():
    resp = http.ticker_24h(symbol="BTCUSDT")
    # {'symbol': 'BTCUSDT', 'priceChange': '-965.92', 'p

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert resp.get("symbol") == "BTCUSDT"
    assert isinstance(resp.get("priceChange"), str)
    assert isinstance(resp.get("priceChangePercent"), str)


def test_ticker_price():
    resp = http.ticker_price(symbol="BTCUSDT")
    # {'symbol': 'BTCUSDT', 'price': '104873.06'}

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert resp.get("symbol") == "BTCUSDT"
    assert isinstance(resp.get("price"), str)


def test_ticker_book_price():
    resp = http.ticker_book_price(symbol="BTCUSDT")
    # {'symbol': 'BTCUSDT', 'bidPrice': '104867.06', 'bi

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert resp.get("symbol") == "BTCUSDT"
    assert isinstance(resp.get("bidPrice"), str)
    assert isinstance(resp.get("bidQty"), str)
    assert isinstance(resp.get("askPrice"), str)
    assert isinstance(resp.get("askQty"), str)


def test_create_sub_account():
    resp = http.create_sub_account("test_subaccount", "test_note")
    error = {
        "code": "730601",
        "msg": "Sub-account name must be a combination of 8-32 letters and numbers",
    }

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert resp == error


def test_sub_account_list():
    resp = http.sub_account_list()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert isinstance(resp.get("subAccounts"), list)


def test_create_sub_account_api_key():
    resp = http.create_sub_account_api_key(
        sub_account="test_subaccount",
        note="test_note",
        permissions="SPOT_ACCOUNT_READ",
    )
    error = {"code": "730002", "msg": "Parameter error"}

    if PRINT_RESPONSE:
        print(str(resp))

    assert isinstance(resp, dict)
    assert resp == error


def test_query_sub_account_api_key():
    resp = http.query_sub_account_api_key(
        sub_account="test_subaccount",
    )
    error = {"code": "730002", "msg": "Parameter error"}

    if PRINT_RESPONSE:
        print(str(resp))

    assert isinstance(resp, dict)
    assert resp == error


def test_delete_sub_account_api_key():
    resp = http.delete_sub_account_api_key(
        sub_account="test_subaccount",
        api_key="test_api_key",
    )
    error = {"code": "730706", "msg": "API KEY information does not exist"}

    if PRINT_RESPONSE:
        print(str(resp))

    assert isinstance(resp, dict)
    assert resp == error


def test_universal_transfer():
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        http.universal_transfer(
            from_account_type="SPOT",
            to_account_type="SPOT",
            asset="USDT",
            amount=0.01,
        )

    if PRINT_RESPONSE:
        print(str(e.value))

    assert e.errisinstance(pymexc.base.MexcAPIError)
    # assert str(e.value) == "(code=700007): No permission to access the endpoint."
    # assert str(e.value) == "(code=700004): Param 'fromAccount' or 'toAccount' must be sent, but both were empty/null!"
    assert "(code=700004): " in str(e.value) or "(code=700007): " in str(e.value)


def test_query_universal_transfer_history():
    resp = http.query_universal_transfer_history(
        from_account_type="SPOT",
        to_account_type="SPOT",
    )

    assert isinstance(resp, dict)
    assert isinstance(resp.get("result"), list)
    assert isinstance(resp.get("totalCount"), int)


def test_sub_account_asset():
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        http.sub_account_asset(
            sub_account="test_subaccount",
            account_type="SPOT",
        )

    assert e.errisinstance(pymexc.base.MexcAPIError)
    assert str(e.value) == "(code=700004): subAccount not exist"


def test_get_kyc_status():
    resp = http.get_kyc_status()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert isinstance(resp.get("status"), str)


def test_get_uid():
    resp = http.get_uid()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "uid" in resp
    assert isinstance(resp.get("uid"), str)


def test_get_default_symbols():
    resp = http.get_default_symbols()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert isinstance(resp.get("data"), list)
    assert "BNBUSDT" in resp.get("data")
    assert resp.get("msg") == "success"


def test_test_order():
    # Test LIMIT order
    resp = http.test_order(
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
    resp = http.test_order(
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
        http.test_order(
            symbol="MXUSDT",
            side="BUY",
            order_type="LIMIT",
        )
    assert "LIMIT orders require both quantity and price" in str(e.value)

    with pytest.raises(ValueError) as e:
        http.test_order(
            symbol="MXUSDT",
            side="BUY",
            order_type="MARKET",
        )
    assert "MARKET orders require either quantity or quoteOrderQty" in str(e.value)


def test_order():
    # Test LIMIT order
    resp = http.order(
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
        http.order(
            symbol="MXUSDT",
            side="BUY",
            order_type="LIMIT",
        )
    assert "LIMIT orders require both quantity and price" in str(e.value)

    with pytest.raises(ValueError) as e:
        http.order(
            symbol="MXUSDT",
            side="BUY",
            order_type="MARKET",
        )
    assert "MARKET orders require either quantity or quoteOrderQty" in str(e.value)


def test_cancel_order():
    # First create an order
    order = http.order(
        symbol="MXUSDT",
        side="BUY",
        order_type="LIMIT",
        quantity=50,
        price=0.1,
    )

    if PRINT_RESPONSE:
        print("Created order:", str(order)[:50])

    # Then cancel it
    resp = http.cancel_order(symbol="MXUSDT", order_id=order["orderId"])

    if PRINT_RESPONSE:
        print("Cancel order response:", str(resp)[:50])

    assert isinstance(resp, dict)
    assert "orderId" in resp
    # Status could be NEW or CANCELED depending on timing
    assert resp["status"] in ["NEW", "CANCELED"]

    # Test error case - invalid order ID
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        http.cancel_order(symbol="MXUSDT", order_id="invalid_order_id")
    assert "code" in str(e.value)
    assert "Unknown order id" in str(e.value)


def test_cancel_all_open_orders():
    # First create a buy order
    order = http.order(
        symbol="MXUSDT",
        side="BUY",
        order_type="LIMIT",
        quantity=50,
        price=0.1,
    )

    if PRINT_RESPONSE:
        print("Created order:", str(order)[:50])

    # Then cancel all
    resp = http.cancel_all_open_orders(symbol="MXUSDT")

    if PRINT_RESPONSE:
        print("Cancel all orders response:", str(resp)[:50])

    assert isinstance(resp, list)
    assert all(isinstance(order, dict) for order in resp)
    for order in resp:
        assert "orderId" in order
        assert "status" in order
        assert order["status"] in ["NEW", "CANCELED"]


def test_query_order():
    # First create an order
    order = http.order(
        symbol="MXUSDT",
        side="BUY",
        order_type="LIMIT",
        quantity=50,
        price=0.1,
    )

    if PRINT_RESPONSE:
        print("Created order:", str(order)[:50])

    # Then query it
    resp = http.query_order(symbol="MXUSDT", order_id=order["orderId"])

    if PRINT_RESPONSE:
        print("Query order response:", str(resp)[:50])

    assert isinstance(resp, dict)
    assert "orderId" in resp
    assert resp["symbol"] == "MXUSDT"
    assert resp["side"] == "BUY"
    assert resp["type"] == "LIMIT"

    # Test error case - invalid order ID
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        http.query_order(symbol="MXUSDT", order_id="invalid_order_id")
    assert "code" in str(e.value)
    assert "Order does not exist" in str(e.value)


def test_current_open_orders():
    # First create a buy order
    order = http.order(
        symbol="MXUSDT",
        side="BUY",
        order_type="LIMIT",
        quantity=50,
        price=0.1,
    )

    if PRINT_RESPONSE:
        print("Created order:", str(order)[:50])

    resp = http.current_open_orders(symbol="MXUSDT")

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


def test_all_orders():
    resp = http.all_orders(symbol="MXUSDT", limit=10)

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


def test_account_information():
    resp = http.account_information()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "balances" in resp
    assert isinstance(resp["balances"], list)


def test_account_trade_list():
    resp = http.account_trade_list(symbol="MXUSDT", limit=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) <= 10
    assert all(isinstance(trade, dict) for trade in resp)


def test_enable_mx_deduct():
    # Test with invalid data
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        http.enable_mx_deduct(mx_deduct_enable=True)

    assert e.errisinstance(pymexc.base.MexcAPIError)
    # Check for either code or msg in error message
    error_str = str(e.value)
    assert any(key in error_str for key in ["code", "msg"])


def test_query_mx_deduct_status():
    resp = http.query_mx_deduct_status()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert "mxDeductEnable" in resp["data"]


def test_query_symbol_commission():
    resp = http.query_symbol_commission(symbol="MXUSDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert "makerCommission" in resp["data"]
    assert "takerCommission" in resp["data"]


def test_get_currency_info():
    resp = http.get_currency_info()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert all(isinstance(currency, dict) for currency in resp)


def test_withdraw():
    # Test with invalid data
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        http.withdraw(coin="INVALID_COIN", address="invalid_address", amount=-1)

    assert e.errisinstance(pymexc.base.MexcAPIError)
    assert "code" in str(e.value)


def test_cancel_withdraw():
    # Test with invalid data - method returns result even for invalid id
    resp = http.cancel_withdraw(id="invalid_id")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    # Method returns dict with id even for invalid withdraw id
    assert isinstance(resp, dict)
    assert "id" in resp


def test_deposit_history():
    resp = http.deposit_history(limit=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) <= 10
    assert all(isinstance(deposit, dict) for deposit in resp)


def test_withdraw_history():
    resp = http.withdraw_history(limit=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert len(resp) <= 10
    assert all(isinstance(withdraw, dict) for withdraw in resp)


def test_generate_deposit_address():
    # Test with invalid data
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        http.generate_deposit_address(coin="INVALID_COIN", network="INVALID_NETWORK")

    assert e.errisinstance(pymexc.base.MexcAPIError)
    assert "code" in str(e.value)


def test_deposit_address():
    resp = http.deposit_address(coin="USDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert all(isinstance(address, dict) for address in resp)


def test_withdraw_address():
    resp = http.withdraw_address(coin="USDT", limit=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert isinstance(resp["data"], list)
    assert len(resp["data"]) <= 10


def test_user_universal_transfer():
    # Test with invalid data
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        http.user_universal_transfer(
            from_account_type="INVALID",
            to_account_type="INVALID",
            asset="INVALID",
            amount=-1,
        )

    assert e.errisinstance(pymexc.base.MexcAPIError)
    assert "code" in str(e.value)


def test_user_universal_transfer_history():
    resp = http.user_universal_transfer_history(from_account_type="SPOT", to_account_type="SPOT", page=1, size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "rows" in resp
    assert isinstance(resp["rows"], list)


def test_user_universal_transfer_history_by_tranid():
    # Test with invalid data
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        http.user_universal_transfer_history_by_tranid(tran_id="invalid_tran_id")

    assert e.errisinstance(pymexc.base.MexcAPIError)
    assert "code" in str(e.value)


def test_get_assets_convert_into_mx():
    resp = http.get_assets_convert_into_mx()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, list)
    assert all(isinstance(asset, dict) for asset in resp)


def test_dust_transfer():
    resp = http.dust_transfer(asset="USDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "convertFee" in resp
    assert "failedList" in resp
    assert "successList" in resp


def test_dustlog():
    resp = http.dustlog(limit=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert isinstance(resp["data"], list)
    assert len(resp["data"]) <= 10


def test_internal_transfer():
    # Test with invalid data
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        http.internal_transfer(
            to_account_type="INVALID",
            to_account="invalid_account",
            asset="INVALID",
            amount=-1,
        )

    assert e.errisinstance(pymexc.base.MexcAPIError)
    assert "code" in str(e.value)


def test_internal_transfer_history():
    current_time = int(time.time() * 1000)
    one_day_ago = current_time - (24 * 60 * 60 * 1000)

    resp = http.internal_transfer_history(start_time=one_day_ago, end_time=current_time)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert isinstance(resp["data"], list)


def test_create_listen_key():
    resp = http.create_listen_key()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "listenKey" in resp


def test_keep_alive_listen_key():
    # First create a listen key
    listen_key = http.create_listen_key()["listenKey"]

    # Then keep it alive
    resp = http.keep_alive_listen_key(listen_key=listen_key)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "listenKey" in resp
    assert resp["listenKey"] == listen_key


def test_get_listen_keys():
    # First create a listen key
    listen_key = http.create_listen_key()["listenKey"]

    # Then get it
    resp = http.get_listen_keys()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "listenKey" in resp
    assert isinstance(resp["listenKey"], list)
    assert listen_key in resp["listenKey"]


def test_close_listen_key():
    # First create a listen key
    listen_key = http.create_listen_key()["listenKey"]

    # Then close it
    resp = http.close_listen_key(listen_key)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "listenKey" in resp
    assert resp["listenKey"] == listen_key


def test_get_rebate_history_records():
    resp = http.get_rebate_history_records(page=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert isinstance(resp["data"], list)


def test_get_rebate_records_detail():
    resp = http.get_rebate_records_detail(page=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert isinstance(resp["data"], list)


def test_get_self_rebate_records_detail():
    resp = http.get_self_rebate_records_detail(page=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert isinstance(resp["data"], list)


def test_query_refercode():
    resp = http.query_refercode()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "referCode" in resp


def test_affiliate_commission_record():
    resp = http.affiliate_commission_record(page=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    # Data could be None if no records
    assert resp["data"] is None or isinstance(resp["data"], list)


def test_affiliate_withdraw_record():
    resp = http.affiliate_withdraw_record(page=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    # Data could be None if no records
    assert resp["data"] is None or isinstance(resp["data"], list)


def test_affiliate_commission_detail_record():
    resp = http.affiliate_commission_detail_record(page=1)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    # Data could be None if no records
    assert resp["data"] is None or isinstance(resp["data"], list)


def test_create_stp_strategy_group():
    # Test creating STP strategy group
    group_name = f"test_group_{int(time.time())}"
    resp = http.create_stp_strategy_group(trade_group_name=group_name)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "code" in resp
    # Cleanup - delete the group if created successfully
    if resp.get("code") == 200 and "data" in resp:
        trade_group_id = resp["data"].get("tradeGroupId")
        if trade_group_id:
            try:
                http.delete_stp_strategy_group(trade_group_id=str(trade_group_id))
            except Exception:
                pass  # Ignore cleanup errors


def test_query_stp_strategy_group():
    resp = http.query_stp_strategy_group()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "code" in resp


def test_affiliate_campaign():
    resp = http.affiliate_campaign(page=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "code" in resp


def test_affiliate_referral():
    resp = http.affiliate_referral(page=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "code" in resp


def test_affiliate_subaffiliates():
    resp = http.affiliate_subaffiliates(page=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "code" in resp
