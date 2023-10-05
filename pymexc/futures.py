"""
### Futures API
Documentation: https://mxcdevelop.github.io/apidocs/contract_v1_en/#update-log

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
from typing import Callable, Literal, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

try:
    from base import _FuturesHTTP
    from base_websocket import _FuturesWebSocket
except ImportError:
    from .base import _FuturesHTTP
    from .base_websocket import _FuturesWebSocket

class HTTP(_FuturesHTTP):
    
    # <=================================================================>
    #
    #                          Market Endpoints
    #
    # <=================================================================>

    def ping(self) -> dict:
        """
        ### Get the server time

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-the-server-time
        """
        return self.call("GET", "api/v1/contract/ping")

    def detail(self, symbol: Optional[str] = None) -> dict:
        """
        ### Get the contract information

        Rate limit: 1 times / 5 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-the-contract-information

        :param symbol: (optional) the name of the contract
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v1/contract/detail", 
                            params = dict(
                                    symbol = symbol
                            ))
    
    def support_currencies(self) -> dict:
        """
        ### Get the transferable currencies

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-the-transferable-currencies

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v1/contract/support_currencies")
    
    def get_depth(self, 
                  symbol: str, 
                  limit:  Optional[int] = None) -> dict:
        """
        ### Get the contract's depth information

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-the-contract-s-depth-information

        :param symbol: the name of the contract
        :type symbol: str
        :param limit: (optional) the limit of the depth
        :type limit: int


        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", f"api/v1/contract/depth/{symbol}",
                            params = dict(
                                    limit  = limit
                            ))

    def depth_commits(self,
                      symbol: str, 
                      limit:  int) -> dict:
        """
        ### Get a snapshot of the latest N depth information of the contract

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-a-snapshot-of-the-latest-n-depth-information-of-the-contract

        :param symbol: the name of the contract
        :type symbol: str
        :param limit: count
        :type limit: int


        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", f"api/v1/contract/depth_commits/{symbol}/{limit}")
    
    def index_price(self, symbol: str) -> dict:
        """
        ### Get contract index price

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-contract-index-price

        :param symbol: the name of the contract
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", f"api/v1/contract/index_price/{symbol}")
    
    def fair_price(self, symbol: str) -> dict:
        """
        ### Get contract fair price

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-contract-fair-price

        :param symbol: the name of the contract
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", f"api/v1/contract/fair_price/{symbol}")
    
    def funding_rate(self, symbol: str) -> dict:
        """
        ### Get contract funding rate

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-contract-funding-rate

        :param symbol: the name of the contract
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", f"api/v1/contract/funding_rate/{symbol}")

    def kline(self, 
              symbol:   str, 
              interval: Optional[Literal["Min1", "Min5", "Min15", "Min30", "Min60", "Hour4", "Hour8", "Day1", "Week1", "Month1"]] = None,
              start:    Optional[int] = None,
              end:      Optional[int] = None) -> dict:
        """
        ### K-line data
        
        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#k-line-data

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
        return self.call("GET", f"api/v1/contract/kline/{symbol}",
                            params = dict(
                                    symbol    = symbol,
                                    interval  = interval,
                                    start     = start,
                                    end       = end
                            ))


    def kline_index_price(self, 
              symbol:   str, 
              interval: Optional[Literal["Min1", "Min5", "Min15", "Min30", "Min60", "Hour4", "Hour8", "Day1", "Week1", "Month1"]] = "Min1",
              start:    Optional[int] = None,
              end:      Optional[int] = None) -> dict:
        """
        ### Get K-line data of the index price
        
        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-k-line-data-of-the-index-price

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
        return self.call("GET", f"api/v1/contract/kline/index_price/{symbol}",
                            params = dict(
                                    symbol    = symbol,
                                    interval  = interval,
                                    start     = start,
                                    end       = end
                            ))
    
    def kline_fair_price(self,
              symbol:   str, 
              interval: Optional[Literal["Min1", "Min5", "Min15", "Min30", "Min60", "Hour4", "Hour8", "Day1", "Week1", "Month1"]] = "Min1",
              start:    Optional[int] = None,
              end:      Optional[int] = None) -> dict:
        """
        ### Get K-line data of the index price
        
        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-k-line-data-of-the-index-price

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
        return self.call("GET", f"api/v1/contract/kline/fair_price/{symbol}",
                            params = dict(
                                    symbol    = symbol,
                                    interval  = interval,
                                    start     = start,
                                    end       = end
                            ))

    def deals(self,
              symbol: str, 
              limit:  Optional[int] = 100) -> dict:
        """
        ### Get contract transaction data

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-contract-transaction-data

        :param symbol: the name of the contract
        :type symbol: str
        :param limit: (optional) consequence set quantity, maximum is 100, default 100 without setting
        :type limit: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", f"api/v1/contract/deals/{symbol}",
                            params = dict(
                                    symbol = symbol,
                                    limit  = limit
                            ))
    
    def ticker(self, symbol: Optional[str] = None) -> dict: 
        """
        ### Get contract trend data

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-contract-trend-data

        :param symbol: (optional)the name of the contract
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v1/contract/ticker",
                            params = dict(
                                    symbol = symbol
                            ))
    
    def risk_reverse(self) -> dict: 
        """
        ### Get all contract risk fund balance

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-all-contract-risk-fund-balance

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v1/contract/risk_reverse")
    
    def risk_reverse_history(self, 
                             symbol:    str, 
                             page_num:  Optional[int] = 1, 
                             page_size: Optional[int] = 20) -> dict: 
        """
        ### Get contract risk fund balance history

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-contract-risk-fund-balance-history

        :param symbol: the name of the contract
        :type symbol: str
        :param page_num: current page number, default is 1
        :type page_num: int
        :param page_size: 	the page size, default 20, maximum 100
        :type page_size: int

        :return: A dictionary containing the risk reverse history.
        """
        return self.call("GET", "api/v1/contract/risk_reverse/history",
                            params = dict(
                                    symbol    = symbol,
                                    page_num  = page_num,
                                    page_size = page_size
                            ))

    def funding_rate_history(self,
                             symbol: str, 
                             page_num: Optional[int] = 1, 
                             page_size: Optional[int] = 20) -> dict: 
        """
        ### Get contract funding rate history

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-contract-funding-rate-history

        :param symbol: the name of the contract
        :type symbol: str
        :param page_num: current page number, default is 1
        :type page_num: int
        :param page_size: 	the page size, default 20, maximum 100
        :type page_size: int

        :return: A dictionary containing the risk reverse history.
        """
        return self.call("GET", "api/v1/contract/funding_rate/history",
                            params = dict(
                                    symbol    = symbol,
                                    page_num  = page_num,
                                    page_size = page_size
                            ))
                             
    # <=================================================================>
    #
    #                   Account and trading endpoints
    #
    # <=================================================================>

    def assets(self) -> dict:
        """
        ### Get all informations of user's asset 
        #### Required permissions: Trade reading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-all-informations-of-user-39-s-asset

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v1/private/account/assets")

    def asset(self, currency: str) -> dict:
        """
        ### Get the user's single currency asset information
        #### Required permissions: Account reading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-the-user-39-s-single-currency-asset-information
        
        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", f"api/v1/private/account/asset/{currency}")
    
    def transfer_record(self, 
                        currency:  Optional[str] = None, 
                        state:     Literal["WAIT", "SUCCESS", "FAILED"] = None, 
                        type:      Literal["IN", "OUT"] = None, 
                        page_num:  Optional[int] = 1, 
                        page_size: Optional[int] = 20) -> dict:
        """
        ### Get the user's asset transfer records
        #### Required permissions: Account reading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-the-user-39-s-asset-transfer-records
        
        :param currency: (optional) The currency.
        :type currency: str
        :param state: (optional) state:WAIT 、SUCCESS 、FAILED
        :type state: str
        :param type: (optional) type:IN 、OUT
        :type type: str
        :param page_num: (optional) current page number, default is 1
        :type page_num: int
        :param page_size: (optional) page size, default 20, maximum 100
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v1/private/account/transfer_record", 
                            params = dict(
                                    currency = currency, 
                                    state = state, 
                                    type = type, 
                                    page_num = page_num, 
                                    page_size = page_size
                            ))
    
    def history_positions(self, 
                          symbol:    Optional[str] = None, 
                          type:      Optional[int] = None, 
                          page_num:  Optional[int] = 1, 
                          page_size: Optional[int] = 20) -> dict:
        """
        ### Get the user's history position information
        #### Required permissions: Trade reading permissions

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-the-user-s-history-position-information
        
        :param symbol: (optional) the name of the contract
        :type symbol: str
        :param type: (optional) position type: 1 - long, 2 -short
        :type type: int
        :param page_num: (optional) current page number , default is 1
        :type page_num: int
        :param page_size: (optional) page size , default 20, maximum 100
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v1/private/position/list/history_positions", 
                            params = dict(
                                    symbol = symbol,
                                    type = type,
                                    page_num = page_num,
                                    page_size = page_size
                            ))
    
    def open_positions(self, symbol: Optional[str] = None) -> dict:
        """
        ### Get the user's current holding position
        #### Required permissions: Trade reading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-the-user-39-s-current-holding-position

        :param symbol: (optional) the name of the contract
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v1/private/position/open_positions", 
                            params = dict(
                                    symbol = symbol
                            ))
    
    def funding_records(self, 
                        symbol:      Optional[str] = None, 
                        position_id: Optional[int] = None, 
                        page_num:    Optional[int] = 1, 
                        page_size:   Optional[int] = 20) -> dict:
        """
        ### Get details of user's funding rate
        #### Required permissions: Trade reading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-details-of-user-s-funding-rate

        :param symbol: the name of the contract
        :type symbol: str
        :param position_id: 	position id
        :type position_id: int
        :param page_num: current page number, default is 1
        :type page_num: int
        :param page_size: 	page size, default 20, maximum 100
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """

        return self.call("GET", "api/v1/private/position/funding_records", 
                            params = dict(
                                    symbol = symbol,
                                    position_id = position_id,
                                    page_num = page_num,
                                    page_size = page_size
                            ))
    
    def open_orders(self, 
                    symbol:    Optional[str] = None, 
                    page_num:  Optional[int] = 1, 
                    page_size: Optional[int] = 20) -> dict:
        """
        ### Get the user's current pending order
        #### Required permissions: Trade reading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-the-user-39-s-current-pending-order

        :param symbol: The name of the contract. Returns all contract parameters if not specified.
        :type symbol: str
        :param page_num: The current page number. Defaults to 1.
        :type page_num: int
        :param page_size: The page size. Defaults to 20. Maximum of 100.
        :type page_size: int

        :return: A dictionary containing the user's current pending order.
        :rtype: dict
        """
        return self.call("GET", f"api/v1/private/order/list/open_orders/{symbol}", 
                            params = dict(
                                    symbol = symbol,
                                    page_num = page_num,
                                    page_size = page_size
                            ))
    
    def history_orders(self, 
                       symbol:     Optional[str] = None, 
                       states:     Optional[str] = None, 
                       category:   Optional[str] = None, 
                       start_time: Optional[int] = None, 
                       end_time:   Optional[int] = None, 
                       side:       Optional[int] = None, 
                       page_num:   Optional[int] = 1, 
                       page_size:  Optional[int] = 20) -> dict:
        """
        ### Get all of the user's historical orders
        #### Required permissions: Trade reading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-all-of-the-user-39-s-historical-orders

        :param symbol: The name of the contract. Returns all contract parameters if not specified.
        :type symbol: str
        :param states: The order state(s) to filter by. Multiple states can be separated by ','. Defaults to None.
        :type states: str
        :param category: The order category to filter by. Defaults to None.
        :type category: int
        :param start_time: The start time of the order history to retrieve. Defaults to None.
        :type start_time: int
        :param end_time: The end time of the order history to retrieve. Defaults to None.
        :type end_time: int
        :param side: The order direction to filter by. Defaults to None.
        :type side: int
        :param page_num: The current page number. Defaults to 1.
        :type page_num: int
        :param page_size: The page size. Defaults to 20. Maximum of 100.
        :type page_size: int

        :return: A dictionary containing all of the user's historical orders.
        :rtype: dict
        """
        return self.call("GET", "api/v1/private/order/history_orders", 
                            params = dict(
                                    symbol = symbol,
                                    states = states,
                                    category = category,
                                    start_time = start_time,
                                    end_time = end_time,
                                    side = side,
                                    page_num = page_num,
                                    page_size = page_size
                            ))
    
    def get_order_external(self, symbol: str, external_oid: int) -> dict:
        """
        ### Query the order based on the external number
        #### Required permissions: Trade reading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#query-the-order-based-on-the-external-number

        :param symbol: The name of the contract.
        :type symbol: str
        :param external_oid: The external order ID.
        :type external_oid: str

        :return: A dictionary containing the queried order based on the external number.
        :rtype: dict
        """

        return self.call("GET", f"api/v1/private/order/external/{symbol}/{external_oid}")
    
    def get_order(self, order_id: int) -> dict:
        """
        ### Query the order based on the order number
        #### Required permissions: Trade reading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#query-the-order-based-on-the-order-number

        :param order_id: The ID of the order to query.
        :type order_id: int

        :return: A dictionary containing the queried order based on the order number.
        :rtype: dict
        """
        return self.call("GET", f"api/v1/private/order/{order_id}")
    
    def batch_query(self, order_ids: List[int]) -> dict:
        """
        ### Query the order in bulk based on the order number
        #### Required permissions: Trade reading permission

        Rate limit: 5 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#query-the-order-in-bulk-based-on-the-order-number

        :param order_ids: An array of order IDs, separated by ",". Maximum of 50 orders.
        :type order_ids: str

        :return: A dictionary containing the queried orders in bulk based on the order number.
        :rtype: dict
        """
        return self.call("GET", "api/v1/private/order/batch_query",
                            params = dict(
                                    order_ids = ','.join(order_ids) if isinstance(order_ids, list) else order_ids
                            ))
    
    def deal_details(self, order_id: int) -> dict:
        """
        ### Get order transaction details based on the order ID
        #### Required permissions: Trade reading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-order-transaction-details-based-on-the-order-id

        :param order_id: The ID of the order to retrieve transaction details for.
        :type order_id: int

        :return: A dictionary containing the transaction details for the given order ID.
        :rtype: dict
        """
        return self.call("GET", f"api/v1/private/order/deal_details/{order_id}")
    
    def order_deals(self, 
                    symbol:     str, 
                    start_time: Optional[int] = None, 
                    end_time:   Optional[int] = None, 
                    page_num:   Optional[int] = 1, 
                    page_size:  Optional[int] = 20) -> dict:
        """
        ### Get all transaction details of the user's order
        #### Required permissions: Trade reading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-all-transaction-details-of-the-user-s-order

        :param symbol: the name of the contact
        :type symbol: str
        :param start_time: (optional) the starting time, the default is to push forward 7 days, and the maximum span is 90 days
        :type start_time: int
        :param end_time: (optional) the end time, start and end time span is 90 days
        :type end_time: int
        :param page_num: current page number, default is 1
        :type page_num: int
        :param page_size: page size , default 20, maximum 100
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v1/private/order/list/order_deals",
                            params = dict(
                                    symbol = symbol,
                                    start_time = start_time,
                                    end_time = end_time,
                                    page_num = page_num,
                                    page_size = page_size
                            ))
    
    def get_trigger_orders(self, 
                         symbol:     Optional[str] = None, 
                         states:     Optional[str] = None, 
                         start_time: Optional[int] = None, 
                         end_time:   Optional[int] = None, 
                         page_num:   int           = 1, 
                         page_size:  int           = 20) -> dict:
        """
        ### Gets the trigger order list
        #### Required permissions: Trade reading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#gets-the-trigger-order-list

        :param symbol: (optional) the name of the contract
        :type symbol: str
        :param states: (optional) order state, 1 uninformed, 2 uncompleted, 3 completed, 4 cancelled, 5 invalid; Multiple separate by ','
        :type states: str
        :param start_time: (optional) start time, start time and end time span can only check 90 days at a time, default return the last 7 days of data without fill in
        :type start_time: int
        :param end_time: (optional) end time, start time, and end time spans can only be checked for 90 days at a time
        :type end_time: int
        :param page_num: current page number, default is 1
        :type page_num: int
        :param page_size: page size, default 20, maximum 100
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v1/private/planorder/list/orders",
                            params = dict(
                                    symbol = symbol,
                                    states = states,
                                    start_time = start_time,
                                    end_time = end_time,
                                    page_num = page_num,
                                    page_size = page_size
                            ))

    def get_stop_limit_orders(self, 
                         symbol:      Optional[str] = None, 
                         is_finished: Optional[int] = None, 
                         start_time:  Optional[int] = None, 
                         end_time:    Optional[int] = None, 
                         page_num:    int           = 1, 
                         page_size:   int           = 20) -> dict:
        """
        ### Get the Stop-Limit order list
        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-the-stop-limit-order-list

        :param symbol: (optional) the name of the contact
        :type symbol: str
        :param is_finished: (optional) final state indicator :0: uncompleted, 1: completed
        :type is_finished: int
        :param start_time: (optional) start time, start time and end time span can only check 90 days at a time, default return the last 7 days of data without fill in
        :type start_time: long
        :param end_time: (optional) end time, start time, and end time spans can only be checked for 90 days at a time
        :type end_time: long
        :param page_num: current page number, default is 1
        :type page_num: int
        :param page_size: page size, default 20, maximum 100
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """

        return self.call("GET", "api/v1/private/stoporder/list/orders",
                            params = dict(
                                    symbol = symbol,
                                    is_finished = is_finished,
                                    start_time = start_time,
                                    end_time = end_time,
                                    page_num = page_num,
                                    page_size = page_size
                            ))
    
    def risk_limit(self, symbol: Optional[str] = None) -> dict:
        """
        ### Get risk limits
        #### Required permissions: Trade reading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-risk-limits

        :param symbol: (optional) the name of the contract , not uploaded will return all
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v1/private/account/risk_limit",
                            params = dict(
                                    symbol = symbol
                            ))

    def tiered_fee_rate(self, symbol: Optional[str] = None) -> dict:
        """
        ### Gets the user's current trading fee rate
        #### Required permissions: Trade reading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#gets-the-user-39-s-current-trading-fee-rate

        :param symbol: the name of the contract
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """

        return self.call("GET", "api/v1/private/account/tiered_fee_rate",
                            params = dict(
                                    symbol = symbol
                            ))
    
    def change_margin(self, 
                      position_id: int, 
                      amount:      int, 
                      type:        str) -> dict:
        """
        ### Increase or decrease margin
        #### Required permissions: Trading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#increase-or-decrease-margin

        :param positionId: position id
        :type positionId: int
        :param amount: amount
        :type amount: float
        :param type: type, ADD: increase, SUB: decrease
        :type type: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("POST", "api/v1/private/position/change_margin",
                            params = dict(
                                    positionId = position_id,
                                    amount = amount,
                                    type = type
                            ))
    
    def get_leverage(self, symbol: str) -> dict:
        """
        ### Get leverage
        #### Required permissions: Trading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-leverage

        :param symbol: symbol
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """

        return self.call("GET", "api/v1/private/position/leverage",
                            params = dict(
                                    symbol = symbol
                            ))
    
    def change_leverage(self, 
                        position_id:   int, 
                        leverage:      int, 
                        open_type:     Optional[int] = None, 
                        symbol:        Optional[str] = None, 
                        position_type: Optional[int] = None) -> dict:
        """
        ### Switch leverage
        #### Required permissions: Trading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#switch-leverage

        :param positionId: position id
        :type positionId: int
        :param leverage: leverage
        :type leverage: int
        :param openType: (optional) Required when there is no position, openType, 1: isolated position, 2: full position
        :type openType: int
        :param symbol: (optional) Required when there is no position, symbol
        :type symbol: str
        :param positionType: (optional) Required when there is no position, positionType: 1 Long 2:short
        :type positionType: int

        :return: response dictionary
        :rtype: dict
        """

        return self.call("POST", "api/v1/private/position/change_leverage",
                            params = dict(
                                    positionId = position_id,
                                    leverage = leverage,
                                    openType = open_type,
                                    symbol = symbol,
                                    positionType = position_type
                            ))
    
    def get_position_mode(self) -> dict:
        """
        ### Get position mode
        #### Required permissions: Trading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#get-position-mode

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v1/private/position/position_mode")

    def change_position_mode(self, position_mode: int) -> dict:
        """
        ### Change position mode
        #### Required permissions: Trading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#change-position-mode

        :param positionMode: 1: Hedge, 2: One-way, the modification of the position mode must ensure that there are no active orders, planned orders, or unfinished positions, otherwise it cannot be modified. When switching the one-way mode in both directions, the risk limit level will be reset to level 1. If you need to change the call interface, modify
        :type positionMode: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call("POST", "api/v1/private/position/change_position_mode",
                            params = dict(
                                    positionMode = position_mode
                            ))
    
    def order(self, 
              symbol:            str, 
              price:             float, 
              vol:               float, 
              side:              int, 
              type:              int, 
              open_type:         int, 
              position_id:       Optional[int]   = None, 
              leverage:          Optional[int]   = None, 
              external_oid:      Optional[str]   = None, 
              stop_loss_price:   Optional[float] = None, 
              take_profit_price: Optional[float] = None, 
              position_mode:     Optional[int]   = None, 
              reduce_only:       Optional[bool]  = False) -> dict:
        """
        ### Order (Under maintenance)
        #### Required permissions: Trading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#order-under-maintenance

        :param symbol: the name of the contract
        :type symbol: str
        :param price: price
        :type price: decimal
        :param vol: volume
        :type vol: decimal
        :param leverage: (optional) leverage, Leverage is necessary on Isolated Margin
        :type leverage: int
        :param side: order direction 1 open long ,2close short,3open short ,4 close l
        :type side: int
        :param type: orderType,1:price limited order,2:Post Only Maker,3:transact or cancel instantly ,4 : transact completely or cancel completely，5:market orders,6 convert market price to current price
        :type type: int
        :param openType: open type,1:isolated,2:cross
        :type openType: int
        :param positionId: (optional) position Id, It is recommended to fill in this parameter when closing a position
        :type positionId: long
        :param externalOid: (optional) external order ID
        :type externalOid: str
        :param stopLossPrice: (optional) stop-loss price
        :type stopLossPrice: decimal
        :param takeProfitPrice: (optional) take-profit price
        :type takeProfitPrice: decimal
        :param positionMode: (optional) position mode,1:hedge,2:one-way,default: the user's current config
        :type positionMode: int
        :param reduceOnly: (optional) Default false,For one-way positions, if you need to only reduce positions, pass in true, and two-way positions will not accept this parameter.
        :type reduceOnly: bool

        :return: response dictionary
        :rtype: dict
        """
        return self.call("POST", "api/v1/private/order/submit",
                            params = dict(
                                    symbol = symbol,
                                    price = price,
                                    vol = vol,
                                    side = side,
                                    type = type,
                                    openType = open_type,
                                    positionId = position_id,
                                    leverage = leverage,
                                    externalOid = external_oid,
                                    stopLossPrice = stop_loss_price,
                                    takeProfitPrice = take_profit_price,
                                    positionMode = position_mode,
                                    reduceOnly = reduce_only
                            ))

    def bulk_order(self, 
                   symbol:            str, 
                   price:             float, 
                   vol:               float, 
                   side:              int, 
                   type:              int, 
                   open_type:         int, 
                   position_id:       Optional[int]   = None, 
                   external_oid:      Optional[str]   = None, 
                   stop_loss_price:   Optional[float] = None, 
                   take_profit_price: Optional[float] = None) -> dict:
        """
        ### Bulk order (Under maintenance)
        #### Required permissions: Trading permission

        Rate limit: 1/2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#bulk-order-under-maintenance

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
        return self.call("POST", "api/v1/private/order/submit_batch",
                            params = dict(
                                    symbol = symbol,
                                    price = price,
                                    vol = vol,
                                    side = side,
                                    type = type,
                                    openType = open_type,
                                    positionId = position_id,
                                    externalOid = external_oid,
                                    stopLossPrice = stop_loss_price,
                                    takeProfitPrice = take_profit_price
                            ))
    
    def cancel_order(self, order_id: Union[List[int], int]) -> dict:
        """
        ### Cancel the order (Under maintenance)
        #### Required permissions: Trading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#cancel-the-order-under-maintenance

        :param order_id_list: list of order ids to cancel, maximum 50
        :type order_id_list: List[int]

        :return: dictionary containing the order ID and error message, if any
        :rtype: dict
        """

        return self.call("POST", "api/v1/private/order/cancel",
                            params = dict(
                                    order_ids = ','.join(order_id) if isinstance(order_id, list) else order_id
                            ))
    
    def cancel_order_with_external(self, symbol: str, external_oid: str) -> dict:
        """
        ### Cancel the order according to the external order ID (Under maintenance)

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#cancel-the-order-according-to-the-external-order-id-under-maintenance

        :param symbol: the name of the contract
        :type symbol: str
        :param external_oid: external order ID of the order to be cancelled
        :type external_oid: str

        :return: response dictionary
        :rtype: dict
        """

        return self.call("POST", "api/v1/private/order/cancel_with_external",
                            params = dict(
                                    symbol = symbol,
                                    externalOid = external_oid
                            ))
    
    def cancel_all(self, symbol: Optional[str] = None) -> dict:
        """
        ### Cancel all orders under a contract (Under maintenance)

        #### Required permissions: Trading permission

        Rate limit: 20 times / 2 seconds

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#cancel-all-orders-under-a-contract-under-maintenance

        :param symbol: (optional) the name of the contract, cancel specific orders placed under this contract when fill the symbol , otherwise , cancel all orders without filling
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """

        return self.call("POST", "api/v1/private/order/cancel_all",
                            params = dict(
                                    symbol = symbol
                            ))
    
    def change_risk_level(self) -> dict:
        """
        ### Switch the risk level

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#switch-the-risk-level

        :return: None
        :rtype: None
        """

        return self.call("POST", "api/v1/private/account/change_risk_level")
    
    def trigger_order(self,
                      symbol:        str,
                      vol:           float,
                      side:          int,
                      open_type:     int,
                      trigger_price: float,
                      trigger_type:  int,
                      execute_cycle: int,
                      order_type:    int,
                      trend:         int,
                      price:         Optional[float] = None,
                      leverage:      Optional[int]   = None) -> dict:
        """
        ### Trigger order (Under maintenance)

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#trigger-order-under-maintenance

        :param symbol: the name of the contract
        :type symbol: str
        :param price: (optional) execute price, market price may not fill in
        :type price: int
        :param vol: volume
        :type vol: int
        :param leverage: (optional) leverage , Leverage is necessary on Isolated Margin
        :type leverage: int
        :param side: 1 for open long, 2 for close short, 3 for open short, and 4 for close long
        :type side: int
        :param openType: open type, 1: isolated, 2: cross
        :type openType: int
        :param triggerPrice: trigger price
        :type triggerPrice: int
        :param triggerType: trigger type, 1: more than or equal, 2: less than or equal
        :type triggerType: int
        :param executeCycle: execution cycle, 1: 24 hours, 2: 7 days
        :type executeCycle: int
        :param orderType: order type, 1: limit order, 2: Post Only Maker, 3: close or cancel instantly, 4: close or cancel completely, 5: Market order
        :type orderType: int
        :param trend: trigger price type, 1: latest price, 2: fair price, 3: index price
        :type trend: int

        :return: response dictionary
        :rtype: dict
        """

        return self.call("POST", "api/v1/private/planorder/place",
                            params = dict(
                                    symbol = symbol,
                                    price = price,
                                    vol = vol,
                                    leverage = leverage,
                                    side = side,
                                    openType = open_type,
                                    triggerPrice = trigger_price,
                                    triggerType = trigger_type,
                                    executeCycle = execute_cycle,
                                    orderType = order_type,
                                    trend = trend
                            ))

    def cancel_trigger_order(self, order_id: int) -> dict:
        """
        ### Cancel the trigger order (Under maintenance)

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#cancel-the-trigger-order-under-maintenance

        :param orderList: list of orders to be cancelled (maximum of 50)
        :type orderList: list[dict]
        :param orderList.symbol: the name of the contract
        :type orderList.symbol: str
        :param orderList.orderId: orderId
        :type orderList.orderId: str

        :return: response dictionary
        :rtype: dict
        """

        return self.call("POST", "api/v1/private/planorder/cancel",
                            params = dict(
                                    order_id = order_id
                            ))

    def cancel_all_trigger_orders(self, symbol: Optional[str] = None) -> dict:
        """
        ### Cancel all trigger orders (Under maintenance)

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#cancel-all-trigger-orders-under-maintenance

        :param symbol: (optional) the name of the contract, cancel specific orders placed under this contract when filled, otherwise, cancel all orders without filling
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """

        return self.call("POST", "api/v1/private/planorder/cancel_all",
                            params = dict(
                                    symbol = symbol
                            ))
    
    def cancel_stop_order(self, order_id: int) -> dict:
        """
        ### Cancel the Stop-Limit trigger order (Under maintenance)

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#cancel-the-stop-limit-trigger-order-under-maintenance

        :param orderList: list of orders to be cancelled (maximum of 50)
        :type orderList: list[str]

        :return: response dictionary
        :rtype: dict
        """

        return self.call("POST", "api/v1/private/stoporder/cancel",
                            params = dict(
                                    order_id = order_id
                            ))

    def cancel_all_stop_order(self, 
                              position_id: Optional[int] = None, 
                              symbol:      Optional[str] = None) -> dict:
        """
        ### Cancel all Stop-Limit price trigger orders (Under maintenance)

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#cancel-all-stop-limit-price-trigger-orders-under-maintenance

        :param positionId: (optional) position id, fill in positionId to only cancel the trigger order of the corresponding position, otherwise check the symbol without filling
        :type positionId: int
        :param symbol: (optional) the name of the contract, only cancels the delegate order under this contract based on the symbol, cancel all orders without filling the symbol
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """

        return self.call("POST", "api/v1/private/stoporder/cancel_all",
                            params = dict(
                                    positionId = position_id,
                                    symbol = symbol
                            ))

    def stop_limit_change_price(self,
                                order_id:          int,
                                stop_loss_price:   Optional[float] = None,
                                take_profit_price: Optional[float] = None) -> dict:
        """
        ### Switch Stop-Limit limited order price

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#switch-stop-limit-limited-order-price

        :param orderId: the limit order ID
        :type orderId: int
        :param stopLossPrice: (optional) stop-loss price, if take-profit and stop-loss price are empty or 0 at the same time, it indicates to cancel and take profit
        :type stopLossPrice: int
        :param takeProfitPrice: (optional) take-profit price, if take-profit and stop-loss price are empty or 0 at the same time, it indicates to cancel stop-loss and take profit
        :type takeProfitPrice: int

        :return: response dictionary
        :rtype: dict
        """

        return self.call("POST", "api/v1/private/stoporder/change_price",
                            params = dict(
                                    orderId = order_id,
                                    stopLossPrice = stop_loss_price,
                                    takeProfitPrice = take_profit_price
                            ))
    
    def stop_limit_change_plan_price(self,
                                     stop_plan_order_id: int,
                                     stop_loss_price:    Optional[float] = None,
                                     take_profit_price:  Optional[float] = None) -> dict:
        """
        ### Switch the Stop-Limit price of trigger orders

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#switch-the-stop-limit-price-of-trigger-orders

        :param stopPlanOrderId: the Stop-Limit price of trigger order ID
        :type stopPlanOrderId: int
        :param stopLossPrice: (optional) stop-loss price. At least one stop-loss price and one take-profit price must not be empty and must be more than 0.
        :type stopLossPrice: int
        :param takeProfitPrice: (optional) take-profit price. At least one take-profit price and stop-loss price must not be empty and must be more than 0.
        :type takeProfitPrice: int

        :return: response dictionary
        :rtype: dict
        """

        return self.call("POST", "api/v1/private/stoporder/change_plan_price",
                            params = dict(
                                    stopPlanOrderId = stop_plan_order_id,
                                    stopLossPrice = stop_loss_price,
                                    takeProfitPrice = take_profit_price
                            ))

