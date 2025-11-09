# pytest tests/test_examples.py -v -s --log-cli-level=INFO

import time
from datetime import datetime, timedelta

import pytest
from dotenv import dotenv_values

import pymexc.base
from pymexc import spot, futures

env = dotenv_values(".env")

api_key = env.get("API_KEY", "")
api_secret = env.get("API_SECRET", "")

http = spot.HTTP(api_key=api_key, api_secret=api_secret)
public_http = spot.HTTP()  # Without auth for public endpoints

PRINT_RESPONSE = True


# ============================================================================
# Test aliases
# ============================================================================


def test_depth_alias():
    """Test depth() alias for order_book()"""
    resp1 = public_http.order_book(symbol="BTCUSDT", limit=5)
    resp2 = public_http.depth(symbol="BTCUSDT", limit=5)

    if PRINT_RESPONSE:
        print(f"order_book response: {resp1}")
        print(f"depth response: {resp2}")

    assert isinstance(resp1, dict), f"order_book should return dict, got {type(resp1)}"
    assert isinstance(resp2, dict), f"depth should return dict, got {type(resp2)}"
    assert "bids" in resp1, f"order_book missing 'bids' key. Keys: {resp1.keys()}"
    assert "asks" in resp1, f"order_book missing 'asks' key. Keys: {resp1.keys()}"
    assert "bids" in resp2, f"depth missing 'bids' key. Keys: {resp2.keys()}"
    assert "asks" in resp2, f"depth missing 'asks' key. Keys: {resp2.keys()}"
    # Compare structure (timestamp may differ)
    assert len(resp1.get("bids", [])) == len(resp2.get("bids", [])), (
        f"Bids length mismatch: {len(resp1.get('bids', []))} != {len(resp2.get('bids', []))}"
    )
    assert len(resp1.get("asks", [])) == len(resp2.get("asks", [])), (
        f"Asks length mismatch: {len(resp1.get('asks', []))} != {len(resp2.get('asks', []))}"
    )


def test_ticker24h_alias():
    """Test ticker24h() alias for ticker_24h()"""
    resp1 = public_http.ticker_24h(symbol="BTCUSDT")
    resp2 = public_http.ticker24h(symbol="BTCUSDT")

    if PRINT_RESPONSE:
        print(f"ticker_24h response: {resp1}")
        print(f"ticker24h response: {resp2}")

    assert isinstance(resp1, dict), f"ticker_24h should return dict, got {type(resp1)}"
    assert isinstance(resp2, dict), f"ticker24h should return dict, got {type(resp2)}"
    assert resp1 == resp2, f"Responses should be equal. ticker_24h: {resp1}, ticker24h: {resp2}"
    assert resp1.get("symbol") == "BTCUSDT", f"Expected symbol BTCUSDT, got {resp1.get('symbol')}"
    assert resp2.get("symbol") == "BTCUSDT", f"Expected symbol BTCUSDT, got {resp2.get('symbol')}"


# ============================================================================
# Test examples from README
# ============================================================================


def test_example_getting_current_price_and_market_data():
    """Test example: Getting Current Price and Market Data"""
    # Get current price
    ticker = public_http.ticker_price("BTCUSDT")
    if PRINT_RESPONSE:
        print(f"Ticker price: {ticker}")
    assert isinstance(ticker, dict), f"Expected dict, got {type(ticker)}"
    assert "price" in ticker, f"Missing 'price' key. Keys: {ticker.keys()}"
    assert ticker.get("symbol") == "BTCUSDT", f"Expected BTCUSDT, got {ticker.get('symbol')}"
    assert float(ticker["price"]) > 0, f"Price should be positive, got {ticker['price']}"

    # Get 24h ticker statistics
    stats = public_http.ticker_24h("BTCUSDT")
    if PRINT_RESPONSE:
        print(f"24h stats: {stats}")
    assert isinstance(stats, dict), f"Expected dict, got {type(stats)}"
    assert "priceChangePercent" in stats, f"Missing 'priceChangePercent' key. Keys: {stats.keys()}"
    assert "volume" in stats, f"Missing 'volume' key. Keys: {stats.keys()}"
    assert stats.get("symbol") == "BTCUSDT", f"Expected BTCUSDT, got {stats.get('symbol')}"

    # Get order book
    orderbook = public_http.order_book("BTCUSDT", limit=10)
    if PRINT_RESPONSE:
        print(f"Order book: {orderbook}")
    assert isinstance(orderbook, dict), f"Expected dict, got {type(orderbook)}"
    assert "bids" in orderbook, f"Missing 'bids' key. Keys: {orderbook.keys()}"
    assert "asks" in orderbook, f"Missing 'asks' key. Keys: {orderbook.keys()}"
    assert len(orderbook["bids"]) > 0, f"Bids should not be empty, got {len(orderbook['bids'])}"
    assert len(orderbook["asks"]) > 0, f"Asks should not be empty, got {len(orderbook['asks'])}"
    assert len(orderbook["bids"]) <= 10, f"Bids should be <= 10, got {len(orderbook['bids'])}"
    assert len(orderbook["asks"]) <= 10, f"Asks should be <= 10, got {len(orderbook['asks'])}"

    # Get recent trades
    trades = public_http.trades("BTCUSDT", limit=10)
    if PRINT_RESPONSE:
        print(f"Trades: {trades[:3] if len(trades) > 3 else trades}")
    assert isinstance(trades, list), f"Expected list, got {type(trades)}"
    assert len(trades) <= 10, f"Should have <= 10 trades, got {len(trades)}"
    if len(trades) > 0:
        assert "price" in trades[0], f"Missing 'price' key in trade. Keys: {trades[0].keys()}"
        assert "qty" in trades[0], f"Missing 'qty' key in trade. Keys: {trades[0].keys()}"


