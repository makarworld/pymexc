from __future__ import annotations
from typing import Any, Literal, Optional, Self, TypeAlias, Union, cast
from typing import Type, TypeVar


import pymexc.proto.PublicDealsV3Api_pb2 as PublicDealsV3Api__pb2
import pymexc.proto.PublicIncreaseDepthsV3Api_pb2 as PublicIncreaseDepthsV3Api__pb2
import pymexc.proto.PublicLimitDepthsV3Api_pb2 as PublicLimitDepthsV3Api__pb2
import pymexc.proto.PrivateOrdersV3Api_pb2 as PrivateOrdersV3Api__pb2
import pymexc.proto.PublicBookTickerV3Api_pb2 as PublicBookTickerV3Api__pb2
import pymexc.proto.PrivateDealsV3Api_pb2 as PrivateDealsV3Api__pb2
import pymexc.proto.PrivateAccountV3Api_pb2 as PrivateAccountV3Api__pb2
import pymexc.proto.PublicSpotKlineV3Api_pb2 as PublicSpotKlineV3Api__pb2
import pymexc.proto.PublicMiniTickerV3Api_pb2 as PublicMiniTickerV3Api__pb2
import pymexc.proto.PublicMiniTickersV3Api_pb2 as PublicMiniTickersV3Api__pb2
import pymexc.proto.PublicBookTickerBatchV3Api_pb2 as PublicBookTickerBatchV3Api__pb2
import pymexc.proto.PublicIncreaseDepthsBatchV3Api_pb2 as PublicIncreaseDepthsBatchV3Api__pb2
import pymexc.proto.PublicAggreDepthsV3Api_pb2 as PublicAggreDepthsV3Api__pb2
import pymexc.proto.PublicAggreDealsV3Api_pb2 as PublicAggreDealsV3Api__pb2
import pymexc.proto.PublicAggreBookTickerV3Api_pb2 as PublicAggreBookTickerV3Api__pb2
import pymexc.proto.PushDataV3ApiWrapper_pb2 as PushDataV3ApiWrapper__pb2


