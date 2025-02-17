import logging
from typing import List, Literal, Optional

logger = logging.getLogger(__name__)

try:
    from base import _WebHTTP
except ImportError:
    from ..base import _WebHTTP

__all__ = ["HTTP"]

class HTTP(_WebHTTP):
    # <=================================================================>
    #
    #                          Market Endpoints
    #
    # <=================================================================>

    def ping(self) -> dict:
        return self.call("GET", "api/v1/contract/ping")

    def detail(self, symbol: Optional[str] = None) -> dict:
        return self.call("GET", "api/v1/contract/detail", params=dict(symbol=symbol))

    def detailV2(self, symbol: Optional[str] = None) -> dict:
        return self.call("GET", "api/v1/contract/detailV2", params=dict(symbol=symbol))

    def support_currencies(self) -> dict:
        return self.call("GET", "api/v1/contract/support_currencies")

    def get_depth(self, symbol: str, limit: Optional[int] = None) -> dict:
        return self.call(
            "GET", f"api/v1/contract/depth/{symbol}", params=dict(limit=limit)
        )

    def depth_commits(self, symbol: str, limit: int) -> dict:
        return self.call("GET", f"api/v1/contract/depth_commits/{symbol}/{limit}")

    def index_price(self, symbol: str) -> dict:
        return self.call("GET", f"api/v1/contract/index_price/{symbol}")

    def fair_price(self, symbol: str) -> dict:
        return self.call("GET", f"api/v1/contract/fair_price/{symbol}")

    def funding_rate(self, symbol: str) -> dict:
        return self.call("GET", f"api/v1/contract/funding_rate/{symbol}")

    def kline(
        self,
        symbol: str,
        interval: Optional[
            Literal[
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
        ] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
    ) -> dict:
        return self.call(
            "GET",
            f"api/v1/contract/kline/{symbol}",
            params=dict(symbol=symbol, interval=interval, start=start, end=end),
        )

    def kline_index_price(
        self,
        symbol: str,
        interval: Optional[
            Literal[
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
        ] = "Min1",
        start: Optional[int] = None,
        end: Optional[int] = None,
    ) -> dict:
        return self.call(
            "GET",
            f"api/v1/contract/kline/index_price/{symbol}",
            params=dict(symbol=symbol, interval=interval, start=start, end=end),
        )

    def kline_fair_price(
        self,
        symbol: str,
        interval: Optional[
            Literal[
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
        ] = "Min1",
        start: Optional[int] = None,
        end: Optional[int] = None,
    ) -> dict:
        return self.call(
            "GET",
            f"api/v1/contract/kline/fair_price/{symbol}",
            params=dict(symbol=symbol, interval=interval, start=start, end=end),
        )

    def deals(self, symbol: str, limit: Optional[int] = 100) -> dict:
        return self.call(
            "GET",
            f"api/v1/contract/deals/{symbol}",
            params=dict(symbol=symbol, limit=limit),
        )

    def ticker(self, symbol: Optional[str] = None) -> dict:
        return self.call("GET", "api/v1/contract/ticker", params=dict(symbol=symbol))

    def risk_reverse(self) -> dict:
        return self.call("GET", "api/v1/contract/risk_reverse")

    def risk_reverse_history(
        self, symbol: str, page_num: Optional[int] = 1, page_size: Optional[int] = 20
    ) -> dict:
        return self.call(
            "GET",
            "api/v1/contract/risk_reverse/history",
            params=dict(symbol=symbol, page_num=page_num, page_size=page_size),
        )

    def funding_rate_history(
        self, symbol: str, page_num: Optional[int] = 1, page_size: Optional[int] = 20
    ) -> dict:
        return self.call(
            "GET",
            "api/v1/contract/funding_rate/history",
            params=dict(symbol=symbol, page_num=page_num, page_size=page_size),
        )

    # <=================================================================>
    #
    #                   Account and trading endpoints
    #
    # <=================================================================>

    def assets(self) -> dict:
        return self.call("GET", "api/v1/private/account/assets")

    def asset(self, currency: str) -> dict:
        return self.call("GET", f"api/v1/private/account/asset/{currency}")

    def transfer_record(
        self,
        currency: Optional[str] = None,
        state: Literal["WAIT", "SUCCESS", "FAILED"] = None,
        type: Literal["IN", "OUT"] = None,
        page_num: Optional[int] = 1,
        page_size: Optional[int] = 20,
    ) -> dict:
        return self.call(
            "GET",
            "api/v1/private/account/transfer_record",
            params=dict(
                currency=currency,
                state=state,
                type=type,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    def history_positions(
        self,
        symbol: Optional[str] = None,
        type: Optional[int] = None,
        page_num: Optional[int] = 1,
        page_size: Optional[int] = 20,
    ) -> dict:
        return self.call(
            "GET",
            "api/v1/private/position/list/history_positions",
            params=dict(
                symbol=symbol, type=type, page_num=page_num, page_size=page_size
            ),
        )

    def open_positions(self, symbol: Optional[str] = None) -> dict:
        return self.call(
            "GET", "api/v1/private/position/open_positions", params=dict(symbol=symbol)
        )

    def funding_records(
        self,
        symbol: Optional[str] = None,
        position_id: Optional[int] = None,
        page_num: Optional[int] = 1,
        page_size: Optional[int] = 20,
    ) -> dict:
        return self.call(
            "GET",
            "api/v1/private/position/funding_records",
            params=dict(
                symbol=symbol,
                position_id=position_id,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    def open_orders(
        self,
        symbol: Optional[str] = None,
        page_num: Optional[int] = None,
        page_size: Optional[int] = 200,
    ) -> dict:
        return self.call(
            "GET",
            "/api/v1/private/order/list/open_orders" + (f"/{symbol}" if symbol else ""),
            params=dict(page_num=page_num, page_size=page_size),
        )

    def history_orders(
        self,
        symbol: Optional[str] = None,
        states: Optional[str] = None,
        category: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        side: Optional[int] = None,
        page_num: Optional[int] = 1,
        page_size: Optional[int] = 20,
    ) -> dict:
        return self.call(
            "GET",
            "api/v1/private/order/history_orders",
            params=dict(
                symbol=symbol,
                states=states,
                category=category,
                start_time=start_time,
                end_time=end_time,
                side=side,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    def get_order_external(self, symbol: str, external_oid: int) -> dict:
        return self.call(
            "GET", f"api/v1/private/order/external/{symbol}/{external_oid}"
        )

    def get_order(self, order_id: int) -> dict:
        return self.call("GET", f"api/v1/private/order/{order_id}")

    def batch_query(self, order_ids: List[int]) -> dict:
        return self.call(
            "GET",
            "api/v1/private/order/batch_query",
            params=dict(
                order_ids=",".join(order_ids)
                if isinstance(order_ids, list)
                else order_ids
            ),
        )

    def deal_details(self, order_id: int) -> dict:
        return self.call("GET", f"api/v1/private/order/deal_details/{order_id}")

    def order_deals(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page_num: Optional[int] = 1,
        page_size: Optional[int] = 20,
    ) -> dict:
        return self.call(
            "GET",
            "api/v1/private/order/list/order_deals",
            params=dict(
                symbol=symbol,
                start_time=start_time,
                end_time=end_time,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    def get_trigger_orders(
        self,
        symbol: Optional[str] = None,
        states: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict:
        return self.call(
            "GET",
            "api/v1/private/planorder/list/orders",
            params=dict(
                symbol=symbol,
                states=states,
                start_time=start_time,
                end_time=end_time,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    def get_stop_limit_orders(
        self,
        symbol: Optional[str] = None,
        is_finished: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict:
        return self.call(
            "GET",
            "api/v1/private/stoporder/list/orders",
            params=dict(
                symbol=symbol,
                is_finished=is_finished,
                start_time=start_time,
                end_time=end_time,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    def risk_limit(self, symbol: Optional[str] = None) -> dict:
        return self.call(
            "GET", "api/v1/private/account/risk_limit", params=dict(symbol=symbol)
        )

    def tiered_fee_rate(self, symbol: Optional[str] = None) -> dict:
        return self.call(
            "GET", "api/v1/private/account/tiered_fee_rate", params=dict(symbol=symbol)
        )
