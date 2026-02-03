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
    func_to_topic: dict[Callable, str] = {
        "deals": "public.aggre.deals",
        "depth": "public.aggre.depth",
        "limit.depth": "public.limit.depth",
        "book.ticker": "public.aggre.bookTicker",
        "book.ticker.batch": "public.bookTicker.batch",
        "mini.tickers": "public.miniTickers",
        "mini.ticker": "public.miniTicker",
        "account.update": "private.account",
        "account.deals": "private.deals",
        "account.orders": "private.orders",
    }
    sub_state: dict[str, bool] = {}

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
        proto=True,
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
        self.subscriptions: dict[str, dict] = {}

        # Set ping settings.
        self.ping_interval: int = ping_interval
        self.ping_timeout: int = ping_timeout
        self.custom_ping_message: str = json.dumps({"method": "PING"})
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
        self.ws = None
        self.wst = None

    @property
    def is_spot(self):
        return self.endpoint.startswith(SPOT)

    @property
    def is_futures(self):
        return self.endpoint.startswith(FUTURES)

    def _base_topic(self, topic):
        """
        Extract base topic name without parameters from channel string.
        For spot channels: spot@public.kline.v3.api.pb@Min1@BTCUSDT -> public.kline
        """
        cleaned = (
            topic.replace("sub.", "")
            .replace("push.", "")
            .replace("rs.sub.", "")
            .replace("spot@", "")
            .replace(".pb", "")
        )
        return cleaned.split(".v3.api")[0]

    def _topic(self, topic):
        """
        Extract topic name with parameters from channel string.
        For spot channels with params: spot@public.kline.v3.api.pb@Min1@BTCUSDT
        Returns: public.kline@Min1@BTCUSDT (with params) or just public.kline (without params)
        """
        # Remove prefixes
        cleaned = (
            topic.replace("sub.", "")
            .replace("push.", "")
            .replace("rs.sub.", "")
            .replace("spot@", "")
            .replace(".pb", "")
        )

        # Split by .v3.api to separate topic from params
        parts = cleaned.split(".v3.api")
        base_topic = parts[0]

        # Check if there are params after .v3.api (format: topic.v3.api@param1@param2...)
        if len(parts) > 1 and "@" in parts[1]:
            # Extract params (everything after .v3.api, split by @)
            params_part = parts[1].lstrip("@")
            params = params_part.split("@") if params_part else []
            # Filter out empty params
            params = [p for p in params if p]
            if params:
                # Join topic with params (keep original order from channel)
                return f"{base_topic}@{'@'.join(params)}"

        return base_topic

    # Valid kline interval values
    KLINE_INTERVALS = frozenset({
        "Min1", "Min5", "Min15", "Min30", "Min60",
        "Hour4", "Hour8", "Day1", "Week1", "Month1"
    })

    def _build_topic_key(self, raw_topic: str, params: dict | list | str, interval: str = None):
        """
        Build unique topic key for callback_directory.
        Format: topic@param1@param2@...
        For kline (with interval): topic@symbol@interval (e.g. spot@public.kline.v3.api.pb@ETHUSDT@Min1)
        For other topics: topic@interval@param1@param2@... (interval first if present)
        """

        if self.is_spot:
            raw_topic = "spot@" + raw_topic + ".v3.api" + (".pb" if self.proto else "")
            # spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT

        # Extract all parameter values
        param_values = []
        detected_interval = interval  # interval passed as separate argument
        
        # Check if interval is inside params dict (for kline_stream)
        if isinstance(params, dict) and "interval" in params:
            interval_value = str(params.get("interval", ""))
            if interval_value in self.KLINE_INTERVALS:
                detected_interval = interval_value
                # Add other params first (excluding interval)
                for key in sorted(params.keys()):
                    if key != "interval":
                        param_values.append(str(params[key]))
                # Add interval at the end
                param_values.append(detected_interval)
                if param_values:
                    return f"{raw_topic}@{'@'.join(param_values)}"
                return raw_topic

        # Check if this is a kline subscription (has valid interval passed separately)
        is_kline = detected_interval and str(detected_interval) in self.KLINE_INTERVALS

        if is_kline:
            # For kline subscriptions: params first, then interval at the end
            # Result: spot@public.kline.v3.api.pb@ETHUSDT@Min1
            if isinstance(params, dict):
                sorted_params = sorted(params.items())
                param_values.extend([str(v) for k, v in sorted_params])
            elif isinstance(params, list):
                param_values.extend([str(p) for p in params])
            elif isinstance(params, str):
                param_values.append(params)
            # Add interval at the end for kline
            param_values.append(str(detected_interval))
        else:
            # For other topics: interval first (if present), then other params
            if detected_interval:
                param_values.append(str(detected_interval))

            if isinstance(params, dict):
                sorted_params = sorted(params.items())
                param_values.extend([str(v) for k, v in sorted_params])
            elif isinstance(params, list):
                param_values.extend([str(p) for p in params])
            elif isinstance(params, str):
                param_values.append(params)

        if param_values:
            return f"{raw_topic}@{'@'.join(param_values)}"

        return raw_topic

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

            for subscription_message in self.subscriptions.values():
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
            logger.debug(f"WebSocket {self.ws_name} attempting connection... to {url}")

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
        recoverable_errors = (
            websocket.WebSocketConnectionClosedException,
            websocket.WebSocketTimeoutException,
            ConnectionResetError,
            BrokenPipeError,
        )

        if not isinstance(error, recoverable_errors):
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
            try:
                self._connect(self.endpoint)
            except Exception:
                logger.exception(f"WebSocket {self.ws_name} reconnect failed")

    def _on_close(self):
        """
        Log WS close.
        """
        logger.info(f"WebSocket {self.ws_name} closed.")

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

        if self.ws:
            try:
                self.ws.close()
            except Exception:
                logger.exception(f"WebSocket {self.ws_name} close failed")

            wait_until = time.time() + 5
            while getattr(self.ws, "sock", None) and time.time() < wait_until:
                time.sleep(0.05)

        if self.wst and self.wst.is_alive():
            self.wst.join(timeout=1)

        self.ws = None
        self.wst = None
        self.exited = True

    def _check_callback_directory(self, topics):
        if isinstance(topics, (str, bytes)):
            topics = [topics]

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

        topic = self._base_topic(message.channel)
        bodies = {
            "public.kline": "publicSpotKline",
            "public.deals": "publicDeals",
            "public.aggre.deals": "publicAggreDeals",
            "public.aggre.depth": "publicAggreDepths",
            "public.limit.depth": "publicLimitDepths",
            "public.aggre.bookTicker": "publicAggreBookTicker",
            "public.bookTicker.batch": "publicBookTickerBatch",
            "public.miniTickers": "publicMiniTickers",
            "public.miniTicker": "publicMiniTicker",
            "private.account": "privateAccount",
            "private.deals": "privateDeals",
            "private.orders": "privateOrders",
        }

        if topic in bodies:
            return getattr(message, bodies[topic])  # default=message

        else:
            logger.warning(f"Body for topic {topic} not found. | Message: {message}")
            return message

    def _process_normal_message(self, message: ProtoTyping.PushDataV3ApiWrapper, parse_only: bool = False):
        """
        Redirect message to callback function
        """
        topic = message.channel
        callback_data = self.get_proto_body(message)

        callback_function = self._get_callback(topic)
        if not callback_function:
            logger.error(f"Callback for topic {topic} not found. | Message: {message}")
            return None, None
        else:
            if parse_only:
                return callback_function, callback_data

            callback_function(callback_data)

    def _process_subscription_message(self, message: dict):
        """
        process message after sub on any topic and check is subscription successful or not
        """

        if message.get("id") == 0 and message.get("code") == 0:
            # idk what to do with this message
            if "msg format invalid" in message.get("msg", ""):
                # disable error logging for a while
                # logger.error(f"Subscription: Got error message: {message.get('msg', '')}")
                return

            if message.get("msg") == "PONG":
                # logger.info(f"Received PONG message: {message}")
                return

            if "Not Subscribed successfully!" in message.get("msg", ""):
                logger.error(f"Subscription: Not Subscribed successfully! | Message: {message.get('msg', '')}")
                if self.last_subsctiption:
                    self._pop_callback(self.last_subsctiption)
                return

            # if not message.get("msg"):
            #    logger.debug(f"Unsubscription successful.")
            #    return

            # If we get successful SPOT subscription, notify user
            state = message["msg"] in self.subscriptions.keys()
            if state:
                logger.info(f"Subscription to {message['msg']} successful.")
            else:
                logger.info(f"Unsubscription to {message['msg']} successful.")

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
        callback_topic = self._topic(topic)
        self._check_callback_directory(callback_topic)

        while not self.is_connected():
            # Wait until the connection is open before subscribing.
            time.sleep(0.1)

        subscription_message = json.dumps(subscription_args)
        self.ws.send(subscription_message)
        self.subscriptions[topic] = subscription_args
        self._set_callback(callback_topic, callback)
        self.last_subsctiption = callback_topic

    def unsubscribe(self, method: str | Callable) -> None:
        if not method:
            return

        if isinstance(method, str):
            # remove callback
            self._pop_callback(method)
            # send unsub message
            self.ws.send(json.dumps({"method": f"unsub.{method}", "param": {}}))
            # remove subscription from list
            for topic, sub in self.subscriptions.items():
                if sub["method"] == f"sub.{method}":
                    self.subscriptions.pop(topic)
                    break

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
            logger.error(f"WebSocket return error: {message}")
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
            time.sleep(0.1)

        subscription_message = json.dumps(subscription_args)
        self.ws.send(subscription_message)
        # Store subscription by base topic (for backward compatibility with unsubscribe)
        # But store all topic keys with params in callback_directory
        for topic in topics:
            self.subscriptions[topic] = subscription_args
            self.subscriptions[topic]["params"] = [topic]
            self.last_subsctiption = topic

        return topics[0] if len(topics) <= 1 else topics

    def unsubscribe(self, *topics: str):
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
                self.ws.send(json.dumps(unsubscribe_message))

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

    def _handle_incoming_message(self, message: dict | ProtoTyping.PushDataV3ApiWrapper):
        def is_subscription_or_pong_message():
            # {'id': 0, 'code': 0, 'msg': 'spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT'}
            # {'id': 0, 'code': 0, 'msg': 'PONG'}
            if isinstance(message, dict) and message.get("id") == 0 and message.get("code") == 0:
                return True
            else:
                return False

        if isinstance(message, dict) and is_subscription_or_pong_message():
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

        return self.subscribe(topic, callback, params, interval)
