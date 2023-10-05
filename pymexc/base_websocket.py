import websocket
import threading
import logging
import time
import json
import hmac

logger = logging.getLogger(__name__)

SPOT = "wss://wbs.mexc.com/ws"
FUTURES = "wss://contract.mexc.com/ws"

class _WebSocketManager:
    def __init__(self, callback_function, ws_name, api_key=None, api_secret=None,
                 ping_interval=20, ping_timeout=10, retries=10,
                 restart_on_error=True, trace_logging=False, 
                 http_proxy_host = None,
                 http_proxy_port = None,
                 http_no_proxy = None,
                 http_proxy_auth = None,
                 http_proxy_timeout = None):
        
        self.proxy_settings = dict(
            http_proxy_host = http_proxy_host,
            http_proxy_port = http_proxy_port,
            http_no_proxy = http_no_proxy,
            http_proxy_auth = http_proxy_auth,
            http_proxy_timeout = http_proxy_timeout
        )

        # Set API keys.
        self.api_key = api_key
        self.api_secret = api_secret

        self.callback = callback_function
        self.ws_name = ws_name
        if api_key:
            self.ws_name += " (Auth)"

        # Setup the callback directory following the format:
        #   {
        #       "topic_name": function
        #   }
        self.callback_directory = {}

        # Record the subscriptions made so that we can resubscribe if the WSS
        # connection is broken.
        self.subscriptions = []

        # Set ping settings.
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.retries = retries

        # Other optional data handling settings.
        self.handle_error = restart_on_error

        # Enable websocket-client's trace logging for extra debug information
        # on the websocket connection, including the raw sent & recv messages
        websocket.enableTrace(trace_logging)

        # Set initial state, initialize dictionary and connect.
        self._reset()
        self.attempting_connection = False

    def _on_open(self):
        """
        Log WS open.
        """
        logger.debug(f"WebSocket {self.ws_name} opened.")

    def _on_message(self, message):
        """
        Parse incoming messages.
        """
        self.callback(json.loads(message))

    def is_connected(self):
        try:
            if self.ws.sock or not self.ws.sock.is_connected:
                return True
            else:
                return False
        except AttributeError:
            return False

    @staticmethod
    def _are_connections_connected(active_connections):
        for connection in active_connections:
            if not connection.is_connected():
                return False
        return True

    def _ping_loop(self, ping_payload: str, ping_interval: int, ping_timeout: int):
        """
        Ping the websocket.
        """
        time.sleep(ping_timeout)
        while True:
            logger.info(f"WebSocket {self.ws_name} send ping...")
            self.ws.send(ping_payload)
            time.sleep(ping_interval)

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
                self.ws.send(subscription_message)

        self.attempting_connection = True

        # Set endpoint.
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
                on_close=self._on_close(),
                on_open=self._on_open(),
                on_error=lambda ws, err: self._on_error(err)
            )

            # Setup the thread running WebSocketApp.
            self.wst = threading.Thread(target=lambda: self.ws.run_forever(
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout,
                **self.proxy_settings
            ))

            # Configure as daemon; start.
            self.wst.daemon = True
            self.wst.start()

            # setup ping loop
            self.wsl = threading.Thread(target=lambda: self._ping_loop(
                ping_payload='{"method":"ping"}',
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout
            ))

            self.wsl.daemon = True
            self.wsl.start()

            retries -= 1
            time.sleep(1)

            # If connection was not successful, raise error.
            if not infinitely_reconnect and retries <= 0:
                self.exit()
                raise websocket.WebSocketTimeoutException(
                    f"WebSocket {self.ws_name} connection failed. Too many "
                    f"connection attempts. pybit will "
                    f"no longer try to reconnect.")

        logger.info(f"WebSocket {self.ws_name} connected")

        # If given an api_key, authenticate.
        if self.api_key and self.api_secret:
            self._auth()

        resubscribe_to_topics()

        self.attempting_connection = False

    def _auth(self):
        # Generate signature
        
        # make auth if futures. spot has a different auth system.

        isspot = self.endpoint.startswith(SPOT)
        if isspot: 
            return

        timestamp = str(int(time.time() * 1000))
        _val = self.api_key + timestamp 
        signature = str(hmac.new(
            bytes(self.api_secret, "utf-8"),
            bytes(_val, "utf-8"), digestmod="sha256"
        ).hexdigest())

        # Authenticate with API.
        self.ws.send(
            json.dumps({
                "subscribe": False,
                "method": "login",
                "param": {
                    "apiKey": self.api_key,
                    "reqTime": timestamp,
                    "signature": signature
                }
            })
        )

    def _on_error(self, error):
        """
        Exit on errors and raise exception, or attempt reconnect.
        """
        if type(error).__name__ not in ["WebSocketConnectionClosedException",
                                        "ConnectionResetError",
                                        "WebSocketTimeoutException"]:
            # Raises errors not related to websocket disconnection.
            self.exit()
            raise error

        if not self.exited:
            logger.error(f"WebSocket {self.ws_name} encountered error: {error}.")
            self.exit()

        # Reconnect.
        if self.handle_error and not self.attempting_connection:
            self._reset()
            self._connect(self.endpoint)

    def _on_close(self):
        """
        Log WS close.
        """
        logger.debug(f"WebSocket {self.ws_name} closed.")

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

        self.ws.close()
        while self.ws.sock:
            continue
        self.exited = True

