"""
### Usage

```python
from pymexc import spot, futures

api_key = "YOUR API KEY"
api_secret = "YOUR API SECRET KEY"

def handle_message(message):
    # handle websocket message
    print(message)


# SPOT V3
# initialize HTTP client
spot_client = spot.HTTP(api_key = api_key, api_secret = api_secret)
# initialize WebSocket client
ws_spot_client = spot.WebSocket(api_key = api_key, api_secret = api_secret)

# make http request to api
print(spot_client.exchange_info())

# create websocket connection to public channel (spot@public.deals.v3.api@BTCUSDT)
# all messages will be handled by function `handle_message`
ws_spot_client.deals_stream(handle_message, "BTCUSDT")


# FUTURES V1

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

try:
    from . import _async, futures, proto, spot, web
    from ._async.futures import HTTP as AsyncFuturesHTTP
    from ._async.futures import WebSocket as AsyncFuturesWebSocket
    from ._async.spot import HTTP as AsyncSpotHTTP
    from ._async.spot import WebSocket as AsyncSpotWebSocket
    from .futures import HTTP as FuturesHTTP
    from .futures import WebSocket as FuturesWebSocket
    from .spot import HTTP as SpotHTTP
    from .spot import WebSocket as SpotWebSocket
except ImportError:
    import pymexc._async as _async
    import pymexc.futures as futures
    import pymexc.proto as proto
    import pymexc.spot as spot
    import pymexc.web as web
    from pymexc._async.futures import HTTP as AsyncFuturesHTTP
    from pymexc._async.futures import WebSocket as AsyncFuturesWebSocket
    from pymexc._async.spot import HTTP as AsyncSpotHTTP
    from pymexc._async.spot import WebSocket as AsyncSpotWebSocket
    from pymexc.futures import HTTP as FuturesHTTP
    from pymexc.futures import WebSocket as FuturesWebSocket
    from pymexc.spot import HTTP as SpotHTTP
    from pymexc.spot import WebSocket as SpotWebSocket

logger = logging.getLogger(__name__)


__all__ = [
    "_async",
    "futures",
    "spot",
    "web",
    "proto",
    "AsyncFuturesHTTP",
    "AsyncFuturesWebSocket",
    "AsyncSpotHTTP",
    "AsyncSpotWebSocket",
    "FuturesHTTP",
    "FuturesWebSocket",
    "SpotHTTP",
    "SpotWebSocket",
]
