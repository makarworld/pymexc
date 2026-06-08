import logging
from typing import List, Literal, Optional, Union

logger = logging.getLogger(__name__)

try:
    from base import _WebHTTP
except ImportError:
    from ..base import _WebHTTP

__all__ = ["HTTP"]


class HTTP(_WebHTTP):
    async def ping(self) -> dict:
        return await self.call("GET", "api/v1/contract/ping")

    async def detail(self, symbol: Optional[str] = None) -> dict:
        return await self.call("GET", "api/v1/contract/detail", params=dict(symbol=symbol))

    async def detailV2(self, symbol: Optional[str] = None) -> dict:
        return await self.call("GET", "api/v1/contract/detailV2", params=dict(symbol=symbol))

    async def support_currencies(self) -> dict:
        return await self.call("GET", "api/v1/contract/support_currencies")

    async def get_depth(self, symbol: str, limit: Optional[int] = None) -> dict:
        return await self.call("GET", f"api/v1/contract/depth/{symbol}", params=dict(limit=limit))

    async def depth_commits(self, symbol: str, limit: int) -> dict:
        return await self.call("GET", f"api/v1/contract/depth_commits/{symbol}/{limit}")

    async def index_price(self, symbol: str) -> dict:
        return await self.call("GET", f"api/v1/contract/index_price/{symbol}")

    async def fair_price(self, symbol: str) -> dict:
        return await self.call("GET", f"api/v1/contract/fair_price/{symbol}")

    async def funding_rate(self, symbol: str) -> dict:
        return await self.call("GET", f"api/v1/contract/funding_rate/{symbol}")

    async def kline(
        self,
        symbol: str,
        interval: Optional[
            Literal["Min1", "Min5", "Min15", "Min30", "Min60", "Hour4", "Hour8", "Day1", "Week1", "Month1"]
        ] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
    ) -> dict:
        return await self.call(
            "GET",
            f"api/v1/contract/kline/{symbol}",
            params=dict(symbol=symbol, interval=interval, start=start, end=end),
        )

    async def kline_index_price(
        self,
        symbol: str,
        interval: Optional[
            Literal["Min1", "Min5", "Min15", "Min30", "Min60", "Hour4", "Hour8", "Day1", "Week1", "Month1"]
        ] = "Min1",
        start: Optional[int] = None,
        end: Optional[int] = None,
    ) -> dict:
        return await self.call(
            "GET",
            f"api/v1/contract/kline/index_price/{symbol}",
            params=dict(symbol=symbol, interval=interval, start=start, end=end),
        )

    async def kline_fair_price(
        self,
        symbol: str,
        interval: Optional[
            Literal["Min1", "Min5", "Min15", "Min30", "Min60", "Hour4", "Hour8", "Day1", "Week1", "Month1"]
        ] = "Min1",
        start: Optional[int] = None,
        end: Optional[int] = None,
    ) -> dict:
        return await self.call(
            "GET",
            f"api/v1/contract/kline/fair_price/{symbol}",
            params=dict(symbol=symbol, interval=interval, start=start, end=end),
        )

    async def deals(self, symbol: str, limit: Optional[int] = 100) -> dict:
        return await self.call("GET", f"api/v1/contract/deals/{symbol}", params=dict(symbol=symbol, limit=limit))

    async def ticker(self, symbol: Optional[str] = None) -> dict:
        return await self.call("GET", "api/v1/contract/ticker", params=dict(symbol=symbol))

    async def risk_reverse(self) -> dict:
        return await self.call("GET", "api/v1/contract/risk_reverse")

    async def risk_reverse_history(self, symbol: str, page_num: Optional[int] = 1, page_size: Optional[int] = 20) -> dict:
        return await self.call(
            "GET",
            "api/v1/contract/risk_reverse/history",
            params=dict(symbol=symbol, page_num=page_num, page_size=page_size),
        )

    async def funding_rate_history(self, symbol: str, page_num: Optional[int] = 1, page_size: Optional[int] = 20) -> dict:
        return await self.call(
            "GET",
            "api/v1/contract/funding_rate/history",
            params=dict(symbol=symbol, page_num=page_num, page_size=page_size),
        )

    async def assets(self) -> dict:
        return await self.call("GET", "api/v1/private/account/assets")

    async def asset(self, currency: str) -> dict:
        return await self.call("GET", f"api/v1/private/account/asset/{currency}")

    async def transfer_record(
        self,
        currency: Optional[str] = None,
        state: Literal["WAIT", "SUCCESS", "FAILED"] = None,
        type: Literal["IN", "OUT"] = None,
        page_num: Optional[int] = 1,
        page_size: Optional[int] = 20,
    ) -> dict:
        return await self.call(
            "GET",
            "api/v1/private/account/transfer_record",
            params=dict(currency=currency, state=state, type=type, page_num=page_num, page_size=page_size),
        )

    async def history_positions(
        self,
        symbol: Optional[str] = None,
        type: Optional[int] = None,
        page_num: Optional[int] = 1,
        page_size: Optional[int] = 20,
    ) -> dict:
        return await self.call(
            "GET",
            "api/v1/private/position/list/history_positions",
            params=dict(symbol=symbol, type=type, page_num=page_num, page_size=page_size),
        )

    async def open_positions(self, symbol: Optional[str] = None) -> dict:
        return await self.call("GET", "api/v1/private/position/open_positions", params=dict(symbol=symbol))

    async def funding_records(
        self,
        symbol: Optional[str] = None,
        position_id: Optional[int] = None,
        page_num: Optional[int] = 1,
        page_size: Optional[int] = 20,
    ) -> dict:
        return await self.call(
            "GET",
            "api/v1/private/position/funding_records",
            params=dict(symbol=symbol, position_id=position_id, page_num=page_num, page_size=page_size),
        )

    async def open_orders(
        self,
        symbol: Optional[str] = None,
        page_num: Optional[int] = 1,
        page_size: Optional[int] = 20,
    ) -> dict:
        return await self.call(
            "GET",
            f"api/v1/private/order/list/open_orders/{symbol}",
            params=dict(symbol=symbol, page_num=page_num, page_size=page_size),
        )

    async def history_orders(
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
        return await self.call(
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

    async def get_order_external(self, symbol: str, external_oid: int) -> dict:
        return await self.call("GET", f"api/v1/private/order/external/{symbol}/{external_oid}")

    async def get_order(self, order_id: int) -> dict:
        return await self.call("GET", f"api/v1/private/order/{order_id}")

    async def batch_query(self, order_ids: List[int]) -> dict:
        return await self.call(
            "GET",
            "api/v1/private/order/batch_query",
            params=dict(order_ids=",".join(order_ids) if isinstance(order_ids, list) else order_ids),
        )

    async def deal_details(self, order_id: int) -> dict:
        return await self.call("GET", f"api/v1/private/order/deal_details/{order_id}")

    async def order_deals(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page_num: Optional[int] = 1,
        page_size: Optional[int] = 20,
    ) -> dict:
        return await self.call(
            "GET",
            "api/v1/private/order/list/order_deals",
            params=dict(symbol=symbol, start_time=start_time, end_time=end_time, page_num=page_num, page_size=page_size),
        )

    async def get_trigger_orders(
        self,
        symbol: Optional[str] = None,
        states: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict:
        return await self.call(
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

    async def get_stop_limit_orders(
        self,
        symbol: Optional[str] = None,
        is_finished: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict:
        return await self.call(
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

    async def risk_limit(self, symbol: Optional[str] = None) -> dict:
        return await self.call("GET", "api/v1/private/account/risk_limit", params=dict(symbol=symbol))

    async def tiered_fee_rate(self, symbol: Optional[str] = None) -> dict:
        return await self.call("GET", "api/v1/private/account/tiered_fee_rate", params=dict(symbol=symbol))

    async def change_margin(self, position_id: int, amount: int, type: str) -> dict:
        return await self.call(
            "POST",
            "api/v1/private/position/change_margin",
            json=dict(positionId=position_id, amount=amount, type=type),
        )

    async def get_leverage(self, symbol: str) -> dict:
        return await self.call("GET", "api/v1/private/position/leverage", params=dict(symbol=symbol))

    async def change_leverage(
        self,
        position_id: int,
        leverage: int,
        open_type: Optional[int] = None,
        symbol: Optional[str] = None,
        position_type: Optional[int] = None,
    ) -> dict:
        return await self.call(
            "POST",
            "api/v1/private/position/change_leverage",
            json=dict(
                positionId=position_id,
                leverage=leverage,
                openType=open_type,
                symbol=symbol,
                positionType=position_type,
            ),
        )

    async def get_position_mode(self) -> dict:
        return await self.call("GET", "api/v1/private/position/position_mode")

    async def change_position_mode(self, position_mode: int) -> dict:
        return await self.call(
            "POST",
            "api/v1/private/position/change_position_mode",
            json=dict(positionMode=position_mode),
        )

    async def order(
        self,
        symbol: str,
        price: float,
        vol: float,
        side: int,
        type: int,
        open_type: int,
        position_id: Optional[int] = None,
        leverage: Optional[int] = None,
        external_oid: Optional[str] = None,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
        position_mode: Optional[int] = None,
        reduce_only: Optional[bool] = False,
    ) -> dict:
        return await self.call(
            "POST",
            "api/v1/private/order/create",
            json=dict(
                symbol=symbol,
                price=price,
                vol=vol,
                side=side,
                type=type,
                openType=open_type,
                positionId=position_id,
                leverage=leverage,
                externalOid=external_oid,
                stopLossPrice=stop_loss_price,
                takeProfitPrice=take_profit_price,
                positionMode=position_mode,
                reduceOnly=reduce_only,
            ),
        )

    async def bulk_order(
        self,
        symbol: str,
        price: float,
        vol: float,
        side: int,
        type: int,
        open_type: int,
        position_id: Optional[int] = None,
        external_oid: Optional[str] = None,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
    ) -> dict:
        return await self.call(
            "POST",
            "api/v1/private/order/submit_batch",
            json=dict(
                symbol=symbol,
                price=price,
                vol=vol,
                side=side,
                type=type,
                openType=open_type,
                positionId=position_id,
                externalOid=external_oid,
                stopLossPrice=stop_loss_price,
                takeProfitPrice=take_profit_price,
            ),
        )

    async def cancel_order(self, order_ids: Union[List[int], int]) -> dict:
        return await self.call("POST", "api/v1/private/order/cancel", json=order_ids if isinstance(order_ids, list) else [order_ids])

    async def cancel_order_with_external(self, symbol: str, external_oid: str) -> dict:
        return await self.call(
            "POST",
            "api/v1/private/order/cancel_with_external",
            json=dict(symbol=symbol, externalOid=external_oid),
        )

    async def cancel_all(self, symbol: Optional[str] = None) -> dict:
        return await self.call("POST", "api/v1/private/order/cancel_all", json=dict(symbol=symbol))

    async def change_risk_level(self) -> dict:
        return await self.call("POST", "api/v1/private/account/change_risk_level")

    async def trigger_order(
        self,
        symbol: str,
        vol: float,
        side: int,
        open_type: int,
        trigger_price: float,
        trigger_type: int,
        execute_cycle: int,
        order_type: int,
        trend: int,
        price: Optional[float] = None,
        leverage: Optional[int] = None,
    ) -> dict:
        return await self.call(
            "POST",
            "api/v1/private/planorder/place",
            json=dict(
                symbol=symbol,
                price=price,
                vol=vol,
                leverage=leverage,
                side=side,
                openType=open_type,
                triggerPrice=trigger_price,
                triggerType=trigger_type,
                executeCycle=execute_cycle,
                orderType=order_type,
                trend=trend,
            ),
        )

    async def cancel_trigger_order(self, order_id: int) -> dict:
        return await self.call("POST", "api/v1/private/planorder/cancel", json=dict(order_id=order_id))

    async def cancel_all_trigger_orders(self, symbol: Optional[str] = None) -> dict:
        return await self.call("POST", "api/v1/private/planorder/cancel_all", json=dict(symbol=symbol))

    async def cancel_stop_order(self, order_id: int) -> dict:
        return await self.call("POST", "api/v1/private/stoporder/cancel", json=dict(order_id=order_id))

    async def cancel_all_stop_order(self, position_id: Optional[int] = None, symbol: Optional[str] = None) -> dict:
        return await self.call(
            "POST",
            "api/v1/private/stoporder/cancel_all",
            json=dict(positionId=position_id, symbol=symbol),
        )

    async def stop_limit_change_price(
        self,
        order_id: int,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
    ) -> dict:
        return await self.call(
            "POST",
            "api/v1/private/stoporder/change_price",
            json=dict(orderId=order_id, stopLossPrice=stop_loss_price, takeProfitPrice=take_profit_price),
        )

    async def stop_limit_change_plan_price(
        self,
        stop_plan_order_id: int,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
    ) -> dict:
        return await self.call(
            "POST",
            "api/v1/private/stoporder/change_plan_price",
            json=dict(
                stopPlanOrderId=stop_plan_order_id,
                stopLossPrice=stop_loss_price,
                takeProfitPrice=take_profit_price,
            ),
        )
