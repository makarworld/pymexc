[![PyPI version](https://badge.fury.io/py/pymexc.svg)](https://badge.fury.io/py/pymexc)
[![License](https://img.shields.io/github/license/makarworld/pymexc.svg?label=License&logo=apache&cacheSeconds=2592000)](https://github.com/makarworld/pymexc/blob/main/LICENSE)
[![image](https://img.shields.io/pypi/pyversions/pymexc.svg)](https://pypi.org/project/pymexc/)
[![Github last commit date](https://img.shields.io/github/last-commit/makarworld/pymexc.svg?label=Updated&logo=github&cacheSeconds=600)](https://github.com/makarworld/pymexc/commits)

# pymexc
`pymexc` is an unofficial Python library for interacting with the [MEXC crypto exchange](https://www.mexc.com/). It provides a simple and intuitive API for making requests to the [MEXC API endpoints](https://mexcdevelop.github.io/apidocs/spot_v3_en/#introduction).

Most of the code was generated with ChatGPT, if you see an error, write to issues.

# Installation
You can install pymexc using pip:

```bash
pip install pymexc
```

# Getting Started
To start working with pymexc, you must import spot or futures from the library. Each of them contains 2 classes: HTTP and WebSocket. To work with simple requests, you need to initialize the HTTP class. To work with web sockets you need to initialize the WebSocket class 


## Example:

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
```


# Documentation
You can find the official documentation for the MEXC API [here](https://mexcdevelop.github.io/apidocs/spot_v3_en/#introduction).

# License
This library is licensed under the MIT License.
