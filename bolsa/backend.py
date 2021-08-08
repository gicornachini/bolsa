import logging
from datetime import date
from functools import cached_property
from typing import Any, Dict, List, Union

from bolsa.connector import B3HttpClientConnector
from bolsa.crawlers import AssetsCrawler, PassiveIncomesCrawler
from bolsa.models import (
    Broker,
    BrokerAccount,
    BrokerAssetExtract,
    PassiveIncome
)

logger = logging.getLogger(__name__)

POOL_CONNECTOR = B3HttpClientConnector()


class B3AsyncBackend:
    def __init__(
        self, username: str, password: str, captcha_service: Union[Any, None] = None
    ):
        self._connector = POOL_CONNECTOR.get_connector()
        self.username = username
        self.password = password
        self.captcha_service = captcha_service

    @cached_property
    def _assets_crawler(self) -> AssetsCrawler:
        return AssetsCrawler(
            connector=self._connector,
            username=self.username,
            password=self.password,
            captcha_service=self.captcha_service,
        )

    @cached_property
    def _passive_incomes_crawler(self) -> PassiveIncomesCrawler:
        return PassiveIncomesCrawler(
            connector=self._connector,
            username=self.username,
            password=self.password,
            captcha_service=self.captcha_service,
        )

    async def session_close(self) -> None:
        await self._assets_crawler.session_close()
        await self._passive_incomes_crawler.session_close()

    async def connection_close(self) -> None:
        await self._connector.close()

    async def get_brokers(self) -> List[Broker]:
        return await self._assets_crawler.get_brokers()

    async def get_broker_accounts(self, broker: Broker) -> Broker:
        return await self._assets_crawler.get_broker_accounts(broker=broker)

    async def get_brokers_with_accounts(self) -> List[Broker]:
        return await self._assets_crawler.get_brokers_with_accounts()

    async def get_broker_account_portfolio_assets_extract(
        self,
        broker: Broker,
        account: BrokerAccount,
        start_date: Union[date, None] = None,
        end_date: Union[date, None] = None,
        as_dict: bool = False,
    ) -> Union[List[BrokerAssetExtract], List[Dict[str, Any]]]:
        return await self._assets_crawler.get_broker_account_portfolio_assets_extract(
            broker=broker,
            account=account,
            start_date=start_date,
            end_date=end_date,
            as_dict=as_dict,
        )

    async def get_brokers_account_portfolio_assets_extract(
        self,
        brokers: List[Broker],
        start_date: Union[date, None] = None,
        end_date: Union[date, None] = None,
        as_dict: bool = False,
    ) -> Union[List[BrokerAssetExtract], List[Dict[str, Any]]]:
        return await self._assets_crawler.get_brokers_account_portfolio_assets_extract(
            brokers=brokers,
            start_date=start_date,
            end_date=end_date,
            as_dict=as_dict,
        )

    async def get_passive_incomes_extract(
        self, date: Union[date, None] = None, as_dict: bool = False
    ) -> Union[List[PassiveIncome], List[Dict[str, Any]]]:
        return await self._passive_incomes_crawler.get_passive_incomes_extract(
            date=date, as_dict=as_dict
        )
