# This example for use subscribe method for many parameters at one topic.
# Goal - subscribe websocket with topic public.deals to all symbols from /api/v3/ticker/24hr (https://mexcdevelop.github.io/apidocs/spot_v3_en/#24hr-ticker-price-change-statistics)
# Use 30 symbols per each websocket connection
from pymexc import spot

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def handle_message(msg: dict):
    print(msg)


# get list of symbols from /api/v3/ticker/24hr
# https://mexcdevelop.github.io/apidocs/spot_v3_en/#24hr-ticker-price-change-statistics
ticker_24h = spot.HTTP().ticker_24h()

# create list with only symbols
symbols = [data["symbol"] for data in ticker_24h]

# separate the list into 30 symbols
symbol_lists = [symbols[i : i + 30] for i in range(0, len(symbols), 30)]

# topic
topic = "public.deals"

# for each 30 symbols in all symbols
for symbols in symbol_lists:
    # create new websocket class and subscribe it to topic with many parameters
    # all messages will be handled by function `handle_message`
    spot.WebSocket()._ws_subscribe(
        topic=topic,
        callback=handle_message,
        params=[{"symbol": symbol} for symbol in symbols],
    )

# loop program forever for save websocket connection
while True:
    pass
