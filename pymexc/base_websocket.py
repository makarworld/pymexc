import hmac
import json
import logging
import threading
import time
from typing import Callable, Dict, List, Union

import websocket

from pymexc.proto import ProtoTyping, PublicSpotKlineV3Api, PushDataV3ApiWrapper

logger = logging.getLogger(__name__)

SPOT = "wss://wbs-api.mexc.com/ws"
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
        ping_timeout=10,
        retries=10,
        restart_on_error=True,
        trace_logging=False,
        private_auth_expire=1,
        http_proxy_host=None,
        http_proxy_port=None,
        http_no_proxy=None,
        http_proxy_auth=None,
        http_proxy_timeout=None,
        proto=False,
        extend_proto_body=False,
    ):
        # Set API keys.
        self.api_key: Union[str, None] = api_key
        self.api_secret: Union[str, None] = api_secret

        # Subscribe to private futures topics if proided
        self.subscribe_callback: Union[Callable, None] = subscribe_callback

        self.callback: Callable[[dict | ProtoTyping.PushDataV3ApiWrapper], None] = callback_function
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

        # Use new protocol
        self.proto = proto
        self.extend_proto_body = extend_proto_body

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
        self.ping_timeout: int = ping_timeout
        self.custom_ping_message: str = json.dumps({"method": "ping"})
        self.retries: int = retries

        # Other optional data handling settings.
        self.restart_on_error: bool = restart_on_error

        # Enable websocket-client's trace logging for extra debug information
        # on the websocket connection, including the raw sent & recv messages
        websocket.enableTrace(trace_logging)

        # Set initial state, initialize dictionary and connect.
        self._reset()
        self.attempting_connection = False

        self.last_subsctiption: Union[str, None] = None
        self.ping_timer = None

    @property
    def is_spot(self):
        return self.endpoint.startswith(SPOT)

    @property
    def is_futures(self):
        return self.endpoint.startswith(FUTURES)

    def _topic(self, topic):
        # Handle None case for private streams
        if topic is None:
            return None
        
        return (
            topic.replace("sub.", "")
            .replace("push.", "")
            .replace("rs.sub.", "")
            .replace("spot@", "")
            .replace(".pb", "")
            .split(".v3.api")[0]
        )

    def _on_open(self):
        """
        Log WS open.
        """
        logger.debug(f"WebSocket {self.ws_name} opened.")

    def _on_message(self, message: str | bytes, parse_only: bool = False):
        """
        Parse incoming messages.
        """
        if isinstance(message, str):
            _message = json.loads(message)

        elif isinstance(message, bytes):
            # Deserialize message
            _message = PushDataV3ApiWrapper()
            _message.ParseFromString(message)

        else:
            raise ValueError(f"Unserializable message type: {type(message)} | {message}")

        if parse_only:
            return _message

        self.callback(_message)

    def is_connected(self):
        try:
            if self.ws.sock.connected:
                return True
            else:
                return False
        except AttributeError:
            return False

    def _connect(self, url):
        """
        Open websocket in a thread.
        """

        def resubscribe_to_topics():
            if not self.subscriptions:
                # There are no subscriptions to resubscribe to, probably
                # because this is a brand new WSS initialisation so there was
                # no previous WSS connection.
                return

            for subscription_message in self.subscriptions:
                self.ws.send(json.dumps(subscription_message))

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
            self.ws = websocket.WebSocketApp(
                url=url,
                on_message=lambda ws, msg: self._on_message(msg),
                on_close=lambda ws, *args: self._on_close(),
                on_open=lambda ws, *args: self._on_open(),
                on_error=lambda ws, err: self._on_error(err),
                on_pong=lambda ws, *args: self._on_pong(),
            )

            # Setup the thread running WebSocketApp.
            self.wst = threading.Thread(
                target=lambda: self.ws.run_forever(
                    ping_interval=self.ping_interval,
                    ping_timeout=self.ping_timeout,
                    **self.proxy_settings,
                )
            )

            # Configure as daemon; start.
            self.wst.daemon = True
            self.wst.start()

            retries -= 1
            while self.wst.is_alive():
                if self.ws.sock and self.is_connected():
                    break

            # If connection was not successful, raise error.
            if not infinitely_reconnect and retries <= 0:
                self.exit()
                raise websocket.WebSocketTimeoutException(
                    f"WebSocket {self.ws_name} ({self.endpoint}) connection "
                    f"failed. Too many connection attempts. pymex will no "
                    f"longer try to reconnect."
                )

        logger.info(f"WebSocket {self.ws_name} connected")

        # If given an api_key, authenticate.
        if self.api_key and self.api_secret:
            self._auth()

        resubscribe_to_topics()
        self._send_initial_ping()

        self.attempting_connection = False

    def _set_personal_callback(self, callback: Callable = None, topics: List[str] = FUTURES_PERSONAL_TOPICS):
        if callback:
            for topic in topics:
                self._set_callback(f"personal.{topic}", callback)

    def _auth(self, parse_only: bool = False):
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

        self._set_personal_callback(self.subscribe_callback, FUTURES_PERSONAL_TOPICS)

        msg = {
            "subscribe": bool(self.subscribe_callback),
            "method": "login",
            "param": {
                "apiKey": self.api_key,
                "reqTime": timestamp,
                "signature": signature,
            },
        }

        if parse_only:
            return msg

        # Authenticate with API.
        self.ws.send(json.dumps(msg))

    def _on_error(self, error: Exception, parse_only: bool = False):
        """
        Exit on errors and raise exception, or attempt reconnect.
        """
        if type(error).__name__ not in [
            "WebSocketConnectionClosedException",
            "ConnectionResetError",
            "WebSocketTimeoutException",
        ]:
            # Raises errors not related to websocket disconnection.
            self.exit()
            raise error

        if not self.exited:
            logger.error(f"WebSocket {self.ws_name} ({self.endpoint}) encountered error: {error}.")
            self.exit()

        if parse_only:
            return

        # Reconnect.
        if self.restart_on_error and not self.attempting_connection:
            self._reset()
            self._connect(self.endpoint)

    def _on_close(self):
        """
        Log WS close.
        """
        logger.debug(f"WebSocket {self.ws_name} closed.")

    def _on_pong(self):
        """
        Sends a custom ping upon the receipt of the pong frame.

        The websocket library will automatically send ping frames. However, to
        ensure the connection to Bybit stays open, we need to send a custom
        ping message separately from this. When we receive the response to the
        ping frame, this method is called, and we will send the custom ping as
        a normal OPCODE_TEXT message and not an OPCODE_PING.
        """
        self._send_custom_ping()

    def _send_custom_ping(self):
        try:
            self.ws.send(self.custom_ping_message)
        except websocket._exceptions.WebSocketConnectionClosedException as e:
            self.ping_timer.cancel()
            self._on_error(e)

    def _send_initial_ping(self):
        """https://github.com/bybit-exchange/pybit/issues/164"""
        if self.ping_timer:
            self.ping_timer.cancel()

        self.ping_timer = threading.Timer(self.ping_interval, self._send_custom_ping)
        self.ping_timer.start()

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

        # Cancel ping thread
        if self.ping_timer:
            self.ping_timer.cancel()
            self.ping_timer = None

        self.ws.close()
        while self.ws.sock:
            continue
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
        return self.callback_directory.pop(topic) if self.callback_directory.get(topic) else None

    def get_proto_body(self, message: ProtoTyping.PushDataV3ApiWrapper) -> dict:
        if self.extend_proto_body:
            return message

        topic = self._topic(message.channel)
        bodies = {
            "public.kline": "publicSpotKline",
            "public.deals": "publicDeals",
            "public.increase.depth": "publicIncreaseDepths",
            "public.limit.depth": "publicLimitDepths",
            "public.bookTicker": "publicBookTicker",
            # Aggregated public topics
            "public.aggre.deals": "publicAggreDeals",
            "public.aggre.depth": "publicAggreDepths",
            "public.aggre.bookTicker": "publicAggreBookTicker",
            "public.bookTicker.batch": "publicBookTickerBatch",
            "private.account": "privateAccount",
            "private.deals": "privateDeals",
            "private.orders": "privateOrders",
        }

        if topic in bodies:
            return getattr(message, bodies[topic])  # default=message

        else:
            logger.warning(f"Body for topic {topic} not found. | Message: {message.__dict__}")
            return message

    def _process_normal_message(self, message: dict | ProtoTyping.PushDataV3ApiWrapper, parse_only: bool = False):
        """
        Redirect message to callback function
        """
        if isinstance(message, dict):
            channel = message.get("channel") or message.get("c")
            
            # Special handling for private messages that might not have channel field
            if channel is None:
                # Log the message structure for debugging
                logger.debug(f"Message without channel - keys: {list(message.keys())[:10]}")
                
                # Check for MEXC private message patterns
                # Private messages might use different field names
                if "s" in message:  # Symbol field often indicates private message
                    # Try to determine topic from message content
                    # Check for order-related fields
                    if "o" in message or "orderId" in message or "orderStatus" in message:
                        topic = "private.orders"
                    # Check for deal/trade fields  
                    elif "t" in message or "tradeId" in message or ("price" in message and "quantity" in message):
                        topic = "private.deals"
                    # Default to account updates
                    else:
                        topic = "private.account"
                        
                    logger.debug(f"Routed private message to {topic} based on content")
                else:
                    # No channel and no recognizable pattern
                    topic = None
                    logger.debug(f"Could not determine topic for message: {str(message)[:200]}")
            else:
                topic = self._topic(channel)
                
            callback_data = message
        else:
            topic = self._topic(message.channel)
            callback_data = self.get_proto_body(message)

        callback_function = self._get_callback(topic)
        if not callback_function:
            logger.warning(f"Callback for topic {topic} not found. | Message: {message}")
            return None, None
        else:
            if parse_only:
                return callback_function, callback_data

            callback_function(callback_data)

    def _process_subscription_message(self, message: dict):
        if message.get("id") == 0 and message.get("code") == 0:
            # If we get successful SPOT subscription, notify user
            logger.debug(f"Subscription to {message['msg']} successful.")
            return

        elif (
            message.get("channel", "").startswith("rs.sub")
            or message.get("channel", "") == "rs.personal.filter"
            and message.get("data") == "success"
        ):
            # If we get successful FUTURES subscription, notify user
            logger.debug(f"Subscription to {message['channel']} successful.")
            return

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
            kwargs.pop("callback_function") if kwargs.get("callback_function") else self._handle_incoming_message
        )

        super().__init__(callback_function, ws_name, **kwargs)

    def subscribe(self, topic, callback, params: dict = {}):
        subscription_args = {"method": topic, "param": params}
        self._check_callback_directory(subscription_args)

        while not self.is_connected():
            # Wait until the connection is open before subscribing.
            time.sleep(0.1)

        subscription_message = json.dumps(subscription_args)
        self.ws.send(subscription_message)
        self.subscriptions.append(subscription_args)
        self._set_callback(self._topic(topic), callback)
        self.last_subsctiption = self._topic(topic)

    def unsubscribe(self, method: str | Callable) -> None:
        if not method:
            return

        if isinstance(method, str):
            # remove callback
            self._pop_callback(method)
            # send unsub message
            self.ws.send(json.dumps({"method": f"unsub.{method}", "param": {}}))
            # remove subscription from list
            for sub in self.subscriptions:
                if sub["method"] == f"sub.{method}":
                    self.subscriptions.remove(sub)
                    break

            logger.debug(f"Unsubscribed from {method}")
        else:
            # this is a func, get name
            topic_name = method.__name__.replace("_stream", "").replace("_", ".")

            return self.unsubscribe(topic_name)

    def _process_auth_message(self, message):
        # If we get successful futures auth, notify user
        if message.get("data") == "success":
            logger.debug(f"Authorization for {self.ws_name} successful.")
            self.auth = True

        # If we get unsuccessful auth, notify user.
        elif message.get("data") != "success":  # !!!!
            logger.debug(f"Authorization for {self.ws_name} failed. Please check your API keys and restart.")

    def _handle_incoming_message(self, message):
        def is_auth_message():
            return message.get("channel", "") == "rs.login"

        def is_subscription_message():
            return message.get("channel", "").startswith("rs.sub") or message.get("channel", "") == "rs.personal.filter"

        def is_pong_message():
            return message.get("channel", "") in ("pong", "clientId")

        def is_error_message():
            return message.get("channel", "") == "rs.error"

        if is_auth_message():
            self._process_auth_message(message)
        elif is_subscription_message():
            self._process_subscription_message(message)
        elif is_pong_message():
            pass
        elif is_error_message():
            print(f"WebSocket return error: {message}")
        else:
            self._process_normal_message(message)

    def custom_topic_stream(self, topic, callback):
        return self.subscribe(topic=topic, callback=callback)


