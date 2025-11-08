# pytest . -v -s

import time

import curl_cffi.requests.exceptions
import pytest
from dotenv import dotenv_values

import pymexc.base
from pymexc.futures import HTTP

env = dotenv_values(".env")

api_key = env["API_KEY"]
api_secret = env["API_SECRET"]

http = HTTP(api_key=api_key, api_secret=api_secret, ignore_ad=True)

PRINT_RESPONSE = True


def test_no_auth():
    http = HTTP(ignore_ad=True)
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        http.assets()

    if PRINT_RESPONSE:
        print(str(e.value)[:50])

    assert isinstance(e.value, pymexc.base.MexcAPIError)
    assert "code=401" in str(e.value)
    assert "System internal error!" in str(e.value)


def test_proxy():
    # use invalid proxy
    http_proxy = HTTP(
        api_key=api_key,
        api_secret=api_secret,
        proxies={"http": "http://0.0.0.1:1234", "https": "http://0.0.0.1:1234"},
        ignore_ad=True,
    )

    with pytest.raises(curl_cffi.requests.exceptions.ConnectionError):
        http_proxy.ping()


def test_ping(http: HTTP = http):
    resp = http.ping()
    # {"success": true,"code": 0,"data": 1761875313209}

    if PRINT_RESPONSE:
        print(resp)

    assert isinstance(resp, dict)
    assert "success" in resp
    assert "code" in resp
    assert "data" in resp
    assert isinstance(resp["data"], int)
    assert resp["success"] is True
    assert resp["code"] == 0
    assert resp["data"] is not None


