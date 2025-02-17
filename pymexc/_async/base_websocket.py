import asyncio
import functools
import hmac
import json
import logging
import time
import warnings
from typing import TYPE_CHECKING, Awaitable, Callable, Dict, List, Union

import websockets.client

if TYPE_CHECKING:
    from .spot import HTTP

logger = logging.getLogger(__name__)

SPOT = "wss://wbs.mexc.com/ws"
FUTURES = "wss://contract.mexc.com/edge"
FUTURES_PERSONAL_TOPICS = [
    "order",
    "order.deal",
    "position",
    "plan.order",
    "stop.order",
    "stop.planorder",
    "risk.limit",
    "adl.level",
    "asset",
    "liquidate.risk",
]


class CustomWebsockerClientProtocol(websockets.client.WebSocketClientProtocol):
    def __init__(self, ws_manager: "_WebSocketManager", *args, **kwargs):
        self.ws_manager: "_WebSocketManager" = ws_manager
        kwargs.pop("ping_timeout")

        super().__init__(*args, **kwargs, ping_timeout=None)

    async def ping(self) -> Awaitable[None]:
        await self.send(self.ws_manager.custom_ping_message)
        # pong_waiter is no released here. ping_timeout must be None.
        return

    def connection_open(self) -> None:
        super().connection_open()
        #
        self.loop.create_task(self.ws_manager._on_open())

    def connection_closed_exc(self) -> Exception:
        self.loop.create_task(self.ws_manager._on_close())
        #
        return super().connection_closed_exc()