class _FuturesWebSocket(_FuturesWebSocketManager):
    def __init__(self, **kwargs):
        self.ws_name = "FuturesV1"
        self.endpoint = FUTURES

        super().__init__(self.ws_name, **kwargs)

    def connect(self):
        if not self.is_connected():
            self._connect(self.endpoint)

    def _ws_subscribe(self, topic, callback, params: list = []):
        self.connect()
        self.subscribe(topic, callback, params)


# # # # # # # # # #
#                 #
#       SPOT      #
#                 #
# # # # # # # # # #


class _SpotWebSocketManager(_WebSocketManager):
    def __init__(self, ws_name, **kwargs):
        callback_function = (
            kwargs.pop("callback_function") if kwargs.get("callback_function") else self._handle_incoming_message
        )
        super().__init__(callback_function, ws_name, **kwargs)

        self.private_topics = ["account", "deals", "orders"]

    def subscribe(self, topic: str, callback: Callable, params_list: list, interval: str = None):
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
            time.sleep(0.1)

        subscription_message = json.dumps(subscription_args)
        self.ws.send(subscription_message)
        self.subscriptions.append(subscription_args)
        self._set_callback(topic, callback)
        self.last_subsctiption = topic

    def unsubscribe(self, *topics: str | Callable):
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
            self.ws.send(
                json.dumps(
                    {
                        "method": "UNSUBSCRIPTION",
                        "params": ["@".join([f"spot@{t}.v3.api" + (".pb" if self.proto else "")]) for t in topics],
                    }
                )
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
            return self.unsubscribe(*topics)

    def _handle_incoming_message(self, message: dict):
        def is_subscription_message():
            if message.get("id") == 0 and message.get("code") == 0:
                return True
            else:
                return False

        if isinstance(message, dict) and is_subscription_message():
            self._process_subscription_message(message)
        else:
            self._process_normal_message(message)

    def custom_topic_stream(self, topic, callback):
        return self.subscribe(topic=topic, callback=callback)


class _SpotWebSocket(_SpotWebSocketManager):
    def __init__(self, endpoint: str = SPOT, **kwargs):
        self.ws_name = "SpotV3"
        self.endpoint = endpoint

        super().__init__(self.ws_name, **kwargs)

    def _ws_subscribe(self, topic, callback, params: list = [], interval: str = None):
        if not self.is_connected():
            self._connect(self.endpoint)

        self.subscribe(topic, callback, params, interval)
