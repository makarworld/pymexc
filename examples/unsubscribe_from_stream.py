import logging
from pymexc import futures


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def handle_message(msg: dict):
    print(msg)


# Init futures WebSocket client with your credentials
ws_client = futures.WebSocket(api_key=..., api_secret=...)

# subscribe for tickers topic
ws_client.tickers_stream(handle_message)

# unsubscribe from tickers topic
ws_client.unsubscribe(ws_client.tickers_stream)
# or
ws_client.unsubscribe("tickers")

# loop program forever for save websocket connection
while True:
    pass
