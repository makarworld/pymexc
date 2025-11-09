"""
### Broker API
Documentation: https://www.mexc.com/api-docs/broker

### Usage

```python
from pymexc import broker

api_key = "YOUR API KEY"
api_secret = "YOUR API SECRET KEY"

async def main():
    # initialize HTTP client
    broker_client = broker.AsyncHTTP(api_key = api_key, api_secret = api_secret)
    
    # make http request to api
    print(await broker_client.query_sub_account_list())

```

"""

import logging
from typing import List, Literal, Optional, Union

logger = logging.getLogger(__name__)

try:
    from .base import _SpotHTTP
except ImportError:
    from pymexc._async.base import _SpotHTTP

__all__ = ["HTTP"]


class HTTP(_SpotHTTP):
    # <=================================================================>
    #
    #                       Broker Endpoints
    #
    # <=================================================================>

    async def query_universal_transfer_history(
        self,
        from_account_type: Literal["SPOT", "FUTURES"],
        to_account_type: Literal["SPOT", "FUTURES"],
        from_account: Optional[str] = None,
        to_account: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        page: Optional[int] = 1,
        limit: Optional[int] = 500,
    ) -> list:
        """
        ### Query Universal Transfer History - broker user
        #### Required permission: SPOT_TRANSFER_READ

        Weight(IP): 1

        https://www.mexc.com/api-docs/broker#query-universal-transfer-history-broker-user

        :param from_account: (optional) Transfer from master account by default if fromAccount is not sent
        :type from_account: str
        :param to_account: (optional) Transfer to master account by default if toAccount is not sent
        :type to_account: str
        :param from_account_type: fromAccountType:"SPOT","FUTURES"
        :type from_account_type: Literal["SPOT", "FUTURES"]
        :param to_account_type: toAccountType:"SPOT","FUTURES"
        :type to_account_type: Literal["SPOT", "FUTURES"]
        :param start_time: (optional) startTime(ms)
        :type start_time: str
        :param end_time: (optional) endTime(ms)
        :type end_time: str
        :param page: (optional) default 1
        :type page: int
        :param limit: (optional) default 500, max 500
        :type limit: int

        :return: response list
        :rtype: list
        """
        return await self.call(
            "GET",
            "/api/v3/broker/sub-account/universalTransfer",
            params=dict(
                fromAccount=from_account,
                toAccount=to_account,
                fromAccountType=from_account_type,
                toAccountType=to_account_type,
                startTime=start_time,
                endTime=end_time,
                page=page,
                limit=limit,
            ),
        )

    async def create_sub_account(self, sub_account: str, note: str, password: Optional[str] = None) -> dict:
        """
        ### Create a Sub-account
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://www.mexc.com/api-docs/broker#create-a-sub-account

        :param sub_account: Sub-account name
        :type sub_account: str
        :param note: Note
        :type note: str
        :param password: (optional) Password (hexadecimal string encrypted by MD5)
        :type password: str

        :return: response dictionary
        :rtype: dict
        """
        params = dict(subAccount=sub_account, note=note)
        if password:
            params["password"] = password
        return await self.call("POST", "/api/v3/broker/sub-account/virtualSubAccount", params=params)

    async def query_sub_account_list(
        self,
        sub_account: Optional[str] = None,
        page: Optional[int] = 1,
        limit: Optional[int] = 10,
    ) -> dict:
        """
        ### Query Sub-account List
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://www.mexc.com/api-docs/broker#query-sub-account-list

        :param sub_account: (optional) Sub-account name
        :type sub_account: str
        :param page: (optional) Default value: 1
        :type page: int
        :param limit: (optional) Default value: 10, Max value: 200
        :type limit: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "GET",
            "/api/v3/broker/sub-account/list",
            params=dict(subAccount=sub_account, page=page, limit=limit),
        )

    async def query_sub_account_status(self, sub_account: str) -> dict:
        """
        ### Query Sub-account Status
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://www.mexc.com/api-docs/broker#query-sub-account-status

        :param sub_account: Sub-account name
        :type sub_account: str

        :return: response dictionary with status field (1:normal, 2:freeze)
        :rtype: dict
        """
        return await self.call("GET", "/api/v3/broker/sub-account/status", params=dict(subAccount=sub_account))

    async def create_sub_account_api_key(
        self,
        sub_account: str,
        permissions: Union[
            str,
            List[
                Literal[
                    "SPOT_ACCOUNT_READ",
                    "SPOT_ACCOUNT_WRITE",
                    "SPOT_DEAL_READ",
                    "SPOT_DEAL_WRITE",
                    "CONTRACT_ACCOUNT_READ",
                    "CONTRACT_ACCOUNT_WRITE",
                    "CONTRACT_DEAL_READ",
                    "CONTRACT_DEAL_WRITE",
                    "SPOT_TRANSFER_READ",
                    "SPOT_TRANSFER_WRITE",
                ]
            ],
        ],
        note: str,
        ip: Optional[str] = None,
    ) -> dict:
        """
        ### Create an APIKey for a Sub-account
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://www.mexc.com/api-docs/broker#create-an-apikey-for-a-sub-account

        :param sub_account: Sub-account name
        :type sub_account: str
        :param permissions: Permission of APIKey
        :type permissions: Union[str, List[str]]
        :param note: Note
        :type note: str
        :param ip: (optional) Link IP addresses, separate with commas if more than one. Support up to 4 addresses.
        :type ip: str

        :return: response dictionary
        :rtype: dict
        """
        params = dict(
            subAccount=sub_account,
            permissions=",".join(permissions) if isinstance(permissions, list) else permissions,
            note=note,
        )
        if ip:
            params["ip"] = ip
        return await self.call("POST", "/api/v3/broker/sub-account/apiKey", params=params)

    async def query_sub_account_api_key(self, sub_account: str) -> dict:
        """
        ### Query the APIKey of a Sub-account
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://www.mexc.com/api-docs/broker#query-the-apikey-of-a-sub-account

        :param sub_account: Sub-account name
        :type sub_account: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("GET", "/api/v3/broker/sub-account/apiKey", params=dict(subAccount=sub_account))

    async def delete_sub_account_api_key(self, sub_account: str, api_key: str) -> dict:
        """
        ### Delete the APIKey of a Sub-account
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://www.mexc.com/api-docs/broker#delete-the-apikey-of-a-sub-account

        :param sub_account: Sub-account name
        :type sub_account: str
        :param api_key: API key
        :type api_key: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "DELETE",
            "/api/v3/broker/sub-account/apiKey",
            params=dict(subAccount=sub_account, apiKey=api_key),
        )

    async def generate_deposit_address(self, coin: str, network: str) -> dict:
        """
        ### Generate Deposit Address of Sub-account
        #### Required permission: SPOT_DEPOSIT_WRITE

        Weight(IP): 1

        https://www.mexc.com/api-docs/broker#generate-deposit-address-of-sub-account

        :param coin: Deposit coin
        :type coin: str
        :param network: Deposit network
        :type network: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "POST",
            "/api/v3/broker/capital/deposit/subAddress",
            params=dict(coin=coin, network=network),
        )

    async def deposit_address(self, coin: str) -> list:
        """
        ### Deposit Address of Sub-account
        #### Required permission: SPOT_DEPOSIT_READ

        Weight(IP): 1

        https://www.mexc.com/api-docs/broker#deposit-address-of-sub-account

        :param coin: Deposit coin
        :type coin: str

        :return: response list
        :rtype: list
        """
        return await self.call("GET", "/api/v3/broker/capital/deposit/subAddress", params=dict(coin=coin))

    async def query_sub_account_deposit_history(
        self,
        coin: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: Optional[int] = 20,
        page: Optional[int] = 1,
    ) -> list:
        """
        ### Query Sub-account Deposit History
        #### Required permission: SPOT_DEPOSIT_READ

        Weight(IP): 1

        https://www.mexc.com/api-docs/broker#query-sub-account-deposit-history

        :param coin: (optional) Deposit coin
        :type coin: str
        :param status: (optional) Deposit status
        :type status: str
        :param start_time: (optional) Default: 10 days ago from current time
        :type start_time: str
        :param end_time: (optional) Default: current time
        :type end_time: str
        :param limit: (optional) Default: 20
        :type limit: int
        :param page: (optional) Default: 1
        :type page: int

        :return: response list
        :rtype: list
        """
        return await self.call(
            "GET",
            "/api/v3/broker/capital/deposit/subHisrec",
            params=dict(
                coin=coin,
                status=status,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                page=page,
            ),
        )

    async def query_all_sub_account_deposit_history(
        self,
        coin: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: Optional[int] = 100,
        page: Optional[int] = 1,
    ) -> list:
        """
        ### Query All Sub-account Deposit History (Recent 3 days)
        #### Master account query all Sub-account deposit history
        #### Required permission: SPOT_DEPOSIT_READ

        Weight(IP): 1

        https://www.mexc.com/api-docs/broker#query-all-sub-account-deposit-history-recent-3-days

        :param coin: (optional) Deposit coin
        :type coin: str
        :param status: (optional) Deposit status
        :type status: str
        :param start_time: (optional) startTime
        :type start_time: str
        :param end_time: (optional) endTime
        :type end_time: str
        :param limit: (optional) Default: 100
        :type limit: int
        :param page: (optional) Default: 1
        :type page: int

        :return: response list
        :rtype: list
        """
        return await self.call(
            "GET",
            "/api/v3/broker/capital/deposit/subHisrec/getall",
            params=dict(
                coin=coin,
                status=status,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                page=page,
            ),
        )

    async def withdraw(
        self,
        coin: str,
        network: str,
        address: str,
        amount: Union[float, str],
        password: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> dict:
        """
        ### Withdraw
        #### Only support withdraw for sub-account, not master account
        #### Required permission: SPOT_TRANSFER_READ

        Weight(IP): 1

        https://www.mexc.com/api-docs/broker#withdraw

        :param coin: Withdraw coin
        :type coin: str
        :param network: Withdraw network
        :type network: str
        :param address: Withdraw address
        :type address: str
        :param amount: Amount
        :type amount: Union[float, str]
        :param password: (optional) Password (hexadecimal string encrypted by MD5)
        :type password: str
        :param remark: (optional) Remark
        :type remark: str

        :return: response dictionary
        :rtype: dict
        """
        params = dict(coin=coin, network=network, address=address, amount=amount)
        if password:
            params["password"] = password
        if remark:
            params["remark"] = remark
        return await self.call("POST", "/api/v3/broker/capital/withdraw/apply", params=params)

    async def universal_transfer(
        self,
        from_account_type: Literal["SPOT", "FUTURES"],
        to_account_type: Literal["SPOT", "FUTURES"],
        asset: str,
        amount: Union[float, str],
        from_account: Optional[str] = None,
        to_account: Optional[str] = None,
    ) -> dict:
        """
        ### Universal Transfer
        #### Only support broker account
        #### Required permission: SPOT_TRANSFER_READ

        Weight(IP): 1

        https://www.mexc.com/api-docs/broker#universal-transfer

        :param from_account: (optional) Transfer from master account by default if fromAccount is not sent
        :type from_account: str
        :param to_account: (optional) Transfer to master account by default if toAccount is not sent
        :type to_account: str
        :param from_account_type: fromAccountType:"SPOT","FUTURES"
        :type from_account_type: Literal["SPOT", "FUTURES"]
        :param to_account_type: toAccountType:"SPOT","FUTURES"
        :type to_account_type: Literal["SPOT", "FUTURES"]
        :param asset: Asset, eg: USDT
        :type asset: str
        :param amount: Amount, eg: 1.82938475
        :type amount: Union[float, str]

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "POST",
            "/api/v3/broker/sub-account/universalTransfer",
            params=dict(
                fromAccount=from_account,
                toAccount=to_account,
                fromAccountType=from_account_type,
                toAccountType=to_account_type,
                asset=asset,
                amount=amount,
            ),
        )

    async def enable_futures_for_sub_account(self, sub_account: str) -> dict:
        """
        ### Enable Futures for Sub-account
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://www.mexc.com/api-docs/broker#enable-futures-for-sub-account

        :param sub_account: Sub-account name
        :type sub_account: str

        :return: response dictionary
        :rtype: dict
        """
        return await self.call("POST", "/api/v3/broker/sub-account/futures", params=dict(subAccount=sub_account))

    async def get_broker_rebate_history_records(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        page: Optional[int] = 1,
        page_size: Optional[int] = 10,
    ) -> dict:
        """
        ### Get Broker Rebate History Records
        #### Required permission: SPOT_ACCOUNT_READ

        Weight(IP): 1

        https://www.mexc.com/api-docs/broker#get-broker-rebate-history-records

        :param start_time: (optional) startTime
        :type start_time: str
        :param end_time: (optional) endTime
        :type end_time: str
        :param page: (optional) Default 1
        :type page: int
        :param page_size: (optional) Default 10
        :type page_size: int

        :return: response dictionary
        :rtype: dict
        """
        return await self.call(
            "GET",
            "/api/v3/broker/rebate/taxQuery",
            params=dict(startTime=start_time, endTime=end_time, page=page, pageSize=page_size),
        )