def test_example_placing_and_managing_orders():
    """Test example: Placing and Managing Orders"""
    if not api_key or not api_secret:
        pytest.skip("API credentials not provided")

    # Get current price first
    ticker = public_http.ticker_price("MXUSDT")
    if PRINT_RESPONSE:
        print(f"Current MXUSDT price: {ticker}")
    current_price = float(ticker["price"])

    # Place a limit buy order 1% below current price
    buy_price = current_price * 0.99
    try:
        result = http.order(
            symbol="MXUSDT", side="BUY", order_type="LIMIT", quantity=50, price=buy_price, time_in_force="GTC"
        )
        if PRINT_RESPONSE:
            print(f"Order placed: {result}")
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "orderId" in result, f"Missing 'orderId' key. Keys: {result.keys()}"
        assert result["symbol"] == "MXUSDT", f"Expected MXUSDT, got {result.get('symbol')}"
        assert result["side"] == "BUY", f"Expected BUY, got {result.get('side')}"

        # Check order status
        order_status = http.query_order("MXUSDT", order_id=result["orderId"])
        if PRINT_RESPONSE:
            print(f"Order status: {order_status}")
        assert isinstance(order_status, dict), f"Expected dict, got {type(order_status)}"
        assert "status" in order_status, f"Missing 'status' key. Keys: {order_status.keys()}"
        assert order_status["orderId"] == result["orderId"], (
            f"Order ID mismatch: {order_status.get('orderId')} != {result['orderId']}"
        )

        # Get all open orders
        open_orders = http.current_open_orders("MXUSDT")
        if PRINT_RESPONSE:
            print(f"Open orders: {open_orders}")
        assert isinstance(open_orders, list), f"Expected list, got {type(open_orders)}"
        assert any(order["orderId"] == result["orderId"] for order in open_orders), (
            f"Order {result['orderId']} not found in open orders"
        )

        # Cancel the order
        cancel_result = http.cancel_order("MXUSDT", order_id=result["orderId"])
        if PRINT_RESPONSE:
            print(f"Cancel result: {cancel_result}")
        assert isinstance(cancel_result, dict), f"Expected dict, got {type(cancel_result)}"
        assert cancel_result["orderId"] == result["orderId"], (
            f"Cancel order ID mismatch: {cancel_result.get('orderId')} != {result['orderId']}"
        )
    except pymexc.base.MexcAPIError as e:
        # Handle insufficient balance or other API errors
        error_msg = str(e)
        if PRINT_RESPONSE:
            print(f"API Error: {error_msg}")
        if "Insufficient" in error_msg or "30004" in error_msg:
            pytest.skip(f"Insufficient balance to place order: {error_msg}")
        else:
            raise


def test_example_market_order():
    """Test example: Market Order"""
    if not api_key or not api_secret:
        pytest.skip("API credentials not provided")

    # Test market order with test_order first (doesn't actually place order)
    result = http.test_order(
        symbol="MXUSDT",
        side="BUY",
        order_type="MARKET",
        quote_order_qty=10,  # Test with $10 worth
    )
    if PRINT_RESPONSE:
        print(f"Test market order result: {result}")
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    assert result == {}, f"Test order should return empty dict on success, got {result}"


def test_example_getting_account_balance():
    """Test example: Getting Account Balance"""
    if not api_key or not api_secret:
        pytest.skip("API credentials not provided")

    # Get account information
    account = http.account_information()
    if PRINT_RESPONSE:
        print(f"Account info: {account}")
    assert isinstance(account, dict), f"Expected dict, got {type(account)}"
    assert "balances" in account, f"Missing 'balances' key. Keys: {account.keys()}"
    assert isinstance(account["balances"], list), f"Balances should be list, got {type(account['balances'])}"

    # Check balance structure
    for balance in account["balances"]:
        assert "asset" in balance, f"Missing 'asset' key. Keys: {balance.keys()}"
        assert "free" in balance, f"Missing 'free' key. Keys: {balance.keys()}"
        assert "locked" in balance, f"Missing 'locked' key. Keys: {balance.keys()}"
        free = float(balance["free"])
        locked = float(balance["locked"])
        total = free + locked
        assert total >= 0, f"Total balance should be >= 0, got {total}"