class _FuturesWebSocketManager(_WebSocketManager):
    def __init__(self, ws_name, **kwargs):
        callback_function = kwargs.pop("callback_function") if \
            kwargs.get("callback_function") else self._handle_incoming_message

        super().__init__(callback_function, ws_name, **kwargs)

        self.private_topics = ["personal.order",     "personal.asset", 
                               "personal.position",  "personal.risk.limit", 
                               "personal.adl.level", "personal.position.mode"]

        self.symbol_wildcard = "*"
        self.symbol_separator = "|"
        self.last_subsctiption = None

    def subscribe(self, topic, callback, params: dict = {}):
        subscription_args = {
            "method": topic,
            "param": params
        } 
        self._check_callback_directory(subscription_args)

        while not self.is_connected():
            # Wait until the connection is open before subscribing.
            time.sleep(0.1)

        subscription_message = json.dumps(subscription_args)
        self.ws.send(subscription_message)
        self.subscriptions.append(subscription_message)
        self._set_callback(topic.replace("sub.", ""), callback)
        self.last_subsctiption = topic.replace("sub.", "")

    def _initialise_local_data(self, topic):
        # Create self.data
        try:
            self.data[topic]
        except KeyError:
            self.data[topic] = []

    def _process_auth_message(self, message):
        # If we get successful futures auth, notify user
        if message.get("data") == "success":
            logger.debug(f"Authorization for {self.ws_name} successful.")
            self.auth = True
        # If we get unsuccessful auth, notify user.
        elif message.get("data") != "success":                                                                            # !!!!
            logger.debug(f"Authorization for {self.ws_name} failed. Please "
                         f"check your API keys and restart.")

    def _process_subscription_message(self, message):
        #try:
        sub = message["channel"]
        #except KeyError:
            #sub = message["c"]  # SPOT PUBLIC & PRIVATE format

        # If we get successful futures subscription, notify user
        if (
                    message.get("channel", "").startswith("rs.") or 
                    message.get("channel", "").startswith("push.")
                ) and message.get("channel", "") != "rs.error":

            logger.debug(f"Subscription to {sub} successful.")
        # Futures subscription fail
        else:
            response = message["data"]
            logger.error("Couldn't subscribe to topic. "
                         f"Error: {response}.")
            if self.last_subsctiption:
                self._pop_callback(self.last_subsctiption)

    def _process_normal_message(self, message):
        topic = message["channel"].replace("push.", "")
        callback_data = message
        callback_function = self._get_callback(topic)
        callback_function(callback_data)

    def _handle_incoming_message(self, message):
        def is_auth_message():
            if message.get("channel", "") == "rs.login":
                return True
            else:
                return False

        def is_subscription_message():
            if str(message).startswith("{'channel': 'push."):
                return True
            else:
                return False
        
        def is_pong_message():
            if message.get("channel", "") in ("pong", "clientId"):
                return True
            else:
                return False

        if is_auth_message():
            self._process_auth_message(message)
        elif is_subscription_message():
            self._process_subscription_message(message)
        elif is_pong_message():
            pass
        else:
            self._process_normal_message(message)

    def custom_topic_stream(self, topic, callback):
        return self.subscribe(topic=topic, callback=callback)

    def _check_callback_directory(self, topics):
        for topic in topics:
            if topic in self.callback_directory:
                raise Exception(f"You have already subscribed to this topic: "
                                f"{topic}")

    def _set_callback(self, topic, callback_function):
        self.callback_directory[topic] = callback_function

    def _get_callback(self, topic): 
        return self.callback_directory[topic]

    def _pop_callback(self, topic):
        self.callback_directory.pop(topic)