class _WebSocketManager:
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
    ):
        # Set API keys.
        self.api_key: Union[str, None] = api_key
        self.api_secret: Union[str, None] = api_secret

        # Subscribe to private futures topics if proided
        self.subscribe_callback: Union[Callable, None] = subscribe_callback

        self.callback: Callable = callback_function
        self.ws_name: str = ws_name
        if api_key:
            self.ws_name += " (Auth)"

        self.proxy_settings = dict(
            http_proxy_host=http_proxy_host,
            http_proxy_port=http_proxy_port,
            http_no_proxy=http_no_proxy,
            http_proxy_auth=http_proxy_auth,
            http_proxy_timeout=http_proxy_timeout,
        )

        # Delta time for private auth expiration in seconds
        self.private_auth_expire = private_auth_expire

        # Setup the callback directory following the format:
        #   {
        #       "topic_name": function
        #   }
        self.callback_directory: Dict[str, Callable] = {}

        # Record the subscriptions made so that we can resubscribe if the WSS
        # connection is broken.
        self.subscriptions: List[dict] = []

        # Set ping settings.
        self.ping_interval: int = ping_interval
        self.custom_ping_message: str = json.dumps({"method": "ping"})
        self.retries: int = retries

        # Other optional data handling settings.
        self.restart_on_error: bool = restart_on_error
        self.trace_logging: bool = trace_logging

        if self.trace_logging:
            logging.getLogger("websockets.protocol").setLevel(logging.DEBUG)

        # Set initial state, initialize dictionary and connect.
        self._reset()
        self.attempting_connection = False

        self.last_subsctiption: Union[str, None] = None
        self.loop = loop or asyncio.get_event_loop()

        if ping_timeout:
            warnings.warn(
                "ping_timeout is deprecated for async websockets, please use just ping_interval.",
            )

    @property
    def is_spot(self):
        return self.endpoint.startswith(SPOT)

    @property
    def is_futures(self):
        return self.endpoint.startswith(FUTURES)

    def _topic(self, topic: str):
        return (
            topic.replace("sub.", "")
            .replace("push.", "")
            .replace("rs.sub.", "")
            .replace("spot@", "")
            .split(".v3.api")[0]
        )

    async def _on_open(self):
        """
        Log WS open.
        """
        logger.debug(f"WebSocket {self.ws_name} opened.")

    async def _loop_recv(self):
        while self.is_connected():
            try:
                msg = await self.ws.recv()
                await self._on_message(msg)
            except Exception as e:
                await self._on_error(e)

    async def _on_message(self, message: str):
        """
        Parse incoming messages.
        """
        message = json.loads(message)
        if self._is_custom_pong(message):
            print("pong", message)
            return
        else:
            await self.callback(message)

    def is_connected(self):
        try:
            if self.ws.open:
                return True
            else:
                return False
        except AttributeError:
            return False

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

            for req_id, subscription_message in self.subscriptions.items():
                await self.ws.send(json.dumps(subscription_message))

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
            self.ws: CustomWebsockerClientProtocol = await websockets.client.connect(
                uri=url,
                loop=self.loop,
                create_protocol=functools.partial(CustomWebsockerClientProtocol, self),
                ping_interval=20,
                ping_timeout=None,
                # on_message=lambda ws, msg: self._on_message(msg),
                # on_close=lambda ws, *args: self._on_close(),
                # on_open=lambda ws, *args: self._on_open(),
                # on_error=lambda ws, err: self._on_error(err),
                # on_pong=lambda ws, *args: self._on_pong(),
            )

            # parse incoming messages
            self.loop.create_task(self._loop_recv())

            # Setup the thread running WebSocketApp.
            # self.wst = threading.Thread(
            #     target=lambda: self.ws.run_forever(
            #         ping_interval=self.ping_interval,
            #         ping_timeout=self.ping_timeout,
            #         **self.proxy_settings,
            #     )
            # )

            # Configure as daemon; start.
            # self.wst.daemon = True
            # self.wst.start()

            # retries -= 1
            # while self.wst.is_alive():
            #     if self.ws.sock and self.is_connected():
            #         break

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

    def _set_personal_callback(
        self, callback: Callable = None, topics: List[str] = FUTURES_PERSONAL_TOPICS
    ):
        if callback:
            for topic in topics:
                self._set_callback(f"personal.{topic}", callback)

    async def _auth(self):
        # Generate signature

        # make auth if futures. spot has a different auth system.

        if self.is_spot:
            return

        timestamp = str(int(time.time() * 1000))
        _val = self.api_key + timestamp
        signature = str(
            hmac.new(
                bytes(self.api_secret, "utf-8"),
                bytes(_val, "utf-8"),
                digestmod="sha256",
            ).hexdigest()
        )

        # Authenticate with API.
        await self.ws.send(
            json.dumps(
                {
                    "subscribe": bool(self.subscribe_callback),
                    "method": "login",
                    "param": {
                        "apiKey": self.api_key,
                        "reqTime": timestamp,
                        "signature": signature,
                    },
                }
            )
        )
        self._set_personal_callback(self.subscribe_callback, FUTURES_PERSONAL_TOPICS)

    async def _on_error(self, error):
        """
        Exit on errors and raise exception, or attempt reconnect.
        """
        if type(error).__name__ not in [
            "WebSocketConnectionClosedException",
            "ConnectionResetError",
            "WebSocketTimeoutException",
            "ConnectionClosedError",
        ]:
            # Raises errors not related to websocket disconnection.
            self.exit()
            raise error

        if not self.exited:
            logger.error(
                f"WebSocket {self.ws_name} ({self.endpoint}) "
                f"encountered error: {error}."
            )
            self.exit()

        # Reconnect.
        if self.restart_on_error and not self.attempting_connection:
            self._reset()
            await self._connect(self.endpoint)

    async def _on_close(self):
        """
        Log WS close.
        """
        logger.debug(f"WebSocket {self.ws_name} closed.")

    @staticmethod
    def _is_custom_pong(message):
        """
        Referring to OPCODE_TEXT pongs from Bybit, not OPCODE_PONG.
        """
        if message.get("ret_msg") == "pong" or message.get("op") == "pong":
            return True

    def _reset(self):
        """
        Set state booleans and initialize dictionary.
        """
        self.exited = False
        self.auth = False
        self.data = {}

    def exit(self):
        """
        Closes the websocket connection.
        """
        self.exited = True

    def _check_callback_directory(self, topics):
        for topic in topics:
            if topic in self.callback_directory:
                raise Exception(f"You have already subscribed to this topic: {topic}")

    def _set_callback(self, topic: str, callback_function: Callable):
        self.callback_directory[topic] = callback_function

    def _get_callback(self, topic: str) -> Union[Callable[..., None], None]:
        return self.callback_directory.get(topic)

    def _pop_callback(self, topic: str) -> Union[Callable[..., None], None]:
        return (
            self.callback_directory.pop(topic)
            if self.callback_directory.get(topic)
            else None
        )

    async def _process_normal_message(self, message: dict):
        """
        Redirect message to callback function
        """
        topic = self._topic(message.get("channel") or message.get("c"))
        callback_data = message
        callback_function = self._get_callback(topic)
        if callback_function:
            await callback_function(callback_data)
        else:
            logger.warning(
                f"Callback for topic {topic} not found. | Message: {message}"
            )

    async def _process_subscription_message(self, message: dict):
        if message.get("id") == 0 and message.get("code") == 0:
            # If we get successful SPOT subscription, notify user
            logger.debug(f"Subscription to {message['msg']} successful.")

        elif (
            message.get("channel", "").startswith("rs.sub")
            or message.get("channel", "") == "rs.personal.filter"
            and message.get("data") == "success"
        ):
            # If we get successful FUTURES subscription, notify user
            logger.debug(f"Subscription to {message['channel']} successful.")

        else:
            # SPOT or FUTURES subscription fail
            response = message.get("msg") or message.get("data")

            logger.error(f"Couldn't subscribe to topic. Error: {response}.")
            if self.last_subsctiption:
                self._pop_callback(self.last_subsctiption)