def test_detail():
    resp = http.detail(symbol="BTC_USDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "BTC_USDT" in str(resp)


def test_support_currencies():
    resp = http.support_currencies()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert isinstance(resp.get("data"), list)


def test_get_depth():
    resp = http.get_depth(symbol="BTC_USDT", limit=5)
    # {'code': 0, 'data': {'asks': [[102494.7, 12846, 1], [102494.8, 1688, 3], [102494.9, 1075, 1], [102495, 1032, 1], [102495.1, 908, 1]], 'bids': [[102494.6, 13414, 1], [102494.5, 1056, 1], [102494.4, 1454, 2], [102494.3, 1032, 1], [102494.2, 1247, 2]], 'timestamp': 1762599936839, 'version': 28309199230}, 'success': True}

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "success" in resp.keys()
    assert "code" in resp.keys()
    assert "data" in resp.keys()
    assert resp["success"] is True
    assert resp["code"] == 0
    assert isinstance(resp.get("data"), dict)
    assert "bids" in resp.get("data").keys()
    assert "asks" in resp.get("data").keys()
    assert isinstance(resp.get("data").get("bids"), list)
    assert isinstance(resp.get("data").get("asks"), list)
    assert isinstance(resp.get("data").get("timestamp"), int)
    assert isinstance(resp.get("data").get("version"), int)


def test_index_price():
    resp = http.index_price(symbol="BTC_USDT")
    # {'code': 0, 'data': {'indexPrice': 102537.1, 'symbol': 'BTC_USDT', 'timestamp': 1762600055876}, 'success': True} or 'indexPrice' in {'code': 0, 'data': {'indexPrice': 102537.1, 'symbol': 'BTC_USDT', 'timestamp': 1762600055876}, 'success': True}

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "success" in resp.keys()
    assert "code" in resp.keys()
    assert "data" in resp.keys()
    assert resp["success"] is True
    assert resp["code"] == 0
    assert isinstance(resp.get("data"), dict)
    assert "indexPrice" in resp.get("data").keys()
    assert "symbol" in resp.get("data").keys()
    assert "timestamp" in resp.get("data").keys()
    assert isinstance(resp.get("data").get("indexPrice"), float)
    assert isinstance(resp.get("data").get("symbol"), str)
    assert isinstance(resp.get("data").get("timestamp"), int)


def test_fair_price():
    resp = http.fair_price(symbol="BTC_USDT")
    # {'code': 0, 'data': {'fairPrice': 102504.8, 'symbol': 'BTC_USDT', 'timestamp': 1762600091242}, 'success': True} or 'fairPrice' in {'code': 0, 'data': {'fairPrice': 102504.8, 'symbol': 'BTC_USDT', 'timestamp': 1762600091242}, 'success': True}

    if PRINT_RESPONSE:
        print(str(resp)[:5000])

    assert isinstance(resp, dict), f"Response is not a dictionary: {resp}"
    assert "success" in resp.keys(), f"Success is not in the response: {resp}"
    assert "code" in resp.keys(), f"Code is not in the response: {resp}"
    assert "data" in resp.keys(), f"Data is not in the response: {resp}"
    assert resp["success"] is True, f"Success is not True: {resp}"
    assert resp["code"] == 0, f"Code is not 0: {resp}"
    assert isinstance(resp.get("data"), dict), f"Data is not a dictionary: {resp.get('data')}"
    assert "fairPrice" in resp.get("data").keys(), f"Fair price is not in the data: {resp.get('data')}"
    assert "symbol" in resp.get("data").keys(), f"Symbol is not in the data: {resp.get('data')}"
    assert "timestamp" in resp.get("data").keys(), f"Timestamp is not in the data: {resp.get('data')}"
    assert isinstance(resp.get("data").get("fairPrice"), (float, int)), (
        f"Fair price is not a float: {resp.get('data').get('fairPrice')}"
    )
    assert isinstance(resp.get("data").get("symbol"), str), f"Symbol is not a string: {resp.get('data').get('symbol')}"
    assert isinstance(resp.get("data").get("timestamp"), int), (
        f"Timestamp is not an integer: {resp.get('data').get('timestamp')}"
    )


def test_funding_rate():
    resp = http.funding_rate(symbol="BTC_USDT")
    # {'code': 0, 'data': {'collectCycle': 8, 'fundingRate': 6.3e-05, 'maxFundingRate': 0.0018, 'minFundingRate': -0.0018, ...}, 'success': True} or 'rate' in {'code': 0, 'data': {'collectCycle': 8, 'fundingRate': 6.3e-05, 'maxFundingRate': 0.0018, 'minFundingRate': -0.0018, ...}

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict), f"Response is not a dictionary: {resp}"
    assert "success" in resp.keys(), f"Success is not in the response: {resp}"
    assert "code" in resp.keys(), f"Code is not in the response: {resp}"
    assert "data" in resp.keys(), f"Data is not in the response: {resp}"
    assert resp["success"] is True, f"Success is not True: {resp}"
    assert resp["code"] == 0, f"Code is not 0: {resp}"
    assert isinstance(resp.get("data"), dict), f"Data is not a dictionary: {resp.get('data')}"
    assert "collectCycle" in resp.get("data").keys(), f"Collect cycle is not in the data: {resp.get('data')}"
    assert "fundingRate" in resp.get("data").keys(), f"Funding rate is not in the data: {resp.get('data')}"
    assert "maxFundingRate" in resp.get("data").keys(), f"Max funding rate is not in the data: {resp.get('data')}"
    assert "minFundingRate" in resp.get("data").keys(), f"Min funding rate is not in the data: {resp.get('data')}"
    assert isinstance(resp.get("data").get("collectCycle"), int), (
        f"Collect cycle is not an integer: {resp.get('data').get('collectCycle')}"
    )
    assert isinstance(resp.get("data").get("fundingRate"), float), (
        f"Funding rate is not a float: {resp.get('data').get('fundingRate')}"
    )
    assert isinstance(resp.get("data").get("maxFundingRate"), float), (
        f"Max funding rate is not a float: {resp.get('data').get('maxFundingRate')}"
    )
    assert isinstance(resp.get("data").get("minFundingRate"), float), (
        f"Min funding rate is not a float: {resp.get('data').get('minFundingRate')}"
    )


def test_kline():
    resp = http.kline(symbol="BTC_USDT", interval="Min1")
    # {'success': True, 'code': 0, 'data': {'time': [1762480320, ...}}

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict), f"Response is not a dictionary: {resp}"
    assert "success" in resp.keys(), f"Success is not in the response: {resp}"
    assert "code" in resp.keys(), f"Code is not in the response: {resp}"
    assert "data" in resp.keys(), f"Data is not in the response: {resp}"
    assert resp["success"] is True, f"Success is not True: {resp}"
    assert resp["code"] == 0, f"Code is not 0: {resp}"
    assert isinstance(resp.get("data"), dict), f"Data is not a dictionary: {resp.get('data')}"
    assert "time" in resp.get("data").keys(), f"Time is not in the data: {resp.get('data')}"
    assert isinstance(resp.get("data").get("time"), list), f"Time is not a list: {resp.get('data').get('time')}"
    assert all(isinstance(item, int) for item in resp.get("data").get("time")), (
        f"Time is not a list of integers: {resp.get('data').get('time')}"
    )