class _FuturesWebSocket(_FuturesWebSocketManager):
    def __init__(self, **kwargs):
        self.ws_name = "FuturesV1"
        self.endpoint = "wss://contract.mexc.com/ws"

        super().__init__(self.ws_name, **kwargs)
        self.ws = None

        self.active_connections = []
        self.kwargs = kwargs

    def is_connected(self):
        return self._are_connections_connected(self.active_connections)

    def _ws_subscribe(self, topic, callback, params: list = []):
        if not self.ws:
            self.ws = _FuturesWebSocketManager(
                self.ws_name, **self.kwargs)
            self.ws._connect(self.endpoint)
            self.active_connections.append(self.ws)
        self.ws.subscribe(topic, callback, params)

class _SpotWebSocketManager(_WebSocketManager):
    def __init__(self, ws_name, **kwargs):
        callback_function = kwargs.pop("callback_function") if \
            kwargs.get("callback_function") else self._handle_incoming_message
        super().__init__(callback_function, ws_name, **kwargs)

        self.private_topics = ["account", "deals", "orders"]

        self.last_subsctiption = None

    def subscribe(self, topic: str, callback, params_list: list):
        subscription_args = {
            "method": "SUBSCRIPTION",
            "params": [
                '@'.join([f"spot@{topic}.v3.api"] + list(map(str, params.values())))
                for params in params_list
            ]
        }
        self._check_callback_directory(subscription_args)

        while not self.is_connected():
            # Wait until the connection is open before subscribing.
            time.sleep(0.1)

        subscription_message = json.dumps(subscription_args)
        self.ws.send(subscription_message)
        self.subscriptions.append(subscription_message)
        self._set_callback(topic, callback)
        self.last_subsctiption = topic

    def _initialise_local_data(self, topic):
        # Create self.data
        try:
            self.data[topic]
        except KeyError:
            self.data[topic] = []


    def _process_subscription_message(self, message):
        sub = message["msg"].replace("spot@", "").split(".v3.api")[0]

        # If we get successful futures subscription, notify user
        if message.get("id") == 0 and message.get("code") == 0:
            logger.debug(f"Subscription to {sub} successful.")
        # Futures subscription fail
        else:
            response = message["msg"]
            logger.error("Couldn't subscribe to topic. "
                         f"Error: {response}.")
            if self.last_subsctiption:
                self._pop_callback(self.last_subsctiption)

    def _process_normal_message(self, message):
        topic = message["c"].replace("spot@", "").split(".v3.api")[0]
        callback_data = message
        callback_function = self._get_callback(topic)
        callback_function(callback_data)

    def _handle_incoming_message(self, message):
        def is_subscription_message():
            if (message.get("id") == 0 and
                message.get("code") == 0 and
                message.get("msg")):
                return True
            else:
                return False

        if is_subscription_message():
            self._process_subscription_message(message)
        else:
            self._process_normal_message(message)

    def custom_topic_stream(self, topic, callback):
        return self.subscribe(topic=topic, callback=callback)

    def _check_callback_directory(self, topics):
        for topic in topics:
            if topic in self.callback_directory:
                raise Exception(f"You have already subscribed to this topic: "
                                f"{topic}")

    def _set_callback(self, topic, callback_function):
        self.callback_directory[topic] = callback_function

    def _get_callback(self, topic):
        return self.callback_directory[topic]

    def _pop_callback(self, topic):
        self.callback_directory.pop(topic)

class _SpotWebSocket(_SpotWebSocketManager):
    def __init__(self, endpoint: str = "wss://wbs.mexc.com/ws", **kwargs):
        self.ws_name = "SpotV3"
        self.endpoint = endpoint


        super().__init__(self.ws_name, **kwargs)
        self.ws = None

        self.active_connections = []
        self.kwargs = kwargs

    def is_connected(self):
        return self._are_connections_connected(self.active_connections)

    def _ws_subscribe(self, topic, callback, params: list = []):
        if not self.ws:
            self.ws = _SpotWebSocketManager(
                self.ws_name, **self.kwargs)
            self.ws._connect(self.endpoint)
            self.active_connections.append(self.ws)
        self.ws.subscribe(topic, callback, params)