# # # # # # # # # #
#                 #
#     FUTURES     #
#                 #
# # # # # # # # # #


class _FuturesWebSocketManager(_WebSocketManager):
    def __init__(self, ws_name, **kwargs):
        callback_function = (
            kwargs.pop("callback_function")
            if kwargs.get("callback_function")
            else self._handle_incoming_message
        )

        super().__init__(callback_function, ws_name, **kwargs)

    async def subscribe(self, topic, callback, params: dict = {}):
        subscription_args = {"method": topic, "param": params}
        self._check_callback_directory(subscription_args)

        while not self.is_connected():
            # Wait until the connection is open before subscribing.
            time.sleep(0.1)

        subscription_message = json.dumps(subscription_args)
        await self.ws.send(subscription_message)
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
            await self.ws.send(json.dumps({"method": f"unsub.{method}", "param": {}}))
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
            logger.debug(
                f"Authorization for {self.ws_name} failed. Please "
                f"check your API keys and restart."
            )

    async def _handle_incoming_message(self, message: dict):
        def is_auth_message():
            return message.get("channel", "") == "rs.login"

        def is_subscription_message():
            return (
                message.get("channel", "").startswith("rs.sub")
                or message.get("channel", "") == "rs.personal.filter"
            )

        def is_pong_message():
            return message.get("channel", "") in ("pong", "clientId")

        def is_error_message():
            return message.get("channel", "") == "rs.error"

        if is_auth_message():
            await self._process_auth_message(message)
        elif is_subscription_message():
            await self._process_subscription_message(message)
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


class _SpotWebSocketManager(_WebSocketManager):
    def __init__(self, ws_name, **kwargs):
        callback_function = (
            kwargs.pop("callback_function")
            if kwargs.get("callback_function")
            else self._handle_incoming_message
        )
        super().__init__(callback_function, ws_name, **kwargs)

        self.private_topics = ["account", "deals", "orders"]

    async def subscribe(self, topic: str, callback: Callable, params_list: list):
        subscription_args = {
            "method": "SUBSCRIPTION",
            "params": [
                "@".join([f"spot@{topic}.v3.api"] + list(map(str, params.values())))
                for params in params_list
            ],
        }
        self._check_callback_directory(subscription_args)

        while not self.is_connected():
            # Wait until the connection is open before subscribing.
            time.sleep(0.1)

        subscription_message = json.dumps(subscription_args)
        await self.ws.send(subscription_message)
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
            await self.ws.send(
                json.dumps(
                    {
                        "method": "UNSUBSCRIPTION",
                        "params": ["@".join([f"spot@{t}.v3.api"]) for t in topics],
                    }
                )
            )

            # remove subscriptions from list
            for i, sub in enumerate(self.subscriptions):
                new_params = [
                    x for x in sub["params"] for _topic in topics if _topic not in x
                ]
                if new_params:
                    self.subscriptions[i]["params"] = new_params
                else:
                    self.subscriptions.remove(sub)
                break

            logger.debug(f"Unsubscribed from {topics}")
        else:
            # some funcs in list
            topics = [
                x.__name__.replace("_stream", "").replace("_", ".")
                if getattr(x, "__name__", None)
                else x
                #
                for x in topics
            ]
            return await self.unsubscribe(*topics)

    async def _handle_incoming_message(self, message):
        def is_subscription_message():
            if (
                message.get("id") == 0
                and message.get("code") == 0
                and message.get("msg")
            ):
                return True
            else:
                return False

        if is_subscription_message():
            await self._process_subscription_message(message)
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

        # for keep alive connection to private spot websocket
        # need to send listen key at connection and send keep-alive request every 60 mins
        if api_key and api_secret:
            # setup keep-alive connection loop
            loop.create_task(self._keep_alive_loop())

        super().__init__(
            self.ws_name, api_key=api_key, api_secret=api_secret, loop=loop, **kwargs
        )

    async def get_listen_key(self):
        auth = await self.http.create_listen_key()
        self.listenKey = auth.get("listenKey")
        logger.debug(f"create listenKey: {self.listenKey}")

    async def _keep_alive_loop(self):
        """
        Runs a loop that sends a keep-alive message every 59 minutes to maintain the connection
        with the MEXC API.

        :return: None
        """
        while True:
            if self.listenKey:
                resp = await self.http.keep_alive_listen_key(self.listenKey)
                logger.debug(
                    f"keep-alive listenKey - {self.listenKey}. Response: {resp}"
                )
            else:
                await self.get_listen_key()

            await asyncio.sleep(59 * 60)  # 59 min

    async def connect(self):
        if not self.is_connected():
            if self.listenKey is None:
                await self.get_listen_key()

            await self._connect(self.endpoint + f"?listenKey={self.listenKey}")

    async def _ws_subscribe(self, topic, callback, params: list = []):
        await self.connect()
        await self.subscribe(topic, callback, params)
