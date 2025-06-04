from re import sub
import re
from dotenv import dotenv_values
import pytest
from unittest.mock import patch

import curl_cffi.requests.exceptions
import pymexc.base

from pymexc.spot import HTTP


env = dotenv_values(".env")

api_key = env["API_KEY"]
api_secret = env["API_SECRET"]

http = HTTP(api_key=api_key, api_secret=api_secret)

PRINT_RESPONSE = True


# def test_no_auth():
#     assert test_exchange_info(HTTP()) is None
#
#
# def test_wrong_api_key():
#     http = HTTP(api_key="wrong_api_key", api_secret="wrong_api_secret")
#     with pytest.raises(pymexc.base.MexcAPIError):
#         http.exchange_info()
#
#
# def test_proxy():
#     # use invalid proxy
#     http_proxy = HTTP(
#         api_key=api_key,
#         api_secret=api_secret,
#         proxies={"http": "http://0.0.0.1:1234", "https": "http://0.0.0.1:1234"},
#     )
#
#     with pytest.raises(curl_cffi.requests.exceptions.ConnectionError):
#         http_proxy.ping()
#
#
# def test_ping():
#     assert http.ping() == {}
#
#
# def test_time():
#     resp = http.time()
#     # {'serverTime': 1749076765439}
#
#     if PRINT_RESPONSE:
#         print(resp)
#
#     assert isinstance(resp, dict)
#     assert resp.get("serverTime") > 0
#     assert isinstance(resp.get("serverTime"), int)
#
#
# def test_default_symbols():
#     resp = http.default_symbols()
#     # {'data': ['SNTUSDT', 'CGPTUSDT', 'SHOOTUSDT', 'WEF
#
#     if PRINT_RESPONSE:
#         print(str(resp)[:50])
#
#     assert isinstance(resp, dict)
#     assert isinstance(resp.get("data"), list)
#     assert "BNBUSDT" in resp.get("data")
#     assert resp.get("msg") == "success"
#
#
# def test_exchange_info(http: HTTP = http):
#     resp = http.exchange_info(symbol="BTCUSDT")
#     # {'timezone': 'CST', 'serverTime': 1749076852582, '
#
#     if PRINT_RESPONSE:
#         print(str(resp)[:50])
#
#     assert isinstance(resp, dict)
#     assert "BTCUSDT" in str(resp)
#
#
# def test_order_book():
#     resp = http.order_book(symbol="BTCUSDT", limit=1)
#     # {'lastUpdateId': 42154878994, 'bids': [['104864.01
#
#     if PRINT_RESPONSE:
#         print(str(resp)[:50])
#
#     assert isinstance(resp, dict)
#     assert "bids" in resp.keys()
#     assert "asks" in resp.keys()
#     assert len(resp.get("asks")) == 1
#     assert resp.get("timestamp") > 0
#
#
# def test_trades():
#     resp = http.trades(symbol="BTCUSDT", limit=1)
#     # [{'id': None, 'price': '104864.01', 'qty': '0.0001
#
#     if PRINT_RESPONSE:
#         print(str(resp)[:50])
#
#     assert isinstance(resp, list)
#     assert len(resp) == 1
#
#
# def test_agg_trades():
#     _time = 1749076263000
#     resp = http.agg_trades(symbol="BTCUSDT", limit=1, start_time=_time, end_time=_time)
#     # [{'a': None, 'f': None, 'l': None, 'p': '104821.27
#
#     if PRINT_RESPONSE:
#         print(str(resp)[:50])
#
#     assert isinstance(resp, list)
#     assert len(resp) == 1
#     assert resp[0].get("T") == _time
#
#
# def test_klines():
#     resp = http.klines(symbol="BTCUSDT", interval="1m", limit=1)
#     # [[1749076800000, '104861.97', '104881.74', '104861
#
#     if PRINT_RESPONSE:
#         print(str(resp)[:50])
#
#     assert isinstance(resp, list)
#     assert len(resp) == 1
#     assert resp[0][0] > 0
#
#
# def test_avg_price():
#     resp = http.avg_price(symbol="BTCUSDT")
#     # {'mins': 5, 'price': '104848.56'}
#
#     if PRINT_RESPONSE:
#         print(str(resp)[:50])
#
#     assert isinstance(resp, dict)
#     assert isinstance(resp.get("mins"), int)
#     assert isinstance(resp.get("price"), str)
#
#
# def test_ticker_24h():
#     resp = http.ticker_24h(symbol="BTCUSDT")
#     # {'symbol': 'BTCUSDT', 'priceChange': '-965.92', 'p
#
#     if PRINT_RESPONSE:
#         print(str(resp)[:50])
#
#     assert isinstance(resp, dict)
#     assert resp.get("symbol") == "BTCUSDT"
#     assert isinstance(resp.get("priceChange"), str)
#     assert isinstance(resp.get("priceChangePercent"), str)
#
#
# def test_ticker_price():
#     resp = http.ticker_price(symbol="BTCUSDT")
#     # {'symbol': 'BTCUSDT', 'price': '104873.06'}
#
#     if PRINT_RESPONSE:
#         print(str(resp)[:50])
#
#     assert isinstance(resp, dict)
#     assert resp.get("symbol") == "BTCUSDT"
#     assert isinstance(resp.get("price"), str)
#
#
# def test_ticker_book_price():
#     resp = http.ticker_book_price(symbol="BTCUSDT")
#     # {'symbol': 'BTCUSDT', 'bidPrice': '104867.06', 'bi
#
#     if PRINT_RESPONSE:
#         print(str(resp)[:50])
#
#     assert isinstance(resp, dict)
#     assert resp.get("symbol") == "BTCUSDT"
#     assert isinstance(resp.get("bidPrice"), str)
#     assert isinstance(resp.get("bidQty"), str)
#     assert isinstance(resp.get("askPrice"), str)
#     assert isinstance(resp.get("askQty"), str)
#
#
# def test_create_sub_account():
#     resp = http.create_sub_account("test_subaccount", "test_note")
#     error = {
#         "code": "730601",
#         "msg": "Sub-account name must be a combination of 8-32 letters and numbers",
#     }
#
#     if PRINT_RESPONSE:
#         print(str(resp)[:50])
#
#     assert isinstance(resp, dict)
#     assert resp == error
#
#
# def test_sub_account_list():
#     resp = http.sub_account_list()
#
#     if PRINT_RESPONSE:
#         print(str(resp)[:50])
#
#     assert isinstance(resp, dict)
#     assert isinstance(resp.get("subAccounts"), list)
#
#
# def test_create_sub_account_api_key():
#     resp = http.create_sub_account_api_key(
#         sub_account="test_subaccount",
#         note="test_note",
#         permissions="SPOT_ACCOUNT_READ",
#     )
#     error = {"code": "730002", "msg": "Parameter error"}
#
#     if PRINT_RESPONSE:
#         print(str(resp))
#
#     assert isinstance(resp, dict)
#     assert resp == error
#
#
# def test_query_sub_account_api_key():
#     resp = http.query_sub_account_api_key(
#         sub_account="test_subaccount",
#     )
#     error = {"code": "730002", "msg": "Parameter error"}
#
#     if PRINT_RESPONSE:
#         print(str(resp))
#
#     assert isinstance(resp, dict)
#     assert resp == error
#
#
# def test_delete_sub_account_api_key():
#     resp = http.delete_sub_account_api_key(
#         sub_account="test_subaccount",
#         api_key="test_api_key",
#     )
#     error = {"code": "730706", "msg": "API KEY information does not exist"}
#
#     if PRINT_RESPONSE:
#         print(str(resp))
#
#     assert isinstance(resp, dict)
#     assert resp == error
#
#
# def test_universal_transfer():
#   with pytest.raises(pymexc.base.MexcAPIError) as e:
#       http.universal_transfer(
#           from_account_type="SPOT",
#           to_account_type="SPOT",
#           asset="USDT",
#           amount=0.01,
#       )
#
#   assert e.errisinstance(pymexc.base.MexcAPIError)
#   assert str(e.value) == "(code=700007): No permission to access the endpoint."
#
#
#
#
# def test_query_universal_transfer_history():
#     resp = http.query_universal_transfer_history(
#         from_account_type="SPOT",
#         to_account_type="SPOT",
#     )
#
#     assert isinstance(resp, dict)
#     assert isinstance(resp.get("result"), list)
#     assert isinstance(resp.get("totalCount"), int)
#
#
# def test_sub_account_asset():
#     with pytest.raises(pymexc.base.MexcAPIError) as e:
#         http.sub_account_asset(
#             sub_account="test_subaccount",
#             account_type="SPOT",
#         )
#
#     assert e.errisinstance(pymexc.base.MexcAPIError)
#     assert str(e.value) == "(code=700004): subAccount not exist"
#
#
# def test_get_kyc_status():
#     resp = http.get_kyc_status()
#
#     if PRINT_RESPONSE:
#         print(str(resp)[:50])
#
#     assert isinstance(resp, dict)
#     assert isinstance(resp.get("status"), str)
#
#
# def test_get_default_symbols():
#     resp = http.get_default_symbols()
#
#     if PRINT_RESPONSE:
#         print(str(resp)[:50])
#
#     assert isinstance(resp, dict)
#     assert isinstance(resp.get("data"), list)
#     assert "BNBUSDT" in resp.get("data")
#     assert resp.get("msg") == "success"
#
#
# def test_test_order():
#     resp = http.test_order(
#         symbol="MXUSDT",
#         side="BUY",
#         order_type="LIMIT",
#         quantity=50,
#         price=0.1,
#     )
#
#     if PRINT_RESPONSE:
#         print(str(resp)[:50])
#
#     assert isinstance(resp, dict)
#     assert resp == {}