class ProtoTyping:
    class protoc:
        def __call__(self, *args: Any, **kwds: Any) -> Self: ...
        def ParseFromString(self, data: bytes) -> Self: ...

    # PublicDealsV3Api__pb2

    class PublicDealsV3ApiItem:
        price: str
        quantity: str
        tradeType: int
        time: int

    class PublicDealsV3Api(protoc):
        deals: list[ProtoTyping.PublicDealsV3ApiItem]
        eventType: str

    # PublicIncreaseDepthsV3Api__pb2

    class PublicIncreaseDepthV3ApiItem(protoc):
        price: str
        quantity: str

    class PublicIncreaseDepthsV3Api(protoc):
        asks: list[ProtoTyping.PublicIncreaseDepthV3ApiItem]
        bids: list[ProtoTyping.PublicIncreaseDepthV3ApiItem]
        eventType: str
        version: str

    # PublicLimitDepthsV3Api__pb2

    class PublicLimitDepthV3ApiItem(protoc):
        price: str
        quantity: str

    class PublicLimitDepthsV3Api(protoc):
        asks: list[ProtoTyping.PublicLimitDepthV3ApiItem]
        bids: list[ProtoTyping.PublicLimitDepthV3ApiItem]
        eventType: str
        version: str

    # PrivateOrdersV3Api__pb2

    class PrivateOrdersV3Api(protoc):
        id: str
        clientId: str
        price: str
        quantity: str
        amount: str
        avgPrice: str
        orderType: int
        tradeType: int
        isMaker: bool
        remainAmount: str
        remainQuantity: str
        lastDealQuantity: Optional[str]
        cumulativeQuantity: str
        cumulativeAmount: str
        status: int
        createTime: int
        market: Optional[str]
        triggerType: Optional[int]
        triggerPrice: Optional[str]
        state: Optional[int]
        ocoId: Optional[str]
        routeFactor: Optional[str]
        symbolId: Optional[str]
        marketId: Optional[str]
        marketCurrencyId: Optional[str]
        currencyId: Optional[str]

    # PublicBookTickerV3Api__pb2

    class PublicBookTickerV3Api(protoc):
        bidPrice: str
        bidQuantity: str
        askPrice: str
        askQuantity: str

    # PrivateDealsV3Api__pb2

    class PrivateDealsV3Api(protoc):
        price: str
        quantity: str
        amount: str
        tradeType: int
        isMaker: bool
        isSelfTrade: bool
        tradeId: str
        clientOrderId: str
        orderId: str
        feeAmount: str
        feeCurrency: str
        time: int

    # PrivateAccountV3Api__pb2

    class PrivateAccountV3Api(protoc):
        vcoinName: str
        coinId: str
        balanceAmount: str
        balanceAmountChange: str
        frozenAmount: str
        frozenAmountChange: str
        type: str
        time: int

    # PublicSpotKlineV3Api__pb2

    class PublicSpotKlineV3Api(protoc):
        interval: Literal[
            "Min1",
            "Min5",
            "Min15",
            "Min30",
            "Min60",
            "Hour4",
            "Hour8",
            "Day1",
            "Week1",
            "Month1",
        ]
        windowStart: int
        openingPrice: str
        closingPrice: str
        highestPrice: str
        lowestPrice: str
        volume: str
        amount: str
        windowEnd: int

    # PublicMiniTickerV3Api__pb2

    class PublicMiniTickerV3Api(protoc):
        symbol: str
        price: str
        rate: str
        zonedRate: str
        high: str
        low: str
        volume: str
        quantity: str
        lastCloseRate: str
        lastCloseZonedRate: str
        lastCloseHigh: str
        lastCloseLow: str

    # PublicMiniTickersV3Api__pb2

    class PublicMiniTickersV3Api(protoc):
        items: list[ProtoTyping.PublicMiniTickerV3Api]

    # PublicBookTickerBatchV3Api__pb2

    class PublicBookTickerBatchV3Api(protoc):
        items: list[ProtoTyping.PublicBookTickerV3Api]

    # PublicIncreaseDepthsBatchV3Api__pb2

    class PublicIncreaseDepthsBatchV3Api(protoc):
        items: list[ProtoTyping.PublicIncreaseDepthsV3Api]
        eventType: str

    # PublicAggreDepthsV3Api__pb2

    class PublicAggreDepthV3ApiItem(protoc):
        price: str
        quantity: str

    class PublicAggreDepthsV3Api(protoc):
        asks: list[ProtoTyping.PublicAggreDepthV3ApiItem]
        bids: list[ProtoTyping.PublicAggreDepthV3ApiItem]
        eventType: str
        fromVersion: str
        toVersion: str

    # PublicAggreDealsV3Api__pb2

    class PublicAggreDealsV3ApiItem(protoc):
        price: str
        quantity: str
        tradeType: int
        time: int

    class PublicAggreDealsV3Api(protoc):
        deals: list[ProtoTyping.PublicAggreDealsV3ApiItem]
        eventType: str

    # PublicAggreBookTickerV3Api__pb2

    class PublicAggreBookTickerV3Api(protoc):
        bidPrice: str
        bidQuantity: str
        askPrice: str
        askQuantity: str

    class PushDataV3ApiWrapper(protoc):
        channel: str

        publicDeals: ProtoTyping.PublicDealsV3Api
        publicIncreaseDepths: ProtoTyping.PublicIncreaseDepthsV3Api
        publicLimitDepths: ProtoTyping.PublicLimitDepthsV3Api
        privateOrders: ProtoTyping.PrivateOrdersV3Api
        publicBookTicker: ProtoTyping.PublicBookTickerV3Api
        privateDeals: ProtoTyping.PrivateDealsV3Api
        privateAccount: ProtoTyping.PrivateAccountV3Api
        publicSpotKline: ProtoTyping.PublicSpotKlineV3Api
        publicMiniTicker: ProtoTyping.PublicMiniTickerV3Api
        publicMiniTickers: ProtoTyping.PublicMiniTickersV3Api
        publicBookTickerBatch: ProtoTyping.PublicBookTickerBatchV3Api
        publicIncreaseDepthsBatch: ProtoTyping.PublicIncreaseDepthsBatchV3Api
        publicAggreDepths: ProtoTyping.PublicAggreDepthsV3Api
        publicAggreDeals: ProtoTyping.PublicAggreDealsV3Api
        publicAggreBookTicker: ProtoTyping.PublicAggreBookTickerV3Api

        symbol: Optional[str]
        symbolId: Optional[str]
        createTime: Optional[int]
        sendTime: Optional[int]


