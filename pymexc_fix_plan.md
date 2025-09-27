# Comprehensive pymexc Library Fix Plan
*Created: 2025-09-27 10:46*

## Goal
Simplify pymexc to enable cleaner, more maintainable code by fixing critical issues in our forked library.

## Priority 1: Critical Fixes (Prevents Crashes)

### 1. Fix blocking operations in async code
- **Problem**: `time.sleep(59 * 60)` blocks entire thread for 59 minutes
- **Location**: `_async/spot.py:_keep_alive_loop()` line 2040
- **Fix**: Replace with `await asyncio.sleep(3540)`
- **Impact**: Prevents async event loop blocking

### 2. Remove threading from async code
- **Problem**: Mixing threading with asyncio causes complexity and potential deadlocks
- **Location**: `spot.py` line 2012 - `threading.Thread(target=lambda: self._keep_alive_loop())`
- **Fix**: Use `asyncio.create_task()` instead of threading
- **Impact**: Cleaner async architecture

## Priority 2: Resource Management (Prevents Memory Leaks)

### 3. Add context manager support
- **Add to WebSocket classes**:
  ```python
  async def __aenter__(self):
      await self.connect()
      return self

  async def __aexit__(self, exc_type, exc_val, exc_tb):
      await self.cleanup_all()
      return False
  ```
- **Files**: `_async/base_websocket.py`, `_async/spot.py`, `_async/futures.py`
- **Impact**: Guaranteed resource cleanup

### 4. Add bulk cleanup operations
- **Add methods**:
  - `async def unsubscribe_all()` - Unsubscribe from all topics at once
  - `async def close_all()` - Close all connections and cleanup
  - Track subscriptions in `self._active_subscriptions = set()`
- **Impact**: Prevents memory leaks from forgotten subscriptions

### 5. Fix subscription tracking
- **Current**: Subscriptions stored in list with inefficient removal
- **Fix**: Use set for O(1) operations
- **Add**: Max subscription limit with automatic cleanup of oldest
- **Impact**: Better memory management

## Priority 3: Simple API Improvements (Minimal Changes)

### 6. Fix confusing defaults
- **Make `proto=True` default** for WebSocket initialization
- **Auto-handle speed parameter** for aggregated streams
- **Better error messages** when proto is missing
- **Impact**: Fewer silent failures

## Priority 4: Documentation

### 7. Update documentation
- Document the context manager usage
- Add examples of proper cleanup
- Explain proto requirement clearly

## Implementation Order

| Step | Task | Time Estimate | Files |
|------|------|--------------|-------|
| 1 | Fix blocking sleep operations | 30 min | `_async/spot.py`, `spot.py` |
| 2 | Remove threading from async | 30 min | `_async/spot.py` |
| 3 | Add context manager support | 1 hour | `_async/base_websocket.py` |
| 4 | Add bulk cleanup methods | 45 min | `_async/base_websocket.py` |
| 5 | Fix subscription tracking | 30 min | `_async/base_websocket.py` |
| 6 | Update defaults | 15 min | `_async/spot.py`, `_async/futures.py` |
| 7 | Test all changes | 1 hour | Create test file |

**Total estimated time**: ~4 hours

## Expected Results

| Metric | Before | After |
|--------|--------|-------|
| Wrapper code needed | 600+ lines | ~50 lines |
| Memory leaks | Common | Eliminated |
| Race conditions | Multiple | None |
| Blocking operations | Yes | No |
| Resource cleanup | Manual | Automatic |
| Code complexity | High | Low (-70%) |

## Sample Usage After Fixes

```python
# Before: Complex wrapper needed
async with WebSocketSession(api_key, api_secret) as session:
    await session.orderbook_manager.subscribe_spot_orderbook("BTCUSDT")
    # Complex cleanup handled by wrapper

# After: Direct usage
async with spot.WebSocket(api_key, api_secret) as ws:
    await ws.depth_stream(callback, "BTCUSDT")
    # Automatic cleanup on exit
```

## Files to Modify

1. `/pymexc/_async/base_websocket.py` - Core async WebSocket logic
2. `/pymexc/_async/spot.py` - Spot WebSocket implementation
3. `/pymexc/_async/futures.py` - Futures WebSocket implementation
4. `/pymexc/spot.py` - Sync spot (fix threading)
5. `/pymexc/base_websocket.py` - Already fixed exit() method

## Success Criteria

- [ ] No blocking operations in async code
- [ ] Context manager support works properly
- [ ] All resources cleaned up on exit
- [ ] No memory leaks in long-running tests
- [ ] WebSocketSession wrapper can be removed/simplified
- [ ] Direct pymexc usage is safe and clean

## Notes

- These are minimal, focused changes to fix critical issues
- No major refactoring or API redesign
- Maintains backward compatibility
- Focus on "do the simplest thing that works" per CLAUDE.md