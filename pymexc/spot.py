"""
### Spot API
Documentation: https://mexcdevelop.github.io/apidocs/spot_v3_en/#introduction

### Usage

```python
from pymexc import spot

api_key = "YOUR API KEY"
api_secret = "YOUR API SECRET KEY"

def handle_message(message):
    # handle websocket message
    print(message)

# initialize HTTP client
spot_client = spot.HTTP(api_key = api_key, api_secret = api_secret)
# initialize WebSocket client
ws_spot_client = spot.WebSocket(api_key = api_key, api_secret = api_secret)

# make http request to api
print(spot_client.exchange_info())

# create websocket connection to public channel (spot@public.deals.v3.api@BTCUSDT)
# all messages will be handled by function `handle_message`
ws_spot_client.deals_stream(handle_message, "BTCUSDT")

# loop forever for save websocket connection
while True:
    ...

"""

import logging
import threading
import time
from typing import Callable, List, Literal, Optional, Union
import warnings
import json
from enum import Enum

logger = logging.getLogger(__name__)

try:
    from _async.spot import HTTP as AsyncHTTP
    from _async.spot import WebSocket as AsyncWebSocket
    from base import _SpotHTTP
    from base_websocket import _SpotWebSocket
    from proto import ProtoTyping
except ImportError:
    from ._async.spot import HTTP as AsyncHTTP
    from ._async.spot import WebSocket as AsyncWebSocket
    from .base import _SpotHTTP
    from .base_websocket import _SpotWebSocket
    from .proto import ProtoTyping

__all__ = ["HTTP", "WebSocket", "AsyncHTTP", "AsyncWebSocket"]


class Timezone(str, Enum):
    """Valid timezone values for miniTicker and miniTickers streams"""
    H24 = "24H"
    UTC_M10 = "UTC-10"
    UTC_M8 = "UTC-8"
    UTC_M7 = "UTC-7"
    UTC_M6 = "UTC-6"
    UTC_M5 = "UTC-5"
    UTC_M4 = "UTC-4"
    UTC_M3 = "UTC-3"
    UTC_0 = "UTC+0"
    UTC_1 = "UTC+1"
    UTC_2 = "UTC+2"
    UTC_3 = "UTC+3"
    UTC_4 = "UTC+4"
    UTC_4_30 = "UTC+4:30"
    UTC_5 = "UTC+5"
    UTC_5_30 = "UTC+5:30"
    UTC_6 = "UTC+6"
    UTC_7 = "UTC+7"
    UTC_8 = "UTC+8"
    UTC_9 = "UTC+9"
    UTC_10 = "UTC+10"
    UTC_11 = "UTC+11"
    UTC_12 = "UTC+12"
    UTC_12_45 = "UTC+12:45"
    UTC_13 = "UTC+13"

VALID_TIMEZONES = {tz.value for tz in Timezone}


