import logging
from pymexc import spot
from pymexc.proto import ProtoTyping


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def handle_message(msg: ProtoTyping.PublicSpotKlineV3Api):
    print(msg.amount)
    print(msg)


# Init futures WebSocket client with your credentials and provide personal callback for capture all account data
ws_client = spot.WebSocket(api_key=..., api_secret=..., proto=True)

# Subscribe for kline topic
ws_client.kline_stream(handle_message, symbol="BTCUSDT", interval="Min1")


# loop program forever for save websocket connection
while True:
    pass
