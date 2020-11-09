import asyncio
import logging
from functools import cached_property

import aiohttp

from bolsa.connector import B3HttpClientConnector
from bolsa.http_client import B3HttpClient
from bolsa.responses import (
    GetBrokerAccountAssetExtractResponse,
    GetBrokerAccountResponse,
    GetBrokersResponse
)

logger = logging.getLogger(__name__)

POOL_CONNECTOR = B3HttpClientConnector()


class B3AsyncBackend():

    def __init__(self, username, password, captcha_service):
        self._connector = POOL_CONNECTOR.get_connector()
        self.username = username
        self.password = password
        self.captcha_service = captcha_service

    @cached_property
    def _session(self):
        logger.info(f'Creating session for username: {self.username}')
        return aiohttp.ClientSession(
            connector=self._connector,
            connector_owner=False
        )

    @cached_property
    def _http_client(self):
        return B3HttpClient(
            username=self.username,
            password=self.password,
            session=self._session,
            captcha_service=self.captcha_service
        )

    async def session_close(self):
        await self._session.close()

    async def connection_close(self):
        await self._connector.close()

    async def get_brokers(self):
        response = await self._http_client.get_brokers()
        response_class = GetBrokersResponse(response)

        return await response_class.data()

    async def get_broker_accounts(self, broker):
        response = await self._http_client.get_broker_accounts(broker)
        response_class = GetBrokerAccountResponse(
            response=response,
            broker=broker
        )

        return await response_class.data()

    async def get_brokers_with_accounts(self):
        brokers = await self.get_brokers()
        brokers_account_routine = [
            asyncio.create_task(
                self.get_broker_accounts(broker)
            )
            for broker in brokers
        ]

        return await asyncio.gather(*brokers_account_routine)

    async def get_broker_account_portfolio_assets_extract(
        self,
        account_id,
        broker_value,
        broker_parse_extra_data,
        account_parse_extra_data
    ):
        response = await self._http_client.get_broker_account_portfolio_assets_extract(  # NOQA
            account_id,
            broker_value,
            broker_parse_extra_data,
            account_parse_extra_data
        )
        response_class = GetBrokerAccountAssetExtractResponse(
            response=response,
            broker_value=broker_value
        )

        return await response_class.data()

    async def get_brokers_account_portfolio_assets_extract(self, brokers):
        brokers_account_assets_extract_routine = [
            asyncio.create_task(
                self.get_broker_account_portfolio_assets_extract(
                    account_id=broker.accounts[0].id,
                    broker_value=broker.value,
                    broker_parse_extra_data=broker.parse_extra_data,
                    account_parse_extra_data=(
                        broker.accounts[0].parse_extra_data
                    )
                )
            )
            for broker in brokers
            if len(broker.accounts) > 0
        ]

        return await asyncio.gather(*brokers_account_assets_extract_routine)