class WebSocket(_FuturesWebSocket):
    def __init__(self, 
                 api_key:            Optional[str]   = None, 
                 api_secret:         Optional[str]   = None,
                 ping_interval:      Optional[int]   = 20, 
                 ping_timeout:       Optional[int]   = 10, 
                 retries:            Optional[int]   = 10,
                 restart_on_error:   Optional[bool]  = True, 
                 trace_logging:      Optional[bool]  = False,
                 http_proxy_host:    Optional[str]   = None,
                 http_proxy_port:    Optional[int]   = None,
                 http_no_proxy:      Optional[list]  = None,
                 http_proxy_auth:    Optional[tuple] = None,
                 http_proxy_timeout: Optional[int]   = None):

        kwargs = dict(
            api_key = api_key,
            api_secret = api_secret,
            ping_interval = ping_interval,
            ping_timeout = ping_timeout,
            retries = retries,
            restart_on_error = restart_on_error,
            trace_logging = trace_logging,
            http_proxy_host = http_proxy_host,
            http_proxy_port = http_proxy_port,
            http_no_proxy = http_no_proxy,
            http_proxy_auth = http_proxy_auth,
            http_proxy_timeout = http_proxy_timeout
        )
        
        super().__init__(**kwargs)
        

    def tickers_stream(self, callback: Callable[..., None]):
        """
        ### Tickers
        Get the latest transaction price, buy-price, sell-price and 24 transaction volume of all the perpetual contracts on the platform without login. 
        Send once a second after subscribing.

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Callable[..., None]

        :return: None
        """
        params = {}
        topic = "sub.tickers"
        self._ws_subscribe(topic, callback, params)

    def ticker_stream(self, callback: Callable[..., None], symbol: str):
        """
        ### Ticker
        Get the latest transaction price, buy price, sell price and 24 transaction volume of a contract, 
        send the transaction data without users' login, and send once a second after subscription.

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Callable[..., None]
        :param symbol: the name of the contract
        :type symbol: str

        :return: None
        """
        params = dict(
            symbol = symbol
        )

        # clear none values
        params = {k: v for k, v in params.items() if v is not None}

        topic = "sub.ticker"
        self._ws_subscribe(topic, callback, params)

    def deal_stream(self, callback: Callable[..., None], symbol: str):
        """
        ### Transaction
        Access to the latest data without login, and keep updating.

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Callable[..., None]
        :param symbol: the name of the contract
        :type symbol: str

        :return: None
        """
        params = dict(
            symbol = symbol
        )

        # clear none values
        params = {k: v for k, v in params.items() if v is not None}

        topic = "sub.deal"
        self._ws_subscribe(topic, callback, params)

    def depth_stream(self, callback: Callable[..., None], symbol: str):
        """
        ### Depth

        Tip: [411.8, 10, 1] 411.8 is price, 10 is the order numbers of the contract ,1 is the order quantity

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Callable[..., None]
        :param symbol: the name of the contract
        :type symbol: str

        :return: None
        """
        params = dict(
            symbol = symbol
        )

        # clear none values
        params = {k: v for k, v in params.items() if v is not None}

        topic = "sub.depth"
        self._ws_subscribe(topic, callback, params)
        
    def depth_full_stream(self, callback: Callable[..., None], symbol: str, limit: int = 20):
        """
        ### Depth full

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Callable[..., None]
        :param symbol: the name of the contract
        :type symbol: str
        :param limit: Limit could be 5, 10 or 20, default 20 without define., only subscribe to the full amount of one gear
        :type limit: int

        :return: None
        """
        params = dict(
            symbol = symbol,
            limit  = limit
        )

        # clear none values
        params = {k: v for k, v in params.items() if v is not None}

        topic = "sub.depth.full"
        self._ws_subscribe(topic, callback, params)

    def kline_stream(self, 
                     callback: Callable[..., None], 
                     symbol: str, 
                     interval: Literal["Min1", "Min5", "Min15", 
                                       "Min60", "Hour1", "Hour4",
                                       "Day1", "Week1"] = "Min1"):
        """
        ### K-line
        Get the k-line data of the contract and keep updating.

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Callable[..., None]
        :param symbol: the name of the contract
        :type symbol: str
        :param interval: Min1, Min5, Min15, Min30, Min60, Hour4, Hour8, Day1, Week1, Month1
        :type interval: str

        :return: None
        """
        params = dict(
            symbol   = symbol,
            interval = interval
        )

        # clear none values
        params = {k: v for k, v in params.items() if v is not None}

        topic = "sub.kline"
        self._ws_subscribe(topic, callback, params)

    def funding_rate_stream(self, 
                            callback: Callable[..., None], 
                            symbol:   str):
        """
        ### Funding rate
        Get the contract funding rate, and keep updating.

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Callable[..., None]
        :param symbol: the name of the contract
        :type symbol: str

        :return: None
        """
        params = dict(
            symbol = symbol
        )

        # clear none values
        params = {k: v for k, v in params.items() if v is not None}

        topic = "sub.funding.rate"
        self._ws_subscribe(topic, callback, params)

    def index_price_stream(self, 
                            callback: Callable[..., None], 
                            symbol:   str):
        """
        ### Index price
        Get the index price, and will keep updating if there is any changes.

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Callable[..., None]
        :param symbol: the name of the contract
        :type symbol: str

        :return: None
        """
        params = dict(
            symbol = symbol
        )

        # clear none values
        params = {k: v for k, v in params.items() if v is not None}

        topic = "sub.index.price"
        self._ws_subscribe(topic, callback, params)

    def fair_price_stream(self, 
                            callback: Callable[..., None], 
                            symbol:   str):
        """
        ### Fair price

        https://mxcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        :param callback: the callback function
        :type callback: Callable[..., None]
        :param symbol: the name of the contract
        :type symbol: str

        :return: None
        """
        params = dict(
            symbol = symbol
        )

        # clear none values
        params = {k: v for k, v in params.items() if v is not None}

        topic = "sub.fair.price"
        self._ws_subscribe(topic, callback, params)
    
    # <=================================================================>
    #
    #                                PRIVATE
    #
    # <=================================================================>

    def order_stream(self, callback, params: dict = {}):
        """
        https://mxcdevelop.github.io/apidocs/contract_v1_en/#public-channels
        """
        topic = "sub.personal.order"
        self._ws_subscribe(topic, callback, params)

    def asset_stream(self, callback, params: dict = {}):
        """
        https://mxcdevelop.github.io/apidocs/contract_v1_en/#public-channels
        """
        topic = "sub.personal.asset"
        self._ws_subscribe(topic, callback, params)

    def position_stream(self, callback, params: dict = {}):
        """
        https://mxcdevelop.github.io/apidocs/contract_v1_en/#public-channels
        """
        topic = "sub.personal.position"
        self._ws_subscribe(topic, callback, params)

    def risk_limit_stream(self, callback, params: dict = {}):
        """
        https://mxcdevelop.github.io/apidocs/contract_v1_en/#public-channels
        """
        topic = "sub.personal.risk.limit"
        self._ws_subscribe(topic, callback, params)

    def adl_level_stream(self, callback, params: dict = {}):
        """
        https://mxcdevelop.github.io/apidocs/contract_v1_en/#public-channels
        """
        topic = "sub.personal.adl.level"
        self._ws_subscribe(topic, callback, params)

    def position_mode_stream(self, callback, params: dict = {}):
        """
        https://mxcdevelop.github.io/apidocs/contract_v1_en/#public-channels
        """
        topic = "sub.personal.position.mode"
        self._ws_subscribe(topic, callback, params)