def test_example_getting_trading_history():
    """Test example: Getting Trading History"""
    if not api_key or not api_secret:
        pytest.skip("API credentials not provided")

    # Get recent trades for a symbol
    trades = http.account_trade_list("MXUSDT", limit=100)
    if PRINT_RESPONSE:
        print(f"Trading history: {len(trades)} trades")
        if len(trades) > 0:
            print(f"First trade: {trades[0]}")
    assert isinstance(trades, list), f"Expected list, got {type(trades)}"
    assert len(trades) <= 100, f"Should have <= 100 trades, got {len(trades)}"

    # Calculate total volume and PnL
    total_volume = 0
    total_cost = 0
    for trade in trades:
        assert "qty" in trade, f"Missing 'qty' key. Keys: {trade.keys()}"
        assert "price" in trade, f"Missing 'price' key. Keys: {trade.keys()}"
        assert "isBuyer" in trade, f"Missing 'isBuyer' key. Keys: {trade.keys()}"
        qty = float(trade["qty"])
        price = float(trade["price"])
        total_volume += qty
        if trade["isBuyer"]:
            total_cost += qty * price
        else:
            total_cost -= qty * price

    if PRINT_RESPONSE:
        print(f"Total volume: {total_volume}, Total cost: {total_cost}")
    assert total_volume >= 0, f"Total volume should be >= 0, got {total_volume}"
    # total_cost can be positive or negative depending on trades


def test_example_getting_kline_data_for_analysis():
    """Test example: Getting Kline/Candlestick Data for Analysis"""
    # Get klines for the last 24 hours
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(days=1)).timestamp() * 1000)

    # Use valid interval format for spot API: "1m", "5m", "15m", "30m", "60m", "4h", "1d", "1M"
    klines = public_http.klines(symbol="BTCUSDT", interval="60m", start_time=start_time, end_time=end_time, limit=24)
    if PRINT_RESPONSE:
        print(f"Klines count: {len(klines)}")
        if len(klines) > 0:
            print(f"First kline: {klines[0]}")
    assert isinstance(klines, list), f"Expected list, got {type(klines)}"
    assert len(klines) > 0, f"Should have at least 1 kline, got {len(klines)}"

    # Check kline structure
    for kline in klines:
        assert isinstance(kline, list)
        assert len(kline) >= 6  # At least open_time, open, high, low, close, volume
        assert isinstance(kline[0], int)  # open_time
        assert float(kline[1]) > 0  # open
        assert float(kline[2]) > 0  # high
        assert float(kline[3]) > 0  # low
        assert float(kline[4]) > 0  # close
        assert float(kline[5]) >= 0  # volume

    # Test with pandas if available
    try:
        import pandas as pd  # type: ignore

        df = pd.DataFrame(
            klines,
            columns=[
                "open_time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_volume",
                "trades",
                "taker_buy_base",
                "taker_buy_quote",
                "ignore",
            ],
        )

        # Convert to numeric
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col])

        # Calculate simple moving average
        df["sma_20"] = df["close"].rolling(window=min(20, len(df))).mean()

        assert len(df) > 0
        assert "sma_20" in df.columns
    except ImportError:
        pass  # pandas not available, skip that part


def test_example_batch_order_placement():
    """Test example: Batch Order Placement"""
    if not api_key or not api_secret:
        pytest.skip("API credentials not provided")

    # Get current price
    ticker = public_http.ticker_price("MXUSDT")
    if PRINT_RESPONSE:
        print(f"Current MXUSDT price: {ticker}")
    current_price = float(ticker["price"])

    # Prepare multiple orders at different price levels
    batch_orders = []
    for i in range(3):  # Use 3 instead of 5 to avoid too many orders
        price = current_price * (0.99 - i * 0.001)
        batch_orders.append({"price": str(price), "quantity": "50"})

    if PRINT_RESPONSE:
        print(f"Batch orders to place: {batch_orders}")

    try:
        # Place batch orders - need to provide quantity and price as function parameters for LIMIT orders
        # The batch_orders list contains additional order-specific parameters
        result = http.batch_orders(
            batch_orders=batch_orders,
            symbol="MXUSDT",
            side="BUY",
            order_type="LIMIT",
            quantity=50,  # Required for LIMIT orders
            price=current_price * 0.99,  # Required for LIMIT orders (will be overridden by batch_orders)
        )

        if PRINT_RESPONSE:
            print(f"Batch orders result: {result}")

        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert len(result) == len(batch_orders), f"Expected {len(batch_orders)} results, got {len(result)}"
        for i, order in enumerate(result):
            assert isinstance(order, dict), f"Order {i} should be dict, got {type(order)}"
            assert "orderId" in order or "code" in order, f"Order {i} missing 'orderId' or 'code'. Keys: {order.keys()}"

        # Cleanup - cancel all orders
        try:
            http.cancel_all_open_orders("MXUSDT")
        except Exception as e:
            if PRINT_RESPONSE:
                print(f"Error canceling orders: {e}")
    except pymexc.base.MexcAPIError as e:
        if PRINT_RESPONSE:
            print(f"API Error placing batch orders: {e}")
        if "Insufficient" in str(e) or "30004" in str(e):
            pytest.skip(f"Insufficient balance to place batch orders: {e}")
        else:
            raise


