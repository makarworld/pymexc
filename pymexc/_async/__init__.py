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

import asyncio
import os

try:
    from . import futures, spot
except ImportError:
    import pymexc._async.futures as futures
    import pymexc._async.spot as spot


if os.name == "nt":
    """
    Avoid error:

    ...\\site-packages\\curl_cffi\\aio.py:137: RuntimeWarning:
        Proactor event loop does not implement add_reader family of methods required.
        Registering an additional selector thread for add_reader support.
        To avoid this warning use:
            asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    self.loop = _get_selector(loop if loop is not None else asyncio.get_running_loop())
    """
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

__all__ = ["futures", "spot"]
