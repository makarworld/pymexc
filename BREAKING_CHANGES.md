# Breaking Changes

## Version: PR #3 Fix (2025-09-27)

### Changed Default for `proto` Parameter

The default value for the `proto` parameter in WebSocket classes has been changed from `False` to `True`.

**Before:**
```python
ws = SpotWebSocket(api_key="key", api_secret="secret")  # proto=False by default
```

**After:**
```python
ws = SpotWebSocket(api_key="key", api_secret="secret")  # proto=True by default
```

**Impact:**
- If you were explicitly setting `proto=True`, no changes needed
- If you were relying on the default `proto=False`, you must now explicitly set it:
  ```python
  ws = SpotWebSocket(api_key="key", api_secret="secret", proto=False)
  ```

**Reason for Change:**
The protobuf protocol (`proto=True`) provides better performance and is the recommended way to use MEXC WebSocket API. Making it the default reduces configuration errors and improves out-of-the-box performance.

### Context Manager Support Added (Optional)

WebSocket classes now support async context manager protocol for automatic resource cleanup. **This is optional** - you can still use the classes directly.

**Option 1: Direct Usage (traditional)**
```python
ws = SpotWebSocket(api_key="key", api_secret="secret")
await ws.connect()
await ws.depth_stream(callback, "BTCUSDT")
# Manual cleanup when done
await ws.close_all()
```

**Option 2: Context Manager (automatic cleanup)**
```python
async with SpotWebSocket(api_key="key", api_secret="secret") as ws:
    await ws.depth_stream(callback, "BTCUSDT")
    # WebSocket automatically cleaned up on exit
```

This is not a breaking change but a new **optional** feature that ensures proper resource management when used.

### Migration Guide

1. **If you use proto=False:** Add explicit `proto=False` to your WebSocket initialization
2. **For better resource management:** Consider using the new context manager pattern
3. **No other code changes required** - All other APIs remain backward compatible