def test_example_error_handling():
    """Test example: Error Handling"""
    if not api_key or not api_secret:
        pytest.skip("API credentials not provided")

    # Test error case - invalid symbol
    with pytest.raises(pymexc.base.MexcAPIError) as exc_info:
        http.order(symbol="INVALID_SYMBOL", side="BUY", order_type="LIMIT", quantity=0.001, price=50000)
    error_msg = str(exc_info.value)
    if PRINT_RESPONSE:
        print(f"Invalid symbol error: {error_msg}")
    assert "code" in error_msg, f"Error message should contain 'code'. Got: {error_msg}"

    # Test error case - missing required parameters
    with pytest.raises(ValueError) as exc_info:
        http.order(
            symbol="BTCUSDT",
            side="BUY",
            order_type="LIMIT",
            # Missing quantity and price
        )
    error_msg = str(exc_info.value)
    if PRINT_RESPONSE:
        print(f"Missing parameters error: {error_msg}")
    assert "LIMIT orders require both quantity and price" in error_msg, (
        f"Error should mention missing parameters. Got: {error_msg}"
    )

    # Test error case - insufficient balance (may not always raise error)
    try:
        result = http.order(
            symbol="BTCUSDT",
            side="BUY",
            order_type="LIMIT",
            quantity=1000000,  # Very large amount
            price=1,  # Very low price
        )
        if PRINT_RESPONSE:
            print(f"Large order result: {result}")
        # If order is placed, it might be rejected by exchange
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    except pymexc.base.MexcAPIError as e:
        error_msg = str(e)
        if PRINT_RESPONSE:
            print(f"Insufficient balance error: {error_msg}")
        # Expected error for insufficient balance
        assert "code" in error_msg, f"Error message should contain 'code'. Got: {error_msg}"


def test_example_checking_deposit_and_withdrawal_history():
    """Test example: Checking Deposit and Withdrawal History"""
    if not api_key or not api_secret:
        pytest.skip("API credentials not provided")

    # Get deposit history
    deposits = http.deposit_history(coin="USDT", limit=50)
    if PRINT_RESPONSE:
        print(f"Deposits: {len(deposits)} records")
        if len(deposits) > 0:
            print(f"First deposit: {deposits[0]}")
    assert isinstance(deposits, list), f"Expected list, got {type(deposits)}"
    assert len(deposits) <= 50, f"Should have <= 50 deposits, got {len(deposits)}"

    # Check deposit structure
    for deposit in deposits[:10]:  # Check first 10
        assert "amount" in deposit, f"Missing 'amount' key. Keys: {deposit.keys()}"
        assert "coin" in deposit, f"Missing 'coin' key. Keys: {deposit.keys()}"
        assert "status" in deposit, f"Missing 'status' key. Keys: {deposit.keys()}"
        assert "insertTime" in deposit, f"Missing 'insertTime' key. Keys: {deposit.keys()}"
        assert isinstance(deposit["insertTime"], (int, float)), (
            f"insertTime should be int or float, got {type(deposit['insertTime'])}"
        )

    # Get withdrawal history
    withdrawals = http.withdraw_history(coin="USDT", limit=50)
    if PRINT_RESPONSE:
        print(f"Withdrawals: {len(withdrawals)} records")
        if len(withdrawals) > 0:
            print(f"First withdrawal: {withdrawals[0]}")
    assert isinstance(withdrawals, list), f"Expected list, got {type(withdrawals)}"
    assert len(withdrawals) <= 50, f"Should have <= 50 withdrawals, got {len(withdrawals)}"

    # Check withdrawal structure
    for withdrawal in withdrawals[:10]:  # Check first 10
        assert "amount" in withdrawal, f"Missing 'amount' key. Keys: {withdrawal.keys()}"
        assert "coin" in withdrawal, f"Missing 'coin' key. Keys: {withdrawal.keys()}"
        assert "status" in withdrawal, f"Missing 'status' key. Keys: {withdrawal.keys()}"
        if "address" in withdrawal:
            assert isinstance(withdrawal["address"], str), f"Address should be str, got {type(withdrawal['address'])}"


