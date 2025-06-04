import logging
from pymexc import futures


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def handle_message(msg: dict):
    print(msg)


# Init futures WebSocket client with your credentials and provide personal callback for capture all account data
ws_client = futures.WebSocket(
    api_key=..., api_secret=..., personal_callback=handle_message
)


# OR


# Init futures WebSocket client with your credentials
ws_client = futures.WebSocket(api_key=..., api_secret=...)
# Subscribe for all personal topics
ws_client.personal_stream(handle_message)


# OR for `order` only


# Subscribe for selected personal topics
ws_client.filter_stream(handle_message, {"filters": [{"filter": "order"}]})


# OR for `order.deal` for symbol `BTCUSDT`


# Subscribe for selected personal topics with rules
ws_client.filter_stream(
    handle_message, {"filters": [{"filter": "order.deal", "rules": ["BTCUSDT"]}]}
)

# loop program forever for save websocket connection
while True:
    pass
