"""
### Spot API
Documentation: https://mxcdevelop.github.io/apidocs/spot_v3_en/#introduction

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
from typing import Callable, Literal, List, Optional, Union
import threading, time, logging

logger = logging.getLogger(__name__)

try:
    from base import _SpotHTTP
    from base_websocket import _SpotWebSocket
except:
    from .base import _SpotHTTP
    from .base_websocket import _SpotWebSocket

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

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#test-connectivity
        """
        return self.call("GET", "/api/v3/ping")
    
    def time(self) -> dict:
        """
        ### Check Server Time

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#check-server-time    
        """
        return self.call("GET", "/api/v3/time")
    
    def default_symbol(self) -> dict:
        """
        ### API default symbol

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#api-default-symbol
        """
        return self.call("GET", "/api/v3/defaultSymbols")

    def exchange_info(self, 
                      symbol:  Optional[str] = None, 
                      symbols: Optional[List[str]] = None) -> dict:
        """
        ### Exchange Information

        Current exchange trading rules and symbol information

        Weight(IP): 10

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#exchange-information

        :param symbol: (optional) The symbol for a specific trading pair.
        :type symbol: str
        :param symbols: (optional) List of symbols to get information for.
        :type symbols: List[str]
        :return: The response from the API containing trading pair information.
        :rtype: dict
        """

        return self.call("GET", "/api/v3/exchangeInfo", 
                            params = dict(
                                    symbol  = symbol, 
                                    symbols = ','.join(symbols) if symbols else None
                            ))

    def order_book(self, 
                   symbol: str, 
                   limit:  Optional[int] = 100) -> dict:
        """
        ### Order Book

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#order-book

        :param symbol: A string representing the trading pair symbol, e.g. "BTCUSDT".
        :type symbol: str
        :param limit: An integer representing the number of order book levels to retrieve. Defaults to 100. Max is 5000.
        :type limit: int
        
        :return: The order book data in JSON format.
        :rtype: dict
        """
        return self.call("GET", "/api/v3/depth", 
                            params = dict(
                                    symbol = symbol, 
                                    limit  = limit
                            ))

    def trades(self, 
               symbol: str, 
               limit:  Optional[int] = 500) -> dict:
        """
        ### Recent Trades List

        Weight(IP): 5

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#recent-trades-list
        
        :param symbol: A string representing the trading pair symbol.
        :type symbol: str
        :param limit: An optional integer representing the maximum number of trades to retrieve. Defaults to 500. Max is 5000.
        :type limit: int
        
        :return: A dictionary containing information about the trades.
        :rtype: dict
        """

        return self.call("GET", "/api/v3/trades", 
                            params = dict(
                                    symbol  = symbol, 
                                    limit   = limit
                            ))
    
    def agg_trades(self, 
                   symbol:     str, 
                   start_time: Optional[int] = None, 
                   end_time:   Optional[int] = None, 
                   limit:      Optional[int] = 500) -> dict:
        """
        ### Compressed/Aggregate Trades List

        Get compressed, aggregate trades. Trades that fill at the time, from the same order, with the same price will have the quantity aggregated.
        
        startTime and endTime must be used at the same time.

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#compressed-aggregate-trades-list

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
        return self.call("GET", "/api/v3/aggTrades", 
                            params = dict(
                                    symbol    = symbol,
                                    startTime = start_time,
                                    endTime   = end_time,
                                    limit     = limit
                            ))
    
    def klines(self, 
               symbol:     str, 
               interval:   Literal["1m", "5m", "15m", 
                                   "30m", "60m", "4h", 
                                   "1d", "1M"]          = "1m", 
               start_time: Optional[int]                = None, 
               end_time:   Optional[int]                = None, 
               limit:      Optional[int]                = 500) -> dict:
        """
        ### Kline/Candlestick Data

        Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time.

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#kline-candlestick-data

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
        return self.call("GET", "/api/v3/klines",
                            params = dict(
                                    symbol    = symbol,
                                    interval  = interval,
                                    startTime = start_time,
                                    endTime   = end_time,
                                    limit     = limit
                            ))

    def avg_price(self, symbol: str):
        """
        ### Current Average Price

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#current-average-price

        :param symbol: The symbol.
        :type symbol: str

        :return: A dictionary containing average price.
        :rtype: dict
        """
        return self.call("GET", "/api/v3/avgPrice",
                            params = dict(
                                    symbol = symbol
                            ))

    def ticker_24h(self, symbol: Optional[str] = None):
        """
        ### 24hr Ticker Price Change Statistics

        Weight(IP): 1 - 1 symbol; 
        Weight(IP): 40 - all symbols; 

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#24hr-ticker-price-change-statistics

        :param symbol: (optional) If the symbol is not sent, tickers for all symbols will be returned in an array.
        :type symbol: str

        :return: A dictionary.
        :rtype: dict
        """
        return self.call("GET", "/api/v3/ticker/24hr",
                            params = dict(
                                    symbol = symbol
                            ))

    def ticker_price(self, symbol: Optional[str] = None):
        """
        ### Symbol Price Ticker

        Weight(IP): 1 - 1 symbol; 
        Weight(IP): 2 - all symbols; 

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#symbol-price-ticker

        :param symbol: (optional) If the symbol is not sent, all symbols will be returned in an array.
        :type symbol: str

        :return: A dictionary.
        :rtype: dict
        """
        return self.call("GET", "/api/v3/ticker/price",
                            params = dict(
                                    symbol = symbol
                            ))

    def ticker_book_price(self, symbol: Optional[str] = None):
        """
        ### Symbol Price Ticker

        Best price/qty on the order book for a symbol or symbols.

        Weight(IP): 1 

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#symbol-order-book-ticker

        :param symbol: (optional) If the symbol is not sent, all symbols will be returned in an array.
        :type symbol: str

        :return: A dictionary.
        :rtype: dict
        """
        return self.call("GET", "/api/v3/ticker/bookTicker",
                            params = dict(
                                    symbol = symbol
                            ))
    
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

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#create-a-sub-account-for-master-account

        :param sub_account: Sub-account Name
        :type sub_account: str
        :param note: Sub-account notes
        :type note: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("POST", "api/v3/sub-account/virtualSubAccount", 
                            params = dict(
                                subAccount = sub_account,
                                note = note
                            ))


    def sub_account_list(self, 
                               sub_account: Optional[str] = None, 
                               is_freeze: Optional[bool]  = None, 
                               page: Optional[int]        = 1, 
                               limit: Optional[int]       = 10) -> dict:
        """
        ### Get details of the sub-account list.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#query-sub-account-list-for-master-account

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
        return self.call("GET", "api/v3/sub-account/list", 
                        params = dict(
                            subAccount = sub_account,
                            isFreeze = is_freeze,
                            page = page,
                            limit = limit
                        ))

    def create_sub_account_api_key(self, 
                                   sub_account: str, 
                                   note:        str, 
                                   permissions: Union[str, List[Literal["SPOT_ACCOUNT_READ",     "SPOT_ACCOUNT_WRITE", 
                                                                        "SPOT_DEAL_READ",        "SPOT_DEAL_WRITE",
                                                                        "CONTRACT_ACCOUNT_READ", "CONTRACT_ACCOUNT_WRITE",
                                                                        "CONTRACT_DEAL_READ",    "CONTRACT_DEAL_WRITE", 
                                                                        "SPOT_TRANSFER_READ",    "SPOT_TRANSFER_WRITE"]]], 
                                   ip:          Optional[str] = None) -> dict:
        """
        ### Create an APIKey for a sub-account.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#create-an-apikey-for-a-sub-account-for-master-account

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
        return self.call("POST", "api/v3/sub-account/apiKey", 
                        params = dict(
                            subAccount = sub_account,
                            note = note,
                            permissions = ','.join(permissions) if isinstance(permissions, list) else permissions,
                            ip = ip
                        ))

    def query_sub_account_api_key(self, sub_account: str) -> dict:
        """
        ### Query the APIKey of a sub-account.
        #### Applies to master accounts only
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#query-the-apikey-of-a-sub-account-for-master-account

        :param sub_account: Sub-account Name
        :type sub_account: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/sub-account/apiKey", 
                        params = dict(
                            subAccount = sub_account
                        ))

    def delete_sub_account_api_key(self, sub_account: str, api_key: str) -> dict:
        """
        ### Delete the APIKey of a sub-account.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#delete-the-apikey-of-a-sub-account-for-master-account

        :param sub_account: Sub-account Name
        :type sub_account: str
        :param api_key: API public key
        :type api_key: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("DELETE", "api/v3/sub-account/apiKey", 
                        params = dict(
                            subAccount = sub_account,
                            apiKey = api_key
                        ))

    def universal_transfer(self,
                           from_account_type: Literal["SPOT", "FUTURES"],
                           to_account_type:   Literal["SPOT", "FUTURES"],
                           asset:             str,
                           amount:            float,
                           from_account:      Optional[str] = None,
                           to_account:        Optional[str] = None) -> dict:
        """
        ### Universal Transfer (For Master Account)
        #### Required permission: SPOT_TRANSFER_WRITE

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#query-universal-transfer-history-for-master-account

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
        return self.call("POST", "api/v3/capital/sub-account/universalTransfer",
                        params = dict(
                            fromAccount = from_account,
                            toAccount = to_account,
                            fromAccountType = from_account_type,
                            toAccountType = to_account_type,
                            asset = asset,
                            amount = amount
                        ))

    def query_universal_transfer_history(self,
                                        from_account_type: Literal["SPOT", "FUTURES"],
                                        to_account_type:   Literal["SPOT", "FUTURES"],
                                        from_account:      Optional[str] = None,
                                        to_account:        Optional[str] = None,
                                        start_time:        Optional[str] = None,
                                        end_time:          Optional[str] = None,
                                        page:              Optional[int] = 1,
                                        limit:             Optional[int] = 500) -> dict:
        """
        ### Query Universal Transfer History.
        #### Required permission: SPOT_TRANSFER_READ

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#query-universal-transfer-history-for-master-account

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
        return self.call("GET", "api/v3/capital/sub-account/universalTransfer",
                        params = dict(
                            fromAccount = from_account,
                            toAccount = to_account,
                            fromAccountType = from_account_type,
                            toAccountType = to_account_type,
                            startTime = start_time,
                            endTime = end_time,
                            page = page,
                            limit = limit
                        ))

    # <=================================================================>
    #
    #                       Spot Account/Trade
    #
    # <=================================================================>

    def all_orders(self, 
                   symbol:     str,
                   start_time: Optional[int] = None,
                   end_time:   Optional[int] = None,
                   limit:      Optional[int] = 500) -> dict:
        
        return self.call("GET", "/api/v3/allOrders",
                            params = dict(
                                    symbol    = symbol,
                                    startTime = start_time,
                                    endTime   = end_time,
                                    limit     = limit
                            ))
                   
    def get_default_symbols(self) -> dict:
        """
        ### User API default symbol.
        #### Required permission: SPOT_ACCOUNT_R

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#user-api-default-symbol

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/selfSymbols")

    def test_new_order(self, 
                       symbol:              str, 
                       side:                str, 
                       order_type:          str, 
                       quantity:            Optional[int] = None, 
                       quote_order_qty:     Optional[int] = None, 
                       price:               Optional[int] = None, 
                       new_client_order_id: Optional[str] = None, 
                       stop_price:          Optional[int] = None, 
                       iceberg_qty:         Optional[int] = None, 
                       time_in_force:       Optional[str] = None) -> dict:
        """
        ### New Order.
        #### Required permission: SPOT_DEAL_WRITE

        Weight(IP): 1, Weight(UID): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#new-order

        :param symbol: 
        :type symbol: str
        :param side: ENUM:Order Side
        :type side: str
        :param order_type: ENUM:Order Type
        :type order_type: str
        :param quantity: (optional) Quantity
        :type quantity: int
        :param quote_order_qty: (optional) Quote order quantity
        :type quote_order_qty: int
        :param price: (optional) Price
        :type price: int
        :param new_client_order_id: (optional) Unique order id
        :type new_client_order_id: str
        :param stop_price: (optional) Stop price
        :type stop_price: int
        :param iceberg_qty: (optional) Iceberg quantity
        :type iceberg_qty: int
        :param time_in_force: (optional) ENUM:Time In Force
        :type time_in_force: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("POST", "/api/v3/order/test", 
                            params = dict(
                                    symbol = symbol, 
                                    side = side, 
                                    type = order_type, 
                                    quantity = quantity, 
                                    quoteOrderQty = quote_order_qty, 
                                    price = price, 
                                    newClientOrderId = new_client_order_id, 
                                    stopPrice = stop_price, 
                                    icebergQty = iceberg_qty, 
                                    timeInForce = time_in_force
                            ))   

    def new_order(self, 
                  symbol:              str, 
                  side:                str, 
                  order_type:          str, 
                  quantity:            Optional[int] = None, 
                  quote_order_qty:     Optional[int] = None, 
                  price:               Optional[int] = None, 
                  new_client_order_id: Optional[str] = None, 
                  stop_price:          Optional[int] = None, 
                  iceberg_qty:         Optional[int] = None, 
                  time_in_force:       Optional[str] = None) -> dict:
        """
        ### New Order.
        #### Required permission: SPOT_DEAL_WRITE

        Weight(IP): 1, Weight(UID): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#new-order

        :param symbol: 
        :type symbol: str
        :param side: ENUM:Order Side
        :type side: str
        :param order_type: ENUM:Order Type
        :type order_type: str
        :param quantity: (optional) Quantity
        :type quantity: int
        :param quote_order_qty: (optional) Quote order quantity
        :type quote_order_qty: int
        :param price: (optional) Price
        :type price: int
        :param new_client_order_id: (optional) Unique order id
        :type new_client_order_id: str
        :param stop_price: (optional) Stop price
        :type stop_price: int
        :param iceberg_qty: (optional) Iceberg quantity
        :type iceberg_qty: int
        :param time_in_force: (optional) ENUM:Time In Force
        :type time_in_force: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("POST", "api/v3/order", 
                            params = dict(
                                    symbol = symbol, 
                                    side = side, 
                                    type = order_type, 
                                    quantity = quantity, 
                                    quoteOrderQty = quote_order_qty, 
                                    price = price, 
                                    newClientOrderId = new_client_order_id, 
                                    stopPrice = stop_price, 
                                    icebergQty = iceberg_qty, 
                                    timeInForce = time_in_force
                            ))    
    
    def batch_orders(self,
                     batch_orders:        List[str],
                     symbol:              str, 
                     side:                Literal["BUY", "SELL"],
                     order_type:          Literal["LIMIT", "MARKET", "LIMIT_MARKET", "IMMEDIATE_OR_CANCEL", "FILL_OR_KILL"],
                     quantity:            Optional[int] = None,
                     quote_order_qty:     Optional[int] = None,
                     price:               Optional[int] = None,
                     new_client_order_id: Optional[str] = None) -> dict:

        """
        ### Batch Orders
        #### Supports 20 orders with a same symbol in a batch,rate limit:2 times/s.
        #### Required permission: SPOT_DEAL_WRITE

        Weight(IP): 1,Weight(UID): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#batch-orders


        :param batch_orders: list of batchOrders,supports max 20 orders
        :type batch_orders: List[dict]
        :param symbol: symbol
        :type symbol: str
        :param side: order side
        :type side: str
        :param order_type: order type
        :type order_type: str
        :param quantity: (optional) quantity
        :type quantity: int
        :param quote_order_qty: (optional) quoteOrderQty
        :type quote_order_qty: int
        :param price: (optional) order price
        :type price: int
        :param new_client_order_id: (optional) ClientOrderId
        :type new_client_order_id: str


        :return: response dictionary
        :rtype: dict
        """
        return self.call("POST", "api/v3/batchOrders",
                        params = dict(
                                batchOrders = batch_orders,
                                symbol = symbol,
                                side = side,
                                type = order_type,
                                quantity = quantity,
                                quoteOrderQty = quote_order_qty,
                                price = price,
                                newClientOrderId = new_client_order_id
                        ))

    def cancel_order(self,
                     symbol:               str,
                     order_id:             Optional[str] = None,
                     orig_client_order_id: Optional[str] = None,
                     new_client_order_id:  Optional[str] = None) -> dict:
        """
        ### Cancel Order.
        #### Required permission: SPOT_DEAL_WRITE

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#cancel-order

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
        return self.call("DELETE", "api/v3/order",
                        params = dict(
                                symbol = symbol,
                                orderId = order_id,
                                origClientOrderId = orig_client_order_id,
                                newClientOrderId = new_client_order_id
                        ))    

    def cancel_all_open_orders(self, symbol: str) -> dict:

        """
        ### Cancel all Open Orders on a Symbol.
        #### Required permission: SPOT_DEAL_WRITE

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#cancel-all-open-orders-on-a-symbol

        :param symbol: maximum input 5 symbols,separated by ",". e.g. "BTCUSDT,MXUSDT,ADAUSDT"
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("DELETE", "api/v3/openOrders",
                        params = dict(
                                symbol = symbol
                        ))

    def query_order(self,
                    symbol:               str, 
                    orig_client_order_id: Optional[str] = None,
                    order_id:             Optional[str] = None) -> dict:

        """
        ### Query Order.
        #### Required permission: SPOT_DEAL_READ
        Check an order's status.

        Weight(IP): 2

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#query-order

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
        return self.call("GET", "api/v3/order",
                        params = dict(
                                symbol = symbol,
                                origClientOrderId = orig_client_order_id,
                                orderId = order_id
                        ))

    def current_open_orders(self, symbol: str) -> dict:

        """
        ### Current Open Orders.
        #### Required permission: SPOT_DEAL_READ

        Weight(IP): 3

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#current-open-orders

        :param symbol: 
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/openOrders", params = dict(symbol = symbol))

    def all_orders(self, 
                   symbol:     str, 
                   start_time: Optional[int] = None, 
                   end_time:   Optional[int] = None, 
                   limit:      Optional[int] = None) -> dict:

        """
        ### All Orders.
        #### Required permission: SPOT_DEAL_READ

        Weight(IP): 10

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#all-orders

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
        return self.call("GET", "api/v3/allOrders",
                        params=dict(
                                symbol=symbol,
                                startTime=start_time,
                                endTime=end_time,
                                limit=limit
                        ))

    def account_information(self) -> dict:

        """
        ### Account Information.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 10

        Get current account information,rate limit:2 times/s.

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#account-information

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/account")

    def account_trade_list(self, 
                           symbol:     str, 
                           order_id:   Optional[str] = None, 
                           start_time: Optional[int] = None, 
                           end_time:   Optional[int] = None, 
                           limit:      Optional[int] = None) -> dict:

        """
        ### Account Trade List.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 10

        Get trades for a specific account and symbol,
        Only the transaction records in the past 1 month can be queried.
        If you want to view more transaction records, please use the export function on the web side, 
        which supports exporting transaction records of the past 3 years at most.

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#account-trade-list

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
        return self.call("GET", "api/v3/myTrades",
                        params = dict(
                                symbol = symbol,
                                orderId = order_id,
                                startTime = start_time,
                                endTime = end_time,
                                limit = limit
                        ))

    def enable_mx_deduct(self, mx_deduct_enable: bool) -> dict:
        """
        ### Enable MX Deduct.
        #### Required permission: SPOT_DEAL_WRITE
        Enable or disable MX deduct for spot commission fee

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#enable-mx-deduct

        :param mx_deduct_enable: true:enable,false:disable
        :type mx_deduct_enable: bool

        :return: response dictionary
        :rtype: dict
        """
        return self.call("POST", "api/v3/mxDeduct/enable",
                        params = dict(
                                mxDeductEnable = mx_deduct_enable
                        ))

    def query_mx_deduct_status(self) -> dict:
        """
        ### Query MX Deduct Status.
        #### Required permission: SPOT_DEAL_READ

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#query-mx-deduct-status

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/mxDeduct/enable")


    # <=================================================================>
    #
    #                          Wallet Endpoints
    #
    # <=================================================================>

    def get_currency_info(self) -> dict:
        """
        ### Query the currency information.
        #### Required permission: SPOT_WITHDRAW_READ

        Weight(IP): 10

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#query-the-currency-information

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/capital/config/getall")

    def withdraw(self,
                 coin:              str,
                 address:           str,
                 amount:            int,
                 withdraw_order_id: Optional[str] = None,
                 network:           Optional[str] = None,
                 memo:              Optional[str] = None,
                 remark:            Optional[str] = None) -> dict:
        """
        ### Withdraw.
        #### Required permission: SPOT_WITHDRAW_WRITE

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#withdraw

        :param coin: coin
        :type coin: str
        :param withdraw_order_id: (optional) withdrawOrderId
        :type withdraw_order_id: str
        :param network: (optional) withdraw network
        :type network: str
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
        return self.call("POST", "api/v3/capital/withdraw/apply",
                        params = dict(
                                coin = coin,
                                withdrawOrderId = withdraw_order_id,
                                network = network,
                                address = address,
                                memo = memo,
                                amount = amount,
                                remark = remark
                        ))

    def cancel_withdraw(self, id: str) -> dict:
        """
        ### Cancel withdraw.
        #### Required permission: SPOT_WITHDRAW_W

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#cancel-withdraw

        :param id: withdraw id
        :type id: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("DELETE", "api/v3/capital/withdraw", params=dict(id=id))

    def deposit_history(self,
                        coin:       Optional[str] = None,
                        status:     Optional[str] = None,
                        start_time: Optional[int] = None,
                        end_time:   Optional[int] = None,
                        limit:      Optional[int] = None) -> dict:

        """
        ### Deposit History(supporting network).
        #### Required permission: SPOT_WITHDRAW_READ

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#deposit-history-supporting-network

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
        return self.call("GET", "api/v3/capital/deposit/hisrec",
                        params = dict(
                                coin = coin,
                                status = status,
                                startTime = start_time,
                                endTime = end_time,
                                limit = limit
                        ))

    def withdraw_history(self, 
                         coin:       Optional[str] = None, 
                         status:     Optional[str] = None, 
                         limit:      Optional[int] = None, 
                         start_time: Optional[str] = None, 
                         end_time:   Optional[str] = None) -> dict:
        """
        ### Withdraw History (supporting network).
        #### Required permission: SPOT_WITHDRAW_READ

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#withdraw-history-supporting-network

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
        return self.call("GET", "api/v3/capital/withdraw/history",
                        params = dict(
                                coin = coin,
                                status = status,
                                limit = limit,
                                startTime = start_time,
                                endTime = end_time
                        ))

    def generate_deposit_address(self, 
                                 coin:    str, 
                                 network: str) -> dict:
        """
        ### Generate deposit address (supporting network).
        #### Required permission: SPOT_WITHDRAW_WRITE

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#generate-deposit-address-supporting-network

        :param coin: coin
        :type coin: str
        :param network: deposit network
        :type network: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("POST", "api/v3/capital/deposit/address",
                        params = dict(
                                coin = coin,
                                network = network
                        ))

    def deposit_address(self, 
                        coin: str, 
                        network: Optional[str] = None) -> dict:
        """
        ### Deposit Address (supporting network).
        #### Required permission: SPOT_WITHDRAW_READ

        Weight(IP): 10

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#deposit-address-supporting-network

        :param coin: coin
        :type coin: str
        :param network: (optional) deposit network
        :type network: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/capital/deposit/address",
                        params = dict(
                                coin = coin,
                                network = network,
                        ))

    def withdraw_address(self, 
                         coin:  Optional[str] = None, 
                         page:  Optional[int] = None, 
                         limit: Optional[int] = None) -> dict:
        """
        ### Withdraw Address (supporting network).
        #### Required permission: SPOT_WITHDRAW_R

        Weight(IP): 10

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#withdraw-address-supporting-network


        :param coin: (optional) coin
        :type coin: str
        :param page: (optional) page,default 1
        :type page: int
        :param limit: (optional) limit for per page,default 20
        :type limit: int


        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/capital/withdraw/address",
                        params = dict(
                                coin = coin,
                                page = page,
                                limit = limit
                        ))

    def user_universal_transfer(self, 
                                from_account_type: str,
                                to_account_type:   str,
                                asset:             str,
                                amount:            int) -> dict:
        """
        ### User Universal Transfer.
        #### Required permission: SPOT_TRANSFER_WRITE

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#user-universal-transfer

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
        return self.call("POST", "api/v3/capital/transfer",
                        params = dict(
                                fromAccountType = from_account_type,
                                toAccountType = to_account_type,
                                asset = asset,
                                amount = amount
                        ))

    def user_universal_transfer_history(self,
                                        from_account_type: Literal["SPOT", "FUTURES"],
                                        to_account_type:   Literal["SPOT", "FUTURES"],
                                        start_time:        Optional[str] = None,
                                        end_time:          Optional[str] = None,
                                        page:              Optional[int] = 1,
                                        size:              Optional[int] = 10) -> dict:
        """
        ### Query User Universal Transfer History.
        #### Required permission: SPOT_TRANSFER_READ
        Only can quary the data for the last six months
        If 'startTime' and 'endTime' are not send, will return the last seven days' data by default

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#query-user-universal-transfer-history

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
        return self.call("GET", "api/v3/capital/transfer",
                        params = dict(
                                fromAccountType = from_account_type,
                                toAccountType = to_account_type,
                                startTime = start_time,
                                endTime = end_time,
                                page = page,
                                size = size
                        ))

    def user_universal_transfer_history_by_tranid(self, tran_id: str) -> dict:
        """
        ### Query User Universal Transfer History (by tranId).
        #### Required permission: SPOT_TRANSFER_R
        Only can quary the data for the last six months

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#query-user-universal-transfer-history-by-tranid

        :param tran_id: tranId
        :type tran_id: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", f"api/v3/capital/transfer/tranId", params=dict(tranId=tran_id))

    def get_assets_convert_into_mx(self) -> dict:
        """
        ### Get Assets That Can Be Converted Into MX.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#get-assets-that-can-be-converted-into-mx

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/capital/convert/list")

    def dust_transfer(self, asset: Union[str, List[str]]) -> dict:
        """
        ### Dust Transfer.
        #### Required permission: SPOT_ACCOUNT_W

        Weight(IP): 10

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#dust-transfer

        :param asset: The asset being converted.(max 15 assert)eg:asset=BTC,FIL,ETH
        :type asset: Union[str, List[str]]

        :return: response dictionary
        :rtype: dict
        """
        return self.call("POST", "api/v3/capital/convert",
                        params = dict(
                                asset = ','.join(asset) if isinstance(asset, list) else asset
                        ))

    def dustlog(self, 
                start_time: Optional[int] = None, 
                end_time:   Optional[int] = None, 
                page:       Optional[int] = None, 
                limit:      Optional[int] = None) -> dict:
        """
        ### DustLog.
        #### Required permission: SPOT_DEAL_READ

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#dustlog

        
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
        return self.call("GET", "api/v3/capital/convert",
                        params = dict(
                                startTime = start_time,
                                endTime = end_time,
                                page = page,
                                limit = limit
                        ))

    # <=================================================================>
    #
    #                               ETF
    #
    # <=================================================================>

    def get_etf_info(self, symbol: Optional[str] = None) -> dict:
        """
        ### Get ETF info.
        #### Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#get-etf-info

        :param symbol: (optional) ETF symbol
        :type symbol: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/etf/info",
                        params = dict(
                                symbol = symbol
                        ))

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

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#listen-key

        Start a new user data stream. The stream will close after 60 minutes unless a keepalive is sent.

        :return: response dictionary
        :rtype: dict
        """
        return self.call("POST", "api/v3/userDataStream", params = {"please_sign_it": None})

    def keep_alive_listen_key(self, listen_key: str) -> dict:
        """
        ### Keep-alive a ListenKey.
        #### Required permission: none

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#listen-key

        :param listen_key: Listen key
        :type listen_key: str

        :return: response dictionary
        :rtype: dict
        """
        return self.call("PUT", "api/v3/userDataStream", params=dict(listenKey=listen_key))

    def close_listen_key(self) -> dict:
        """
        ### Close a ListenKey.
        #### Required permission: None

        Weight(IP): 1, Weight(UID): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#listen-key

        :return: response dictionary
        :rtype: dict
        """
        return self.call("DELETE", "api/v3/userDataStream", params = {"please_sign_it": None})

    # <=================================================================>
    #
    #                          Rabate Endpoints
    #
    # <=================================================================>
    def get_rebate_history_records(self, 
                                   start_time: Optional[int] = None, 
                                   end_time:   Optional[int] = None, 
                                   page:       Optional[int] = None) -> dict:
        """
        ### Get Rebate History Records.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#rebate-endpoints

        
        :param start_time: (optional) 
        :type start_time: int
        :param end_time: (optional) 
        :type end_time: int
        :param page: (optional) default 1
        :type page: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/rebate/taxQuery",
                        params = dict(
                                startTime = start_time,
                                endTime = end_time,
                                page = page
                        ))

    def get_rebate_records_detail(self, 
                                  start_time: Optional[int] = None,
                                  end_time:   Optional[int] = None, 
                                  page:       Optional[int] = None) -> dict:

        """
        ### Get Rebate Records Detail.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#get-rebate-records-detail


        :param start_time: (optional) 
        :type start_time: int
        :param end_time: (optional) 
        :type end_time: int
        :param page: (optional) default 1
        :type page: int


        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/rebate/detail", 
                            params = dict(
                                    startTime = start_time, 
                                    endTime = end_time, 
                                    page = page
                            ))

    def get_self_rebate_records_detail(self, 
                                       start_time: Optional[int] = None, 
                                       end_time:   Optional[int] = None, 
                                       page:       Optional[int] = None) -> dict:
        """
        ### Get Self Rebate Records Detail.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#get-self-rebate-records-detail

        :param start_time: (optional) 
        :type start_time: int
        :param end_time: (optional) 
        :type end_time: int
        :param page: (optional) default 1
        :type page: int

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/rebate/detail/kickback",
                        params = dict(
                                startTime = start_time,
                                endTime = end_time,
                                page = page
                        ))

    def query_refercode(self) -> dict:
        """
        ### Query ReferCode.
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#query-refercode

        :return: response dictionary
        :rtype: dict
        """
        return self.call("GET", "api/v3/rebate/referCode", params=dict(please_sign_me = None))

class WebSocket(_SpotWebSocket):
    def __init__(self, 
                 api_key:            Optional[str]  = None, 
                 api_secret:         Optional[str]  = None,
                 listenKey:          Optional[str]  = None,
                 ping_interval:      Optional[int]  = 20, 
                 ping_timeout:       Optional[int]  = 10, 
                 retries:            Optional[int]  = 10,
                 restart_on_error:   Optional[bool] = True, 
                 trace_logging:      Optional[bool] = False,
                 http_proxy_host:    Optional[str]   = None,
                 http_proxy_port:    Optional[int]   = None,
                 http_no_proxy:      Optional[list]  = None,
                 http_proxy_auth:    Optional[tuple] = None,
                 http_proxy_timeout: Optional[int]   = None):
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
        """
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

        self.listenKey = listenKey

        # for keep alive connection to private spot websocket
        # need to send listen key at connection and send keep-alive request every 60 mins
        if api_key and api_secret:
            if not self.listenKey:
                auth = HTTP(api_key=api_key, api_secret=api_secret).create_listen_key()
                self.listenKey = auth.get("listenKey")
                logger.debug(f"create listenKey: {self.listenKey}")

            if not self.listenKey:
                raise Exception(f"ListenKey not found. Error: {auth}")

            kwargs["endpoint"] = f"wss://wbs.mexc.com/ws?listenKey={self.listenKey}"

            # setup keep-alive connection loop
            self.kal = threading.Thread(target=lambda: self._keep_alive_loop())
            self.kal.daemon = True
            self.kal.start()


        super().__init__(**kwargs)

    def _keep_alive_loop(self):
        """
        Runs a loop that sends a keep-alive message every 59 minutes to maintain the connection
        with the MEXC API. 

        :return: None
        """

        while True:
            time.sleep(59 * 60) # 59 min
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

    def deals_stream(self, 
                     callback: Callable[..., None],
                     symbol:   str):
        """
        ### Trade Streams
        The Trade Streams push raw trade information; each trade has a unique buyer and seller.

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#trade-streams

        :param callback: the callback function
        :type callback: Callable[..., None]
        :param symbol: the name of the contract
        :type symbol: str

        :return: None
        """
        params = [dict(
            symbol = symbol
        )]
        topic = "public.deals"
        self._ws_subscribe(topic, callback, params)

    def kline_stream(self, 
                     callback: Callable[..., None],
                     symbol:   str,
                     interval: int):
        """
        ### Kline Streams
        The Kline/Candlestick Stream push updates to the current klines/candlestick every second.

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#kline-streams

        :param callback: the callback function
        :type callback: Callable[..., None]
        :param symbol: the name of the contract
        :type symbol: str
        :param interval: the interval of the kline
        :type interval: int

        :return: None
        """
        params = [dict(
            symbol   = symbol,
            interval = interval
        )]
        topic = "public.kline"
        self._ws_subscribe(topic, callback, params)

    def increase_depth_stream(self, 
                     callback: Callable[..., None],
                     symbol:   str):
        """
        ### Diff.Depth Stream
        If the quantity is 0, it means that the order of the price has been cancel or traded,remove the price level.

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#diff-depth-stream

        :param callback: the callback function
        :type callback: Callable[..., None]
        :param symbol: the name of the contract
        :type symbol: str

        :return: None
        """
        params = [dict(
            symbol = symbol
        )]
        topic = "public.increase.depth"
        self._ws_subscribe(topic, callback, params)

    def limit_depth_stream(self, 
                     callback: Callable[..., None],
                     symbol:   str,
                     level:    int):
        """
        ### Partial Book Depth Streams
        Top bids and asks, Valid are 5, 10, or 20.

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#partial-book-depth-streams

        :param callback: the callback function
        :type callback: Callable[..., None]
        :param symbol: the name of the contract
        :type symbol: str
        :param level: the level of the depth. Valid are 5, 10, or 20.
        :type level: int

        :return: None
        """
        params = [dict(
            symbol = symbol,
            level  = level
        )]
        topic = "public.limit.depth"
        self._ws_subscribe(topic, callback, params)

    def book_ticker(self, 
                     callback: Callable[..., None],
                     symbol:   str):
        """
        ### Individual Symbol Book Ticker Streams
        Pushes any update to the best bid or ask's price or quantity in real-time for a specified symbol.

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#partial-book-depth-streams

        :param callback: the callback function
        :type callback: Callable[..., None]
        :param symbols: the names of the contracts
        :type symbols: str

        :return: None
        """
        params = [dict(
            symbol = symbol
        )]
        topic = "public.bookTicker"
        self._ws_subscribe(topic, callback, params)

    # <=================================================================>
    #
    #                                Private
    #
    # <=================================================================>

    def account_update(self, callback: Callable[..., None]):
        """
        ### Spot Account Update
        The server will push an update of the account assets when the account balance changes.

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#websocket-user-data-streams

        :param callback: the callback function
        :type callback: Callable[..., None]

        :return: None
        """
        params = [{}]
        topic = "private.account"
        self._ws_subscribe(topic, callback, params)

    def account_deals(self, callback: Callable[..., None]):
        """
        ### Spot Account Deals

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#spot-account-deals

        :param callback: the callback function
        :type callback: Callable[..., None]

        :return: None
        """
        params = [{}]
        topic = "private.deals"
        self._ws_subscribe(topic, callback, params)
    
    def account_orders(self, callback: Callable[..., None]):
        """
        ### Spot Account Orders

        https://mxcdevelop.github.io/apidocs/spot_v3_en/#spot-account-orders

        :param callback: the callback function
        :type callback: Callable[..., None]

        :return: None
        """
        params = [{}]
        topic = "private.orders"
        self._ws_subscribe(topic, callback, params)

