# pytest . -v -s

import asyncio
import json
import time
import pytest
import pytest_asyncio
from unittest.mock import patch
from dotenv import dotenv_values

import pymexc.base
from pymexc.spot import WebSocket

env = dotenv_values(".env")
api_key = env["API_KEY"]
api_secret = env["API_SECRET"]

PRINT_RESPONSE = True

ws_client = WebSocket(api_key=api_key, api_secret=api_secret)

tests = True


def test_deals_stream():
    def unsubscribe(msg):
        print(msg)
        ws_client.unsubscribe(ws_client.deals_stream)


    ws_client.deals_stream(unsubscribe, symbol="WBTCUSDT")
