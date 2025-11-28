"""
### Futures API
Documentation: https://www.mexc.com/api-docs/futures/market-endpoints#get-server-time

### Usage

```python
from pymexc import futures

api_key = "YOUR API KEY"
api_secret = "YOUR API SECRET KEY"

def handle_message(message):
    # handle websocket message
    print(message)

# initialize HTTP client
futures_client = futures.HTTP(api_key = api_key, api_secret = api_secret)
# initialize WebSocket client
ws_futures_client = futures.WebSocket(api_key = api_key, api_secret = api_secret)

# make http request to api
print(futures_client.index_price("MX_USDT"))

# create websocket connection to public channel (sub.tickers)
# all messages will be handled by function `handle_message`
ws_futures_client.tickers_stream(handle_message)

# loop forever for save websocket connection
while True:
    ...

"""

import logging
from asyncio import AbstractEventLoop
from typing import Awaitable, Callable, Dict, List, Literal, Optional, Union
import warnings

logger = logging.getLogger(__name__)

try:
    from .base import _FuturesHTTP
    from .base_websocket import _FuturesWebSocket
    from ..base_websocket import FUTURES_PERSONAL_TOPICS
except ImportError:
    from pymexc._async.base import _FuturesHTTP
    from pymexc._async.base_websocket import _FuturesWebSocket
    from pymexc.base_websocket import FUTURES_PERSONAL_TOPICS