def test_example_getting_multiple_symbols_data():
    """Test example: Getting Multiple Symbols Data"""
    # Get prices for multiple symbols
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"]
    prices = public_http.ticker_price(symbols=symbols)

    if PRINT_RESPONSE:
        print(f"Prices for {len(symbols)} symbols: {prices}")

    assert isinstance(prices, list), f"Expected list, got {type(prices)}"
    # API may return all symbols or just requested ones
    assert len(prices) >= len(symbols), f"Should have at least {len(symbols)} prices, got {len(prices)}"

    # Check that all requested symbols are present
    returned_symbols = [ticker.get("symbol") for ticker in prices if "symbol" in ticker]
    for symbol in symbols:
        assert symbol in returned_symbols, f"Symbol {symbol} not found in response. Got: {returned_symbols[:10]}"

    # Check structure of returned tickers
    for ticker in prices:
        assert "symbol" in ticker, f"Missing 'symbol' key. Keys: {ticker.keys()}"
        assert "price" in ticker, f"Missing 'price' key. Keys: {ticker.keys()}"
        if ticker["symbol"] in symbols:
            assert float(ticker["price"]) > 0, f"Price for {ticker['symbol']} should be positive, got {ticker['price']}"

    # Get 24h stats for multiple symbols
    stats = public_http.ticker_24h(symbols=symbols)
    if PRINT_RESPONSE:
        print(f"24h stats for {len(symbols)} symbols: {stats[:5] if len(stats) > 5 else stats}")

    assert isinstance(stats, list), f"Expected list, got {type(stats)}"
    # API may return all symbols or just requested ones
    assert len(stats) >= len(symbols), f"Should have at least {len(symbols)} stats, got {len(stats)}"

    # Check that all requested symbols are present
    returned_symbols = [stat.get("symbol") for stat in stats if "symbol" in stat]
    for symbol in symbols:
        assert symbol in returned_symbols, f"Symbol {symbol} not found in stats. Got: {returned_symbols[:10]}"

    # Check structure
    for stat in stats:
        if stat.get("symbol") in symbols:
            assert "symbol" in stat, f"Missing 'symbol' key. Keys: {stat.keys()}"
            assert "priceChangePercent" in stat, f"Missing 'priceChangePercent' key. Keys: {stat.keys()}"
            assert "highPrice" in stat, f"Missing 'highPrice' key. Keys: {stat.keys()}"
            assert "lowPrice" in stat, f"Missing 'lowPrice' key. Keys: {stat.keys()}"
            change = float(stat["priceChangePercent"])
            assert isinstance(change, float), f"priceChangePercent should be float, got {type(change)}"


def test_example_futures_getting_position_information():
    """Test example: Futures: Getting Position Information"""
    if not api_key or not api_secret:
        pytest.skip("API credentials not provided")

    futures_client = futures.HTTP(api_key=api_key, api_secret=api_secret, ignore_ad=True)

    # Get all open positions
    positions = futures_client.open_positions()
    if PRINT_RESPONSE:
        print(f"Futures positions: {positions}")
    assert isinstance(positions, dict), f"Expected dict, got {type(positions)}"
    assert "data" in positions, f"Missing 'data' key. Keys: {positions.keys()}"
    assert isinstance(positions["data"], list), f"Data should be list, got {type(positions['data'])}"

    # Check position structure
    for pos in positions.get("data", []):
        assert "symbol" in pos, f"Missing 'symbol' key. Keys: {pos.keys()}"
        assert "holdVol" in pos, f"Missing 'holdVol' key. Keys: {pos.keys()}"
        assert "unrealisedPnl" in pos, f"Missing 'unrealisedPnl' key. Keys: {pos.keys()}"

    # Get account assets
    assets = futures_client.assets()
    if PRINT_RESPONSE:
        print(f"Futures assets: {assets}")
    assert isinstance(assets, dict), f"Expected dict, got {type(assets)}"
    assert "data" in assets, f"Missing 'data' key. Keys: {assets.keys()}"
    assert isinstance(assets["data"], list), f"Data should be list, got {type(assets['data'])}"

    # Check asset structure
    for asset in assets.get("data", []):
        assert "currency" in asset, f"Missing 'currency' key. Keys: {asset.keys()}"
        assert "availableBalance" in asset, f"Missing 'availableBalance' key. Keys: {asset.keys()}"
        assert "frozenBalance" in asset, f"Missing 'frozenBalance' key. Keys: {asset.keys()}"
        assert float(asset["availableBalance"]) >= 0, (
            f"Available balance should be >= 0, got {asset['availableBalance']}"
        )
        assert float(asset["frozenBalance"]) >= 0, f"Frozen balance should be >= 0, got {asset['frozenBalance']}"


def test_example_async_await():
    """Test example: Async/Await Example"""
    if not api_key or not api_secret:
        pytest.skip("API credentials not provided")

    import asyncio
    from pymexc.spot import AsyncHTTP

    async def test_async():
        async_client = AsyncHTTP(api_key=api_key, api_secret=api_secret)

        # Make multiple requests concurrently
        tasks = [
            async_client.ticker_price("BTCUSDT"),
            async_client.ticker_price("ETHUSDT"),
            async_client.ticker_24h("BTCUSDT"),
            async_client.account_information(),
        ]

        results = await asyncio.gather(*tasks)

        btc_price, eth_price, btc_stats, account = results

        if PRINT_RESPONSE:
            print(
                f"Async results - BTC price: {btc_price}, ETH price: {eth_price}, BTC stats: {btc_stats}, Account: {account}"
            )

        assert isinstance(btc_price, dict), f"Expected dict, got {type(btc_price)}"
        assert "price" in btc_price, f"Missing 'price' key. Keys: {btc_price.keys()}"
        assert btc_price.get("symbol") == "BTCUSDT", f"Expected BTCUSDT, got {btc_price.get('symbol')}"

        assert isinstance(eth_price, dict), f"Expected dict, got {type(eth_price)}"
        assert "price" in eth_price, f"Missing 'price' key. Keys: {eth_price.keys()}"
        assert eth_price.get("symbol") == "ETHUSDT", f"Expected ETHUSDT, got {eth_price.get('symbol')}"

        assert isinstance(btc_stats, dict), f"Expected dict, got {type(btc_stats)}"
        assert "priceChangePercent" in btc_stats, f"Missing 'priceChangePercent' key. Keys: {btc_stats.keys()}"
        assert btc_stats.get("symbol") == "BTCUSDT", f"Expected BTCUSDT, got {btc_stats.get('symbol')}"

        assert isinstance(account, dict), f"Expected dict, got {type(account)}"
        assert "balances" in account, f"Missing 'balances' key. Keys: {account.keys()}"
        assert isinstance(account["balances"], list), f"Balances should be list, got {type(account['balances'])}"

    # Run async test
    asyncio.run(test_async())


