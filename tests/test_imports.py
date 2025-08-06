#!/usr/bin/env python3
"""
Тестовый файл для проверки импортов pymexc
"""

print("Тестирование импортов...")

try:
    # Основной импорт
    import pymexc

    print("✓ pymexc импортирован успешно")

    # Импорт модулей
    from pymexc import spot, futures, _async

    print("✓ spot, futures, _async импортированы успешно")

    # Импорт классов
    from pymexc import SpotHTTP, SpotWebSocket, FuturesHTTP, FuturesWebSocket

    print("✓ HTTP и WebSocket классы импортированы успешно")

    # Импорт async классов
    from pymexc import AsyncSpotHTTP, AsyncSpotWebSocket, AsyncFuturesHTTP, AsyncFuturesWebSocket

    print("✓ Async HTTP и WebSocket классы импортированы успешно")

    print("\n🎉 Все импорты работают корректно!")

except Exception as e:
    print(f"❌ Ошибка импорта: {e}")
    import traceback

    traceback.print_exc()
