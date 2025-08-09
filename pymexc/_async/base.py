import hashlib
import hmac
import logging
import time
from abc import ABC
from typing import Literal, Union
from urllib.parse import urlencode

from curl_cffi import requests

logger = logging.getLogger(__name__)

SPOT = "https://api.mexc.com"
FUTURES = "https://contract.mexc.com"


class MexcAPIError(Exception):
    pass


class MexcSDK(ABC):
    """
    Initializes a new instance of the class with the given `api_key` and `api_secret` parameters.

    :param api_key: A string representing the API key.
    :param api_secret: A string representing the API secret.
    :param base_url: A string representing the base URL of the API.
    """

    def __init__(self, api_key: str, api_secret: str, base_url: str, proxies: dict = None):
        self.api_key = api_key
        self.api_secret = api_secret

        self.recvWindow = 5000

        self.base_url = base_url

        self.session = requests.AsyncSession()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
            }
        )

        if proxies:
            self.session.proxies.update(proxies)

    @classmethod
    def sign(self, **kwargs) -> str: ...

    @classmethod
    async def call(
        self,
        method: Union[Literal["GET"], Literal["POST"], Literal["PUT"], Literal["DELETE"]],
        router: str,
        *args,
        **kwargs,
    ) -> dict: ...


class _SpotHTTP(MexcSDK):
    def __init__(self, api_key: str = None, api_secret: str = None, proxies: dict = None):
        super().__init__(api_key, api_secret, SPOT, proxies=proxies)

        self.session.headers.update({"X-MEXC-APIKEY": self.api_key})

    def sign(self, query_string: str) -> str:
        """
        Generates a signature for an API request using HMAC SHA256 encryption.

        Args:
            **kwargs: Arbitrary keyword arguments representing request parameters.

        Returns:
            A hexadecimal string representing the signature of the request.
        """
        # Generate signature
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    async def call(
        self,
        method: Union[Literal["GET"], Literal["POST"], Literal["PUT"], Literal["DELETE"]],
        router: str,
        auth: bool = True,
        *args,
        **kwargs,
    ) -> dict:
        if not router.startswith("/"):
            router = f"/{router}"

        # clear None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if kwargs.get("params"):
            kwargs["params"] = {k: v for k, v in kwargs["params"].items() if v is not None}
        else:
            kwargs["params"] = {}

        timestamp = str(int(time.time() * 1000))
        kwargs["params"]["timestamp"] = timestamp
        kwargs["params"]["recvWindow"] = self.recvWindow

        kwargs["params"] = {k: v for k, v in sorted(kwargs["params"].items())}
        params = kwargs.pop("params")
        encoded_params = urlencode(params, doseq=True).replace("+", "%20")

        if self.api_key and self.api_secret and auth:
            params["signature"] = self.sign(encoded_params)

        response = await self.session.request(method, f"{self.base_url}{router}", params=params, *args, **kwargs)

        if not response.ok:
            print(response.json())
            raise MexcAPIError(f"(code={response.json()['code']}): {response.json()['msg']}")

        return response.json()


class _FuturesHTTP(MexcSDK):
    def __init__(
        self,
        api_key: str = None,
        api_secret: str = None,
        proxies: dict = None,
        ignore_ad: bool = False,
    ):
        super().__init__(api_key, api_secret, FUTURES, proxies=proxies)
        if not ignore_ad:
            print(
                "[pymexc] You can bypass Futures API maintance. See https://github.com/makarworld/pymexc/issues/15 for more information."
            )

        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "ApiKey": self.api_key,
            }
        )

    def sign(self, timestamp: str, **kwargs) -> str:
        """
        Generates a signature for an API request using HMAC SHA256 encryption.

        :param timestamp: A string representing the timestamp of the request.
        :type timestamp: str
        :param kwargs: Arbitrary keyword arguments representing request parameters.
        :type kwargs: dict

        :return: A hexadecimal string representing the signature of the request.
        :rtype: str
        """
        # Generate signature
        query_string = "&".join([f"{k}={v}" for k, v in sorted(kwargs.items())])
        query_string = self.api_key + timestamp + query_string
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    async def call(
        self,
        method: Union[Literal["GET"], Literal["POST"], Literal["PUT"], Literal["DELETE"]],
        router: str,
        *args,
        **kwargs,
    ) -> dict:
        """
        Makes a request to the specified HTTP method and router using the provided arguments.

        :param method: A string that represents the HTTP method(GET, POST, PUT, or DELETE) to be used.
        :type method: str
        :param router: A string that represents the API endpoint to be called.
        :type router: str
        :param *args: Variable length argument list.
        :type *args: list
        :param **kwargs: Arbitrary keyword arguments.
        :type **kwargs: dict

        :return: A dictionary containing the JSON response of the request.
        """

        if not router.startswith("/"):
            router = f"/{router}"

        # Clear None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Ensure only one of 'json' or 'params' is set
        if "json" in kwargs and "params" in kwargs:
            raise ValueError("Only one of 'json' or 'params' can be specified.")

        # Clean None values inside 'json' or 'params'
        for variant in ("params", "json"):
            if kwarg_variant := kwargs.get(variant):
                if isinstance(kwarg_variant, dict):
                    kwargs[variant] = {k: v for k, v in kwarg_variant.items() if v is not None}
                # ! func cancel_order may be list
                elif isinstance(kwarg_variant, list):
                    kwargs[variant] = [v for v in kwarg_variant if v is not None]

        if self.api_key and self.api_secret:
            # Add signature
            timestamp = str(int(time.time() * 1000))
            payload = kwargs.get("json") or kwargs.get("params") or {}

            kwargs["headers"] = {
                "Request-Time": timestamp,
                "Signature": self.sign(timestamp, **payload),
            }

        response = await self.session.request(method, f"{self.base_url}{router}", *args, **kwargs)

        return response.json()