def test_example_exchange_info_multiple_symbols():
    """Test exchange_info with multiple symbols"""
    # Test with single symbol
    resp1 = public_http.exchange_info(symbol="BTCUSDT")
    if PRINT_RESPONSE:
        print(f"Exchange info (single): {resp1}")
    assert isinstance(resp1, dict), f"Expected dict, got {type(resp1)}"
    assert "BTCUSDT" in str(resp1), f"BTCUSDT not found in response: {resp1}"

    # Test with multiple symbols
    resp2 = public_http.exchange_info(symbols=["BTCUSDT", "ETHUSDT"])
    if PRINT_RESPONSE:
        print(f"Exchange info (multiple): {resp2}")
    assert isinstance(resp2, dict), f"Expected dict, got {type(resp2)}"
    assert "BTCUSDT" in str(resp2) or "ETHUSDT" in str(resp2), f"BTCUSDT or ETHUSDT not found in response: {resp2}"

    # Test without parameters (all symbols)
    resp3 = public_http.exchange_info()
    if PRINT_RESPONSE:
        print(f"Exchange info (all): {resp3}")
    assert isinstance(resp3, dict), f"Expected dict, got {type(resp3)}"
    assert "symbols" in resp3, f"Missing 'symbols' key. Keys: {resp3.keys()}"


def test_example_ticker_price_all_symbols():
    """Test ticker_price without symbol (all symbols)"""
    resp = public_http.ticker_price()
    if PRINT_RESPONSE:
        print(f"Ticker price (all symbols): {len(resp)} symbols")
    assert isinstance(resp, list), f"Expected list, got {type(resp)}"
    assert len(resp) > 0, f"Should have at least 1 ticker, got {len(resp)}"
    assert all("symbol" in ticker and "price" in ticker for ticker in resp), (
        "All tickers should have 'symbol' and 'price' keys"
    )


def test_example_ticker_24h_all_symbols():
    """Test ticker_24h without symbol (all symbols)"""
    resp = public_http.ticker_24h()
    if PRINT_RESPONSE:
        print(f"Ticker 24h (all symbols): {len(resp)} symbols")
    assert isinstance(resp, list), f"Expected list, got {type(resp)}"
    assert len(resp) > 0, f"Should have at least 1 ticker, got {len(resp)}"
    assert all("symbol" in ticker for ticker in resp), "All tickers should have 'symbol' key"


def test_example_ticker_book_price_all_symbols():
    """Test ticker_book_price without symbol (all symbols)"""
    resp = public_http.ticker_book_price()
    if PRINT_RESPONSE:
        print(f"Ticker book price (all symbols): {len(resp)} symbols")
    assert isinstance(resp, list), f"Expected list, got {type(resp)}"
    assert len(resp) > 0, f"Should have at least 1 ticker, got {len(resp)}"
    assert all("symbol" in ticker for ticker in resp), "All tickers should have 'symbol' key"


def test_example_klines_with_time_range():
    """Test klines with time range"""
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(hours=2)).timestamp() * 1000)

    # Use valid interval format
    klines = public_http.klines(symbol="BTCUSDT", interval="5m", start_time=start_time, end_time=end_time, limit=100)

    if PRINT_RESPONSE:
        print(f"Klines with time range: {len(klines)} candles")
        if len(klines) > 0:
            print(f"First kline time: {klines[0][0]}, Last kline time: {klines[-1][0]}")

    assert isinstance(klines, list), f"Expected list, got {type(klines)}"
    assert len(klines) > 0, f"Should have at least 1 kline, got {len(klines)}"
    assert len(klines) <= 100, f"Should have <= 100 klines, got {len(klines)}"

    # Verify time range
    if len(klines) > 0:
        first_time = klines[0][0]
        last_time = klines[-1][0]
        assert start_time <= first_time <= end_time, (
            f"First kline time {first_time} not in range [{start_time}, {end_time}]"
        )
        assert start_time <= last_time <= end_time, (
            f"Last kline time {last_time} not in range [{start_time}, {end_time}]"
        )


def test_example_agg_trades_with_time_range():
    """Test agg_trades with time range"""
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(hours=1)).timestamp() * 1000)

    trades = public_http.agg_trades(symbol="BTCUSDT", start_time=start_time, end_time=end_time, limit=100)

    if PRINT_RESPONSE:
        print(f"Agg trades with time range: {len(trades)} trades")
        if len(trades) > 0:
            print(f"First trade: {trades[0]}")

    assert isinstance(trades, list), f"Expected list, got {type(trades)}"
    assert len(trades) <= 100, f"Should have <= 100 trades, got {len(trades)}"

    # Check trade structure
    for trade in trades:
        assert "p" in trade, f"Missing 'p' (price) key. Keys: {trade.keys()}"
        assert "q" in trade, f"Missing 'q' (quantity) key. Keys: {trade.keys()}"
        assert "T" in trade, f"Missing 'T' (timestamp) key. Keys: {trade.keys()}"
        assert start_time <= trade["T"] <= end_time, (
            f"Trade timestamp {trade['T']} not in range [{start_time}, {end_time}]"
        )


