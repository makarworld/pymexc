import asyncio
import logging
from pymexc import spot, futures


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
api_key = "YOUR API KEY"
api_secret = "YOUR API SECRET KEY"


async def handle_message(message: dict):
    # handle websocket message
    print(message)


async def main():
    # SPOT V3

    # initialize HTTP client
    spot_client = spot.AsyncHTTP(api_key=api_key, api_secret=api_secret)
    # initialize WebSocket client
    ws_spot_client = spot.AsyncWebSocket(api_key=api_key, api_secret=api_secret)

    # FUTURES V1

    # initialize HTTP client
    futures_client = futures.AsyncHTTP(api_key=api_key, api_secret=api_secret)
    # initialize WebSocket client
    ws_futures_client = futures.AsyncWebSocket(api_key=api_key, api_secret=api_secret)

    # SPOT

    # make http request to api
    print(await spot_client.exchange_info())

    # create websocket connection to public channel (spot@public.deals.v3.api@BTCUSDT)
    # all messages will be handled by function `handle_message`
    await ws_spot_client.deals_stream(handle_message, "BTCUSDT")

    # Unsubscribe from deals topic
    # await ws_spot_client.unsubscribe(ws_spot_client.deals_stream)
    # OR
    # await ws_spot_client.unsubscribe("deals")

    # FUTURES

    # make http request to api
    print(await futures_client.index_price("MX_USDT"))

    # create websocket connection to public channel (sub.tickers)
    # all messages will be handled by function `handle_message`
    await ws_futures_client.tickers_stream(handle_message)

    # Unsubscribe from tickers topic
    await ws_futures_client.unsubscribe(ws_futures_client.tickers_stream)
    # OR
    # await ws_futures_client.unsubscribe("tickers")


# create new loop
loop = asyncio.new_event_loop()

# run main function
loop.run_until_complete(main())

# run forever for keep websocket connection
loop.run_forever()
