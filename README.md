[![PyPI version](https://badge.fury.io/py/pymexc.svg)](https://badge.fury.io/py/pymexc)
[![License](https://img.shields.io/github/license/makarworld/pymexc.svg?label=License&logo=apache&cacheSeconds=2592000)](https://github.com/makarworld/pymexc/blob/main/LICENSE)
[![image](https://img.shields.io/pypi/pyversions/pymexc.svg)](https://pypi.org/project/pymexc/)
[![Github last commit date](https://img.shields.io/github/last-commit/makarworld/pymexc.svg?label=Updated&logo=github&cacheSeconds=600)](https://github.com/makarworld/pymexc/commits)

# pymexc

`pymexc` is an unofficial Python library for interacting with the [MEXC crypto exchange](https://www.mexc.com/). It provides a simple and intuitive API for making requests to the [MEXC API endpoints](https://mexcdevelop.github.io/apidocs/spot_v3_en/#introduction).

Base of code was taken from [pybit](https://github.com/bybit-exchange/pybit) library.

# Futures orders API

MEXC Futures API for create orders is on maintance now. **_But you can bypass it_**. See [this issue](https://github.com/makarworld/pymexc/issues/15) for more information.

# Installation

You can install pymexc using pip:

```bash
pip install pymexc
```

# Getting Started

To start working with pymexc, you must import spot or futures from the library. Each of them contains 2 classes: HTTP and WebSocket. To work with simple requests, you need to initialize the HTTP class. To work with web sockets you need to initialize the WebSocket class

## Example

```python
from pymexc import spot, futures

api_key = "YOUR API KEY"
api_secret = "YOUR API SECRET KEY"

def handle_message(message): 
    # handle websocket message
    print(message)


# SPOT V3

# initialize HTTP client
spot_client = spot.HTTP(api_key = api_key, api_secret = api_secret)
# initialize WebSocket client
ws_spot_client = spot.WebSocket(api_key = api_key, api_secret = api_secret)

# make http request to api
print(spot_client.exchange_info())

# create websocket connection to public channel (spot@public.deals.v3.api@BTCUSDT)
# all messages will be handled by function `handle_message`
ws_spot_client.deals_stream(handle_message, "BTCUSDT")


# FUTURES V1

# initialize HTTP client
futures_client = futures.HTTP(api_key = api_key, api_secret = api_secret)
# initialize WebSocket client
ws_futures_client = futures.WebSocket(api_key = api_key, api_secret = api_secret, 
                                      # subscribe on personal information about about account
                                      # if not provided, will not be subscribed
                                      # you can subsctibe later by calling ws_futures_client.personal_stream(callback) for all info
                                      # or ws_futures_client.filter_stream(callback, params={"filters":[{"filter":"..."}]}) for specific info (https://mexcdevelop.github.io/apidocs/contract_v1_en/#filter-subscription)
                                      personal_callback = handle_message)

# make http request to api
print(futures_client.index_price("MX_USDT"))

# create websocket connection to public channel (sub.tickers)
# all messages will be handled by function `handle_message`
ws_futures_client.tickers_stream(handle_message)

# loop forever for save websocket connection 
while True: 
    ...
```

## Common Usage Examples

### Getting Current Price and Market Data

```python
from pymexc import spot

spot_client = spot.HTTP()

# Get current price
ticker = spot_client.ticker_price("BTCUSDT")
print(f"BTC Price: {ticker['price']}")

# Get 24h ticker statistics
stats = spot_client.ticker_24h("BTCUSDT")
print(f"24h Change: {stats['priceChangePercent']}%")
print(f"24h Volume: {stats['volume']}")

# Get order book
orderbook = spot_client.order_book("BTCUSDT", limit=10)
print(f"Best Bid: {orderbook['bids'][0]}")
print(f"Best Ask: {orderbook['asks'][0]}")

# Get recent trades
trades = spot_client.trades("BTCUSDT", limit=10)
for trade in trades:
    print(f"Price: {trade['price']}, Qty: {trade['qty']}")
```

### Placing and Managing Orders

```python
from pymexc import spot

spot_client = spot.HTTP(api_key="YOUR_KEY", api_secret="YOUR_SECRET")

# Get current price first
ticker = spot_client.ticker_price("BTCUSDT")
current_price = float(ticker['price'])

# Place a limit buy order 1% below current price
buy_price = current_price * 0.99
result = spot_client.order(
    symbol="BTCUSDT",
    side="BUY",
    order_type="LIMIT",
    quantity=0.001,
    price=buy_price,
    time_in_force="GTC"
)
print(f"Order placed: {result}")

# Check order status
order_status = spot_client.query_order("BTCUSDT", order_id=result['orderId'])
print(f"Order status: {order_status['status']}")

# Get all open orders
open_orders = spot_client.current_open_orders("BTCUSDT")
print(f"Open orders: {len(open_orders)}")

# Cancel an order
if open_orders:
    cancel_result = spot_client.cancel_order("BTCUSDT", order_id=open_orders[0]['orderId'])
    print(f"Order cancelled: {cancel_result}")
```

### Market Order Example

```python
from pymexc import spot

spot_client = spot.HTTP(api_key="YOUR_KEY", api_secret="YOUR_SECRET")

# Place a market buy order for $100 worth of BTC
result = spot_client.order(
    symbol="BTCUSDT",
    side="BUY",
    order_type="MARKET",
    quote_order_qty=100  # Buy $100 worth
)
print(f"Market order executed: {result}")
```

### Getting Account Balance

```python
from pymexc import spot

spot_client = spot.HTTP(api_key="YOUR_KEY", api_secret="YOUR_SECRET")

# Get account information
account = spot_client.account_information()

# Print balances for assets with non-zero amounts
for balance in account['balances']:
    free = float(balance['free'])
    locked = float(balance['locked'])
    total = free + locked
    if total > 0:
        print(f"{balance['asset']}: Free={free}, Locked={locked}, Total={total}")
```

### Getting Trading History

```python
from pymexc import spot
import time

spot_client = spot.HTTP(api_key="YOUR_KEY", api_secret="YOUR_SECRET")

# Get recent trades for a symbol
trades = spot_client.account_trade_list("BTCUSDT", limit=100)

# Calculate total volume and PnL
total_volume = 0
total_cost = 0
for trade in trades:
    qty = float(trade['qty'])
    price = float(trade['price'])
    total_volume += qty
    if trade['isBuyer']:
        total_cost += qty * price
    else:
        total_cost -= qty * price

print(f"Total Volume: {total_volume} BTC")
print(f"Net Cost: {total_cost} USDT")
```

### Real-time Price Monitoring with WebSocket

```python
from pymexc import spot
from pymexc.proto import PublicMiniTickerV3Api
import time

def handle_price_update(message):
    """Handle real-time price updates"""
    # WebSocket uses protobuf by default, so message is a protobuf object
    if isinstance(message, PublicMiniTickerV3Api):
        symbol = message.symbol if hasattr(message, "symbol") else "N/A"
        price = message.price if hasattr(message, "price") else "N/A"
        volume = message.volume if hasattr(message, "volume") else "N/A"
        print(f"{symbol}: Price={price}, Volume={volume}")
    elif isinstance(message, dict) and "d" in message:
        # Fallback for JSON format (if proto=False)
        data = message["d"]
        symbol = data.get("symbol", "N/A")
        price = data.get("p", "N/A")
        volume = data.get("v", "N/A")
        print(f"{symbol}: Price={price}, Volume={volume}")

# Initialize WebSocket client
ws_client = spot.WebSocket()

# Subscribe to ticker updates
ws_client.mini_ticker_stream(handle_price_update, "BTCUSDT")

# Keep connection alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping...")
    ws_client.exit()
```

### Monitoring Order Book Depth

```python
from pymexc import spot
from pymexc.proto import PublicAggreDepthsV3Api
import time

def handle_depth_update(message):
    """Handle order book depth updates"""
    # WebSocket uses protobuf by default, so message is a protobuf object
    if isinstance(message, PublicAggreDepthsV3Api):
        bids = list(message.bids) if hasattr(message, "bids") else []
        asks = list(message.asks) if hasattr(message, "asks") else []
        
        if bids and asks:
            best_bid_price = float(bids[0].price) if bids and hasattr(bids[0], "price") else None
            best_ask_price = float(asks[0].price) if asks and hasattr(asks[0], "price") else None
            if best_bid_price and best_ask_price:
                spread = best_ask_price - best_bid_price
                print(f"Bid={best_bid_price}, Ask={best_ask_price}, Spread={spread:.2f}")
    elif isinstance(message, dict) and "d" in message:
        # Fallback for JSON format (if proto=False)
        data = message["d"]
        symbol = data.get("symbol", "N/A")
        bids = data.get("bids", [])
        asks = data.get("asks", [])
        
        if bids and asks:
            best_bid = bids[0][0] if bids else "N/A"
            best_ask = asks[0][0] if asks else "N/A"
            spread = float(best_ask) - float(best_bid) if best_ask != "N/A" and best_bid != "N/A" else 0
            print(f"{symbol}: Bid={best_bid}, Ask={best_ask}, Spread={spread:.2f}")

# Initialize WebSocket client
ws_client = spot.WebSocket()

# Subscribe to depth updates
ws_client.depth_stream(handle_depth_update, "BTCUSDT", interval="100ms")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    ws_client.exit()
```

### Getting Kline/Candlestick Data for Analysis

```python
from pymexc import spot
import pandas as pd
from datetime import datetime, timedelta

spot_client = spot.HTTP()

# Get klines for the last 24 hours
end_time = int(datetime.now().timestamp() * 1000)
start_time = int((datetime.now() - timedelta(days=1)).timestamp() * 1000)

klines = spot_client.klines(
    symbol="BTCUSDT",
    interval="1h",
    start_time=start_time,
    end_time=end_time,
    limit=24
)

# Convert to DataFrame for analysis
df = pd.DataFrame(klines, columns=[
    'open_time', 'open', 'high', 'low', 'close', 'volume',
    'close_time', 'quote_volume', 'trades', 'taker_buy_base',
    'taker_buy_quote', 'ignore'
])

# Convert to numeric
for col in ['open', 'high', 'low', 'close', 'volume']:
    df[col] = pd.to_numeric(df[col])

# Calculate simple moving average
df['sma_20'] = df['close'].rolling(window=20).mean()

# Print latest data
print(df[['open_time', 'open', 'high', 'low', 'close', 'volume', 'sma_20']].tail())
```

### Batch Order Placement

```python
from pymexc import spot

spot_client = spot.HTTP(api_key="YOUR_KEY", api_secret="YOUR_SECRET")

# Get current price
ticker = spot_client.ticker_price("BTCUSDT")
current_price = float(ticker['price'])

# Prepare multiple orders at different price levels
batch_orders = []
for i in range(5):
    price = current_price * (0.99 - i * 0.001)  # 1% to 0.5% below current price
    batch_orders.append({
        "price": str(price),
        "quantity": "0.001"
    })

# Place batch orders
result = spot_client.batch_orders(
    batch_orders=batch_orders,
    symbol="BTCUSDT",
    side="BUY",
    order_type="LIMIT"
)

print(f"Placed {len(result)} orders")
```

### Error Handling

```python
from pymexc import spot

spot_client = spot.HTTP(api_key="YOUR_KEY", api_secret="YOUR_SECRET")

try:
    # Attempt to place an order
    result = spot_client.order(
        symbol="BTCUSDT",
        side="BUY",
        order_type="LIMIT",
        quantity=0.001,
        price=50000
    )
    print(f"Order placed successfully: {result}")
except Exception as e:
    print(f"Error placing order: {e}")
    # Handle specific error cases
    if "insufficient balance" in str(e).lower():
        print("Not enough balance for this order")
    elif "invalid symbol" in str(e).lower():
        print("Invalid trading pair")
    else:
        print(f"Unknown error: {e}")
```

### Checking Deposit and Withdrawal History

```python
from pymexc import spot
from datetime import datetime, timedelta

spot_client = spot.HTTP(api_key="YOUR_KEY", api_secret="YOUR_SECRET")

# Get deposit history
deposits = spot_client.deposit_history(coin="USDT", limit=50)
print("Recent Deposits:")
for deposit in deposits[:10]:  # Show last 10
    print(f"Amount: {deposit['amount']} {deposit['coin']}, "
          f"Status: {deposit['status']}, "
          f"Time: {datetime.fromtimestamp(deposit['insertTime']/1000)}")

# Get withdrawal history
withdrawals = spot_client.withdraw_history(coin="USDT", limit=50)
print("\nRecent Withdrawals:")
for withdrawal in withdrawals[:10]:  # Show last 10
    print(f"Amount: {withdrawal['amount']} {withdrawal['coin']}, "
          f"Status: {withdrawal['status']}, "
          f"Address: {withdrawal['address']}")
```

### Getting Multiple Symbols Data

```python
from pymexc import spot

spot_client = spot.HTTP()

# Get prices for multiple symbols
symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"]
prices = spot_client.ticker_price(symbols=symbols)

print("Current Prices:")
for ticker in prices:
    print(f"{ticker['symbol']}: {ticker['price']}")

# Get 24h stats for multiple symbols
stats = spot_client.ticker_24h(symbols=symbols)
print("\n24h Statistics:")
for stat in stats:
    change = float(stat['priceChangePercent'])
    emoji = "📈" if change > 0 else "📉"
    print(f"{emoji} {stat['symbol']}: {change:+.2f}% "
          f"(High: {stat['highPrice']}, Low: {stat['lowPrice']})")
```

### Futures: Getting Position Information

```python
from pymexc import futures

futures_client = futures.HTTP(api_key="YOUR_KEY", api_secret="YOUR_SECRET")

# Get all open positions
positions = futures_client.open_positions()
print("Open Positions:")
for pos in positions.get('data', []):
    print(f"Symbol: {pos['symbol']}, "
          f"Side: {'Long' if pos['holdVol'] > 0 else 'Short'}, "
          f"Volume: {pos['holdVol']}, "
          f"Unrealized PnL: {pos['unrealisedPnl']}")

# Get account assets
assets = futures_client.assets()
print("\nAccount Assets:")
for asset in assets.get('data', []):
    if float(asset['availableBalance']) > 0:
        print(f"{asset['currency']}: {asset['availableBalance']} "
              f"(Frozen: {asset['frozenBalance']})")
```

### Async/Await Example

```python
import asyncio
from pymexc import spot

async def main():
    # Initialize async client
    async_client = spot.AsyncHTTP(api_key="YOUR_KEY", api_secret="YOUR_SECRET")
    
    # Make multiple requests concurrently
    tasks = [
        async_client.ticker_price("BTCUSDT"),
        async_client.ticker_price("ETHUSDT"),
        async_client.ticker_24h("BTCUSDT"),
        async_client.account_information()
    ]
    
    results = await asyncio.gather(*tasks)
    
    btc_price, eth_price, btc_stats, account = results
    
    print(f"BTC Price: {btc_price['price']}")
    print(f"ETH Price: {eth_price['price']}")
    print(f"BTC 24h Change: {btc_stats['priceChangePercent']}%")
    print(f"Account Balance: {len(account['balances'])} assets")

# Run async function
asyncio.run(main())
```

### WebSocket: Monitoring Account Updates

```python
from pymexc import spot
from pymexc.proto import PrivateAccountV3Api, PrivateOrdersV3Api
import time

def handle_account_update(message):
    """Handle account balance updates"""
    # WebSocket uses protobuf by default, so message is a protobuf object
    if isinstance(message, PrivateAccountV3Api):
        # PrivateAccountV3Api has fields: vcoinName, coinId, balanceAmount, frozenAmount, etc.
        vcoin_name = message.vcoinName if hasattr(message, "vcoinName") else "N/A"
        balance = float(message.balanceAmount) if hasattr(message, "balanceAmount") and message.balanceAmount else 0
        frozen = float(message.frozenAmount) if hasattr(message, "frozenAmount") and message.frozenAmount else 0
        if balance > 0 or frozen > 0:
            print(f"{vcoin_name}: Balance={balance}, Frozen={frozen}")
    elif isinstance(message, dict) and "d" in message:
        # Fallback for JSON format (if proto=False)
        data = message["d"]
        balances = data.get("B", [])
        for balance in balances:
            asset = balance.get("a", "")
            free = balance.get("f", "0")
            locked = balance.get("l", "0")
            if float(free) > 0 or float(locked) > 0:
                print(f"{asset}: Free={free}, Locked={locked}")

# Initialize WebSocket with authentication
ws_client = spot.WebSocket(api_key="YOUR_KEY", api_secret="YOUR_SECRET")

# Subscribe to account updates
ws_client.account_update(handle_account_update)

# Also subscribe to order updates
def handle_order_update(message):
    """Handle order status updates"""
    # WebSocket uses protobuf by default, so message is a protobuf object
    if isinstance(message, PrivateOrdersV3Api):
        # PrivateOrdersV3Api has fields: id, clientId, price, quantity, amount, status, etc.
        order_id = message.id if hasattr(message, "id") else "N/A"
        price = message.price if hasattr(message, "price") else "N/A"
        quantity = message.quantity if hasattr(message, "quantity") else "N/A"
        status = message.status if hasattr(message, "status") else "N/A"
        print(f"Order Update: ID={order_id}, Price={price}, Quantity={quantity}, Status={status}")
    elif isinstance(message, dict) and "d" in message:
        # Fallback for JSON format (if proto=False)
        order = message["d"]
        print(f"Order Update: {order.get('s')} {order.get('S')} "
              f"{order.get('q')} @ {order.get('p')} - Status: {order.get('X')}")

ws_client.account_orders(handle_order_update)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    ws_client.exit()
```

# Documentation

You can find the official documentation for the MEXC API [here](https://www.mexc.com/api-docs/spot-v3/introduction).

## API Reference

### Spot API (HTTP)

#### Market Data Endpoints

##### `ping()`
Test connectivity to the Rest API.

```python
result = spot_client.ping()
```

##### `time()`
Check Server Time.

```python
result = spot_client.time()
```

##### `default_symbols()`
Get API default symbols.

```python
result = spot_client.default_symbols()
```

##### `exchange_info(symbol=None, symbols=None)`
Get exchange trading rules and symbol information.

```python
# Get all symbols
result = spot_client.exchange_info()

# Get specific symbol
result = spot_client.exchange_info(symbol="BTCUSDT")

# Get multiple symbols
result = spot_client.exchange_info(symbols=["BTCUSDT", "ETHUSDT"])
```

##### `order_book(symbol, limit=100)` / `depth(symbol, limit=100)`
Get order book depth.

```python
# Using order_book
result = spot_client.order_book("BTCUSDT", limit=100)

# Using alias depth
result = spot_client.depth("BTCUSDT", limit=100)
```

##### `trades(symbol, limit=500)`
Get recent trades list.

```python
result = spot_client.trades("BTCUSDT", limit=100)
```

##### `agg_trades(symbol, start_time=None, end_time=None, limit=500)`
Get compressed/aggregate trades list.

```python
result = spot_client.agg_trades("BTCUSDT", limit=100)
```

##### `klines(symbol, interval="1m", start_time=None, end_time=None, limit=500)`
Get kline/candlestick data.

```python
result = spot_client.klines("BTCUSDT", interval="1h", limit=100)
```

##### `avg_price(symbol)`
Get current average price.

```python
result = spot_client.avg_price("BTCUSDT")
```

##### `ticker_24h(symbol=None, symbols=None)` / `ticker24h(symbol=None, symbols=None)`
Get 24hr ticker price change statistics.

```python
# Get all tickers
result = spot_client.ticker_24h()

# Get specific ticker
result = spot_client.ticker_24h(symbol="BTCUSDT")

# Using alias
result = spot_client.ticker24h("BTCUSDT")
```

##### `ticker_price(symbol=None, symbols=None)`
Get symbol price ticker.

```python
result = spot_client.ticker_price("BTCUSDT")
```

##### `ticker_book_price(symbol=None)`
Get best price/qty on the order book.

```python
result = spot_client.ticker_book_price("BTCUSDT")
```

#### Sub-Account Endpoints

##### `create_sub_account(sub_account, note)`
Create a sub-account from the master account.

```python
result = spot_client.create_sub_account("sub_account_name", "note")
```

##### `sub_account_list(sub_account=None, is_freeze=None, page=1, limit=10)`
Get details of the sub-account list.

```python
result = spot_client.sub_account_list()
```

##### `create_sub_account_api_key(sub_account, note, permissions, ip=None)`
Create an APIKey for a sub-account.

```python
result = spot_client.create_sub_account_api_key(
    "sub_account_name",
    "note",
    ["SPOT_ACCOUNT_READ", "SPOT_DEAL_READ"]
)
```

##### `query_sub_account_api_key(sub_account)`
Query the APIKey of a sub-account.

```python
result = spot_client.query_sub_account_api_key("sub_account_name")
```

##### `delete_sub_account_api_key(sub_account, api_key)`
Delete the APIKey of a sub-account.

```python
result = spot_client.delete_sub_account_api_key("sub_account_name", "api_key")
```

##### `universal_transfer(from_account_type, to_account_type, asset, amount, from_account=None, to_account=None)`
Universal Transfer (For Master Account).

```python
result = spot_client.universal_transfer("SPOT", "FUTURES", "USDT", 100.0)
```

##### `query_universal_transfer_history(from_account_type, to_account_type, from_account=None, to_account=None, start_time=None, end_time=None, page=1, limit=500)`
Query Universal Transfer History.

```python
result = spot_client.query_universal_transfer_history("SPOT", "FUTURES")
```

##### `sub_account_asset(sub_account, account_type)`
Query Sub-account Asset.

```python
result = spot_client.sub_account_asset("sub_account_name", "SPOT")
```

#### Spot Account/Trade Endpoints

##### `get_kyc_status()`
Query KYC status.

```python
result = spot_client.get_kyc_status()
```

##### `get_uid()`
Query UID.

```python
result = spot_client.get_uid()
```

##### `get_default_symbols()`
Get user API default symbols.

```python
result = spot_client.get_default_symbols()
```

##### `test_order(symbol, side, order_type, quantity=None, quote_order_qty=None, price=None, ...)`
Test new order (does not place actual order).

```python
result = spot_client.test_order(
    symbol="BTCUSDT",
    side="BUY",
    order_type="LIMIT",
    quantity=0.001,
    price=50000
)
```

##### `order(symbol, side, order_type, quantity=None, quote_order_qty=None, price=None, ...)`
Place a new order.

```python
# Limit order
result = spot_client.order(
    symbol="BTCUSDT",
    side="BUY",
    order_type="LIMIT",
    quantity=0.001,
    price=50000,
    time_in_force="GTC"
)

# Market order
result = spot_client.order(
    symbol="BTCUSDT",
    side="BUY",
    order_type="MARKET",
    quote_order_qty=100
)
```

##### `batch_orders(batch_orders, symbol, side, order_type, ...)`
Place batch orders (up to 20 orders).

```python
result = spot_client.batch_orders(
    batch_orders=[{"price": "50000", "quantity": "0.001"}],
    symbol="BTCUSDT",
    side="BUY",
    order_type="LIMIT"
)
```

##### `cancel_order(symbol, order_id=None, orig_client_order_id=None, new_client_order_id=None)`
Cancel an order.

```python
result = spot_client.cancel_order("BTCUSDT", order_id="123456")
```

##### `cancel_all_open_orders(symbol)`
Cancel all open orders on a symbol.

```python
result = spot_client.cancel_all_open_orders("BTCUSDT")
```

##### `query_order(symbol, orig_client_order_id=None, order_id=None)`
Query order status.

```python
result = spot_client.query_order("BTCUSDT", order_id="123456")
```

##### `current_open_orders(symbol)`
Get current open orders.

```python
result = spot_client.current_open_orders("BTCUSDT")
```

##### `all_orders(symbol, start_time=None, end_time=None, limit=None)`
Get all orders (active, cancelled, or completed).

```python
result = spot_client.all_orders("BTCUSDT", limit=100)
```

##### `account_information()`
Get account information.

```python
result = spot_client.account_information()
```

##### `account_trade_list(symbol, order_id=None, start_time=None, end_time=None, limit=None)`
Get account trade list.

```python
result = spot_client.account_trade_list("BTCUSDT", limit=100)
```

##### `enable_mx_deduct(mx_deduct_enable)`
Enable or disable MX deduct for spot commission fee.

```python
result = spot_client.enable_mx_deduct(True)
```

##### `query_mx_deduct_status()`
Query MX deduct status.

```python
result = spot_client.query_mx_deduct_status()
```

##### `create_stp_strategy_group(trade_group_name)`
Create STP strategy group.

```python
result = spot_client.create_stp_strategy_group("group_name")
```

##### `query_stp_strategy_group(trade_group_name=None)`
Query STP strategy group.

```python
result = spot_client.query_stp_strategy_group()
```

##### `delete_stp_strategy_group(trade_group_id)`
Delete STP strategy group.

```python
result = spot_client.delete_stp_strategy_group("group_id")
```

##### `add_uid_to_stp_strategy_group(uid, trade_group_id)`
Add uid to STP strategy group.

```python
result = spot_client.add_uid_to_stp_strategy_group("123456", "group_id")
```

##### `delete_uid_from_stp_strategy_group(uid, trade_group_id)`
Delete uid from STP strategy group.

```python
result = spot_client.delete_uid_from_stp_strategy_group("123456", "group_id")
```

#### Wallet Endpoints

##### `query_symbol_commission(symbol)`
Query symbol commission.

```python
result = spot_client.query_symbol_commission("BTCUSDT")
```

##### `get_currency_info()`
Query the currency information.

```python
result = spot_client.get_currency_info()
```

##### `withdraw(coin, address, amount, contract_address=None, withdraw_order_id=None, network=None, memo=None, remark=None)`
Withdraw funds.

```python
result = spot_client.withdraw("USDT", "address", 100.0, network="TRC20")
```

##### `cancel_withdraw(id)`
Cancel withdraw.

```python
result = spot_client.cancel_withdraw("withdraw_id")
```

##### `deposit_history(coin=None, status=None, start_time=None, end_time=None, limit=None)`
Get deposit history.

```python
result = spot_client.deposit_history(coin="USDT", limit=100)
```

##### `withdraw_history(coin=None, status=None, limit=None, start_time=None, end_time=None)`
Get withdraw history.

```python
result = spot_client.withdraw_history(coin="USDT", limit=100)
```

##### `generate_deposit_address(coin, network)`
Generate deposit address.

```python
result = spot_client.generate_deposit_address("USDT", "TRC20")
```

##### `deposit_address(coin, network=None)`
Get deposit address.

```python
result = spot_client.deposit_address("USDT", "TRC20")
```

##### `withdraw_address(coin=None, page=None, limit=None)`
Get withdraw address.

```python
result = spot_client.withdraw_address(coin="USDT")
```

##### `user_universal_transfer(from_account_type, to_account_type, asset, amount)`
User Universal Transfer.

```python
result = spot_client.user_universal_transfer("SPOT", "FUTURES", "USDT", 100.0)
```

##### `user_universal_transfer_history(from_account_type, to_account_type, start_time=None, end_time=None, page=1, size=10)`
Query User Universal Transfer History.

```python
result = spot_client.user_universal_transfer_history("SPOT", "FUTURES")
```

##### `user_universal_transfer_history_by_tranid(tran_id)`
Query User Universal Transfer History by tranId.

```python
result = spot_client.user_universal_transfer_history_by_tranid("tran_id")
```

##### `get_assets_convert_into_mx()`
Get assets that can be converted into MX.

```python
result = spot_client.get_assets_convert_into_mx()
```

##### `dust_transfer(asset)`
Dust transfer (convert small amounts to MX).

```python
result = spot_client.dust_transfer(["BTC", "ETH"])
```

##### `dustlog(start_time=None, end_time=None, page=None, limit=None)`
Get dust transfer log.

```python
result = spot_client.dustlog()
```

##### `internal_transfer(to_account_type, to_account, asset, amount, area_code=None)`
Internal transfer.

```python
result = spot_client.internal_transfer("EMAIL", "user@example.com", "USDT", 100.0)
```

##### `internal_transfer_history(start_time=None, end_time=None, page=None, limit=None, tran_id=None)`
Get internal transfer history.

```python
result = spot_client.internal_transfer_history()
```

#### WebSocket User Data Streams

##### `create_listen_key()`
Create a listen key for user data stream.

```python
result = spot_client.create_listen_key()
```

##### `get_listen_keys()`
Get valid listen keys.

```python
result = spot_client.get_listen_keys()
```

##### `keep_alive_listen_key(listen_key)`
Keep-alive a listen key.

```python
result = spot_client.keep_alive_listen_key("listen_key")
```

##### `close_listen_key(listen_key)`
Close a listen key.

```python
result = spot_client.close_listen_key("listen_key")
```

#### Rebate Endpoints

##### `get_rebate_history_records(start_time=None, end_time=None, page=None)`
Get rebate history records.

```python
result = spot_client.get_rebate_history_records()
```

##### `get_rebate_records_detail(start_time=None, end_time=None, page=None)`
Get rebate records detail.

```python
result = spot_client.get_rebate_records_detail()
```

##### `get_self_rebate_records_detail(start_time=None, end_time=None, page=None)`
Get self rebate records detail.

```python
result = spot_client.get_self_rebate_records_detail()
```

##### `query_refercode()`
Query refer code.

```python
result = spot_client.query_refercode()
```

##### `affiliate_commission_record(start_time=None, end_time=None, invite_code=None, page=None, page_size=None)`
Get affiliate commission record (affiliate only).

```python
result = spot_client.affiliate_commission_record()
```

##### `affiliate_withdraw_record(start_time=None, end_time=None, invite_code=None, page=None, page_size=None)`
Get affiliate withdraw record (affiliate only).

```python
result = spot_client.affiliate_withdraw_record()
```

##### `affiliate_commission_detail_record(start_time=None, end_time=None, invite_code=None, page=None, page_size=None, type=None)`
Get affiliate commission detail record (affiliate only).

```python
result = spot_client.affiliate_commission_detail_record()
```

##### `affiliate_campaign(start_time=None, end_time=None, page=None, page_size=None)`
Get affiliate campaign data (affiliate only).

```python
result = spot_client.affiliate_campaign()
```

##### `affiliate_referral(start_time=None, end_time=None, uid=None, invite_code=None, page=None, page_size=None)`
Get affiliate referral data (affiliate only).

```python
result = spot_client.affiliate_referral()
```

##### `affiliate_subaffiliates(start_time=None, end_time=None, invite_code=None, page=None, page_size=None)`
Get subaffiliates data (affiliate only).

```python
result = spot_client.affiliate_subaffiliates()
```

### Spot API (WebSocket)

#### Public Streams

##### `deals_stream(callback, symbol, interval=None)`
Subscribe to trade streams.

```python
def handle_deals(message):
    print(message)

ws_spot_client.deals_stream(handle_deals, "BTCUSDT")
```

##### `kline_stream(callback, symbol, interval)`
Subscribe to kline streams.

```python
def handle_kline(message):
    print(message)

ws_spot_client.kline_stream(handle_kline, "BTCUSDT", "Min1")
```

##### `depth_stream(callback, symbol, interval="100ms")`
Subscribe to diff depth stream.

```python
def handle_depth(message):
    print(message)

ws_spot_client.depth_stream(handle_depth, "BTCUSDT", "100ms")
```

##### `limit_depth_stream(callback, symbol, level)`
Subscribe to partial book depth streams.

```python
def handle_limit_depth(message):
    print(message)

ws_spot_client.limit_depth_stream(handle_limit_depth, "BTCUSDT", 10)
```

##### `book_ticker_stream(callback, symbol, interval="100ms")`
Subscribe to individual symbol book ticker streams.

```python
def handle_book_ticker(message):
    print(message)

ws_spot_client.book_ticker_stream(handle_book_ticker, "BTCUSDT")
```

##### `book_ticker_batch_stream(callback, symbols)`
Subscribe to batch book ticker streams.

```python
def handle_batch_ticker(message):
    print(message)

ws_spot_client.book_ticker_batch_stream(handle_batch_ticker, ["BTCUSDT", "ETHUSDT"])
```

##### `mini_tickers_stream(callback, timezone="UTC+8")`
Subscribe to mini tickers of all trading pairs.

```python
def handle_mini_tickers(message):
    print(message)

ws_spot_client.mini_tickers_stream(handle_mini_tickers)
```

##### `mini_ticker_stream(callback, symbol, timezone="UTC+8")`
Subscribe to mini ticker of specified trading pair.

```python
def handle_mini_ticker(message):
    print(message)

ws_spot_client.mini_ticker_stream(handle_mini_ticker, "BTCUSDT")
```

#### Private Streams

##### `account_update(callback)`
Subscribe to spot account updates.

```python
def handle_account_update(message):
    print(message)

ws_spot_client.account_update(handle_account_update)
```

##### `account_deals(callback)`
Subscribe to spot account deals.

```python
def handle_account_deals(message):
    print(message)

ws_spot_client.account_deals(handle_account_deals)
```

##### `account_orders(callback)`
Subscribe to spot account orders.

```python
def handle_account_orders(message):
    print(message)

ws_spot_client.account_orders(handle_account_orders)
```

### Futures API (HTTP)

#### Market Endpoints

##### `ping()`
Get server time.

```python
result = futures_client.ping()
```

##### `detail(symbol=None)`
Get contract info.

```python
result = futures_client.detail("BTC_USDT")
```

##### `support_currencies()`
Get transferable currencies.

```python
result = futures_client.support_currencies()
```

##### `get_depth(symbol, limit=None)`
Get contract order book depth.

```python
result = futures_client.get_depth("BTC_USDT", limit=100)
```

##### `depth_commits(symbol, limit)`
Get the last N depth snapshots.

```python
result = futures_client.depth_commits("BTC_USDT", 5)
```

##### `index_price(symbol)`
Get index price.

```python
result = futures_client.index_price("BTC_USDT")
```

##### `fair_price(symbol)`
Get fair price.

```python
result = futures_client.fair_price("BTC_USDT")
```

##### `funding_rate(symbol)`
Get funding rate.

```python
result = futures_client.funding_rate("BTC_USDT")
```

##### `kline(symbol, interval=None, start=None, end=None)`
Get candlestick data.

```python
result = futures_client.kline("BTC_USDT", interval="Min1")
```

##### `kline_index_price(symbol, interval="Min1", start=None, end=None)`
Get index price candles.

```python
result = futures_client.kline_index_price("BTC_USDT", interval="Min1")
```

##### `kline_fair_price(symbol, interval="Min1", start=None, end=None)`
Get fair price candles.

```python
result = futures_client.kline_fair_price("BTC_USDT", interval="Min1")
```

##### `deals(symbol, limit=100)`
Get recent trades.

```python
result = futures_client.deals("BTC_USDT", limit=100)
```

##### `ticker(symbol=None)`
Get ticker (contract market data).

```python
result = futures_client.ticker("BTC_USDT")
```

##### `risk_reverse(symbol)`
Get insurance fund balance.

```python
result = futures_client.risk_reverse("BTC_USDT")
```

##### `risk_reverse_history(symbol, page_num=1, page_size=20)`
Get insurance fund balance history.

```python
result = futures_client.risk_reverse_history("BTC_USDT")
```

##### `funding_rate_history(symbol, page_num=1, page_size=20)`
Get funding rate history.

```python
result = futures_client.funding_rate_history("BTC_USDT")
```

#### Account and Trading Endpoints

##### `assets()`
Get all account assets.

```python
result = futures_client.assets()
```

##### `asset(currency)`
Get single currency asset information.

```python
result = futures_client.asset("USDT")
```

##### `transfer_record(currency=None, state=None, type=None, page_num=1, page_size=20)`
Get asset transfer records.

```python
result = futures_client.transfer_record()
```

##### `history_positions(symbol=None, type=None, start_time=None, end_time=None, page_num=1, page_size=20)`
Get historical positions.

```python
result = futures_client.history_positions()
```

##### `open_positions(symbol=None, position_id=None)`
Get open positions.

```python
result = futures_client.open_positions()
```

##### `funding_records(position_type, start_time, end_time, symbol=None, position_id=None, page_num=1, page_size=20)`
Get funding fee details.

```python
result = futures_client.funding_records(1, start_time, end_time)
```

##### `open_orders(symbol=None, page_num=1, page_size=20)`
Get current open orders.

```python
result = futures_client.open_orders()
```

##### `history_orders(symbol=None, states=None, category=None, start_time=None, end_time=None, side=None, order_id=None, page_num=1, page_size=20)`
Get all historical orders.

```python
result = futures_client.history_orders()
```

##### `get_order_external(symbol, external_oid)`
Get order by external ID.

```python
result = futures_client.get_order_external("BTC_USDT", "ext_123")
```

##### `get_order(order_id)`
Get order information by order ID.

```python
result = futures_client.get_order(123456)
```

##### `batch_query(order_ids)`
Batch query orders by order ID.

```python
result = futures_client.batch_query([123456, 123457])
```

##### `deal_details(symbol, order_id)`
Get trade details by order ID.

```python
result = futures_client.deal_details("BTC_USDT", 123456)
```

##### `order_deals(symbol, start_time=None, end_time=None, page_num=1, page_size=20)`
Get historical order deal details.

```python
result = futures_client.order_deals("BTC_USDT")
```

##### `get_trigger_orders(symbol=None, states=None, side=None, start_time=None, end_time=None, page_num=1, page_size=20)`
Get plan order list.

```python
result = futures_client.get_trigger_orders()
```

##### `get_stop_limit_orders(symbol=None, is_finished=None, state=None, type=None, start_time=None, end_time=None, page_num=1, page_size=20)`
Get take-profit/stop-loss order list.

```python
result = futures_client.get_stop_limit_orders()
```

##### `risk_limit(symbol=None)`
Get risk limits.

```python
result = futures_client.risk_limit()
```

##### `tiered_fee_rate(symbol=None)`
Get fee details.

```python
result = futures_client.tiered_fee_rate()
```

##### `change_margin(position_id, amount, type)`
Modify position margin (Under Maintenance).

```python
result = futures_client.change_margin(123, 100.0, "ADD")
```

##### `get_leverage(symbol)`
Get position leverage multipliers.

```python
result = futures_client.get_leverage("BTC_USDT")
```

##### `change_leverage(leverage, position_id=None, open_type=None, symbol=None, position_type=None, leverage_mode=None, margin_selected=None, leverage_selected=None)`
Modify leverage (Under Maintenance).

```python
result = futures_client.change_leverage(10, symbol="BTC_USDT")
```

##### `get_position_mode()`
Get user position mode.

```python
result = futures_client.get_position_mode()
```

##### `change_position_mode(position_mode)`
Modify user position mode (Under Maintenance).

```python
result = futures_client.change_position_mode(1)
```

##### `order(symbol, price, vol, side, type, open_type, position_id=None, leverage=None, ...)`
Place order (Under Maintenance).

```python
result = futures_client.order(
    symbol="BTC_USDT",
    price=50000,
    vol=0.001,
    side=1,
    type=1,
    open_type=1,
    leverage=10
)
```

##### `bulk_order(symbol, price, vol, side, type, open_type, position_id=None, external_oid=None, ...)`
Bulk order (Under Maintenance).

```python
result = futures_client.bulk_order(
    symbol="BTC_USDT",
    price=50000,
    vol=0.001,
    side=1,
    type=1,
    open_type=1
)
```

##### `cancel_order(order_ids)`
Cancel orders (Under Maintenance).

```python
result = futures_client.cancel_order([123456, 123457])
```

##### `cancel_order_with_external(orders)`
Cancel by external order ID (Under Maintenance).

```python
result = futures_client.cancel_order_with_external([
    {"symbol": "BTC_USDT", "externalOid": "ext_123"}
])
```

##### `cancel_all(symbol=None)`
Cancel all orders under a contract (Under Maintenance).

```python
result = futures_client.cancel_all("BTC_USDT")
```

##### `trigger_order(symbol, vol, side, open_type, trigger_price, trigger_type, execute_cycle, order_type, trend, leverage, ...)`
Place plan order (Under Maintenance).

```python
result = futures_client.trigger_order(
    symbol="BTC_USDT",
    vol=0.001,
    side=1,
    open_type=1,
    trigger_price=50000,
    trigger_type=1,
    execute_cycle=1,
    order_type=1,
    trend=1,
    leverage=10
)
```

##### `cancel_trigger_order(orders)`
Cancel planned orders (Under Maintenance).

```python
result = futures_client.cancel_trigger_order([
    {"symbol": "BTC_USDT", "orderId": 123456}
])
```

##### `cancel_all_trigger_orders(symbol=None)`
Cancel all planned orders (Under Maintenance).

```python
result = futures_client.cancel_all_trigger_orders("BTC_USDT")
```

##### `cancel_stop_order(orders)`
Cancel TP/SL planned orders (Under Maintenance).

```python
result = futures_client.cancel_stop_order([
    {"stopPlanOrderId": 123456}
])
```

##### `cancel_all_stop_orders(symbol=None)`
Cancel all TP/SL orders (Under Maintenance).

```python
result = futures_client.cancel_all_stop_orders("BTC_USDT")
```

##### `place_stop_order(symbol, vol, side, open_type, trigger_price, trigger_type, order_type, trend, position_id, ...)`
Place TP/SL order (Under Maintenance).

```python
result = futures_client.place_stop_order(
    symbol="BTC_USDT",
    vol=0.001,
    side=1,
    open_type=1,
    trigger_price=50000,
    trigger_type=1,
    order_type=1,
    trend=1,
    position_id=123
)
```

### Broker API (HTTP)

##### `query_universal_transfer_history(from_account_type, to_account_type, from_account=None, to_account=None, start_time=None, end_time=None, page=1, limit=500)`
Query Universal Transfer History - broker user.

```python
result = broker_client.query_universal_transfer_history("SPOT", "FUTURES")
```

##### `create_sub_account(sub_account, note, password=None)`
Create a Sub-account.

```python
result = broker_client.create_sub_account("sub_account_name", "note")
```

##### `query_sub_account_list(sub_account=None, page=1, limit=10)`
Query Sub-account List.

```python
result = broker_client.query_sub_account_list()
```

##### `query_sub_account_status(sub_account)`
Query Sub-account Status.

```python
result = broker_client.query_sub_account_status("sub_account_name")
```

##### `create_sub_account_api_key(sub_account, permissions, note, ip=None)`
Create an APIKey for a Sub-account.

```python
result = broker_client.create_sub_account_api_key(
    "sub_account_name",
    ["SPOT_ACCOUNT_READ"],
    "note"
)
```

##### `query_sub_account_api_key(sub_account)`
Query the APIKey of a Sub-account.

```python
result = broker_client.query_sub_account_api_key("sub_account_name")
```

##### `delete_sub_account_api_key(sub_account, api_key)`
Delete the APIKey of a Sub-account.

```python
result = broker_client.delete_sub_account_api_key("sub_account_name", "api_key")
```

##### `generate_deposit_address(coin, network)`
Generate Deposit Address of Sub-account.

```python
result = broker_client.generate_deposit_address("USDT", "TRC20")
```

##### `deposit_address(coin)`
Deposit Address of Sub-account.

```python
result = broker_client.deposit_address("USDT")
```

##### `query_sub_account_deposit_history(coin=None, status=None, start_time=None, end_time=None, limit=20, page=1)`
Query Sub-account Deposit History.

```python
result = broker_client.query_sub_account_deposit_history()
```

##### `query_all_sub_account_deposit_history(coin=None, status=None, start_time=None, end_time=None, limit=100, page=1)`
Query All Sub-account Deposit History (Recent 3 days).

```python
result = broker_client.query_all_sub_account_deposit_history()
```

##### `withdraw(coin, network, address, amount, password=None, remark=None)`
Withdraw.

```python
result = broker_client.withdraw("USDT", "TRC20", "address", 100.0)
```

##### `universal_transfer(from_account_type, to_account_type, asset, amount, from_account=None, to_account=None)`
Universal Transfer.

```python
result = broker_client.universal_transfer("SPOT", "FUTURES", "USDT", 100.0)
```

##### `enable_futures_for_sub_account(sub_account)`
Enable Futures for Sub-account.

```python
result = broker_client.enable_futures_for_sub_account("sub_account_name")
```

##### `get_broker_rebate_history_records(start_time=None, end_time=None, page=1, page_size=10)`
Get Broker Rebate History Records.

```python
result = broker_client.get_broker_rebate_history_records()
```

# License

This library is licensed under the MIT License.