class HTTP(_SpotHTTP):
    # <=================================================================>
    #
    #                       Market Data Endpoints
    #
    # <=================================================================>

    def ping(self) -> dict:
        """
        ### Test connectivity to the Rest API.

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#test-connectivity
        """
        return self.call("GET", "/api/v3/ping", auth=False)

    def time(self) -> dict:
        """
        ### Check Server Time

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#check-server-time
        """
        return self.call("GET", "/api/v3/time", auth=False)

    def default_symbols(self) -> dict:
        """
        ### API default symbol

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#api-default-symbol
        """
        return self.call("GET", "/api/v3/defaultSymbols", auth=False)

    def exchange_info(self, symbol: Optional[str] = None, symbols: Optional[List[str]] = None) -> dict:
        """
        ### Exchange Information

        Current exchange trading rules and symbol information

        Weight(IP): 10

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#exchange-information

        :param symbol: (optional) The symbol for a specific trading pair.
        :type symbol: str
        :param symbols: (optional) List of symbols to get information for.
        :type symbols: List[str]
        :return: The response from the API containing trading pair information.
        :rtype: dict
        """

        return self.call(
            "GET",
            "/api/v3/exchangeInfo",
            params=dict(symbol=symbol, symbols=",".join(symbols) if symbols else None),
            auth=False,
        )

    def order_book(self, symbol: str, limit: Optional[int] = 100) -> dict:
        """
        ### Order Book

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#order-book

        :param symbol: A string representing the trading pair symbol, e.g. "BTCUSDT".
        :type symbol: str
        :param limit: An integer representing the number of order book levels to retrieve. Defaults to 100. Max is 5000.
        :type limit: int

        :return: The order book data in JSON format.
        :rtype: dict
        """
        return self.call("GET", "/api/v3/depth", params=dict(symbol=symbol, limit=limit), auth=False)

    def trades(self, symbol: str, limit: Optional[int] = 500) -> list:
        """
        ### Recent Trades List

        Weight(IP): 5

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#recent-trades-list

        :param symbol: A string representing the trading pair symbol.
        :type symbol: str
        :param limit: An optional integer representing the maximum number of trades to retrieve. Defaults to 500. Max is 5000.
        :type limit: int

        :return: A dictionary containing information about the trades.
        :rtype: dict
        """

        return self.call("GET", "/api/v3/trades", params=dict(symbol=symbol, limit=limit), auth=False)

    def agg_trades(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: Optional[int] = 500,
    ) -> list:
        """
        ### Compressed/Aggregate Trades List

        Get compressed, aggregate trades. Trades that fill at the time, from the same order, with the same price will have the quantity aggregated.

        startTime and endTime must be used at the same time.

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#compressed-aggregate-trades-list

        :param symbol: The symbol to retrieve trades for.
        :type symbol: str
        :param start_time: (optional) Timestamp in ms to get aggregate trades from INCLUSIVE.
        :type start_time: int
        :param end_time: (optional) Timestamp in ms to get aggregate trades until INCLUSIVE.
        :type end_time: int
        :param limit: (optional) The maximum number of trades to retrieve. Default is 500. Max is 5000.
        :type limit: int

        :return: A dictionary containing the retrieved trades.
        :rtype: dict
        """
        return self.call(
            "GET",
            "/api/v3/aggTrades",
            params=dict(symbol=symbol, startTime=start_time, endTime=end_time, limit=limit),
            auth=False,
        )

    def klines(
        self,
        symbol: str,
        interval: Literal["1m", "5m", "15m", "30m", "60m", "4h", "1d", "1M"] = "1m",
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: Optional[int] = 500,
    ) -> list:
        """
        ### Kline/Candlestick Data

        Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time.

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#kline-candlestick-data

        :param symbol: The symbol to retrieve trades for.
        :type symbol: str
        :param interval: The interval for the kline.
        :type interval: ENUM_Kline
        :param start_time: (optional) Timestamp in ms to get aggregate trades from INCLUSIVE.
        :type start_time: int
        :param end_time: (optional) Timestamp in ms to get aggregate trades until INCLUSIVE.
        :type end_time: int
        :param limit: (optional) The maximum number of trades to retrieve. Default is 500. Max is 5000.
        :type limit: int

        :return: A dictionary containing the klines.
        :rtype: dict
        """
        return self.call(
            "GET",
            "/api/v3/klines",
            params=dict(
                symbol=symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
            auth=True,
        )

    def avg_price(self, symbol: str):
        """
        ### Current Average Price

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#current-average-price

        :param symbol: The symbol.
        :type symbol: str

        :return: A dictionary containing average price.
        :rtype: dict
        """
        return self.call("GET", "/api/v3/avgPrice", params=dict(symbol=symbol), auth=True)

    def ticker_24h(self, symbol: Optional[str] = None):
        """
        ### 24hr Ticker Price Change Statistics

        Weight(IP): 1 - 1 symbol;
        Weight(IP): 40 - all symbols;

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#24hr-ticker-price-change-statistics

        :param symbol: (optional) If the symbol is not sent, tickers for all symbols will be returned in an array.
        :type symbol: str

        :return: A dictionary.
        :rtype: dict
        """
        return self.call("GET", "/api/v3/ticker/24hr", params=dict(symbol=symbol), auth=False)

    def ticker_price(self, symbol: Optional[str] = None):
        """
        ### Symbol Price Ticker

        Weight(IP): 1 - 1 symbol;
        Weight(IP): 2 - all symbols;

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#symbol-price-ticker

        :param symbol: (optional) If the symbol is not sent, all symbols will be returned in an array.
        :type symbol: str

        :return: A dictionary.
        :rtype: dict
        """
        return self.call("GET", "/api/v3/ticker/price", params=dict(symbol=symbol), auth=False)

    def ticker_book_price(self, symbol: Optional[str] = None):
        """
        ### Symbol Price Ticker

        Best price/qty on the order book for a symbol or symbols.

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#symbol-order-book-ticker

        :param symbol: (optional) If the symbol is not sent, all symbols will be returned in an array.
        :type symbol: str

        :return: A dictionary.
        :rtype: dict
        """
        return self.call("GET", "/api/v3/ticker/bookTicker", params=dict(symbol=symbol), auth=False)

    # <=================================================================>
    #
    #                       Sub-Account Endpoints
    #
    # <=================================================================>

    def create_sub_account(self, sub_account: str, note: str) -> dict:
        """
        ### Create a sub-account from the master account.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#create-a-sub-account-for-master-account

        :param sub_account: Sub-account Name
        :type sub_account: str
        :param note: Sub-account notes
        :type note: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "POST",
            "api/v3/sub-account/virtualSubAccount",
            params=dict(subAccount=sub_account, note=note),
        )

    def sub_account_list(
        self,
        sub_account: Optional[str] = None,
        is_freeze: Optional[bool] = None,
        page: Optional[int] = 1,
        limit: Optional[int] = 10,
    ) -> dict:
        """
        ### Get details of the sub-account list.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-sub-account-list-for-master-account

        :param sub_account: (optional) Sub-account Name
        :type sub_account: str
        :param is_freeze: (optional) true or false
        :type is_freeze: bool
        :param page: (optional) Default value: 1
        :type page: int
        :param limit: (optional) Default value: 10, Max value: 200
        :type limit: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "api/v3/sub-account/list",
            params=dict(subAccount=sub_account, isFreeze=is_freeze, page=page, limit=limit),
        )

    def create_sub_account_api_key(
        self,
        sub_account: str,
        note: str,
        permissions: Union[
            str,
            List[
                Literal[
                    "SPOT_ACCOUNT_READ",
                    "SPOT_ACCOUNT_WRITE",
                    "SPOT_DEAL_READ",
                    "SPOT_DEAL_WRITE",
                    "CONTRACT_ACCOUNT_READ",
                    "CONTRACT_ACCOUNT_WRITE",
                    "CONTRACT_DEAL_READ",
                    "CONTRACT_DEAL_WRITE",
                    "SPOT_TRANSFER_READ",
                    "SPOT_TRANSFER_WRITE",
                ]
            ],
        ],
        ip: Optional[str] = None,
    ) -> dict:
        """
        ### Create an APIKey for a sub-account.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#create-an-apikey-for-a-sub-account-for-master-account

        :param sub_account: Sub-account Name
        :type sub_account: str
        :param note: APIKey note
        :type note: str
        :param permissions: Permission of APIKey: SPOT_ACCOUNT_READ, SPOT_ACCOUNT_WRITE, SPOT_DEAL_READ, SPOT_DEAL_WRITE, CONTRACT_ACCOUNT_READ, CONTRACT_ACCOUNT_WRITE, CONTRACT_DEAL_READ, CONTRACT_DEAL_WRITE, SPOT_TRANSFER_READ, SPOT_TRANSFER_WRITE
        :type permissions: list
        :param ip: (optional) Link IP addresses, separate with commas if more than one. Support up to 20 addresses.
        :type ip: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "POST",
            "api/v3/sub-account/apiKey",
            params=dict(
                subAccount=sub_account,
                note=note,
                permissions=",".join(permissions) if isinstance(permissions, list) else permissions,
                ip=ip,
            ),
        )

    def query_sub_account_api_key(self, sub_account: str) -> dict:
        """
        ### Query the APIKey of a sub-account.
        #### Applies to master accounts only
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-the-apikey-of-a-sub-account-for-master-account

        :param sub_account: Sub-account Name
        :type sub_account: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/sub-account/apiKey", params=dict(subAccount=sub_account))

    def delete_sub_account_api_key(self, sub_account: str, api_key: str) -> dict:
        """
        ### Delete the APIKey of a sub-account.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#delete-the-apikey-of-a-sub-account-for-master-account

        :param sub_account: Sub-account Name
        :type sub_account: str
        :param api_key: API public key
        :type api_key: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "DELETE",
            "api/v3/sub-account/apiKey",
            params=dict(subAccount=sub_account, apiKey=api_key),
        )

    def universal_transfer(
        self,
        from_account_type: Literal["SPOT", "FUTURES"],
        to_account_type: Literal["SPOT", "FUTURES"],
        asset: str,
        amount: float,
        from_account: Optional[str] = None,
        to_account: Optional[str] = None,
    ) -> dict:
        """
        ### Universal Transfer (For Master Account)
        #### Required permission: SPOT_TRANSFER_WRITE

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-universal-transfer-history-for-master-account

        :param from_account: (optional) Transfer from master account by default if fromAccount is not sent
        :type from_account: str
        :param to_account: (optional) Transfer to master account by default if toAccount is not sent
        :type to_account: str
        :param from_account_type: fromAccountType:"SPOT","FUTURES"
        :type from_account_type: str
        :param to_account_type: toAccountType:"SPOT","FUTURES"
        :type to_account_type: str
        :param asset: asset,eg:USDT
        :type asset: str
        :param amount: amount,eg:1.82938475
        :type amount: float

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "POST",
            "api/v3/capital/sub-account/universalTransfer",
            params=dict(
                fromAccount=from_account,
                toAccount=to_account,
                fromAccountType=from_account_type,
                toAccountType=to_account_type,
                asset=asset,
                amount=amount,
            ),
        )

    def query_universal_transfer_history(
        self,
        from_account_type: Literal["SPOT", "FUTURES"],
        to_account_type: Literal["SPOT", "FUTURES"],
        from_account: Optional[str] = None,
        to_account: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        page: Optional[int] = 1,
        limit: Optional[int] = 500,
    ) -> dict:
        """
        ### Query Universal Transfer History.
        #### Required permission: SPOT_TRANSFER_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-universal-transfer-history-for-master-account

        :param from_account: (optional) Transfer from master account by default if fromAccount is not sent
        :type from_account: str
        :param to_account: (optional) Transfer to master account by default if toAccount is not sent
        :type to_account: str
        :param from_account_type: fromAccountType:"SPOT","FUTURES"
        :type from_account_type: str
        :param to_account_type: toAccountType:"SPOT","FUTURES"
        :type to_account_type: str
        :param start_time: (optional) startTime
        :type start_time: str
        :param end_time: (optional) endTime
        :type end_time: str
        :param page: (optional) default 1
        :type page: int
        :param limit: (optional) default 500, max 500
        :type limit: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "api/v3/capital/sub-account/universalTransfer",
            params=dict(
                fromAccount=from_account,
                toAccount=to_account,
                fromAccountType=from_account_type,
                toAccountType=to_account_type,
                startTime=start_time,
                endTime=end_time,
                page=page,
                limit=limit,
            ),
        )

    def sub_account_asset(
        self,
        sub_account: str,
        account_type: Literal["SPOT", "FUTURES"],
    ) -> dict:
        """
        ### Query Sub-account Asset
        #### Required permission: SPOT_TRANSFER_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-sub-account-asset

        :param sub_account: subAccount
        :type sub_account: str
        :param account_type: accountType:"SPOT","FUTURES"
        :type account_type: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "api/v3/sub-account/asset",
            params=dict(
                subAccount=sub_account,
                accountType=account_type,
            ),
        )

    # <=================================================================>
    #
    #                       Spot Account/Trade
    #
    # <=================================================================>

    def get_kyc_status(self) -> dict:
        """
        ### Query KYC status
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-kyc-status

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/kyc/status")

    def get_default_symbols(self) -> dict:
        """
        ### User API default symbol.
        #### Required permission: SPOT_ACCOUNT_R

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#user-api-default-symbol

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/selfSymbols")

    def test_new_order(self, *args, **kwargs) -> dict:
        warnings.warn("test_new_order is deprecated, use test_order instead", DeprecationWarning)
        return self.test_order(*args, **kwargs)

    def test_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Optional[int] = None,
        quote_order_qty: Optional[int] = None,
        price: Optional[int] = None,
        new_client_order_id: Optional[str] = None,
        stop_price: Optional[int] = None,
        iceberg_qty: Optional[int] = None,
        time_in_force: Optional[str] = None,
    ) -> dict:
        """
        ### Test New Order.
        #### Required permission: SPOT_DEAL_WRITE

        Weight(IP): 1, Weight(UID): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#test-new-order

        :param symbol: Trading pair
        :type symbol: str
        :param side: Order side (BUY/SELL)
        :type side: str
        :param order_type: Order type (LIMIT/MARKET)
        :type order_type: str
        :param quantity: Order quantity
        :type quantity: Optional[int]
        :param quote_order_qty: Quote order quantity
        :type quote_order_qty: Optional[int]
        :param price: Order price
        :type price: Optional[int]
        :param new_client_order_id: Client order ID
        :type new_client_order_id: Optional[str]
        :param stop_price: Stop price
        :type stop_price: Optional[int]
        :param iceberg_qty: Iceberg quantity
        :type iceberg_qty: Optional[int]
        :param time_in_force: Time in force
        :type time_in_force: Optional[str]

        :return: Empty dict if successful
        :rtype: dict
        """
        # Validate required parameters based on order type
        if order_type == "LIMIT":
            if not quantity or not price:
                raise ValueError("LIMIT orders require both quantity and price")
        elif order_type == "MARKET":
            if not quantity and not quote_order_qty:
                raise ValueError("MARKET orders require either quantity or quoteOrderQty")

        return self.call(
            "POST",
            "/api/v3/order/test",
            params=dict(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=quantity,
                quoteOrderQty=quote_order_qty,
                price=price,
                newClientOrderId=new_client_order_id,
                stopPrice=stop_price,
                icebergQty=iceberg_qty,
                timeInForce=time_in_force,
            ),
        )

    def new_order(self, *args, **kwargs) -> dict:
        warnings.warn("new_order is deprecated, use order instead", DeprecationWarning)
        return self.order(*args, **kwargs)

    def order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Optional[int] = None,
        quote_order_qty: Optional[int] = None,
        price: Optional[int] = None,
        new_client_order_id: Optional[str] = None,
        stop_price: Optional[int] = None,
        iceberg_qty: Optional[int] = None,
        time_in_force: Optional[str] = None,
    ) -> dict:
        """
        ### New Order.
        #### Required permission: SPOT_DEAL_WRITE

        Weight(IP): 1, Weight(UID): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#new-order

        :param symbol: Trading pair
        :type symbol: str
        :param side: Order side (BUY/SELL)
        :type side: str
        :param order_type: Order type (LIMIT/MARKET)
        :type order_type: str
        :param quantity: Order quantity
        :type quantity: Optional[int]
        :param quote_order_qty: Quote order quantity
        :type quote_order_qty: Optional[int]
        :param price: Order price
        :type price: Optional[int]
        :param new_client_order_id: Client order ID
        :type new_client_order_id: Optional[str]
        :param stop_price: Stop price
        :type stop_price: Optional[int]
        :param iceberg_qty: Iceberg quantity
        :type iceberg_qty: Optional[int]
        :param time_in_force: Time in force
        :type time_in_force: Optional[str]

        :return: Order response dictionary
        :rtype: dict
        """
        # Validate required parameters based on order type
        if order_type == "LIMIT":
            if not quantity or not price:
                raise ValueError("LIMIT orders require both quantity and price")
        elif order_type == "MARKET":
            if not quantity and not quote_order_qty:
                raise ValueError("MARKET orders require either quantity or quoteOrderQty")

        return self.call(
            "POST",
            "api/v3/order",
            params=dict(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=quantity,
                quoteOrderQty=quote_order_qty,
                price=price,
                newClientOrderId=new_client_order_id,
                stopPrice=stop_price,
                icebergQty=iceberg_qty,
                timeInForce=time_in_force,
            ),
        )

    def batch_orders(
        self,
        batch_orders: List[dict],
        symbol: str,
        side: Literal["BUY", "SELL"],
        order_type: Literal["LIMIT", "MARKET", "LIMIT_MARKET", "IMMEDIATE_OR_CANCEL", "FILL_OR_KILL"],
        quantity: Optional[float] = None,
        quote_order_qty: Optional[float] = None,
        price: Optional[float] = None,
        new_client_order_id: Optional[str] = None,
    ) -> list:
        """
        ### Batch Orders.
        #### Required permission: SPOT_DEAL_WRITE

        Weight(IP): 1, Weight(UID): 1

        Supports 20 orders with a same symbol in a batch, rate limit: 2 times/s.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#batch-orders

        :param batch_orders: list of batchOrders, supports max 20 orders
        :type batch_orders: List[dict]
        :param symbol: symbol
        :type symbol: str
        :param side: order side
        :type side: Literal["BUY", "SELL"]
        :param order_type: order type
        :type order_type: Literal["LIMIT", "MARKET", "LIMIT_MARKET", "IMMEDIATE_OR_CANCEL", "FILL_OR_KILL"]
        :param quantity: quantity (required for LIMIT and MARKET orders)
        :type quantity: Optional[float]
        :param quote_order_qty: quoteOrderQty (required for MARKET orders if quantity not provided)
        :type quote_order_qty: Optional[float]
        :param price: order price (required for LIMIT orders)
        :type price: Optional[float]
        :param new_client_order_id: ClientOrderId
        :type new_client_order_id: Optional[str]

        :return: list of order responses
        :rtype: list
        """
        # Validate required parameters based on order type
        if order_type == "LIMIT":
            if not quantity or not price:
                raise ValueError("LIMIT orders require both quantity and price")
        elif order_type == "MARKET":
            if not quantity and not quote_order_qty:
                raise ValueError("MARKET orders require either quantity or quoteOrderQty")

        # Prepare batch orders
        orders = []
        for order in batch_orders:
            order_data = {
                "symbol": symbol,
                "side": side,
                "type": order_type,
            }

            if quantity:
                order_data["quantity"] = str(quantity)
            if quote_order_qty:
                order_data["quoteOrderQty"] = str(quote_order_qty)
            if price:
                order_data["price"] = str(price)
            if new_client_order_id:
                order_data["newClientOrderId"] = new_client_order_id

            # Add any additional fields from the batch order
            order_data.update(order)
            orders.append(order_data)

        return self.call("POST", "api/v3/batchOrders", params=dict(batchOrders=json.dumps(orders)))

    def cancel_order(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        orig_client_order_id: Optional[str] = None,
        new_client_order_id: Optional[str] = None,
    ) -> dict:
        """
        ### Cancel Order.
        #### Required permission: SPOT_DEAL_WRITE

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#cancel-order

        :param symbol:
        :type symbol: str
        :param order_id: (optional) Order id
        :type order_id: str
        :param orig_client_order_id: (optional)
        :type orig_client_order_id: str
        :param new_client_order_id: (optional) Unique order id
        :type new_client_order_id: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "DELETE",
            "api/v3/order",
            params=dict(
                symbol=symbol,
                orderId=order_id,
                origClientOrderId=orig_client_order_id,
                newClientOrderId=new_client_order_id,
            ),
        )

    def cancel_all_open_orders(self, symbol: str) -> dict:
        """
        ### Cancel all Open Orders on a Symbol.
        #### Required permission: SPOT_DEAL_WRITE

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#cancel-all-open-orders-on-a-symbol

        :param symbol: maximum input 5 symbols,separated by ",". e.g. "BTCUSDT,MXUSDT,ADAUSDT"
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("DELETE", "api/v3/openOrders", params=dict(symbol=symbol))

    def query_order(
        self,
        symbol: str,
        orig_client_order_id: Optional[str] = None,
        order_id: Optional[str] = None,
    ) -> dict:
        """
        ### Query Order.
        #### Required permission: SPOT_DEAL_READ
        Check an order's status.

        Weight(IP): 2

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-order

        :param symbol:
        :type symbol: str
        :param orig_client_order_id: (optional) Unique order id
        :type orig_client_order_id: str
        :param order_id: (optional) Order id
        :type order_id: str
        :param recv_window: (optional) Request timeout
        :type recv_window: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "api/v3/order",
            params=dict(symbol=symbol, origClientOrderId=orig_client_order_id, orderId=order_id),
        )

    def current_open_orders(self, symbol: str) -> dict:
        """
        ### Current Open Orders.
        #### Required permission: SPOT_DEAL_READ

        Weight(IP): 3

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#current-open-orders

        :param symbol:
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/openOrders", params=dict(symbol=symbol))

    def all_orders(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        """
        ### All Orders.
        #### Required permission: SPOT_DEAL_READ

        Weight(IP): 10

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#all-orders

        Get all account orders including active, cancelled or completed orders(the query period is the latest 24 hours by default). You can query a maximum of the latest 7 days.

        :param symbol: Symbol
        :type symbol: str
        :param start_time: (optional)
        :type start_time: int
        :param end_time: (optional)
        :type end_time: int
        :param limit: (optional) Default 500; max 1000;
        :type limit: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "api/v3/allOrders",
            params=dict(symbol=symbol, startTime=start_time, endTime=end_time, limit=limit),
        )

    def account_information(self) -> dict:
        """
        ### Account Information.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 10

        Get current account information,rate limit:2 times/s.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#account-information

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/account")

    def account_trade_list(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        """
        ### Account Trade List.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 10

        Get trades for a specific account and symbol,
        Only the transaction records in the past 1 month can be queried.
        If you want to view more transaction records, please use the export function on the web side,
        which supports exporting transaction records of the past 3 years at most.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#account-trade-list

        :param symbol:
        :type symbol: str
        :param order_id: (optional) order Id
        :type order_id: str
        :param start_time: (optional)
        :type start_time: int
        :param end_time: (optional)
        :type end_time: int
        :param limit: (optional) Default 500; max 1000;
        :type limit: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "api/v3/myTrades",
            params=dict(
                symbol=symbol,
                orderId=order_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    def enable_mx_deduct(self, mx_deduct_enable: bool) -> dict:
        """
        ### Enable MX Deduct.
        #### Required permission: SPOT_DEAL_WRITE
        Enable or disable MX deduct for spot commission fee

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#enable-mx-deduct

        :param mx_deduct_enable: true:enable,false:disable
        :type mx_deduct_enable: bool

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "POST",
            "api/v3/mxDeduct/enable",
            params=dict(mxDeductEnable=mx_deduct_enable),
        )

    def query_mx_deduct_status(self) -> dict:
        """
        ### Query MX Deduct Status.
        #### Required permission: SPOT_DEAL_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-mx-deduct-status

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/mxDeduct/enable")

    # <=================================================================>
    #
    #                          Wallet Endpoints
    #
    # <=================================================================>

    def query_symbol_commission(self, symbol: str) -> dict:
        """
        ### Query Symbol Commission.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 20

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-symbol-commission

        :param symbol: symbol
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/tradeFee", params=dict(symbol=symbol))

    def get_currency_info(self) -> dict:
        """
        ### Query the currency information.
        #### Required permission: SPOT_WITHDRAW_READ

        Weight(IP): 10

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-the-currency-information

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/capital/config/getall")

    def withdraw(
        self,
        coin: str,
        address: str,
        amount: int,
        contract_address: Optional[str] = None,
        withdraw_order_id: Optional[str] = None,
        network: Optional[str] = None,
        memo: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> dict:
        """
        ### Withdraw.
        #### Required permission: SPOT_WITHDRAW_WRITE

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#withdraw-new

        :param coin: coin
        :type coin: str
        :param withdraw_order_id: (optional) withdrawOrderId
        :type withdraw_order_id: str
        :param network: (optional) withdraw network
        :type network: str
        :param contract_address: (optional) contract address
        :type contract_address: str
        :param address: withdraw address
        :type address: str
        :param memo: (optional) memo(If memo is required in the address, it must be passed in)
        :type memo: str
        :param amount: withdraw amount
        :type amount: int
        :param remark: (optional) remark
        :type remark: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "POST",
            "api/v3/capital/withdraw",
            params=dict(
                coin=coin,
                withdrawOrderId=withdraw_order_id,
                netWork=network,
                contractAddress=contract_address,
                address=address,
                memo=memo,
                amount=amount,
                remark=remark,
            ),
        )

    def cancel_withdraw(self, id: str) -> dict:
        """
        ### Cancel withdraw.
        #### Required permission: SPOT_WITHDRAW_W

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#cancel-withdraw

        :param id: withdraw id
        :type id: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("DELETE", "api/v3/capital/withdraw", params=dict(id=id))

    def deposit_history(
        self,
        coin: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        """
        ### Deposit History(supporting network).
        #### Required permission: SPOT_WITHDRAW_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#deposit-history-supporting-network

        Ensure that the default timestamp of 'startTime' and 'endTime' does not exceed 90 days.

        :param coin: (optional) coin
        :type coin: str
        :param status: (optional) status
        :type status: str
        :param start_time: (optional) default: 90 days ago from current time
        :type start_time: int
        :param end_time: (optional) default:current time
        :type end_time: int
        :param limit: (optional) default:1000,max:1000
        :type limit: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "api/v3/capital/deposit/hisrec",
            params=dict(
                coin=coin,
                status=status,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    def withdraw_history(
        self,
        coin: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> dict:
        """
        ### Withdraw History (supporting network).
        #### Required permission: SPOT_WITHDRAW_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#withdraw-history-supporting-network

        :param coin: (optional) coin
        :type coin: str
        :param status: (optional) withdraw status
        :type status: str
        :param limit: (optional) default:1000, max:1000
        :type limit: int
        :param start_time: (optional) default: 90 days ago from current time
        :type start_time: str
        :param end_time: (optional) default:current time
        :type end_time: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "api/v3/capital/withdraw/history",
            params=dict(
                coin=coin,
                status=status,
                limit=limit,
                startTime=start_time,
                endTime=end_time,
            ),
        )

    def generate_deposit_address(self, coin: str, network: str) -> dict:
        """
        ### Generate deposit address (supporting network).
        #### Required permission: SPOT_WITHDRAW_WRITE

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#generate-deposit-address-supporting-network

        :param coin: coin
        :type coin: str
        :param network: deposit network
        :type network: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "POST",
            "api/v3/capital/deposit/address",
            params=dict(coin=coin, network=network),
        )

    def deposit_address(self, coin: str, network: Optional[str] = None) -> dict:
        """
        ### Deposit Address (supporting network).
        #### Required permission: SPOT_WITHDRAW_READ

        Weight(IP): 10

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#deposit-address-supporting-network

        :param coin: coin
        :type coin: str
        :param network: (optional) deposit network
        :type network: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "api/v3/capital/deposit/address",
            params=dict(
                coin=coin,
                network=network,
            ),
        )

    def withdraw_address(
        self,
        coin: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        """
        ### Withdraw Address (supporting network).
        #### Required permission: SPOT_WITHDRAW_R

        Weight(IP): 10

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#withdraw-address-supporting-network


        :param coin: (optional) coin
        :type coin: str
        :param page: (optional) page,default 1
        :type page: int
        :param limit: (optional) limit for per page,default 20
        :type limit: int


        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "api/v3/capital/withdraw/address",
            params=dict(coin=coin, page=page, limit=limit),
        )

    def user_universal_transfer(self, from_account_type: str, to_account_type: str, asset: str, amount: int) -> dict:
        """
        ### User Universal Transfer.
        #### Required permission: SPOT_TRANSFER_WRITE

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#user-universal-transfer

        :param from_account_type: fromAccountType:"SPOT","FUTURES"
        :type from_account_type: str
        :param to_account_type: toAccountType:"SPOT","FUTURES"
        :type to_account_type: str
        :param asset: asset
        :type asset: str
        :param amount: amount
        :type amount: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "POST",
            "api/v3/capital/transfer",
            params=dict(
                fromAccountType=from_account_type,
                toAccountType=to_account_type,
                asset=asset,
                amount=amount,
            ),
        )

    def user_universal_transfer_history(
        self,
        from_account_type: Literal["SPOT", "FUTURES"],
        to_account_type: Literal["SPOT", "FUTURES"],
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        page: Optional[int] = 1,
        size: Optional[int] = 10,
    ) -> dict:
        """
        ### Query User Universal Transfer History.
        #### Required permission: SPOT_TRANSFER_READ
        Only can quary the data for the last six months
        If 'startTime' and 'endTime' are not send, will return the last seven days' data by default

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-user-universal-transfer-history

        :param from_account_type: fromAccountType:"SPOT","FUTURES"
        :type from_account_type: str
        :param to_account_type: toAccountType:"SPOT","FUTURES"
        :type to_account_type: str
        :param start_time: (optional) startTime
        :type start_time: str
        :param end_time: (optional) endTime
        :type end_time: str
        :param page: (optional) default:1
        :type page: int
        :param size: (optional) default:10, max:100
        :type size: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "api/v3/capital/transfer",
            params=dict(
                fromAccountType=from_account_type,
                toAccountType=to_account_type,
                startTime=start_time,
                endTime=end_time,
                page=page,
                size=size,
            ),
        )

    def user_universal_transfer_history_by_tranid(self, tran_id: str) -> dict:
        """
        ### Query User Universal Transfer History (by tranId).
        #### Required permission: SPOT_TRANSFER_R
        Only can quary the data for the last six months

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-user-universal-transfer-history-by-tranid

        :param tran_id: tranId
        :type tran_id: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/capital/transfer/tranId", params=dict(tranId=tran_id))

    def get_assets_convert_into_mx(self) -> dict:
        """
        ### Get Assets That Can Be Converted Into MX.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-assets-that-can-be-converted-into-mx

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/capital/convert/list")

    def dust_transfer(self, asset: Union[str, List[str]]) -> dict:
        """
        ### Dust Transfer.
        #### Required permission: SPOT_ACCOUNT_W

        Weight(IP): 10

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#dust-transfer

        :param asset: The asset being converted.(max 15 assert)eg:asset=BTC,FIL,ETH
        :type asset: Union[str, List[str]]

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "POST",
            "api/v3/capital/convert",
            params=dict(asset=",".join(asset) if isinstance(asset, list) else asset),
        )

    def dustlog(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        """
        ### DustLog.
        #### Required permission: SPOT_DEAL_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#dustlog


        :param start_time: (optional) startTime
        :type start_time: int
        :param end_time: (optional) endTime
        :type end_time: int
        :param page: (optional) page,default 1
        :type page: int
        :param limit: (optional) limit,default 1; max 1000
        :type limit: int


        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "api/v3/capital/convert",
            params=dict(startTime=start_time, endTime=end_time, page=page, limit=limit),
        )

    def internal_transfer(self, to_account_type: str, to_account: str, asset: str, amount: float) -> dict:
        """
        ### Internal Transfer.
        #### Required permission: SPOT_WITHDRAW_WRITE

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#internal-transfer

        :param to_account_type: toAccountType:"EMAIL","UID","MOBILE"
        :type to_account_type: str
        :param to_account: toAccount
        :type to_account: str
        :param asset: asset
        :type asset: str
        :param amount: amount
        :type amount: float

        :return: response dictionary
        :rtype: dict
        """

        return self.call(
            "POST",
            "api/v3/capital/transfer/internal",
            params=dict(
                toAccountType=to_account_type,
                toAccount=to_account,
                asset=asset,
                amount=amount,
            ),
        )

    def internal_transfer_history(self, start_time: int, end_time: int) -> dict:
        """
        ### Internal Transfer History.
        #### Required permission: SPOT_WITHDRAW_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#internal-transfer-history

        :param start_time: startTime
        :type start_time: int
        :param end_time: endTime
        :type end_time: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "api/v3/capital/transfer/internal",
            params=dict(startTime=start_time, endTime=end_time),
        )

    # <=================================================================>
    #
    #                     Websocket Market Streams
    #
    # <=================================================================>

    # realized in spot.WebSocket class

    # <=================================================================>
    #
    #                   Websocket User Data Streams
    #
    # <=================================================================>

    def create_listen_key(self) -> dict:
        """
        ### Create a ListenKey.
        #### Required permission: SPOT_ACCOUNT_R

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#listen-key

        Start a new user data stream. The stream will close after 60 minutes unless a keepalive is sent.

        :return: response dictionary containing listenKey
        :rtype: dict
        """
        return self.call("POST", "api/v3/userDataStream")

    def get_listen_keys(self) -> dict:
        """
        ### Get Valid Listen Keys.
        #### Required permission: SPOT_ACCOUNT_R

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#listen-key

        Retrieves all currently valid listen keys.

        :return: response dictionary containing list of listenKeys
        :rtype: dict
        """
        return self.call("GET", "api/v3/userDataStream")

    def keep_alive_listen_key(self, listen_key: str) -> dict:
        """
        ### Keep-alive a ListenKey.
        #### Required permission: SPOT_ACCOUNT_R

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#listen-key

        Extends the validity to 60 minutes from the time of this call. It is recommended to send a request every 30 minutes.

        :param listen_key: Listen key
        :type listen_key: str

        :return: response dictionary containing listenKey
        :rtype: dict
        """
        return self.call("PUT", "api/v3/userDataStream", params=dict(listenKey=listen_key))

    def close_listen_key(self, listen_key: str) -> dict:
        """
        ### Close a ListenKey.
        #### Required permission: SPOT_ACCOUNT_R

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#listen-key

        Closes the user data stream.

        :param listen_key: Listen key
        :type listen_key: str

        :return: response dictionary containing listenKey
        :rtype: dict
        """
        return self.call("DELETE", "api/v3/userDataStream", params=dict(listenKey=listen_key))

    # <=================================================================>
    #
    #                          Rabate Endpoints
    #
    # <=================================================================>
    def get_rebate_history_records(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page: Optional[int] = None,
    ) -> dict:
        """
        ### Get Rebate History Records.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#rebate-endpoints


        :param start_time: (optional)
        :type start_time: int
        :param end_time: (optional)
        :type end_time: int
        :param page: (optional) default 1
        :type page: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "api/v3/rebate/taxQuery",
            params=dict(startTime=start_time, endTime=end_time, page=page),
        )

    def get_rebate_records_detail(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page: Optional[int] = None,
    ) -> dict:
        """
        ### Get Rebate Records Detail.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-rebate-records-detail


        :param start_time: (optional)
        :type start_time: int
        :param end_time: (optional)
        :type end_time: int
        :param page: (optional) default 1
        :type page: int


        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "api/v3/rebate/detail",
            params=dict(startTime=start_time, endTime=end_time, page=page),
        )

    def get_self_rebate_records_detail(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page: Optional[int] = None,
    ) -> dict:
        """
        ### Get Self Rebate Records Detail.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-self-rebate-records-detail

        :param start_time: (optional)
        :type start_time: int
        :param end_time: (optional)
        :type end_time: int
        :param page: (optional) default 1
        :type page: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "api/v3/rebate/detail/kickback",
            params=dict(startTime=start_time, endTime=end_time, page=page),
        )

    def query_refercode(self) -> dict:
        """
        ### Query ReferCode.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-refercode

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/rebate/referCode", params=dict(please_sign_me=None))

    def affiliate_commission_record(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        invite_code: Optional[int] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> dict:
        """
        ### Get Affiliate Commission Record (affiliate only)
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-affiliate-commission-record-affiliate-only

        :param start_time: (optional)
        :type start_time: int
        :param end_time: (optional)
        :type end_time: int
        :param invite_code: (optional)
        :type invite_code: int
        :param page: (optional) default 1
        :type page: int
        :param page_size: (optional) default 10
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "/api/v3/rebate/affiliate/commission",
            params=dict(
                startTime=start_time,
                endTime=end_time,
                inviteCode=invite_code,
                page=page,
                pageSize=page_size,
            ),
        )

    def affiliate_withdraw_record(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        invite_code: Optional[int] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> dict:
        """
        ### Get Affiliate Withdraw Record (affiliate only)
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-affiliate-withdraw-record-affiliate-only

        :param start_time: (optional)
        :type start_time: int
        :param end_time: (optional)
        :type end_time: int
        :param invite_code: (optional)
        :type invite_code: int
        :param page: (optional) default 1
        :type page: int
        :param page_size: (optional) default 10
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "/api/v3/rebate/affiliate/withdraw",
            params=dict(
                startTime=start_time,
                endTime=end_time,
                inviteCode=invite_code,
                page=page,
                pageSize=page_size,
            ),
        )

    def affiliate_commission_detail_record(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        invite_code: Optional[int] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        type: Optional[Literal[1, 2, 3]] = None,
    ) -> dict:
        """
        ### Get Affiliate Withdraw Record (affiliate only)
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-affiliate-withdraw-record-affiliate-only

        :param start_time: (optional)
        :type start_time: int
        :param end_time: (optional)
        :type end_time: int
        :param invite_code: (optional)
        :type invite_code: int
        :param page: (optional) default 1
        :type page: int
        :param page_size: (optional) default 10
        :type page_size: int
        :param type: (optional) commission type, 1:spot, 2:futures, 3:ETF
        :type type: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call(
            "GET",
            "/api/v3/rebate/affiliate/commission/detail",
            params=dict(
                startTime=start_time,
                endTime=end_time,
                inviteCode=invite_code,
                page=page,
                pageSize=page_size,
                type=type,
            ),
        )


class WebSocket(_SpotWebSocket):
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        listenKey: Optional[str] = None,
        ping_interval: Optional[int] = 20,
        ping_timeout: Optional[int] = 10,
        retries: Optional[int] = 10,
        restart_on_error: Optional[bool] = True,
        trace_logging: Optional[bool] = False,
        http_proxy_host: Optional[str] = None,
        http_proxy_port: Optional[int] = None,
        http_no_proxy: Optional[list] = None,
        http_proxy_auth: Optional[tuple] = None,
        http_proxy_timeout: Optional[int] = None,
        proto: Optional[bool] = False,
        extend_proto_body: Optional[bool] = False,
    ):
        """
        Initializes the class instance with the provided arguments.

        :param api_key: API key for authentication. (Optional)
        :type api_key: str

        :param api_secret: API secret for authentication. (Optional)
        :type api_secret: str

        :param listenKey: The listen key for the connection to private channels.
                          If not provided, a listen key will be generated from HTTP api [Permission: SPOT_ACCOUNT_R] (Optional)
        :type listenKey: str

        :param ping_interval: The interval in seconds to send a ping request. (Optional)
        :type ping_interval: int

        :param ping_timeout: The timeout in seconds for a ping request. (Optional)
        :type ping_timeout: int

        :param retries: The number of times to retry a request. (Optional)
        :type retries: int

        :param restart_on_error: Whether or not to restart the connection on error. (Optional)
        :type restart_on_error: bool

        :param trace_logging: Whether or not to enable trace logging. (Optional)
        :type trace_logging: bool

        :param http_proxy_host: The host for the HTTP proxy. (Optional)
        :type http_proxy_host: str

        :param http_proxy_port: The port for the HTTP proxy. (Optional)
        :type http_proxy_port: int

        :param http_no_proxy: A list of hosts to exclude from the HTTP proxy. (Optional)
        :type http_no_proxy: list

        :param http_proxy_auth: A tuple containing the username and password for the HTTP proxy. (Optional)
        :type http_proxy_auth: tuple

        :param http_proxy_timeout: The timeout in seconds for the HTTP proxy. (Optional)
        :type http_proxy_timeout: int

        :param proto: Whether or not to use the proto protocol. (Optional)
        :type proto: bool

        :param extend_proto_body: Whether or not to extend the proto body. (Optional)
        :type extend_proto_body: bool

        :return: None
        """
        kwargs = dict(
            api_key=api_key,
            api_secret=api_secret,
            ping_interval=ping_interval,
            ping_timeout=ping_timeout,
            retries=retries,
            restart_on_error=restart_on_error,
            trace_logging=trace_logging,
            http_proxy_host=http_proxy_host,
            http_proxy_port=http_proxy_port,
            http_no_proxy=http_no_proxy,
            http_proxy_auth=http_proxy_auth,
            http_proxy_timeout=http_proxy_timeout,
            proto=proto,
            extend_proto_body=extend_proto_body,
        )
        self.listenKey = listenKey

        super().__init__(**kwargs)

        # for keep alive connection to private spot websocket
        # need to send listen key at connection and send keep-alive request every 60 mins
        if api_key and api_secret:
            if not self.listenKey:
                auth = HTTP(api_key=api_key, api_secret=api_secret).create_listen_key()
                self.listenKey = auth.get("listenKey")
                logger.debug(f"create listenKey: {self.listenKey}")

            if not self.listenKey:
                raise Exception(f"ListenKey not found. Error: {auth}")

            self.endpoint = f"wss://wbs-api.mexc.com/ws?listenKey={self.listenKey}"

            # setup keep-alive connection loop
            self.kal = threading.Thread(target=lambda: self._keep_alive_loop())
            self.kal.daemon = True
            self.kal.start()

    def _keep_alive_loop(self):
        """
        Runs a loop that sends a keep-alive message every 59 minutes to maintain the connection
        with the MEXC API.

        :return: None
        """

        while True:
            time.sleep(59 * 60)  # 59 min
            if self.listenKey:
                resp = HTTP(api_key=self.api_key, api_secret=self.api_secret).keep_alive_listen_key(self.listenKey)
                logger.debug(f"keep-alive listenKey - {self.listenKey}. Response: {resp}")
            else:
                break

    # <=================================================================>
    #
    #                                Public
    #
    # <=================================================================>

    def deals_stream(
        self,
        callback: Callable[[dict | ProtoTyping.PublicDealsV3Api], None],
        symbol: Union[str, List[str]],
        speed: str = "100ms",
    ):
        """
        ### Trade Streams
        The Trade Streams push raw trade information; each trade has a unique buyer and seller.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#trade-streams

        :param callback: the callback function
        :type callback: Callable[[dict | ProtoTyping.PublicDealsV3Api], None]
        :param symbol: the name of the contract
        :type symbol: Union[str,List[str]]
        :param speed: aggregated stream speed. Possible values '100ms' or '10ms'
        :type symbol: str

        :return: None
        """
        if isinstance(symbol, str):
            symbols = [symbol]  # str
        else:
            symbols = symbol  # list
        params = [dict(symbol=s) for s in symbols]
        topic = "public.aggre.deals"
        self._ws_subscribe(topic, callback, params, speed)

    def kline_stream(
        self,
        callback: Callable[[dict | ProtoTyping.PublicSpotKlineV3Api], None],
        symbol: str,
        interval: Literal[
            "Min1",
            "Min5",
            "Min15",
            "Min30",
            "Min60",
            "Hour4",
            "Hour8",
            "Day1",
            "Week1",
            "Month1",
        ],
    ):
        """
        ### Kline Streams
        The Kline/Candlestick Stream push updates to the current klines/candlestick every second.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#k-line-streams

        :param callback: the callback function
        :type callback: Callable[[dict | ProtoTyping.PublicSpotKlineV3Api], None]
        :param symbol: the name of the contract
        :type symbol: str
        :param interval: the interval of the kline
        :type interval: int

        :return: None
        """
        params = [dict(symbol=symbol, interval=interval)]
        topic = "public.kline"
        self._ws_subscribe(topic, callback, params)

    def depth_stream(
        self,
        callback: Callable[[dict | ProtoTyping.PublicIncreaseDepthsV3Api], None],
        symbol: str,
        speed: str = "100ms",
    ):
        """
        ### Diff.Depth Stream
        If the order quantity (quantity) for a price level is 0, it indicates that the order at that price has been canceled or executed, and that price level should be removed.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#diff-depth-stream

        :param callback: the callback function
        :type callback: Callable[[dict | ProtoTyping.PublicIncreaseDepthsV3Api], None]
        :param symbol: the name of the contract
        :type symbol: str

        :return: None
        """
        params = [dict(symbol=symbol)]
        topic = "public.aggre.depth"
        self._ws_subscribe(topic, callback, params, speed)

    def limit_depth_stream(
        self,
        callback: Callable[[dict | ProtoTyping.PublicLimitDepthsV3Api], None],
        symbol: str,
        level: int,
    ):
        """
        ### Partial Book Depth Streams
        Top bids and asks, Valid are 5, 10, or 20.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#partial-book-depth-streams

        :param callback: the callback function
        :type callback: Callable[[dict | ProtoTyping.PublicLimitDepthsV3Api], None]
        :param symbol: the name of the contract
        :type symbol: str
        :param level: the level of the depth. Valid are 5, 10, or 20.
        :type level: int

        :return: None
        """
        params = [dict(symbol=symbol, level=level)]
        topic = "public.limit.depth"
        self._ws_subscribe(topic, callback, params)

    def book_ticker_stream(
        self,
        callback: Callable[[dict | ProtoTyping.PublicBookTickerV3Api], None],
        symbol: str,
        speed: str = "100ms",
    ):
        """
        ### Individual Symbol Book Ticker Streams
        Pushes any update to the best bid or ask's price or quantity in real-time for a specified symbol.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#partial-book-depth-streams

        :param callback: the callback function
        :type callback: Callable[[dict | ProtoTyping.PublicBookTickerV3Api], None]
        :param symbols: the names of the contracts
        :type symbols: str

        :return: None
        """
        params = [dict(symbol=symbol)]
        topic = "public.aggre.bookTicker"
        self._ws_subscribe(topic, callback, params, speed)

    def book_ticker_batch_stream(
        self,
        callback: Callable[[dict | ProtoTyping.PublicBookTickerBatchV3Api], None],
        symbols: List[str],
    ):
        """
        ### Individual Symbol Book Ticker Streams (Batch Aggregation)
        This batch aggregation version pushes the best order information for a specified trading pair.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#individual-symbol-book-ticker-streams-batch-aggregation

        :param callback: the callback function
        :type callback: Callable[[dict | ProtoTyping.PublicBookTickerBatchV3Api], None]
        :param symbols: the names of the contracts
        :type symbols: List[str]

        :return: None
        """
        params = [dict(symbol=symbol) for symbol in symbols]
        topic = "public.bookTicker.batch"
        self._ws_subscribe(topic, callback, params)

    def mini_ticker_stream(
        self,
        callback: Callable[[dict | ProtoTyping.PublicMiniTickerV3Api], None],
        symbol: str,
        timezone: str = "UTC+8",
    ):
        """
        ### MiniTicker Stream
        MiniTicker of the specified trading pair in the specified timezone, pushed every 3 seconds.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#miniticker

        :param callback: the callback function
        :type callback: Callable[[dict | ProtoTyping.PublicMiniTickerV3Api], None]
        :param symbol: the name of the trading pair
        :type symbol: str
        :param timezone: timezone for the ticker data. Valid values: 24H, UTC-10, UTC-8, UTC-7, UTC-6, UTC-5, UTC-4, UTC-3, UTC+0, UTC+1, UTC+2, UTC+3, UTC+4, UTC+4:30, UTC+5, UTC+5:30, UTC+6, UTC+7, UTC+8 (default), UTC+9, UTC+10, UTC+11, UTC+12, UTC+12:45, UTC+13
        :type timezone: str

        :return: None
        """
        if timezone not in VALID_TIMEZONES:
            raise ValueError(f"Invalid timezone: {timezone}. Must be one of {sorted(VALID_TIMEZONES)}")
        params = [dict(symbol=symbol, timezone=timezone)]
        topic = "public.miniTicker"
        self._ws_subscribe(topic, callback, params)

    def mini_tickers_stream(
        self,
        callback: Callable[[dict | ProtoTyping.PublicMiniTickersV3Api], None],
        timezone: str = "UTC+8",
    ):
        """
        ### MiniTickers Stream
        MiniTickers of all trading pairs in the specified timezone, pushed every 3 seconds.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#minitickers

        :param callback: the callback function
        :type callback: Callable[[dict | ProtoTyping.PublicMiniTickersV3Api], None]
        :param timezone: timezone for the ticker data. Valid values: 24H, UTC-10, UTC-8, UTC-7, UTC-6, UTC-5, UTC-4, UTC-3, UTC+0, UTC+1, UTC+2, UTC+3, UTC+4, UTC+4:30, UTC+5, UTC+5:30, UTC+6, UTC+7, UTC+8 (default), UTC+9, UTC+10, UTC+11, UTC+12, UTC+12:45, UTC+13
        :type timezone: str

        :return: None
        """
        if timezone not in VALID_TIMEZONES:
            raise ValueError(f"Invalid timezone: {timezone}. Must be one of {sorted(VALID_TIMEZONES)}")
        params = [dict(timezone=timezone)]
        topic = "public.miniTickers"
        self._ws_subscribe(topic, callback, params)

    # <=================================================================>
    #
    #                                Private
    #
    # <=================================================================>

    def account_update(self, callback: Callable[[dict | ProtoTyping.PrivateAccountV3Api], None]):
        """
        ### Spot Account Update
        The server will push an update of the account assets when the account balance changes.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#websocket-user-data-streams

        :param callback: the callback function
        :type callback: Callable[[dict | ProtoTyping.PrivateAccountV3Api], None]

        :return: None
        """
        params = [{}]
        topic = "private.account"
        self._ws_subscribe(topic, callback, params)

    def account_deals(self, callback: Callable[[dict | ProtoTyping.PrivateDealsV3Api], None]):
        """
        ### Spot Account Deals

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#spot-account-deals

        :param callback: the callback function
        :type callback: Callable[[dict | ProtoTyping.PrivateDealsV3Api], None]

        :return: None
        """
        params = [{}]
        topic = "private.deals"
        self._ws_subscribe(topic, callback, params)

    def account_orders(self, callback: Callable[[dict | ProtoTyping.PrivateOrdersV3Api], None]):
        """
        ### Spot Account Orders

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#spot-account-orders

        :param callback: the callback function
        :type callback: Callable[[dict | ProtoTyping.PrivateOrdersV3Api], None]

        :return: None
        """
        params = [{}]
        topic = "private.orders"
        self._ws_subscribe(topic, callback, params)
