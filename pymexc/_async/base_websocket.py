import asyncio
import json
import logging
import time
import warnings
from typing import TYPE_CHECKING, Awaitable, Callable, Dict, List, Union

import aiohttp
import websockets.client

from pymexc.base_websocket import (
    _WebSocketManager,
    SPOT,
    FUTURES,
)
from aiohttp import ClientSession, ClientTimeout

if TYPE_CHECKING:
    from .spot import HTTP

logger = logging.getLogger(__name__)


class _AsyncWebSocketManager(_WebSocketManager):
    endpoint: str

    def __init__(
        self,
        callback_function,
        ws_name,
        api_key=None,
        api_secret=None,
        subscribe_callback=None,
        ping_interval=20,
        ping_timeout=None,
        retries=10,
        restart_on_error=True,
        trace_logging=False,
        private_auth_expire=1,
        http_proxy_host=None,
        http_proxy_port=None,
        http_no_proxy=None,
        http_proxy_auth=None,
        http_proxy_timeout=None,
        loop=None,
        proto=False,
        extend_proto_body=False,
    ):
        super().__init__(
            callback_function,
            ws_name,
            api_key=api_key,
            api_secret=api_secret,
            subscribe_callback=subscribe_callback,
            ping_interval=ping_interval,
            ping_timeout=ping_timeout,
            retries=retries,
            restart_on_error=restart_on_error,
            trace_logging=trace_logging,
            private_auth_expire=private_auth_expire,
            http_proxy_host=http_proxy_host,
            http_proxy_port=http_proxy_port,
            http_no_proxy=http_no_proxy,
            http_proxy_auth=http_proxy_auth,
            http_proxy_timeout=http_proxy_timeout,
            proto=proto,
            extend_proto_body=extend_proto_body,
        )
        self.connected = False
        self.loop = loop or asyncio.get_event_loop()

        if ping_timeout:
            warnings.warn(
                "ping_timeout is deprecated for async websockets, please use just ping_interval.",
            )

    async def _on_open(self):
        self.connected = True
        super()._on_open()

    async def _loop_recv(self):
        try:
            async for msg in self.ws:
                if msg.type in [aiohttp.WSMsgType.TEXT, aiohttp.WSMsgType.BINARY]:
                    await self._on_message(msg.data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    await self._on_error(msg)
                    break
        finally:
            await self._on_close()
            await self.session.close()

    async def _on_message(self, message: str | bytes):
        """
        Parse incoming messages.
        """
        _message = super()._on_message(message, parse_only=True)
        await self.callback(_message)

    def is_connected(self):
        return self.connected

    async def _connect(self, url):
        """
        Open websocket in a thread.
        """

        async def resubscribe_to_topics():
            if not self.subscriptions:
                # There are no subscriptions to resubscribe to, probably
                # because this is a brand new WSS initialisation so there was
                # no previous WSS connection.
                return

            for subscription_message in self.subscriptions:
                await self.ws.send_json(subscription_message)

        self.attempting_connection = True

        self.endpoint = url

        # Attempt to connect for X seconds.
        retries = self.retries
        if retries == 0:
            infinitely_reconnect = True
        else:
            infinitely_reconnect = False

        while (infinitely_reconnect or retries > 0) and not self.is_connected():
            logger.info(f"WebSocket {self.ws_name} attempting connection...")

            self.session = ClientSession()
            timeout = ClientTimeout(total=60)
            self.ws = await self.session.ws_connect(
                url=url,
                proxy=f"http://{self.proxy_settings['http_proxy_host']}:{self.proxy_settings['http_proxy_port']}"
                if self.proxy_settings["http_proxy_host"]
                else None,
                proxy_auth=self.proxy_settings["http_proxy_auth"],
                timeout=timeout,
            )

            # parse incoming messages
            await self._on_open()
            self.loop.create_task(self._loop_recv())

            if not self.is_connected():
                # If connection was not successful, raise error.
                if not infinitely_reconnect and retries <= 0:
                    self.exit()
                    raise Exception(
                        f"WebSocket {self.ws_name} ({self.endpoint}) connection "
                        f"failed. Too many connection attempts. pymexc will no "
                        f"longer try to reconnect."
                    )

        logger.info(f"WebSocket {self.ws_name} connected")

        # If given an api_key, authenticate.
        if self.api_key and self.api_secret:
            await self._auth()

        await resubscribe_to_topics()

        self.attempting_connection = False

    async def _auth(self):
        msg = super()._auth(parse_only=True)

        # Authenticate with API.
        await self.ws.send_json(msg)

    async def _on_error(self, error: Exception):
        super()._on_error(error, parse_only=True)

        # Reconnect.
        if self.restart_on_error and not self.attempting_connection:
            self._reset()
            await self._connect(self.endpoint)

    async def _on_close(self):
        self.connected = False
        super()._on_close()

    async def _process_normal_message(self, message: dict):
        callback_function, callback_data = super()._process_normal_message(message=message, parse_only=True)

        if callback_function is None:
            return

        await callback_function(callback_data)


# # # # # # # # # #
#                 #
#     FUTURES     #
#                 #
# # # # # # # # # #


class _FuturesWebSocketManager(_AsyncWebSocketManager):
    def __init__(self, ws_name, **kwargs):
        callback_function = (
            kwargs.pop("callback_function") if kwargs.get("callback_function") else self._handle_incoming_message
        )

        super().__init__(callback_function, ws_name, **kwargs)

    async def subscribe(self, topic, callback, params: dict = {}):
        subscription_args = {"method": topic, "param": params}
        self._check_callback_directory(subscription_args)

        while not self.is_connected():
            # Wait until the connection is open before subscribing.
            await asyncio.sleep(0.1)

        await self.ws.send_json(subscription_args)
        self.subscriptions.append(subscription_args)
        self._set_callback(self._topic(topic), callback)
        self.last_subsctiption = self._topic(topic)

    async def unsubscribe(self, method: str | Callable) -> None:
        if not method:
            return

        if isinstance(method, str):
            # remove callback
            self._pop_callback(method)
            # send unsub message
            await self.ws.send_json({"method": f"unsub.{method}", "param": {}})

            # remove subscription from list
            for sub in self.subscriptions:
                if sub["method"] == f"sub.{method}":
                    self.subscriptions.remove(sub)
                    break

            logger.debug(f"Unsubscribed from {method}")
        else:
            # this is a func, get name
            topic_name = method.__name__.replace("_stream", "").replace("_", ".")

            return await self.unsubscribe(topic_name)

    async def _process_auth_message(self, message: dict):
        # If we get successful futures auth, notify user
        if message.get("data") == "success":
            logger.debug(f"Authorization for {self.ws_name} successful.")
            self.auth = True

        # If we get unsuccessful auth, notify user.
        elif message.get("data") != "success":  # !!!!
            logger.debug(f"Authorization for {self.ws_name} failed. Please check your API keys and restart.")

    async def _handle_incoming_message(self, message: dict):
        def is_auth_message():
            return message.get("channel", "") == "rs.login"

        def is_subscription_message():
            return message.get("channel", "").startswith("rs.sub") or message.get("channel", "") == "rs.personal.filter"

        def is_pong_message():
            return message.get("channel", "") in ("pong", "clientId")

        def is_error_message():
            return message.get("channel", "") == "rs.error"

        if is_auth_message():
            await self._process_auth_message(message)
        elif is_subscription_message():
            self._process_subscription_message(message)
        elif is_pong_message():
            pass
        elif is_error_message():
            print(f"WebSocket return error: {message}")
        else:
            await self._process_normal_message(message)

    async def custom_topic_stream(self, topic, callback):
        return await self.subscribe(topic=topic, callback=callback)


class _FuturesWebSocket(_FuturesWebSocketManager):
    def __init__(
        self,
        api_key: str = None,
        api_secret: str = None,
        loop: asyncio.AbstractEventLoop = None,
        subscribe_callback: Callable = None,
        **kwargs,
    ):
        self.ws_name = "FuturesV1"
        self.endpoint = FUTURES
        loop = loop or asyncio.get_event_loop()

        if subscribe_callback:
            loop.create_task(self.connect())

        super().__init__(
            self.ws_name,
            api_key=api_key,
            api_secret=api_secret,
            loop=loop,
            subscribe_callback=subscribe_callback,
            **kwargs,
        )

    async def connect(self):
        if not self.is_connected():
            await self._connect(self.endpoint)

    async def _ws_subscribe(self, topic, callback, params: list = []):
        await self.connect()
        await self.subscribe(topic, callback, params)


# # # # # # # # # #
#                 #
#       SPOT      #
#                 #
# # # # # # # # # #


class _SpotWebSocketManager(_AsyncWebSocketManager):
    def __init__(self, ws_name, **kwargs):
        callback_function = (
            kwargs.pop("callback_function") if kwargs.get("callback_function") else self._handle_incoming_message
        )
        super().__init__(callback_function, ws_name, **kwargs)

        self.private_topics = ["account", "deals", "orders"]

    async def subscribe(self, topic: str, callback: Callable, params_list: list, interval: str = None):
        subscription_args = {
            "method": "SUBSCRIPTION",
            "params": [
                "@".join(
                    [f"spot@{topic}.v3.api" + (".pb" if self.proto else "")] 
                    + ([str(interval)] if interval else [])
                    + list(map(str, params.values()))
                )
                for params in params_list
            ],
        }
        self._check_callback_directory(subscription_args)

        while not self.is_connected():
            # Wait until the connection is open before subscribing.
            await asyncio.sleep(0.1)

        await self.ws.send_json(subscription_args)
        self.subscriptions.append(subscription_args)
        self._set_callback(topic, callback)
        self.last_subsctiption = topic

    async def unsubscribe(self, *topics: str | Callable):
        if all([isinstance(topic, str) for topic in topics]):
            topics = [
                f"private.{topic}"
                if topic in self.private_topics
                else f"public.{topic}"
                # if user provide function .book_ticker_stream()
                .replace("book.ticker", "bookTicker")
                for topic in topics
            ]
            # remove callbacks
            for topic in topics:
                self._pop_callback(topic)

            # send unsub message
            await self.ws.send_json(
                {
                    "method": "UNSUBSCRIPTION",
                    "params": ["@".join([f"spot@{t}.v3.api" + (".pb" if self.proto else "")]) for t in topics],
                }
            )

            # remove subscriptions from list
            for i, sub in enumerate(self.subscriptions):
                new_params = [x for x in sub["params"] for _topic in topics if _topic not in x]
                if new_params:
                    self.subscriptions[i]["params"] = new_params
                else:
                    self.subscriptions.remove(sub)
                break

            logger.debug(f"Unsubscribed from {topics}")
        else:
            # some funcs in list
            topics = [
                x.__name__.replace("_stream", "").replace("_", ".") if getattr(x, "__name__", None) else x
                #
                for x in topics
            ]
            return await self.unsubscribe(*topics)

    async def _handle_incoming_message(self, message):
        def is_subscription_message():
            if message.get("id") == 0 and message.get("code") == 0 and message.get("msg"):
                return True
            else:
                return False

        if isinstance(message, dict) and is_subscription_message():
            self._process_subscription_message(message)
        else:
            await self._process_normal_message(message)

    async def custom_topic_stream(self, topic, callback):
        return await self.subscribe(topic=topic, callback=callback)


class _SpotWebSocket(_SpotWebSocketManager):
    listenKey: str
    http: "HTTP"

    def __init__(
        self,
        endpoint: str = SPOT,
        api_key: str = None,
        api_secret: str = None,
        loop: asyncio.AbstractEventLoop = None,
        **kwargs,
    ):
        self.ws_name = "SpotV3"
        self.endpoint = endpoint
        loop = loop or asyncio.get_event_loop()

        super().__init__(self.ws_name, api_key=api_key, api_secret=api_secret, loop=loop, **kwargs)

    async def _ws_subscribe(self, topic, callback, params: list = [], interval: str = None):
        # For private topics, ensure we have a listenKey before connecting
        if topic.startswith("private.") and self.api_key and self.api_secret:
            # Wait for listenKey to be generated if needed
            if not hasattr(self, 'listenKey') or not self.listenKey:
                # Wait a bit for _keep_alive_loop to generate the listenKey
                import asyncio
                for _ in range(10):  # Try for up to 5 seconds
                    await asyncio.sleep(0.5)
                    if hasattr(self, 'listenKey') and self.listenKey:
                        break
                else:
                    # If still no listenKey, we have a problem
                    raise Exception("Failed to generate listenKey for private streams. Check API credentials.")
        
        if not self.is_connected():
            await self._connect(self.endpoint)

        await self.subscribe(topic, callback, params, interval)
