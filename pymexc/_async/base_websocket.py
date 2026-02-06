import asyncio
import json
import logging
import warnings
from typing import TYPE_CHECKING, Callable

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from pymexc.base_websocket import (
    FUTURES,
    SPOT,
    _WebSocketManager,
)

if TYPE_CHECKING:
    from pymexc._async.spot import HTTP

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
        proto=True,
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

    def exit(self):
        if getattr(self, "exited", False):
            return

        if hasattr(self, "ping_timer") and self.ping_timer:
            self.ping_timer.cancel()
            self.ping_timer = None

        _ws = getattr(self, "ws", None)
        _session = getattr(self, "session", None)

        async def _shutdown():
            if _ws and not _ws.closed:
                await _ws.close()
            if _session and not _session.closed:
                await _session.close()

        try:
            running_loop = None
            try:
                running_loop = asyncio.get_running_loop()
            except RuntimeError:
                pass

            if self.loop and self.loop.is_running():
                if running_loop is self.loop:
                    self.loop.create_task(_shutdown())
                else:
                    asyncio.run_coroutine_threadsafe(_shutdown(), self.loop)
            else:
                asyncio.run(_shutdown())
        except Exception:
            logger.exception(f"WebSocket {self.ws_name} shutdown failed")
        finally:
            self.ws = None
            if hasattr(self, "session"):
                self.session = None
            self.exited = True

    async def __aenter__(self):
        """Async context manager entry - ensures connection is established."""
        if not self.is_connected() and hasattr(self, 'endpoint'):
            await self._connect(self.endpoint)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - ensures proper cleanup."""
        if hasattr(self, 'unsubscribe_all'):
            try:
                await self.unsubscribe_all()
            except Exception:
                pass

        if self.ws and not self.ws.closed:
            await self.ws.close()

        if hasattr(self, 'session') and self.session:
            await self.session.close()

        self.connected = False
        return False

    async def close_all(self):
        """Close all connections and cleanup resources."""
        await self.__aexit__(None, None, None)

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
            if self.session is not None and not self.session.closed:
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

            for subscription_message in self.subscriptions.values():
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
            logger.debug(f"WebSocket {self.ws_name} attempting connection... to {url}")

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
        self.ping_task = self.loop.create_task(self._ping_loop())

        self.attempting_connection = False

    async def _ping_loop(self):
        while True:
            try:
                await self.ws.send_str(self.custom_ping_message)
            except aiohttp.ClientPayloadError as e:
                await self._on_error(e)

            await asyncio.sleep(self.ping_interval)

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
        callback_topic = self._topic(topic)
        self._check_callback_directory(callback_topic)

        while not self.is_connected():
            # Wait until the connection is open before subscribing.
            await asyncio.sleep(0.1)

        await self.ws.send_json(subscription_args)
        self.subscriptions[topic] = subscription_args
        self._set_callback(callback_topic, callback)
        self.last_subsctiption = callback_topic

    async def unsubscribe(self, method: str | Callable) -> None:
        if not method:
            return

        if isinstance(method, str):
            # remove callback
            self._pop_callback(method)
            # send unsub message
            await self.ws.send_json({"method": f"unsub.{method}", "param": {}})

            # remove subscription from list
            for topic, sub in self.subscriptions.items():
                if sub["method"] == f"sub.{method}":
                    self.subscriptions.pop(topic)
                    break

            logger.debug(f"Unsubscribed from {method}")
        else:
            # this is a func, get name
            topic_name = method.__name__.replace("_stream", "").replace("_", ".")

            return await self.unsubscribe(topic_name)

    async def unsubscribe_all(self) -> None:
        """Unsubscribe from all active subscriptions."""
        topics = list(self.subscriptions.keys())
        for topic in topics:
            # Extract method name (remove "sub." prefix if present)
            method = topic[4:] if topic.startswith("sub.") else topic
            try:
                await self.unsubscribe(method)
            except Exception:
                logger.debug(f"Failed to unsubscribe from {method}")

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
            logger.error(f"WebSocket return error: {message}")
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
        topics = [
            self._build_topic_key(topic, params, interval)
            #
            for params in params_list
        ]

        subscription_args = {
            "method": "SUBSCRIPTION",
            "params": topics,
        }

        # Create unique topic keys for each params combination
        for topic_key in topics:
            self._check_callback_directory(topic_key)
            # Set callback for each unique topic key
            self._set_callback(topic_key, callback)

        while not self.is_connected():
            # Wait until the connection is open before subscribing.
            await asyncio.sleep(0.1)

        subscription_message = json.dumps(subscription_args)
        await self.ws.send_str(subscription_message)
        # Store subscription by base topic (for backward compatibility with unsubscribe)
        # But store all topic keys with params in callback_directory
        for topic in topics:
            self.subscriptions[topic] = subscription_args
            self.subscriptions[topic]["params"] = [topic]
            self.last_subsctiption = topic

        return topics[0] if len(topics) <= 1 else topics

    async def unsubscribe(self, *topics: str):
        if all([isinstance(topic, str) for topic in topics]):
            unsubscribe_message = {
                "method": "UNSUBSCRIPTION",
                "params": list(topics),
            }

            # remove callbacks and collect params for unsubscription
            for topic in topics:
                # Find subscription by base topic
                if topic in self.subscriptions:
                    # unsubscribe_message["params"].extend(self.subscriptions[topic]["params"])
                    self.subscriptions.pop(topic, None)

                # Remove all callbacks that start with this topic (including params)
                # Find all keys in callback_directory that match this topic
                keys_to_remove = [
                    k for k in list(self.callback_directory.keys()) if k == topic or k.startswith(topic + "@")
                ]
                for key in keys_to_remove:
                    self._pop_callback(key)

            # send unsub message
            if unsubscribe_message["params"]:
                await self.ws.send_str(json.dumps(unsubscribe_message))

            logger.debug(f"Unsubscribed from {topics}")
        else:
            # some funcs in list
            # topics = [
            #     x.__name__.replace("_stream", "").replace("_", ".") if getattr(x, "__name__", None) else x
            #     #
            #     for x in topics
            # ]
            # eturn self.unsubscribe(*topics)
            raise ValueError(f"Invalid topics, only `str` is allowed, got {[type(t) for t in topics]}: {topics}")

    async def unsubscribe_all(self) -> None:
        """Unsubscribe from all active subscriptions."""
        topics = list(self.subscriptions.keys())
        if topics:
            try:
                await self.unsubscribe(*topics)
            except Exception:
                logger.debug(f"Failed to unsubscribe from topics: {topics}")

    async def _handle_incoming_message(self, message):
        logger.debug(f"_handle_incoming_message: {message}")

        def is_subscription_message():
            if message.get("id") == 0 and message.get("code") == 0:
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
        if isinstance(topic, str) and topic.startswith("private."):
            ensure_listen_key = getattr(self, "_ensure_listen_key", None)
            logger.debug(f"ensure_listen_key: {ensure_listen_key}")
            if ensure_listen_key:
                await ensure_listen_key()

        if not self.is_connected():
            await self._connect(self.endpoint)

        logger.info(f"Subscribing to topic: {topic} | params: {params} | interval: {interval}")
        return await self.subscribe(topic, callback, params, interval)