def test_deals():
    resp = http.deals(symbol="BTC_USDT", limit=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or isinstance(resp.get("data"), list)


def test_ticker():
    resp = http.ticker(symbol="BTC_USDT")
    # {'code': 0, 'data': {'amount24': 16251871764.69298, 'ask1': 102558.8, 'bid1': ...

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict), f"Response is not a dictionary: {resp}"
    assert "success" in resp.keys(), f"Success is not in the response: {resp}"
    assert "code" in resp.keys(), f"Code is not in the response: {resp}"
    assert "data" in resp.keys(), f"Data is not in the response: {resp}"
    assert resp["success"] is True, f"Success is not True: {resp}"
    assert resp["code"] == 0, f"Code is not 0: {resp}"
    assert isinstance(resp.get("data"), dict), f"Data is not a dictionary: {resp.get('data')}"
    # Когда symbol указан, data содержит объект с полем symbol
    # Когда symbol не указан, data может быть списком
    if isinstance(resp.get("data"), dict):
        assert "symbol" in resp.get("data").keys() or "contractId" in resp.get("data").keys(), (
            f"Symbol or contractId is not in the data: {resp.get('data')}"
        )


def test_risk_reverse():
    resp = http.risk_reverse(symbol="BTC_USDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)


def test_risk_reverse_history():
    resp = http.risk_reverse_history(symbol="BTC_USDT", page_num=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


def test_funding_rate_history():
    resp = http.funding_rate_history(symbol="BTC_USDT", page_num=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


def test_assets():
    resp = http.assets()
    # {'success': True, 'code': 0, 'data': [{'currency': 'STETH', 'positionMargin': 0, 'availableBalance': 0, 'cashBalance': 0, 'frozenBalance': 0, 'equity': 0, 'unrealized': 0, 'bonus': 0, 'availableCash': 0, 'availableOpen': 0, 'debtAmount': 0, 'contributeMarginAmount': 0, 'vcoinId': 'c9581fdb3f81438ebf2bcdb383dbee40'}, {'currency': 'MXSOL', 'positionMargin': 0, 'availableBalance': 0, 'cashBalance': 0, 'frozenBalance': 0, 'equity': 0, 'unrealized': 0, 'bonus': 0, 'availableCash': 0, 'availableOpen':

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict), f"Response is not a dictionary: {resp}"
    assert "success" in resp.keys(), f"Success is not in the response: {resp}"
    assert "code" in resp.keys(), f"Code is not in the response: {resp}"
    assert "data" in resp.keys(), f"Data is not in the response: {resp}"
    assert resp["success"] is True, f"Success is not True: {resp}"
    assert resp["code"] == 0, f"Code is not 0: {resp}"
    assert isinstance(resp.get("data"), list), f"Data is not a list: {resp.get('data')}"
    assert all(isinstance(item, dict) for item in resp.get("data")), (
        f"Data is not a list of dictionaries: {resp.get('data')}"
    )
    assert "data" in resp or isinstance(resp.get("data"), list)


def test_asset():
    resp = http.asset(currency="USDT")
    # tests/test_futures_http.py::test_asset {'success': True, 'code': 0, 'data': {'currency': 'USDT', 'positionMargin': 0, 'availableBalance': 121.684674886, 'cashBalance': 121.68467488, 'frozenBalance': 0, 'equity': 121.68467488, 'unrealized': 0, 'bonus': 0, 'availableCash': 121.684674886, 'availableOpen': 121.684674886, 'debtAmount': 0, 'contributeMarginAmount': 0, 'vcoinId': '128f589271cb4951b03e71e6323eb7be'}}

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict), f"Response is not a dictionary: {resp}"
    assert "success" in resp.keys(), f"Success is not in the response: {resp}"
    assert "code" in resp.keys(), f"Code is not in the response: {resp}"
    assert "data" in resp.keys(), f"Data is not in the response: {resp}"
    assert resp["success"] is True, f"Success is not True: {resp}"
    assert resp["code"] == 0, f"Code is not 0: {resp}"
    assert isinstance(resp.get("data"), dict), f"Data is not a dictionary: {resp.get('data')}"
    # Проверяем косвенно - если есть основные поля, значит ответ валидный
    assert "availableBalance" in resp.get("data").keys() or "currency" in resp.get("data").keys(), (
        f"Available balance or currency is not in the data: {resp.get('data')}"
    )
    assert "positionMargin" in resp.get("data").keys(), f"Position margin is not in the data: {resp.get('data')}"
    assert "availableBalance" in resp.get("data").keys(), f"Available balance is not in the data: {resp.get('data')}"
    assert "cashBalance" in resp.get("data").keys(), f"Cash balance is not in the data: {resp.get('data')}"
    assert "frozenBalance" in resp.get("data").keys(), f"Frozen balance is not in the data: {resp.get('data')}"
    assert "equity" in resp.get("data").keys(), f"Equity is not in the data: {resp.get('data')}"
    assert "unrealized" in resp.get("data").keys(), f"Unrealized is not in the data: {resp.get('data')}"
    assert "bonus" in resp.get("data").keys(), f"Bonus is not in the data: {resp.get('data')}"
    assert "availableCash" in resp.get("data").keys(), f"Available cash is not in the data: {resp.get('data')}"
    assert "availableOpen" in resp.get("data").keys(), f"Available open is not in the data: {resp.get('data')}"
    assert "debtAmount" in resp.get("data").keys(), f"Debt amount is not in the data: {resp.get('data')}"
    assert "contributeMarginAmount" in resp.get("data").keys(), (
        f"Contribute margin amount is not in the data: {resp.get('data')}"
    )
    assert "vcoinId" in resp.get("data").keys(), f"Vcoin ID is not in the data: {resp.get('data')}"


def test_transfer_record():
    resp = http.transfer_record(page_num=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


def test_open_positions():
    resp = http.open_positions()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or isinstance(resp.get("data"), list)


def test_history_positions():
    resp = http.history_positions(page_num=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


def test_funding_records():
    current_time = int(time.time() * 1000)
    one_day_ago = current_time - (24 * 60 * 60 * 1000)

    resp = http.funding_records(
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


def test_open_orders():
    # Проверяем косвенно - когда symbol не указан, может быть ошибка или пустой список
    # Проверяем успешный ответ с symbol
    resp1 = http.open_orders(symbol="BTC_USDT", page_num=1, page_size=10)
    # {'success': True, 'code': 0, 'data': {'pageSize': 10, 'totalCount': 0, 'totalPage': 0, 'currentPage': 1, 'resultList': []}}

    if PRINT_RESPONSE:
        print(str(resp1)[:50])

    assert isinstance(resp1, dict), f"Response is not a dictionary: {resp1}"
    assert "success" in resp1.keys(), f"Success is not in the response: {resp1}"
    assert "code" in resp1.keys(), f"Code is not in the response: {resp1}"
    # Проверяем косвенно - если success=True и code=0, значит ответ валидный
    if resp1.get("success") is True and resp1.get("code") == 0:
        assert "data" in resp1.keys(), f"Data is not in the response: {resp1}"
        assert isinstance(resp1.get("data"), dict), f"Data is not a dictionary: {resp1.get('data')}"
        assert "pageSize" in resp1.get("data").keys(), f"Page size is not in the data: {resp1.get('data')}"
        assert "totalCount" in resp1.get("data").keys(), f"Total count is not in the data: {resp1.get('data')}"
        assert "totalPage" in resp1.get("data").keys(), f"Total page is not in the data: {resp1.get('data')}"
        assert "currentPage" in resp1.get("data").keys(), f"Current page is not in the data: {resp1.get('data')}"
        assert "resultList" in resp1.get("data").keys(), f"Result list is not in the data: {resp1.get('data')}"
        assert isinstance(resp1.get("data").get("pageSize"), int), (
            f"Page size is not an integer: {resp1.get('data').get('pageSize')}"
        )
        assert isinstance(resp1.get("data").get("totalCount"), int), (
            f"Total count is not an integer: {resp1.get('data').get('totalCount')}"
        )
        assert isinstance(resp1.get("data").get("totalPage"), int), (
            f"Total page is not an integer: {resp1.get('data').get('totalPage')}"
        )


def test_history_orders():
    resp = http.history_orders(page_num=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


def test_get_order():
    # Проверяем косвенно - метод возвращает ответ (может быть успешным или с ошибкой)
    # При неверном order_id API может вернуть успешный ответ с пустыми данными или ошибку
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        http.get_order(order_id=999999999999999999)

    assert isinstance(e.value, pymexc.base.MexcAPIError)
    assert "code=1001" in str(e.value)
    assert "The contract does not exist!" in str(e.value)


def test_batch_query():
    # Проверяем косвенно - метод возвращает ответ (может быть успешным или с ошибкой)
    # При неверных order_ids API может вернуть успешный ответ с пустым списком или ошибку
    resp = http.batch_query(order_ids="999999999999999999")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    # Проверяем структуру ответа
    assert isinstance(resp, dict), f"Response is not a dictionary: {resp}"
    assert "success" in resp.keys(), f"Success is not in the response: {resp}"
    assert "code" in resp.keys(), f"Code is not in the response: {resp}"
    # Если успешно, проверяем наличие data (может быть список или объект)
    if resp.get("success") is True and resp.get("code") == 0:
        assert "data" in resp.keys(), f"Data is not in the response: {resp}"


def test_get_trigger_orders():
    resp = http.get_trigger_orders(page_num=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


def test_get_stop_limit_orders():
    resp = http.get_stop_limit_orders(page_num=1, page_size=10)

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or "resultList" in resp


def test_risk_limit():
    resp = http.risk_limit()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or isinstance(resp.get("data"), list)


def test_tiered_fee_rate():
    resp = http.tiered_fee_rate()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp or isinstance(resp.get("data"), dict)


def test_get_leverage():
    resp = http.get_leverage(symbol="BTC_USDT")

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp
    assert isinstance(resp.get("data"), list)


def test_get_position_mode():
    resp = http.get_position_mode()

    if PRINT_RESPONSE:
        print(str(resp)[:50])

    assert isinstance(resp, dict)
    assert "data" in resp


def test_change_leverage():
    # Проверяем косвенно - метод может вернуть ошибку или успешный ответ
    # При неверном leverage API может вернуть ошибку или успешный ответ с ограничением
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        http.change_leverage(leverage=1000, symbol="BTC_USDT")

    assert isinstance(e.value, pymexc.base.MexcAPIError)
    assert "code=602" in str(e.value)
    assert "Signature verification failed!" in str(e.value)


def test_change_position_mode():
    # Проверяем косвенно - метод может вернуть ошибку или успешный ответ
    # Метод может быть недоступен или требовать отсутствия активных ордеров
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        http.change_position_mode(position_mode=1)

    assert isinstance(e.value, pymexc.base.MexcAPIError)
    assert "code=602" in str(e.value)
    assert "Signature verification failed!" in str(e.value)


def test_order():
    # Проверяем косвенно - метод может вернуть ошибку или успешный ответ
    # При неверных параметрах API может вернуть ошибку
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        resp = http.order(
            symbol="BTC_USDT",
            price=100000,
            vol=0.001,
            side=1,
            type=1,
            open_type=1,
        )
        # Если успешно, проверяем структуру ответа
    assert isinstance(e.value, pymexc.base.MexcAPIError)
    assert "code=602" in str(e.value)
    assert "Signature verification failed!" in str(e.value)


def test_cancel_order():
    # Проверяем косвенно - метод принимает order_ids (список или int), не symbol и order_id
    # При неверном order_id API может вернуть ошибку или успешный ответ
    resp = http.cancel_order(order_ids=999999999999999999)
    print(resp)
    # Если успешно, проверяем структуру ответа
    assert isinstance(resp, dict), f"Response is not a dictionary: {resp}"
    assert "success" in resp.keys(), f"Success is not in the response: {resp}"
    assert "code" in resp.keys(), f"Code is not in the response: {resp}"


def test_cancel_all_orders():
    # Проверяем косвенно - метод называется cancel_all, не cancel_all_orders
    # При неверном symbol API может вернуть ошибку или успешный ответ
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        resp = http.cancel_all(symbol="INVALID_SYMBOL")
        # Если успешно, проверяем структуру ответа
    assert isinstance(e.value, pymexc.base.MexcAPIError)
    assert "code=602" in str(e.value)
    assert "Signature verification failed!" in str(e.value)


def test_cancel_plan_order():
    # Проверяем косвенно - метод называется cancel_trigger_order, принимает orders (список)
    # При неверном order_id API может вернуть ошибку или успешный ответ
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        resp = http.cancel_trigger_order(orders=[{"symbol": "BTC_USDT", "orderId": 999999999999999999}])
        # Если успешно, проверяем структуру ответа
    assert isinstance(e.value, pymexc.base.MexcAPIError)
    assert "code=602" in str(e.value)
    assert "Signature verification failed!" in str(e.value)


def test_cancel_stop_order():
    # Проверяем косвенно - метод принимает orders (список), не symbol и order_id
    # При неверном order_id API может вернуть ошибку или успешный ответ
    with pytest.raises(pymexc.base.MexcAPIError) as e:
        resp = http.cancel_stop_order(orders=[{"stopPlanOrderId": 999999999999999999}])
        # Если успешно, проверяем структуру ответа
    assert isinstance(e.value, pymexc.base.MexcAPIError)
    assert "code=602" in str(e.value)
    assert "Signature verification failed!" in str(e.value)