# ============================================================================
# WebSocket examples tests
# ============================================================================


def test_example_websocket_price_monitoring():
    """Test example: Real-time Price Monitoring with WebSocket"""
    if not api_key or not api_secret:
        pytest.skip("API credentials not provided")

    from pymexc.spot import WebSocket
    from pymexc.proto import PublicMiniTickerV3Api
    import threading

    messages_received = []
    done = threading.Event()

    def handle_price_update(message):
        """Handle real-time price updates"""
        messages_received.append(message)
        if PRINT_RESPONSE:
            print(f"Received price update: {message}")
        # WebSocket uses protobuf by default, so message is a protobuf object
        if isinstance(message, PublicMiniTickerV3Api):
            symbol = message.symbol if hasattr(message, "symbol") else "N/A"
            price = message.price if hasattr(message, "price") else "N/A"
            volume = message.volume if hasattr(message, "volume") else "N/A"
            assert symbol == "BTCUSDT" or symbol == "N/A", f"Unexpected symbol: {symbol}"
            if price != "N/A" and price:
                assert float(price) > 0, f"Price should be positive, got {price}"
        elif isinstance(message, dict) and "d" in message:
            # Fallback for JSON format
            data = message["d"]
            symbol = data.get("symbol", "N/A")
            price = data.get("p", "N/A")
            volume = data.get("v", "N/A")
            assert symbol == "BTCUSDT" or symbol == "N/A", f"Unexpected symbol: {symbol}"
            if price != "N/A":
                assert float(price) > 0, f"Price should be positive, got {price}"
        if len(messages_received) >= 2:
            done.set()

    ws_client = WebSocket(api_key=api_key, api_secret=api_secret)

    try:
        # Subscribe to ticker updates
        ws_client.mini_ticker_stream(handle_price_update, "BTCUSDT")
        time.sleep(1)  # Give WebSocket time to connect

        # Wait for messages with longer timeout
        if not done.wait(timeout=20):
            if PRINT_RESPONSE:
                print(f"Received {len(messages_received)} messages, expected at least 2")
            # WebSocket may not always send messages immediately, so we check if we got at least 1
            assert len(messages_received) >= 1, (
                f"Did not receive enough WebSocket messages. Got {len(messages_received)}, expected at least 1"
            )
        else:
            assert len(messages_received) >= 2, f"Expected at least 2 messages, got {len(messages_received)}"
    finally:
        ws_client.exit()
        time.sleep(1)


def test_example_websocket_order_book_depth():
    """Test example: Monitoring Order Book Depth"""
    if not api_key or not api_secret:
        pytest.skip("API credentials not provided")

    from pymexc.spot import WebSocket
    from pymexc.proto import PublicAggreDepthsV3Api
    import threading

    messages_received = []
    done = threading.Event()

    def handle_depth_update(message):
        """Handle order book depth updates"""
        messages_received.append(message)
        if PRINT_RESPONSE:
            print(f"Received depth update: {message}")
        # WebSocket uses protobuf by default, so message is a protobuf object
        if isinstance(message, PublicAggreDepthsV3Api):
            bids = list(message.bids) if hasattr(message, "bids") else []
            asks = list(message.asks) if hasattr(message, "asks") else []
            if bids and asks:
                best_bid_price = float(bids[0].price) if bids and hasattr(bids[0], "price") else None
                best_ask_price = float(asks[0].price) if asks and hasattr(asks[0], "price") else None
                if best_bid_price and best_ask_price:
                    spread = best_ask_price - best_bid_price
                    assert spread >= 0, f"Spread should be >= 0, got {spread}"
        elif isinstance(message, dict) and "d" in message:
            # Fallback for JSON format
            data = message["d"]
            symbol = data.get("symbol", "N/A")
            bids = data.get("bids", [])
            asks = data.get("asks", [])

            assert symbol == "BTCUSDT" or symbol == "N/A", f"Unexpected symbol: {symbol}"
            if bids and asks:
                best_bid = bids[0][0] if bids else "N/A"
                best_ask = asks[0][0] if asks else "N/A"
                if best_bid != "N/A" and best_ask != "N/A":
                    spread = float(best_ask) - float(best_bid)
                    assert spread >= 0, f"Spread should be >= 0, got {spread}"
        if len(messages_received) >= 2:
            done.set()

    ws_client = WebSocket(api_key=api_key, api_secret=api_secret)

    try:
        # Subscribe to depth updates
        ws_client.depth_stream(handle_depth_update, "BTCUSDT", interval="100ms")
        time.sleep(1)  # Give WebSocket time to connect

        # Wait for messages with longer timeout
        if not done.wait(timeout=20):
            if PRINT_RESPONSE:
                print(f"Received {len(messages_received)} messages, expected at least 2")
            # WebSocket may not always send messages immediately, so we check if we got at least 1
            assert len(messages_received) >= 1, (
                f"Did not receive enough WebSocket messages. Got {len(messages_received)}, expected at least 1"
            )
        else:
            assert len(messages_received) >= 2, f"Expected at least 2 messages, got {len(messages_received)}"
    finally:
        ws_client.exit()
        time.sleep(1)