PublicSpotKlineV3ApiClass: TypeAlias = "type[ProtoTyping.PublicSpotKlineV3Api]"
PublicSpotKlineV3Api = cast(PublicSpotKlineV3ApiClass, PublicSpotKlineV3Api__pb2.PublicSpotKlineV3Api)
PublicDealsV3ApiClass: TypeAlias = "type[ProtoTyping.PublicDealsV3Api]"
PublicDealsV3Api = cast(PublicDealsV3ApiClass, PublicDealsV3Api__pb2.PublicDealsV3Api)
PublicIncreaseDepthV3ApiItemClass: TypeAlias = "type[ProtoTyping.PublicIncreaseDepthV3ApiItem]"
PublicIncreaseDepthV3ApiItem = cast(
    PublicIncreaseDepthV3ApiItemClass, PublicIncreaseDepthsV3Api__pb2.PublicIncreaseDepthV3ApiItem
)
PublicIncreaseDepthsV3ApiClass: TypeAlias = "type[ProtoTyping.PublicIncreaseDepthsV3Api]"
PublicIncreaseDepthsV3Api = cast(
    PublicIncreaseDepthsV3ApiClass, PublicIncreaseDepthsV3Api__pb2.PublicIncreaseDepthsV3Api
)
PublicLimitDepthV3ApiItemClass: TypeAlias = "type[ProtoTyping.PublicLimitDepthV3ApiItem]"
PublicLimitDepthV3ApiItem = cast(PublicLimitDepthV3ApiItemClass, PublicLimitDepthsV3Api__pb2.PublicLimitDepthV3ApiItem)
PublicLimitDepthsV3ApiClass: TypeAlias = "type[ProtoTyping.PublicLimitDepthsV3Api]"
PublicLimitDepthsV3Api = cast(PublicLimitDepthsV3ApiClass, PublicLimitDepthsV3Api__pb2.PublicLimitDepthsV3Api)
PrivateOrdersV3ApiClass: TypeAlias = "type[ProtoTyping.PrivateOrdersV3Api]"
PrivateOrdersV3Api = cast(PrivateOrdersV3ApiClass, PrivateOrdersV3Api__pb2.PrivateOrdersV3Api)
PublicBookTickerV3ApiClass: TypeAlias = "type[ProtoTyping.PublicBookTickerV3Api]"
PublicBookTickerV3Api = cast(PublicBookTickerV3ApiClass, PublicBookTickerV3Api__pb2.PublicBookTickerV3Api)
PrivateDealsV3ApiClass: TypeAlias = "type[ProtoTyping.PrivateDealsV3Api]"
PrivateDealsV3Api = cast(PrivateDealsV3ApiClass, PrivateDealsV3Api__pb2.PrivateDealsV3Api)
PrivateAccountV3ApiClass: TypeAlias = "type[ProtoTyping.PrivateAccountV3Api]"
PrivateAccountV3Api = cast(PrivateAccountV3ApiClass, PrivateAccountV3Api__pb2.PrivateAccountV3Api)
PublicMiniTickerV3ApiClass: TypeAlias = "type[ProtoTyping.PublicMiniTickerV3Api]"
PublicMiniTickerV3Api = cast(PublicMiniTickerV3ApiClass, PublicMiniTickerV3Api__pb2.PublicMiniTickerV3Api)
PublicMiniTickersV3ApiClass: TypeAlias = "type[ProtoTyping.PublicMiniTickersV3Api]"
PublicMiniTickersV3Api = cast(PublicMiniTickersV3ApiClass, PublicMiniTickersV3Api__pb2.PublicMiniTickersV3Api)
PublicBookTickerBatchV3ApiClass: TypeAlias = "type[ProtoTyping.PublicBookTickerBatchV3Api]"
PublicBookTickerBatchV3Api = cast(
    PublicBookTickerBatchV3ApiClass, PublicBookTickerBatchV3Api__pb2.PublicBookTickerBatchV3Api
)
PublicIncreaseDepthsBatchV3ApiClass: TypeAlias = "type[ProtoTyping.PublicIncreaseDepthsBatchV3Api]"
PublicIncreaseDepthsBatchV3Api = cast(
    PublicIncreaseDepthsBatchV3ApiClass, PublicIncreaseDepthsBatchV3Api__pb2.PublicIncreaseDepthsBatchV3Api
)
PublicAggreDepthsV3ApiClass: TypeAlias = "type[ProtoTyping.PublicAggreDepthsV3Api]"
PublicAggreDepthsV3Api = cast(PublicAggreDepthsV3ApiClass, PublicAggreDepthsV3Api__pb2.PublicAggreDepthsV3Api)
PublicAggreDealsV3ApiClass: TypeAlias = "type[ProtoTyping.PublicAggreDealsV3Api]"
PublicAggreDealsV3Api = cast(PublicAggreDealsV3ApiClass, PublicAggreDealsV3Api__pb2.PublicAggreDealsV3Api)
PublicAggreBookTickerV3ApiClass: TypeAlias = "type[ProtoTyping.PublicAggreBookTickerV3Api]"
PublicAggreBookTickerV3Api = cast(
    PublicAggreBookTickerV3ApiClass, PublicAggreBookTickerV3Api__pb2.PublicAggreBookTickerV3Api
)
PushDataV3ApiWrapperClass: TypeAlias = "type[ProtoTyping.PushDataV3ApiWrapper]"
PushDataV3ApiWrapper = cast(PushDataV3ApiWrapperClass, PushDataV3ApiWrapper__pb2.PushDataV3ApiWrapper)


__all__ = [
    "PublicSpotKlineV3Api",
    "PublicDealsV3Api",
    "PublicIncreaseDepthV3ApiItem",
    "PublicIncreaseDepthsV3Api",
    "PublicLimitDepthV3ApiItem",
    "PublicLimitDepthsV3Api",
    "PrivateOrdersV3Api",
    "PublicBookTickerV3Api",
    "PrivateDealsV3Api",
    "PrivateAccountV3Api",
    "PublicMiniTickerV3Api",
    "PublicMiniTickersV3Api",
    "PublicBookTickerBatchV3Api",
    "PublicIncreaseDepthsBatchV3Api",
    "PublicAggreDepthsV3Api",
    "PublicAggreDealsV3Api",
    "PublicAggreBookTickerV3Api",
    "PushDataV3ApiWrapper",
    "ProtoTyping",
]