class HTTP(_FuturesHTTP):
    # <=================================================================>
    #
    #                          Market Endpoints
    #
    # <=================================================================>

    async def ping(self) -> dict:
        """
        ### Get Server Time

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/market-endpoints#get-server-time
        """
        return await self.call("GET", "api/v1/contract/ping")

    async def detail(self, symbol: Optional[str] = None) -> dict:
        """
        ### Get Contract Info

        Rate limit: 1 time / 5 seconds

        https://www.mexc.com/api-docs/futures/market-endpoints#get-contract-info

        :param symbol: (optional) Contract name
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", "api/v1/contract/detail", params=dict(symbol=symbol))

    async def support_currencies(self) -> dict:
        """
        ### Get Transferable Currencies

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/market-endpoints#get-transferable-currencies

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", "api/v1/contract/support_currencies")

    async def get_depth(self, symbol: str, limit: Optional[int] = None) -> dict:
        """
        ### Get Contract Order Book Depth

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/market-endpoints#get-contract-order-book-depth

        :param symbol: the name of the contract
        :type symbol: str
        :param limit: (optional) the limit of the depth
        :type limit: int


        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", f"api/v1/contract/depth/{symbol}", params=dict(limit=limit))

    async def depth_commits(self, symbol: str, limit: int) -> dict:
        """
        ### Get the Last N Depth Snapshots

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/market-endpoints#get-the-last-n-depth-snapshots

        :param symbol: the name of the contract
        :type symbol: str
        :param limit: count
        :type limit: int


        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", f"api/v1/contract/depth_commits/{symbol}/{limit}")

    async def index_price(self, symbol: str) -> dict:
        """
        ### Get Index Price

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/market-endpoints#get-index-price

        :param symbol: the name of the contract
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", f"api/v1/contract/index_price/{symbol}")

    async def fair_price(self, symbol: str) -> dict:
        """
        ### Get Fair Price

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/market-endpoints#get-fair-price

        :param symbol: the name of the contract
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", f"api/v1/contract/fair_price/{symbol}")

    async def funding_rate(self, symbol: str) -> dict:
        """
        ### Get Funding Rate

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/market-endpoints#get-funding-rate

        :param symbol: the name of the contract
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", f"api/v1/contract/funding_rate/{symbol}")

    async def kline(
        self,
        symbol: str,
        interval: Optional[
            Literal[
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
            ]
        ] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
    ) -> dict:
        """
        ### Get Candlestick Data

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/market-endpoints#get-candlestick-data

        :param symbol: the name of the contract
        :type symbol: str
        :param interval: The time interval for the Kline data. Must be one of "Min1", "Min5", "Min15", "Min30", "Min60", "Hour4", "Hour8", "Day1", "Week1", "Month1". Defaults to "Min1".
        :type interval: Optional[Literal["Min1", "Min5", "Min15", "Min30", "Min60", "Hour4", "Hour8", "Day1", "Week1", "Month1"]]
        :param start: (optional) The start time of the Kline data in Unix timestamp format.
        :type start: Optional[int]
        :param end: (optional) The end time of the Kline data in Unix timestamp format.
        :type end: Optional[int]

        :return: A dictionary containing the Kline data for the specified symbol and interval within the specified time range.
        :rtype: dict
        """
        return await self.call(
            "GET",
            f"api/v1/contract/kline/{symbol}",
            params=dict(symbol=symbol, interval=interval, start=start, end=end),
        )

    async def kline_index_price(
        self,
        symbol: str,
        interval: Optional[
            Literal[
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
            ]
        ] = "Min1",
        start: Optional[int] = None,
        end: Optional[int] = None,
    ) -> dict:
        """
        ### Get Index Price Candles

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/market-endpoints#get-index-price-candles

        :param symbol: the name of the contract
        :type symbol: str
        :param interval: The time interval for the Kline data. Must be one of "Min1", "Min5", "Min15", "Min30", "Min60", "Hour4", "Hour8", "Day1", "Week1", "Month1". Defaults to "Min1".
        :type interval: Optional[Literal["Min1", "Min5", "Min15", "Min30", "Min60", "Hour4", "Hour8", "Day1", "Week1", "Month1"]]
        :param start: (optional) The start time of the Kline data in Unix timestamp format.
        :type start: Optional[int]
        :param end: (optional) The end time of the Kline data in Unix timestamp format.
        :type end: Optional[int]

        :return: A dictionary containing the Kline data for the specified symbol and interval within the specified time range.
        :rtype: dict
        """
        return await self.call(
            "GET",
            f"api/v1/contract/kline/index_price/{symbol}",
            params=dict(symbol=symbol, interval=interval, start=start, end=end),
        )

    async def kline_fair_price(
        self,
        symbol: str,
        interval: Optional[
            Literal[
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
            ]
        ] = "Min1",
        start: Optional[int] = None,
        end: Optional[int] = None,
    ) -> dict:
        """
        ### Get Fair Price Candles

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/market-endpoints#get-fair-price-candles

        :param symbol: the name of the contract
        :type symbol: str
        :param interval: The time interval for the Kline data. Must be one of "Min1", "Min5", "Min15", "Min30", "Min60", "Hour4", "Hour8", "Day1", "Week1", "Month1". Defaults to "Min1".
        :type interval: Optional[Literal["Min1", "Min5", "Min15", "Min30", "Min60", "Hour4", "Hour8", "Day1", "Week1", "Month1"]]
        :param start: (optional) The start time of the Kline data in Unix timestamp format.
        :type start: Optional[int]
        :param end: (optional) The end time of the Kline data in Unix timestamp format.
        :type end: Optional[int]

        :return: A dictionary containing the Kline data for the specified symbol and interval within the specified time range.
        :rtype: dict
        """
        return await self.call(
            "GET",
            f"api/v1/contract/kline/fair_price/{symbol}",
            params=dict(symbol=symbol, interval=interval, start=start, end=end),
        )

    async def deals(self, symbol: str, limit: Optional[int] = 100) -> dict:
        """
        ### Get Recent Trades

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/market-endpoints#get-recent-trades

        :param symbol: the name of the contract
        :type symbol: str
        :param limit: (optional) consequence set quantity, maximum is 100, default 100 without setting
        :type limit: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "GET",
            f"api/v1/contract/deals/{symbol}",
            params=dict(symbol=symbol, limit=limit),
        )

    async def ticker(self, symbol: Optional[str] = None) -> dict:
        """
        ### Get Ticker (Contract Market Data)

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/market-endpoints#get-ticker-contract-market-data

        :param symbol: (optional) the name of the contract
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", "api/v1/contract/ticker", params=dict(symbol=symbol))

    async def risk_reverse(self, symbol: str) -> dict:
        """
        ### Get Insurance Fund Balance

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/market-endpoints#get-insurance-fund-balance

        :param symbol: Contract symbol
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", f"api/v1/contract/risk_reverse/{symbol}")

    async def risk_reverse_history(
        self, symbol: str, page_num: Optional[int] = 1, page_size: Optional[int] = 20
    ) -> dict:
        """
        ### Get Insurance Fund Balance History

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/market-endpoints#get-insurance-fund-balance-history

        :param symbol: the name of the contract
        :type symbol: str
        :param page_num: current page number, default is 1
        :type page_num: int
        :param page_size: 	the page size, default 20, maximum 100
        :type page_size: int

        :return: A dictionary containing the risk reverse history.
        """
        return await self.call(
            "GET",
            "api/v1/contract/risk_reverse/history",
            params=dict(symbol=symbol, page_num=page_num, page_size=page_size),
        )

    async def funding_rate_history(
        self, symbol: str, page_num: Optional[int] = 1, page_size: Optional[int] = 20
    ) -> dict:
        """
        ### Get Funding Rate History

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/market-endpoints#get-funding-rate-history

        :param symbol: the name of the contract
        :type symbol: str
        :param page_num: current page number, default is 1
        :type page_num: int
        :param page_size: 	the page size, default 20, maximum 1000
        :type page_size: int

        :return: A dictionary containing the funding rate history.
        """
        return await self.call(
            "GET",
            "api/v1/contract/funding_rate/history",
            params=dict(symbol=symbol, page_num=page_num, page_size=page_size),
        )

    # <=================================================================>
    #
    #                   Account and trading endpoints
    #
    # <=================================================================>

    async def assets(self) -> dict:
        """
        ### Get All Account Assets
        #### Required permissions: View Account Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-all-account-assets

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", "api/v1/private/account/assets")

    async def asset(self, currency: str) -> dict:
        """
        ### Get Single Currency Asset Information
        #### Required permissions: View Account Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-single-currency-asset-information

        :param currency: Currency
        :type currency: str
        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", f"api/v1/private/account/asset/{currency}")

    async def transfer_record(
        self,
        currency: Optional[str] = None,
        state: Optional[Literal["WAIT", "SUCCESS", "FAILED"]] = None,
        type: Optional[Literal["IN", "OUT"]] = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        ### Get Asset Transfer Records
        #### Required permissions: View Account Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-asset-transfer-records

        :param currency: (optional) The currency.
        :type currency: str
        :param state: (optional) state:WAIT 、SUCCESS 、FAILED
        :type state: str
        :param type: (optional) type:IN 、OUT
        :type type: str
        :param page_num: current page number, default is 1
        :type page_num: int
        :param page_size: page size, default 20, maximum 100
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "GET",
            "api/v1/private/account/transfer_record",
            params=dict(
                currency=currency,
                state=state,
                type=type,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    async def history_positions(
        self,
        symbol: Optional[str] = None,
        type: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        ### Get Historical Positions
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-historical-positions

        :param symbol: (optional) the name of the contract
        :type symbol: str
        :param type: (optional) position type: 1 - long, 2 -short
        :type type: int
        :param start_time: (optional) Start time
        :type start_time: int
        :param end_time: (optional) End time
        :type end_time: int
        :param page_num: current page number , default is 1
        :type page_num: int
        :param page_size: page size , default 20, maximum 100
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "GET",
            "api/v1/private/position/list/history_positions",
            params=dict(
                symbol=symbol,
                type=type,
                start_time=start_time,
                end_time=end_time,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    async def open_positions(self, symbol: Optional[str] = None, position_id: Optional[int] = None) -> dict:
        """
        ### Get Open Positions
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-open-positions

        :param symbol: (optional) the name of the contract
        :type symbol: str
        :param position_id: (optional) Position ID
        :type position_id: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "GET", "api/v1/private/position/open_positions", params=dict(symbol=symbol, positionId=position_id)
        )

    async def funding_records(
        self,
        position_type: int,
        start_time: int,
        end_time: int,
        symbol: Optional[str] = None,
        position_id: Optional[int] = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        ### Get Funding Fee Details
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-funding-fee-details

        :param symbol: (optional) the name of the contract
        :type symbol: str
        :param position_id: (optional) position id
        :type position_id: int
        :param position_type: Position type, 1 long 2 short
        :type position_type: int
        :param start_time: Start time
        :type start_time: int
        :param end_time: End time
        :type end_time: int
        :param page_num: current page number, default is 1
        :type page_num: int
        :param page_size: page size, default 20, maximum 100
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """

        return await self.call(
            "GET",
            "api/v1/private/position/funding_records",
            params=dict(
                symbol=symbol,
                position_id=position_id,
                position_type=position_type,
                start_time=start_time,
                end_time=end_time,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    async def open_orders(
        self,
        symbol: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        ### Get Current Open Orders
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-current-open-orders

        :param symbol: (optional) The name of the contract. Returns all contract parameters if not specified.
        :type symbol: str
        :param page_num: The current page number. Defaults to 1.
        :type page_num: int
        :param page_size: The page size. Defaults to 20. Maximum of 100.
        :type page_size: int

        :return: A dictionary containing the user's current pending order.
        :rtype: dict
        """
        if symbol:
            return await self.call(
                "GET",
                f"api/v1/private/order/open_orders/{symbol}",
                params=dict(page_num=page_num, page_size=page_size),
            )
        else:
            return await self.call(
                "GET",
                "api/v1/private/order/open_orders",
                params=dict(page_num=page_num, page_size=page_size),
            )

    async def history_orders(
        self,
        symbol: Optional[str] = None,
        states: Optional[str] = None,
        category: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        side: Optional[int] = None,
        order_id: Optional[int] = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        ### Get All Historical Orders
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-all-historical-orders

        :param symbol: (optional) The name of the contract. Returns all contract parameters if not specified.
        :type symbol: str
        :param states: (optional) The order state(s) to filter by. Multiple states can be separated by ','. Defaults to None.
        :type states: str
        :param category: (optional) The order category to filter by. Defaults to None.
        :type category: int
        :param start_time: (optional) The start time of the order history to retrieve. Defaults to None.
        :type start_time: int
        :param end_time: (optional) The end time of the order history to retrieve. Defaults to None.
        :type end_time: int
        :param side: (optional) The order direction to filter by. Defaults to None.
        :type side: int
        :param order_id: (optional) Order ID
        :type order_id: int
        :param page_num: The current page number. Defaults to 1.
        :type page_num: int
        :param page_size: The page size. Defaults to 20. Maximum of 100.
        :type page_size: int

        :return: A dictionary containing all of the user's historical orders.
        :rtype: dict
        """
        return await self.call(
            "GET",
            "api/v1/private/order/list/history_orders",
            params=dict(
                symbol=symbol,
                states=states,
                category=category,
                startTime=start_time,
                endTime=end_time,
                side=side,
                orderId=order_id,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    async def get_order_external(self, symbol: str, external_oid: str) -> dict:
        """
        ### Get Order by External ID
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-order-by-external-id

        :param symbol: The name of the contract.
        :type symbol: str
        :param external_oid: The external order ID.
        :type external_oid: str

        :return: A dictionary containing the queried order based on the external number.
        :rtype: dict
        """

        return await self.call("GET", f"api/v1/private/order/external/{symbol}/{external_oid}")

    async def get_order(self, order_id: Union[str, int]) -> dict:
        """
        ### Get Order Information by Order ID
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-order-information-by-order-id

        :param order_id: Order ID
        :type order_id: Union[str, int]

        :return: A dictionary containing the queried order based on the order number.
        :rtype: dict
        """
        return await self.call("GET", f"api/v1/private/order/get/{order_id}")

    async def batch_query(self, order_ids: Union[List[int], str]) -> dict:
        """
        ### Batch Query Orders by Order ID
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#batch-query-orders-by-order-id

        :param order_ids: An array of order IDs, separated by ",". Maximum of 50 orders.
        :type order_ids: Union[List[int], str]

        :return: A dictionary containing the queried orders in bulk based on the order number.
        :rtype: dict
        """
        if isinstance(order_ids, list):
            order_ids_str = ",".join(str(oid) for oid in order_ids)
        else:
            order_ids_str = order_ids
        return await self.call(
            "GET",
            "api/v1/private/order/batch_query",
            params=dict(order_ids=order_ids_str),
        )

    async def deal_details(self, symbol: str, order_id: Union[str, int]) -> dict:
        """
        ### Get Trade Details by Order ID
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-trade-details-by-order-id

        :param symbol: Contract symbol
        :type symbol: str
        :param order_id: The ID of the order to retrieve transaction details for.
        :type order_id: Union[str, int]

        :return: A dictionary containing the transaction details for the given order ID.
        :rtype: dict
        """
        return await self.call("GET", f"api/v1/private/order/deal_details/{order_id}", params=dict(symbol=symbol))

    async def order_deals(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        ### Get Historical Order Deal Details
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-historical-order-deal-details

        :param symbol: the name of the contract
        :type symbol: str
        :param start_time: (optional) the starting time, the default is to push forward 7 days, and the maximum span is 90 days
        :type start_time: int
        :param end_time: (optional) the end time, start and end time span is 90 days
        :type end_time: int
        :param page_num: current page number, default is 1
        :type page_num: int
        :param page_size: page size , default 20, maximum 1000
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "GET",
            "api/v1/private/order/list/order_deals/v3",
            params=dict(
                symbol=symbol,
                start_time=start_time,
                end_time=end_time,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    async def get_trigger_orders(
        self,
        symbol: Optional[str] = None,
        states: Optional[str] = None,
        side: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        ### Get Plan Order List
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-plan-order-list

        :param symbol: (optional) the name of the contract
        :type symbol: str
        :param states: (optional) order state, 1 untriggered, 2 canceled, 3 executed, 4 invalidated, 5 execution failed; Multiple separate by ','
        :type states: str
        :param side: (optional) Order side,1: open long,2: close short,3: open short,4: close long
        :type side: int
        :param start_time: (optional) start time, 13-digit timestamp
        :type start_time: int
        :param end_time: (optional) end time, 13-digit timestamp
        :type end_time: int
        :param page_num: current page number, default is 1
        :type page_num: int
        :param page_size: page size, default 20, maximum 100
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "GET",
            "api/v1/private/planorder/list/orders",
            params=dict(
                symbol=symbol,
                states=states,
                side=side,
                start_time=start_time,
                end_time=end_time,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    async def get_stop_limit_orders(
        self,
        symbol: Optional[str] = None,
        is_finished: Optional[int] = None,
        state: Optional[int] = None,
        type: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        ### Get Take-Profit/Stop-Loss Order List
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-take-profitstop-loss-order-list

        :param symbol: (optional) the name of the contract
        :type symbol: str
        :param is_finished: (optional) final state indicator :0: unfinished, 1: finished
        :type is_finished: int
        :param state: (optional) Status：1 untriggered 2 canceled 3 executed 4 invalidated 5 execution failed
        :type state: int
        :param type: (optional) Position type,1: long，2: short
        :type type: int
        :param start_time: (optional) start time, 13-digit timestamp
        :type start_time: int
        :param end_time: (optional) end time, 13-digit timestamp
        :type end_time: int
        :param page_num: current page number, default is 1
        :type page_num: int
        :param page_size: page size, default 20, maximum 100
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """

        return await self.call(
            "GET",
            "api/v1/private/stoporder/list/orders",
            params=dict(
                symbol=symbol,
                is_finished=is_finished,
                state=state,
                type=type,
                start_time=start_time,
                end_time=end_time,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    async def risk_limit(self, symbol: Optional[str] = None) -> dict:
        """
        ### Get Risk Limits
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-risk-limits

        :param symbol: (optional) the name of the contract , not uploaded will return all
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", "api/v1/private/account/risk_limit", params=dict(symbol=symbol))

    async def tiered_fee_rate(self, symbol: Optional[str] = None) -> dict:
        """
        ### Get Fee Details
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-fee-details

        :param symbol: (optional) the name of the contract; when symbol is provided, query fee rate info under that contract
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """

        return await self.call("GET", "api/v1/private/account/tiered_fee_rate/v2", params=dict(symbol=symbol))

    async def change_margin(self, position_id: int, amount: float, type: str) -> dict:
        """
        ### Modify Position Margin (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#modify-position-marginunder-maintenance

        :param position_id: position id
        :type position_id: int
        :param amount: amount
        :type amount: float
        :param type: type, ADD: increase, SUB: decrease
        :type type: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "POST",
            "api/v1/private/position/change_margin",
            params=dict(positionId=position_id, amount=amount, type=type),
        )

    async def get_leverage(self, symbol: str) -> dict:
        """
        ### Get Position Leverage Multipliers
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-position-leverage-multipliers

        :param symbol: Contract name
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """

        return await self.call("GET", "api/v1/private/position/leverage", params=dict(symbol=symbol))

    async def change_leverage(
        self,
        leverage: int,
        position_id: Optional[int] = None,
        open_type: Optional[int] = None,
        symbol: Optional[str] = None,
        position_type: Optional[int] = None,
        leverage_mode: Optional[int] = None,
        margin_selected: Optional[bool] = None,
        leverage_selected: Optional[bool] = None,
    ) -> dict:
        """
        ### Modify Leverage (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#modify-leverageunder-maintenance

        :param leverage: leverage
        :type leverage: int
        :param position_id: (optional) position id, provide when a position exists
        :type position_id: int
        :param open_type: (optional) Required when there is no position, openType, 1: isolated, 2: cross
        :type open_type: int
        :param symbol: (optional) Required when there is no position, contract name
        :type symbol: str
        :param position_type: (optional) When no position exists, position type， 1 long 2 short
        :type position_type: int
        :param leverage_mode: (optional) Leverage mode 1: advanced mode 2: simple mode
        :type leverage_mode: int
        :param margin_selected: (optional) Flag for adjusting all contracts' margin mode - whether selected
        :type margin_selected: bool
        :param leverage_selected: (optional) Flag for adjusting all contracts' leverage mode - whether selected
        :type leverage_selected: bool

        :return: response dictionary
        :rtype: dict
        """

        return await self.call(
            "POST",
            "api/v1/private/position/change_leverage",
            params=dict(
                positionId=position_id,
                leverage=leverage,
                openType=open_type,
                symbol=symbol,
                positionType=position_type,
                leverageMode=leverage_mode,
                marginSelected=margin_selected,
                leverageSelected=leverage_selected,
            ),
        )

    async def get_position_mode(self) -> dict:
        """
        ### Get User Position Mode
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-user-position-mode

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", "api/v1/private/position/position_mode")

    async def change_position_mode(self, position_mode: int) -> dict:
        """
        ### Modify User Position Mode (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#modify-user-position-modeunder-maintenance

        :param position_mode: 1: dual-side, 2: one-way. To modify the position mode, you must ensure there are no active orders, plan orders, or unfinished positions; otherwise, it cannot be modified. When switching from dual-side to one-way mode, the risk limit level will reset to level 1. To change it, call the interface to modify.
        :type position_mode: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "POST",
            "api/v1/private/position/change_position_mode",
            params=dict(positionMode=position_mode),
        )

    async def order(
        self,
        symbol: str,
        price: float,
        vol: float,
        side: int,
        type: int,
        open_type: int,
        position_id: Optional[int] = None,
        leverage: Optional[int] = None,
        external_oid: Optional[str] = None,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
        loss_trend: Optional[int] = None,
        profit_trend: Optional[int] = None,
        price_protect: Optional[int] = None,
        position_mode: Optional[int] = None,
        reduce_only: Optional[bool] = False,
        market_ceiling: Optional[bool] = None,
        flash_close: Optional[bool] = None,
        bbo_type_num: Optional[int] = None,
    ) -> dict:
        """
        ### Place Order (Under Maintenance)
        #### Required permissions: Trading permission

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#place-order-under-maintenance

        :param symbol: the name of the contract
        :type symbol: str
        :param price: price
        :type price: float
        :param vol: volume
        :type vol: float
        :param leverage: (optional) leverage, must be provided when opening a position
        :type leverage: int
        :param side: order direction 1 open long, 2 close short, 3 open short, 4 close long
        :type side: int
        :param type: orderType,1: limit,2: Post Only (maker only),3: IOC,4: FOK,5: market
        :type type: int
        :param open_type: open type,1: isolated,2: cross
        :type open_type: int
        :param position_id: (optional) position Id, It is recommended to fill in this parameter when closing a position
        :type position_id: int
        :param external_oid: (optional) external order ID
        :type external_oid: str
        :param stop_loss_price: (optional) stop-loss price
        :type stop_loss_price: float
        :param take_profit_price: (optional) take-profit price
        :type take_profit_price: float
        :param loss_trend: (optional) Stop-loss price type;1: latest price (default);2: fair price;3: index price
        :type loss_trend: int
        :param profit_trend: (optional) Take-profit price type;1: latest price (default);2: fair price;3: index price
        :type profit_trend: int
        :param price_protect: (optional) Conditional order trigger protection: "1","0", default "0" disabled. Required only for plan orders/TP-SL orders
        :type price_protect: int
        :param position_mode: (optional) position mode, default dual-side; 2: one-way; 1: dual-side
        :type position_mode: int
        :param reduce_only: (optional) Reduce-only, only applicable in one-way mode
        :type reduce_only: bool
        :param market_ceiling: (optional) 100% market open
        :type market_ceiling: bool
        :param flash_close: (optional) Flash close
        :type flash_close: bool
        :param bbo_type_num: (optional) Limit order type - BBO type; 0: not BBO;1: opposite-1;2: opposite-5;3: same-side-1;4: same-side-5;
        :type bbo_type_num: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "POST",
            "api/v1/private/order/create",
            params=dict(
                symbol=symbol,
                price=price,
                vol=vol,
                side=side,
                type=type,
                openType=open_type,
                positionId=position_id,
                leverage=leverage,
                externalOid=external_oid,
                stopLossPrice=stop_loss_price,
                takeProfitPrice=take_profit_price,
                lossTrend=loss_trend,
                profitTrend=profit_trend,
                priceProtect=price_protect,
                positionMode=position_mode,
                reduceOnly=reduce_only,
                marketCeiling=market_ceiling,
                flashClose=flash_close,
                bboTypeNum=bbo_type_num,
            ),
        )

    async def bulk_order(
        self,
        symbol: str,
        price: float,
        vol: float,
        side: int,
        type: int,
        open_type: int,
        position_id: Optional[int] = None,
        external_oid: Optional[str] = None,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
    ) -> dict:
        """
        ### Bulk order (Under maintenance)
        #### Required permissions: Trading permission

        Rate limit: 1/2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#bulk-order-under-maintenance

        :param symbol: the name of the contract
        :type symbol: str
        :param price: price
        :type price: decimal
        :param vol: volume
        :type vol: decimal
        :param leverage: (optional) leverage, Leverage is necessary on Isolated Margin
        :type leverage: int
        :param side: order side 1open long,2close short,3open short, 4 close long
        :type side: int
        :param type: order type :1 price limited order,2:Post Only Maker,3:transact or cancel instantly ,4 : transact completely or cancel completely，5:market orders,6 convert market price to current price
        :type type: int
        :param openType: open type,1:isolated,2:cross
        :type openType: int
        :param positionId: (optional) position Id, It is recommended to fill in this parameter when closing a position
        :type positionId: int
        :param externalOid: (optional) external order ID, return the existing order ID if it already exists
        :type externalOid: str
        :param stopLossPrice: (optional) stop-loss price
        :type stopLossPrice: decimal
        :param takeProfitPrice: (optional) take-profit price
        :type takeProfitPrice: decimal

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "POST",
            "api/v1/private/order/submit_batch",
            params=dict(
                symbol=symbol,
                price=price,
                vol=vol,
                side=side,
                type=type,
                openType=open_type,
                positionId=position_id,
                externalOid=external_oid,
                stopLossPrice=stop_loss_price,
                takeProfitPrice=take_profit_price,
            ),
        )

    async def cancel_order(self, order_ids: Union[List[int], int]) -> dict:
        """
        ### Cancel the order (Under maintenance)
        #### Required permissions: Trading permission

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#cancel-orders-under-maintenance

        :param order_ids: list of order ids to cancel, maximum 50
        :type order_ids: List[int]

        :return: dictionary containing the order ID and error message, if any
        :rtype: dict
        """

        return await self.call(
            "POST",
            "api/v1/private/order/cancel",
            json=order_ids if isinstance(order_ids, list) else [order_ids],
        )

    async def cancel_order_with_external(self, orders: List[Dict[str, str]]) -> dict:
        """
        ### Cancel by External Order ID (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#cancel-by-external-order-idunder-maintenance

        :param orders: list collection; e.g. [{"symbol":"BTC_USDT", "externalOid":"ext_11"}]
        :type orders: List[Dict[str, str]]

        :return: response dictionary
        :rtype: dict
        """

        return await self.call(
            "POST",
            "api/v1/private/order/cancel_with_external",
            json=orders,
        )

    async def cancel_all(self, symbol: Optional[str] = None) -> dict:
        """
        ### Cancel all orders under a contract (Under maintenance)

        #### Required permissions: Trading permission

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#cancel-all-orders-under-a-contractunder-maintenance

        :param symbol: (optional) the name of the contract, cancel specific orders placed under this contract when fill the symbol , otherwise , cancel all orders without filling
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """

        return await self.call("POST", "api/v1/private/order/cancel_all", params=dict(symbol=symbol))

    async def change_risk_level(self) -> dict:
        """
        ### Switch the risk level

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#change-risk-levelunder-maintenance

        :return: None
        :rtype: None
        """

        return await self.call("POST", "api/v1/private/account/change_risk_level")

    async def trigger_order(
        self,
        symbol: str,
        vol: float,
        side: int,
        open_type: int,
        trigger_price: float,
        trigger_type: int,
        execute_cycle: int,
        order_type: int,
        trend: int,
        leverage: int,
        price: Optional[float] = None,
        price_protect: Optional[int] = None,
        position_mode: Optional[int] = None,
        loss_trend: Optional[int] = None,
        profit_trend: Optional[int] = None,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
        reduce_only: Optional[bool] = None,
    ) -> dict:
        """
        ### Place Plan Order (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#place-plan-orderunder-maintenance

        :param symbol: the name of the contract
        :type symbol: str
        :param price: (optional) execute price, not required for market
        :type price: float
        :param vol: volume
        :type vol: float
        :param leverage: leverage, required when opening
        :type leverage: int
        :param side: 1 open long, 2 close short, 3 open short, 4 close long
        :type side: int
        :param open_type: open type, 1: isolated, 2: cross
        :type open_type: int
        :param trigger_price: trigger price
        :type trigger_price: float
        :param trigger_type: trigger type, 1: greater than or equal to，2: less than or equal to
        :type trigger_type: int
        :param execute_cycle: execution cycle, 1: 24 hours, 2: 7 days
        :type execute_cycle: int
        :param order_type: order type, 1: limit, 2: Post Only (maker only), 3: IOC, 4: FOK, 5: market
        :type order_type: int
        :param trend: trigger price type, 1: latest price，2: fair price，3: index price
        :type trend: int
        :param price_protect: (optional) Conditional order trigger protection: "1","0", default "0" disabled
        :type price_protect: int
        :param position_mode: (optional) User-set position type default 0: historical orders no record 2: one-way 1: dual-side
        :type position_mode: int
        :param loss_trend: (optional) Stop-loss reference price type 1 latest price 2 fair price 3 index price
        :type loss_trend: int
        :param profit_trend: (optional) Take-profit reference price type 1 latest price 2 fair price 3 index price
        :type profit_trend: int
        :param stop_loss_price: (optional) Stop-loss price
        :type stop_loss_price: float
        :param take_profit_price: (optional) Take-profit price
        :type take_profit_price: float
        :param reduce_only: (optional) Reduce-only
        :type reduce_only: bool

        :return: response dictionary
        :rtype: dict
        """

        return await self.call(
            "POST",
            "api/v1/private/planorder/place/v2",
            params=dict(
                symbol=symbol,
                price=price,
                vol=vol,
                leverage=leverage,
                side=side,
                openType=open_type,
                triggerPrice=trigger_price,
                triggerType=trigger_type,
                executeCycle=execute_cycle,
                orderType=order_type,
                trend=trend,
                priceProtect=price_protect,
                positionMode=position_mode,
                lossTrend=loss_trend,
                profitTrend=profit_trend,
                stopLossPrice=stop_loss_price,
                takeProfitPrice=take_profit_price,
                reduceOnly=reduce_only,
            ),
        )

    async def cancel_trigger_order(self, orders: List[Dict[str, Union[str, int]]]) -> dict:
        """
        ### Cancel Planned Orders (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#cancel-planned-ordersmaintenance

        :param orders: list of orders to be cancelled (maximum of 50), e.g. [{"symbol":"BTC_USDT","orderId":1}]
        :type orders: List[Dict[str, Union[str, int]]]

        :return: response dictionary
        :rtype: dict
        """

        return await self.call("POST", "api/v1/private/planorder/cancel", json=orders)

    async def cancel_all_trigger_orders(self, symbol: Optional[str] = None) -> dict:
        """
        ### Cancel all trigger orders (Under maintenance)

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#cancel-all-planned-ordersmaintenance

        :param symbol: (optional) the name of the contract, cancel specific orders placed under this contract when filled, otherwise, cancel all orders without filling
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """

        return await self.call("POST", "api/v1/private/planorder/cancel_all", params=dict(symbol=symbol))

    async def cancel_stop_order(self, orders: List[Dict[str, int]]) -> dict:
        """
        ### Cancel TP/SL Planned Orders (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#cancel-tpsl-planned-ordersmaintenance

        :param orders: list of orders to be cancelled (maximum of 50), e.g. [{"stopPlanOrderId":1}]
        :type orders: List[Dict[str, int]]

        :return: response dictionary
        :rtype: dict
        """

        return await self.call("POST", "api/v1/private/stoporder/cancel", json=orders)

    async def cancel_all_stop_order(self, position_id: Optional[int] = None, symbol: Optional[str] = None) -> dict:
        """
        ### Cancel all Stop-Limit price trigger orders (Under maintenance)

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#cancel-all-tpsl-planned-ordersmaintenance

        :param positionId: (optional) position id, fill in positionId to only cancel the trigger order of the corresponding position, otherwise check the symbol without filling
        :type positionId: int
        :param symbol: (optional) the name of the contract, only cancels the delegate order under this contract based on the symbol, cancel all orders without filling the symbol
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """

        return await self.call(
            "POST",
            "api/v1/private/stoporder/cancel_all",
            params=dict(positionId=position_id, symbol=symbol),
        )

    async def stop_limit_change_price(
        self,
        order_id: int,
        symbol: str,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
        loss_trend: Optional[int] = None,
        profit_trend: Optional[int] = None,
        take_profit_reverse: Optional[int] = None,
        stop_loss_reverse: Optional[int] = None,
    ) -> dict:
        """
        ### Switch Stop-Limit limited order price

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#modify-tpsl-prices-on-a-limit-orderunder-maintenance

        :param orderId: the limit order ID
        :type orderId: int
        :param stopLossPrice: (optional) stop-loss price, if take-profit and stop-loss price are empty or 0 at the same time, it indicates to cancel and take profit
        :type stopLossPrice: int
        :param takeProfitPrice: (optional) take-profit price, if take-profit and stop-loss price are empty or 0 at the same time, it indicates to cancel stop-loss and take profit
        :type takeProfitPrice: int

        :return: response dictionary
        :rtype: dict
        """

        return await self.call(
            "POST",
            "api/v1/private/stoporder/change_price",
            params=dict(
                orderId=order_id,
                symbol=symbol,
                stopLossPrice=stop_loss_price,
                takeProfitPrice=take_profit_price,
                lossTrend=loss_trend,
                profitTrend=profit_trend,
                takeProfitReverse=take_profit_reverse,
                stopLossReverse=stop_loss_reverse,
            ),
        )

    async def stop_limit_change_plan_price(
        self,
        stop_plan_order_id: int,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
        loss_trend: Optional[int] = None,
        profit_trend: Optional[int] = None,
        take_profit_reverse: Optional[int] = None,
        stop_loss_reverse: Optional[int] = None,
    ) -> dict:
        """
        ### Switch the Stop-Limit price of trigger orders

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#modify-tpsl-prices-on-a-tpsl-planned-orderunder-maintenance

        :param stopPlanOrderId: the Stop-Limit price of trigger order ID
        :type stopPlanOrderId: int
        :param stopLossPrice: (optional) stop-loss price. At least one stop-loss price and one take-profit price must not be empty and must be more than 0.
        :type stopLossPrice: int
        :param takeProfitPrice: (optional) take-profit price. At least one take-profit price and stop-loss price must not be empty and must be more than 0.
        :type takeProfitPrice: int

        :return: response dictionary
        :rtype: dict
        """

        return await self.call(
            "POST",
            "api/v1/private/stoporder/change_plan_price",
            params=dict(
                stopPlanOrderId=stop_plan_order_id,
                stopLossPrice=stop_loss_price,
                takeProfitPrice=take_profit_price,
                lossTrend=loss_trend,
                profitTrend=profit_trend,
                takeProfitReverse=take_profit_reverse,
                stopLossReverse=stop_loss_reverse,
            ),
        )

    async def close_orders(
        self,
        symbol: Optional[str] = None,
        category: Optional[int] = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        ### Get Closed Orders
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-closed-orders

        :param symbol: (optional) Contract
        :type symbol: str
        :param category: (optional) Order category,1: limit,2: liquidation custody,3: custody close,4: ADL reduction
        :type category: int
        :param page_num: current page number, default is 1
        :type page_num: int
        :param page_size: page size, default 20, max 100
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "GET",
            "api/v1/private/order/close_orders",
            params=dict(symbol=symbol, category=category, page_num=page_num, page_size=page_size),
        )

    async def open_stop_orders(self, symbol: Optional[str] = None) -> dict:
        """
        ### Get Current Take-Profit/Stop-Loss Order List
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#get-current-take-profitstop-loss-order-list

        :param symbol: (optional) Contract
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", "api/v1/private/stoporder/open_orders", params=dict(symbol=symbol))

    async def batch_query_with_external(self, orders: List[Dict[str, str]]) -> dict:
        """
        ### Batch Query - Get Orders by External Order ID
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#batch-query---get-orders-by-external-order-id

        :param orders: list collection; e.g. [{"symbol":"BTC_USDT", "externalOid":"ext_11"}]
        :type orders: List[Dict[str, str]]

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("POST", "api/v1/private/order/batch_query_with_external", json=orders)

    async def place_stop_order(
        self,
        position_id: int,
        vol: float,
        loss_trend: int,
        profit_trend: int,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
        price_protect: Optional[int] = None,
        profit_loss_vol_type: Optional[str] = None,
        take_profit_vol: Optional[float] = None,
        stop_loss_vol: Optional[float] = None,
        vol_type: Optional[int] = None,
        take_profit_reverse: Optional[int] = None,
        stop_loss_reverse: Optional[int] = None,
        mtoken: Optional[str] = None,
        take_profit_type: Optional[int] = None,
        take_profit_order_price: Optional[float] = None,
        stop_loss_type: Optional[int] = None,
        stop_loss_order_price: Optional[float] = None,
    ) -> dict:
        """
        ### Place TP/SL Order by Position (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#place-tpsl-order-by-positionunder-maintenance

        :param position_id: Position id
        :type position_id: int
        :param vol: Order quantity; must be within the allowed range for the contract; the order quantity plus existing TP/SL order quantity must be less than the closable quantity; position quantity will not be frozen, but checks are required
        :type vol: float
        :param loss_trend: Stop-loss type: 1 latest price 2 fair price 3 index price
        :type loss_trend: int
        :param profit_trend: Take-profit type: 1 latest price 2 fair price 3 index price
        :type profit_trend: int
        :param stop_loss_price: (optional) Stop-loss price; at least one of stop-loss or take-profit must be non-empty and greater than 0
        :type stop_loss_price: float
        :param take_profit_price: (optional) Take-profit price; at least one of stop-loss or take-profit must be non-empty and greater than 0
        :type take_profit_price: float
        :param price_protect: (optional) Trigger protection: "1","0"
        :type price_protect: int
        :param profit_loss_vol_type: (optional) TP/SL quantity type (SAME: same quantity; SEPARATE: different quantities)
        :type profit_loss_vol_type: str
        :param take_profit_vol: (optional) Take-profit quantity (when profitLossVolType == SEPARATE)
        :type take_profit_vol: float
        :param stop_loss_vol: (optional) Stop-loss quantity (when profitLossVolType == SEPARATE)
        :type stop_loss_vol: float
        :param vol_type: (optional) Quantity type 1: partial TP/SL 2: position TP/SL
        :type vol_type: int
        :param take_profit_reverse: (optional) Take-profit reverse: 1 yes 2 no
        :type take_profit_reverse: int
        :param stop_loss_reverse: (optional) Stop-loss reverse: 1 yes 2 no
        :type stop_loss_reverse: int
        :param mtoken: (optional) Web device id
        :type mtoken: str
        :param take_profit_type: (optional) Take-profit type 0 - market TP 1 - limit TP
        :type take_profit_type: int
        :param take_profit_order_price: (optional) Limit TP order price
        :type take_profit_order_price: float
        :param stop_loss_type: (optional) Stop-loss type 0 - market SL 1 - limit SL
        :type stop_loss_type: int
        :param stop_loss_order_price: (optional) Limit SL order price
        :type stop_loss_order_price: float

        :return: response dictionary
        :rtype: dict
        """

        return await self.call(
            "POST",
            "api/v1/private/stoporder/place",
            params=dict(
                positionId=position_id,
                vol=vol,
                lossTrend=loss_trend,
                profitTrend=profit_trend,
                stopLossPrice=stop_loss_price,
                takeProfitPrice=take_profit_price,
                priceProtect=price_protect,
                profitLossVolType=profit_loss_vol_type,
                takeProfitVol=take_profit_vol,
                stopLossVol=stop_loss_vol,
                volType=vol_type,
                takeProfitReverse=take_profit_reverse,
                stopLossReverse=stop_loss_reverse,
                mtoken=mtoken,
                takeProfitType=take_profit_type,
                takeProfitOrderPrice=take_profit_order_price,
                stopLossType=stop_loss_type,
                stopLossOrderPrice=stop_loss_order_price,
            ),
        )

    async def close_all(self) -> dict:
        """
        ### Close All (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#close-allunder-maintenance

        :return: response dictionary
        :rtype: dict
        """

        return await self.call("POST", "api/v1/private/position/close_all")

    async def reverse_position(self, symbol: str, position_id: int, vol: float) -> dict:
        """
        ### Reverse Open Position (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#reverse-open-positionunder-maintenance

        :param symbol: Contract
        :type symbol: str
        :param position_id: Position id
        :type position_id: int
        :param vol: Quantity
        :type vol: float

        :return: response dictionary
        :rtype: dict
        """

        return await self.call(
            "POST",
            "api/v1/private/position/reverse",
            params=dict(symbol=symbol, positionId=position_id, vol=vol),
        )

    async def change_limit_order(self, order_id: int, price: float, vol: float) -> dict:
        """
        ### Modify Order Price & Quantity (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#modify-order-price--quantityunder-maintenance

        :param order_id: Order ID
        :type order_id: int
        :param price: Price
        :type price: float
        :param vol: Quantity
        :type vol: float

        :return: response dictionary
        :rtype: dict
        """

        return await self.call(
            "POST",
            "api/v1/private/order/change_limit_order",
            params=dict(orderId=order_id, price=price, vol=vol),
        )

    async def chase_limit_order(self, order_id: int) -> dict:
        """
        ### Chase Order (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 times / 2 seconds

        Modify order price to the corresponding one-tick price

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#chase-orderunder-maintenance

        :param order_id: Order ID
        :type order_id: int

        :return: response dictionary
        :rtype: dict
        """

        return await self.call(
            "POST",
            "api/v1/private/order/chase_limit_order",
            params=dict(orderId=order_id),
        )

    async def open_order_total_count(self) -> dict:
        """
        ### Query In-Flight Order Counts
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#query-in-flight-order-counts

        :return: response dictionary
        :rtype: dict
        """

        return await self.call("POST", "api/v1/private/order/open_order_total_count")

    async def change_auto_add_im(self, position_id: int, is_enabled: bool) -> dict:
        """
        ### Enable or Disable Auto-Add Margin (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 requests / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#enable-or-disable-auto-add-marginunder-maintenance

        :param position_id: Position ID
        :type position_id: int
        :param is_enabled: Whether to enable
        :type is_enabled: bool

        :return: response dictionary
        :rtype: dict
        """

        return await self.call(
            "POST",
            "api/v1/private/position/change_auto_add_im",
            params=dict(positionId=position_id, isEnabled=is_enabled),
        )

    async def batch_cancel_with_external(self, orders: List[Dict[str, str]]) -> dict:
        """
        ### Batch Cancel by External Order ID (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#batch-cancel-by-external-order-idunder-maintenance

        :param orders: list collection; e.g. [{"symbol":"BTC_USDT", "externalOid":"ext_11"}]
        :type orders: List[Dict[str, str]]

        :return: response dictionary
        :rtype: dict
        """

        return await self.call(
            "POST",
            "api/v1/private/order/batch_cancel_with_external",
            json=orders,
        )

    async def profit_rate(self, type: int) -> dict:
        """
        ### View Personal Profit Rate
        #### Required permissions: View Account Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#view-personal-profit-rate

        :param type: Type: 1 Day; 2 Week
        :type type: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", f"api/v1/private/account/profit_rate/{type}")

    async def asset_analysis(
        self,
        currency: str,
        type: int,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> dict:
        """
        ### Asset Analysis
        #### Required permissions: View Account Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#asset-analysis

        :param currency: Currency
        :type currency: str
        :param type: Type: 1 This week; 2 This month; 3 All; 4 Custom time range
        :type type: int
        :param start_time: (optional) Start time (ms)
        :type start_time: int
        :param end_time: (optional) End time (ms)
        :type end_time: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "GET",
            f"api/v1/private/account/asset/analysis/{type}",
            params=dict(currency=currency, startTime=start_time, endTime=end_time),
        )

    async def yesterday_pnl(self) -> dict:
        """
        ### Yesterday's PnL
        #### Required permissions: View Account Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#yesterdays-pnl

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", "api/v1/private/account/asset/analysis/yesterday_pnl")

    async def asset_analysis_v3(
        self,
        start_time: int,
        end_time: int,
        reverse: Optional[int] = None,
        include_unrealised_pnl: Optional[int] = None,
        symbol: Optional[str] = None,
    ) -> dict:
        """
        ### User Asset Analysis API
        #### Required permissions: View Account Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#user-asset-analysis-api

        :param start_time: Start time (ms)
        :type start_time: int
        :param end_time: End time (ms)
        :type end_time: int
        :param reverse: (optional) Contract type: 0 All; 1 USDT-M; 2 Coin-M; 3 USDC-M
        :type reverse: int
        :param include_unrealised_pnl: (optional) Include unrealized PnL: 0 No; 1 Yes
        :type include_unrealised_pnl: int
        :param symbol: (optional) Trading pair
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "POST",
            "api/v1/private/account/asset/analysis/v3",
            params=dict(
                startTime=start_time,
                endTime=end_time,
                reverse=reverse,
                includeUnrealisedPnl=include_unrealised_pnl,
                symbol=symbol,
            ),
        )

    async def asset_analysis_calendar_daily_v3(
        self,
        start_time: int,
        end_time: int,
        reverse: Optional[int] = None,
        include_unrealised_pnl: Optional[int] = None,
    ) -> dict:
        """
        ### User Asset Calendar Analysis (Daily)
        #### Required permissions: View Account Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#user-asset-calendar-analysis-daily

        :param start_time: Start time (ms)
        :type start_time: int
        :param end_time: End time (ms)
        :type end_time: int
        :param reverse: (optional) Contract type: 0 All; 1 USDT-M; 2 Coin-M; 3 USDC-M
        :type reverse: int
        :param include_unrealised_pnl: (optional) Include unrealized PnL: 0 No; 1 Yes
        :type include_unrealised_pnl: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "POST",
            "api/v1/private/account/asset/analysis/calendar/daily/v3",
            params=dict(
                startTime=start_time,
                endTime=end_time,
                reverse=reverse,
                includeUnrealisedPnl=include_unrealised_pnl,
            ),
        )

    async def asset_analysis_calendar_monthly_v3(
        self,
        reverse: Optional[int] = None,
        include_unrealised_pnl: Optional[int] = None,
    ) -> dict:
        """
        ### User Asset Calendar Analysis (Monthly)
        #### Required permissions: View Account Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#user-asset-calendar-analysis-monthly

        :param reverse: (optional) Contract type: 0 All; 1 USDT-M; 2 Coin-M; 3 USDC-M
        :type reverse: int
        :param include_unrealised_pnl: (optional) Include unrealized PnL: 0 No; 1 Yes
        :type include_unrealised_pnl: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "POST",
            "api/v1/private/account/asset/analysis/calendar/monthly/v3",
            params=dict(reverse=reverse, includeUnrealisedPnl=include_unrealised_pnl),
        )

    async def asset_analysis_recent_v3(
        self,
        reverse: Optional[int] = None,
        include_unrealised_pnl: Optional[int] = None,
        symbol: Optional[str] = None,
    ) -> dict:
        """
        ### Recent User Asset Analysis
        #### Required permissions: View Account Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#recent-user-asset-analysis

        :param reverse: (optional) Contract type: 0 All; 1 USDT-M; 2 Coin-M; 3 USDC-M
        :type reverse: int
        :param include_unrealised_pnl: (optional) Include unrealized PnL: 0 No; 1 Yes
        :type include_unrealised_pnl: int
        :param symbol: (optional) Trading pair
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "POST",
            "api/v1/private/account/asset/analysis/recent/v3",
            params=dict(reverse=reverse, includeUnrealisedPnl=include_unrealised_pnl, symbol=symbol),
        )

    async def today_pnl(
        self,
        reverse: Optional[int] = None,
        include_unrealised_pnl: Optional[int] = None,
    ) -> dict:
        """
        ### Today's User Asset Analysis
        #### Required permissions: View Account Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#todays-user-asset-analysis

        :param reverse: (optional) Contract type: 0 All; 1 USDT-M; 2 Coin-M; 3 USDC-M
        :type reverse: int
        :param include_unrealised_pnl: (optional) Include unrealized PnL: 0 No; 1 Yes
        :type include_unrealised_pnl: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "GET",
            "api/v1/private/account/asset/analysis/today_pnl",
            params=dict(reverse=reverse, includeUnrealisedPnl=include_unrealised_pnl),
        )

    async def contract_fee_discount_config(self) -> dict:
        """
        ### Query All Spot Discount Configuration Information
        #### Required permissions: View Account Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#query-all-spot-discount-configuration-information

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", "api/v1/private/account/config/contractFeeDiscountConfig")

    async def fee_details(
        self,
        symbol: str,
        ids: Optional[List[int]] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        ### Query Contract Fee Deduction Details
        #### Required permissions: View Order Details

        Rate limit: 20 requests / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#query-contract-fee-deduction-details

        :param symbol: Contract name
        :type symbol: str
        :param ids: (optional) Deal ID; up to 20 can be sent in a batch
        :type ids: List[int]
        :param start_time: (optional) Start time; if omitted, defaults to current time minus 7 days; max span 90 days
        :type start_time: int
        :param end_time: (optional) End time; the span between start and end is 90 days
        :type end_time: int
        :param page_num: (optional) Current page number, default 1
        :type page_num: int
        :param page_size: (optional) Page size, default 20, max 100
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """
        params = dict(symbol=symbol, page_num=page_num, page_size=page_size)
        if ids:
            params["ids"] = ",".join(str(id) for id in ids)
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        return await self.call("GET", "api/v1/private/order/fee_details", params=params)

    async def discount_type(self) -> dict:
        """
        ### Query User Discount Usage
        #### Required permissions: View Account Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#query-user-discount-usage

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", "api/v1/private/account/discountType")

    async def export_pnl_analysis(
        self,
        start_time: int,
        end_time: int,
        file_type: int,
        language: str,
        timezone: str,
        reverse: Optional[int] = None,
        include_unrealised_pnl: Optional[int] = None,
        symbol: Optional[str] = None,
    ) -> dict:
        """
        ### Export PnL Analysis
        #### Required permissions: View Account Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#export-pnl-analysis

        :param start_time: Export start time (ms)
        :type start_time: int
        :param end_time: Export end time (ms)
        :type end_time: int
        :param file_type: File type: 1-EXCEL 2-PDF
        :type file_type: int
        :param language: Language; e.g., zh-CN
        :type language: str
        :param timezone: Timezone; e.g., UTC+08:00
        :type timezone: str
        :param reverse: (optional) Contract type: 0: All; 1: USDT-M; 2: Coin-M
        :type reverse: int
        :param include_unrealised_pnl: (optional) Include unrealized PnL: 0: No; 1: Yes
        :type include_unrealised_pnl: int
        :param symbol: (optional) Trading pair
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "GET",
            "api/v1/private/account/asset/analysis/export",
            headers={"timezone-login": timezone},
            params=dict(
                startTime=start_time,
                endTime=end_time,
                reverse=reverse,
                includeUnrealisedPnl=include_unrealised_pnl,
                symbol=symbol,
                fileType=file_type,
                language=language,
            ),
        )

    async def order_deal_fee_total(self) -> dict:
        """
        ### 30-Day Fee Statistics
        #### Required permissions: View Account Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#30-day-fee-statistics

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", "api/v1/private/account/asset_book/order_deal_fee/total")

    async def contract_fee_rate(self, symbol: Optional[str] = None) -> dict:
        """
        ### Fee Details Under a Specific Contract
        #### Required permissions: View Account Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#fee-details-under-a-specific-contract

        :param symbol: (optional) Trading pair
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", "api/v1/private/account/contract/fee_rate", params=dict(symbol=symbol))

    async def zero_fee_rate(self, symbol: Optional[str] = None) -> dict:
        """
        ### Zero-Fee Trading Pairs
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#zero-fee-trading-pairs

        :param symbol: (optional) Trading pair
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", "api/v1/private/account/contract/zero_fee_rate", params=dict(symbol=symbol))

    async def place_track_order(
        self,
        symbol: str,
        leverage: int,
        side: int,
        vol: float,
        open_type: int,
        trend: int,
        back_type: int,
        back_value: float,
        position_mode: int,
        active_price: Optional[float] = None,
        reduce_only: Optional[bool] = None,
    ) -> dict:
        """
        ### Place Trailing Order (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#place-trailing-orderunder-maintenance

        :param symbol: Contract name
        :type symbol: str
        :param leverage: Leverage
        :type leverage: int
        :param side: 1 Open Long; 2 Close Short; 3 Open Short; 4 Close Long
        :type side: int
        :param vol: Order quantity
        :type vol: float
        :param open_type: Position mode: 1 Isolated; 2 Cross
        :type open_type: int
        :param trend: Price type: 1 Latest; 2 Fair; 3 Index
        :type trend: int
        :param back_type: Callback type: 1 Percentage; 2 Absolute value
        :type back_type: int
        :param back_value: Callback value
        :type back_value: float
        :param position_mode: Position mode. Default 0: no record for historical orders; 1: Two-way (hedged); 2: One-way
        :type position_mode: int
        :param active_price: (optional) Activation price
        :type active_price: float
        :param reduce_only: (optional) Reduce-only
        :type reduce_only: bool

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "POST",
            "api/v1/private/trackorder/place",
            json=dict(
                symbol=symbol,
                leverage=leverage,
                side=side,
                vol=vol,
                openType=open_type,
                trend=trend,
                backType=back_type,
                backValue=back_value,
                positionMode=position_mode,
                activePrice=active_price,
                reduceOnly=reduce_only,
            ),
        )

    async def cancel_track_order(
        self,
        symbol: Optional[str] = None,
        track_order_id: Optional[int] = None,
    ) -> dict:
        """
        ### Cancel Trailing Order (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#cancel-trailing-orderunder-maintenance

        :param symbol: (optional) Contract name
        :type symbol: str
        :param track_order_id: (optional) Trailing order ID
        :type track_order_id: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "POST",
            "api/v1/private/trackorder/cancel",
            json=dict(symbol=symbol, trackOrderId=track_order_id),
        )

    async def change_track_order(
        self,
        symbol: str,
        track_order_id: int,
        trend: int,
        back_type: int,
        back_value: float,
        vol: float,
        active_price: Optional[float] = None,
    ) -> dict:
        """
        ### Modify Trailing Order (Under Maintenance)
        #### Required permissions: Order Placing

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#modify-trailing-orderunder-maintenance

        :param symbol: Contract name
        :type symbol: str
        :param track_order_id: Trailing order ID
        :type track_order_id: int
        :param trend: Price type: 1 Latest; 2 Fair; 3 Index
        :type trend: int
        :param back_type: Callback type: 1 Percentage; 2 Absolute value
        :type back_type: int
        :param back_value: Callback value
        :type back_value: float
        :param vol: Order quantity
        :type vol: float
        :param active_price: (optional) Activation price
        :type active_price: float

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "POST",
            "api/v1/private/trackorder/change_order",
            json=dict(
                symbol=symbol,
                trackOrderId=track_order_id,
                trend=trend,
                activePrice=active_price,
                backType=back_type,
                backValue=back_value,
                vol=vol,
            ),
        )

    async def get_track_orders(
        self,
        states: List[int],
        symbol: Optional[str] = None,
        side: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page_index: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> dict:
        """
        ### Query Trailing Orders
        #### Required permissions: View Order Details

        Rate limit: 20 times / 2 seconds

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints#query-trailing-orders

        :param states: Order status: 0 Not activated; 1 Activated; 2 Triggered successfully; 3 Trigger failed; 4 Canceled
        :type states: List[int]
        :param symbol: (optional) Contract name
        :type symbol: str
        :param side: (optional) 1 Open Long; 2 Close Short; 3 Open Short; 4 Close Long
        :type side: int
        :param start_time: (optional) Start time
        :type start_time: int
        :param end_time: (optional) End time
        :type end_time: int
        :param page_index: (optional) Page index
        :type page_index: int
        :param page_size: (optional) Page size
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """
        params = dict(states=",".join(str(s) for s in states))
        if symbol:
            params["symbol"] = symbol
        if side is not None:
            params["side"] = side
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if page_index:
            params["pageIndex"] = page_index
        if page_size:
            params["pageSize"] = page_size
        return await self.call("GET", "api/v1/private/trackorder/list/orders", params=params)


class WebSocket(_FuturesWebSocket):
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        loop: Optional[AbstractEventLoop] = None,
        personal_callback: Optional[Awaitable[Callable[..., None]]] = None,
        ping_interval: Optional[int] = 20,
        ping_timeout: Optional[int] = None,
        retries: Optional[int] = 10,
        restart_on_error: Optional[bool] = True,
        trace_logging: Optional[bool] = False,
        http_proxy_host: Optional[str] = None,
        http_proxy_port: Optional[int] = None,
        http_no_proxy: Optional[list] = None,
        http_proxy_auth: Optional[tuple] = None,
        http_proxy_timeout: Optional[int] = None,
        proto: Optional[bool] = True,
    ):
        super().__init__(
            api_key=api_key,
            api_secret=api_secret,
            subscribe_callback=personal_callback,
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
            loop=loop,
        )

        if proto:
            warnings.warn("proto is not supported in futures websocket api", DeprecationWarning)

    async def unsubscribe(self, method: str | Callable):
        personal_filters = ["personal.filter", "filter", "personal"]
        if (
            method in personal_filters
            or getattr(method, "__name__", "").replace("_stream", "").replace("_", ".") in personal_filters
        ):
            return await self.personal_stream(lambda: ...)

        return await super().unsubscribe(method)

    async def tickers_stream(self, callback: Awaitable[Callable[..., None]]):
        """
        ### Tickers
        Get the latest transaction price, buy-price, sell-price and 24 transaction volume of all the perpetual contracts on the platform without login.
        Send once a second after subscribing.

        https://mexcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Awaitable[Callable[..., None]]

        :return: None
        """
        params = {}
        topic = "sub.tickers"
        await self._ws_subscribe(topic, callback, params)

    async def ticker_stream(self, callback: Awaitable[Callable[..., None]], symbol: str):
        """
        ### Ticker
        Get the latest transaction price, buy price, sell price and 24 transaction volume of a contract,
        send the transaction data without users' login, and send once a second after subscription.

        https://mexcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Awaitable[Callable[..., None]]
        :param symbol: the name of the contract
        :type symbol: str

        :return: None
        """
        params = dict(symbol=symbol)

        # clear none values
        params = {k: v for k, v in params.items() if v is not None}

        topic = "sub.ticker"
        await self._ws_subscribe(topic, callback, params)

    async def deal_stream(self, callback: Awaitable[Callable[..., None]], symbol: str):
        """
        ### Transaction
        Access to the latest data without login, and keep updating.

        https://mexcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Awaitable[Callable[..., None]]
        :param symbol: the name of the contract
        :type symbol: str

        :return: None
        """
        params = dict(symbol=symbol)

        # clear none values
        params = {k: v for k, v in params.items() if v is not None}

        topic = "sub.deal"
        await self._ws_subscribe(topic, callback, params)

    async def depth_stream(self, callback: Awaitable[Callable[..., None]], symbol: str):
        """
        ### Depth

        Tip: [411.8, 10, 1] 411.8 is price, 10 is the order numbers of the contract ,1 is the order quantity

        https://mexcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Awaitable[Callable[..., None]]
        :param symbol: the name of the contract
        :type symbol: str

        :return: None
        """
        params = dict(symbol=symbol)

        # clear none values
        params = {k: v for k, v in params.items() if v is not None}

        topic = "sub.depth"
        await self._ws_subscribe(topic, callback, params)

    async def depth_full_stream(self, callback: Awaitable[Callable[..., None]], symbol: str, limit: int = 20):
        """
        ### Depth full

        https://mexcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Awaitable[Callable[..., None]]
        :param symbol: the name of the contract
        :type symbol: str
        :param limit: Limit could be 5, 10 or 20, default 20 without define., only subscribe to the full amount of one gear
        :type limit: int

        :return: None
        """
        params = dict(symbol=symbol, limit=limit)

        # clear none values
        params = {k: v for k, v in params.items() if v is not None}

        topic = "sub.depth.full"
        await self._ws_subscribe(topic, callback, params)

    async def kline_stream(
        self,
        callback: Awaitable[Callable[..., None]],
        symbol: str,
        interval: Literal["Min1", "Min5", "Min15", "Min60", "Hour1", "Hour4", "Day1", "Week1"] = "Min1",
    ):
        """
        ### K-line
        Get the k-line data of the contract and keep updating.

        https://mexcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Awaitable[Callable[..., None]]
        :param symbol: the name of the contract
        :type symbol: str
        :param interval: Min1, Min5, Min15, Min30, Min60, Hour4, Hour8, Day1, Week1, Month1
        :type interval: str

        :return: None
        """
        params = dict(symbol=symbol, interval=interval)

        # clear none values
        params = {k: v for k, v in params.items() if v is not None}

        topic = "sub.kline"
        await self._ws_subscribe(topic, callback, params)

    async def funding_rate_stream(self, callback: Awaitable[Callable[..., None]], symbol: str):
        """
        ### Funding rate
        Get the contract funding rate, and keep updating.

        https://mexcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Awaitable[Callable[..., None]]
        :param symbol: the name of the contract
        :type symbol: str

        :return: None
        """
        params = dict(symbol=symbol)

        # clear none values
        params = {k: v for k, v in params.items() if v is not None}

        topic = "sub.funding.rate"
        await self._ws_subscribe(topic, callback, params)

    async def index_price_stream(self, callback: Awaitable[Callable[..., None]], symbol: str):
        """
        ### Index price
        Get the index price, and will keep updating if there is any changes.

        https://mexcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Awaitable[Callable[..., None]]
        :param symbol: the name of the contract
        :type symbol: str

        :return: None
        """
        params = dict(symbol=symbol)

        # clear none values
        params = {k: v for k, v in params.items() if v is not None}

        topic = "sub.index.price"
        await self._ws_subscribe(topic, callback, params)

    async def fair_price_stream(self, callback: Awaitable[Callable[..., None]], symbol: str):
        """
        ### Fair price

        https://mexcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Awaitable[Callable[..., None]]
        :param symbol: the name of the contract
        :type symbol: str

        :return: None
        """
        params = dict(symbol=symbol)

        # clear none values
        params = {k: v for k, v in params.items() if v is not None}

        topic = "sub.fair.price"
        await self._ws_subscribe(topic, callback, params)

    # <=================================================================>
    #
    #                                PRIVATE
    #
    # <=================================================================>

    async def filter_stream(self, callback: Callable, params: Dict[str, List[dict]] = {"filters": []}):
        """
        ## Filter personal data about account
        Provide `{"filters":[]}` as params for subscribe to all info
        """
        if params.get("filters") is None:
            raise ValueError("Please provide filters")

        topics = [x.get("filter") for x in params.get("filters", [])]
        for topic in topics:
            if topic not in FUTURES_PERSONAL_TOPICS:
                raise ValueError(f"Invalid filter: `{topic}`. Valid filters: {FUTURES_PERSONAL_TOPICS}")

        await self._ws_subscribe("personal.filter", callback, params)
        # set callback for provided filters
        self._set_personal_callback(callback, topics)

    async def personal_stream(self, callback: Awaitable[Callable]):
        await self.filter_stream(callback, params={"filters": []})
        # set callback for all filters
        self._set_personal_callback(callback, FUTURES_PERSONAL_TOPICS)