def test_example_websocket_account_updates():
    """Test example: WebSocket: Monitoring Account Updates"""
    if not api_key or not api_secret:
        pytest.skip("API credentials not provided")

    from pymexc.spot import WebSocket
    from pymexc.proto import PrivateAccountV3Api, PrivateOrdersV3Api
    import threading

    account_messages = []
    order_messages = []
    account_done = threading.Event()
    order_done = threading.Event()

    def handle_account_update(message):
        """Handle account balance updates"""
        account_messages.append(message)
        if PRINT_RESPONSE:
            print(f"Received account update: {message}")
        # WebSocket uses protobuf by default, so message is a protobuf object
        if isinstance(message, PrivateAccountV3Api):
            # PrivateAccountV3Api has fields: vcoinName, coinId, balanceAmount, frozenAmount, etc.
            assert hasattr(message, "vcoinName") or hasattr(message, "coinId"), (
                f"Account update should have vcoinName or coinId. Message: {message}"
            )
            if hasattr(message, "balanceAmount"):
                balance = float(message.balanceAmount) if message.balanceAmount else 0
                assert balance >= 0, f"Balance should be >= 0, got {balance}"
            if hasattr(message, "frozenAmount"):
                frozen = float(message.frozenAmount) if message.frozenAmount else 0
                assert frozen >= 0, f"Frozen amount should be >= 0, got {frozen}"
            if len(account_messages) >= 1:
                account_done.set()
        elif isinstance(message, dict) and "d" in message:
            # Fallback for JSON format
            data = message["d"]
            balances = data.get("B", [])
            for balance in balances:
                asset = balance.get("a", "")
                free = balance.get("f", "0")
                locked = balance.get("l", "0")
                assert isinstance(asset, str), f"Asset should be str, got {type(asset)}"
                assert float(free) >= 0, f"Free balance should be >= 0, got {free}"
                assert float(locked) >= 0, f"Locked balance should be >= 0, got {locked}"
            if len(account_messages) >= 1:
                account_done.set()

    def handle_order_update(message):
        """Handle order status updates"""
        order_messages.append(message)
        if PRINT_RESPONSE:
            print(f"Received order update: {message}")
        # WebSocket uses protobuf by default, so message is a protobuf object
        if isinstance(message, PrivateOrdersV3Api):
            # PrivateOrdersV3Api has fields: id, clientId, price, quantity, amount, etc.
            assert hasattr(message, "id"), f"Order should have 'id' field. Message: {message}"
            if hasattr(message, "price") and message.price:
                assert float(message.price) >= 0, f"Price should be >= 0, got {message.price}"
            if hasattr(message, "quantity") and message.quantity:
                assert float(message.quantity) >= 0, f"Quantity should be >= 0, got {message.quantity}"
            if len(order_messages) >= 1:
                order_done.set()
        elif isinstance(message, dict) and "d" in message:
            # Fallback for JSON format
            order = message["d"]
            assert "s" in order or "S" in order, f"Order should have 's' or 'S' key. Keys: {order.keys()}"
            if len(order_messages) >= 1:
                order_done.set()

    ws_client = WebSocket(api_key=api_key, api_secret=api_secret)

    try:
        # Subscribe to account updates
        ws_client.account_update(handle_account_update)

        # Subscribe to order updates
        ws_client.account_orders(handle_order_update)

        time.sleep(2)  # Give WebSocket time to connect and receive initial updates

        # Trigger an order to test order updates
        try:
            # Create a test order
            test_order = http.order(symbol="MXUSDT", side="BUY", order_type="LIMIT", quantity=20, price=0.1)
            if PRINT_RESPONSE:
                print(f"Created test order: {test_order}")
            time.sleep(3)

            # Cancel the order
            cancel_result = http.cancel_order("MXUSDT", order_id=test_order["orderId"])
            if PRINT_RESPONSE:
                print(f"Canceled order: {cancel_result}")
            time.sleep(3)
        except pymexc.base.MexcAPIError as e:
            if PRINT_RESPONSE:
                print(f"Error creating/canceling order (may be expected): {e}")
            # Continue test even if order creation fails

        # Wait for account update
        if not account_done.wait(timeout=15):
            if PRINT_RESPONSE:
                print("Account update not received within timeout")

        # Wait for order update
        if not order_done.wait(timeout=15):
            if PRINT_RESPONSE:
                print("Order update not received within timeout")

        # At least one type of message should be received (initial connection may send updates)
        if PRINT_RESPONSE:
            print(f"Account messages: {len(account_messages)}, Order messages: {len(order_messages)}")
        # WebSocket may send initial account snapshot, so we check for any messages
        assert len(account_messages) > 0 or len(order_messages) > 0, (
            f"Expected at least one message. Got account: {len(account_messages)}, orders: {len(order_messages)}"
        )
    finally:
        ws_client.exit()
        time.sleep(1)
