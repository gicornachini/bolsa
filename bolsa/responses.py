import logging
import re
from typing import AsyncGenerator, List, Tuple

from aiohttp.client_reqrep import ClientResponse
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag

from bolsa.models import (
    Broker,
    BrokerAccount,
    BrokerAccountParseExtraData,
    BrokerAssetExtract,
    BrokerParseExtraData,
    PassiveIncome
)

logger = logging.getLogger(__name__)


class _BrokerResponseBase:
    BROKERS_SELECT_ID = "ctl00_ContentPlaceHolder1_ddlAgentes"
    DEFAULT_INVALID_BROKER_VALUE = "-1"

    def __init__(self, response: ClientResponse) -> None:
        self.response = response

    @staticmethod
    async def _get_date_input_ids() -> Tuple[str, str]:
        raise NotImplementedError()

    async def data(self) -> List[Broker]:
        html = await self.response.text()
        return await self._parse_brokers(html)

    async def _parse_brokers(self, html: str) -> List[Broker]:
        soup = BeautifulSoup(html, "html.parser")
        brokers_select = soup.find("select", id=self.BROKERS_SELECT_ID)
        brokers_option = brokers_select.find_all("option")
        start_date_id, end_date_id = await self._get_date_input_ids()
        start_date = soup.find(id=start_date_id).text
        end_date = soup.find(id=end_date_id).text

        return [
            Broker(
                name=broker_option.text,
                value=broker_option["value"],
                parse_extra_data=BrokerParseExtraData(start_date, end_date),
            )
            for broker_option in brokers_option
            if broker_option["value"] != self.DEFAULT_INVALID_BROKER_VALUE
        ]


class BrokerAssetsResponse(_BrokerResponseBase):
    @staticmethod
    async def _get_date_input_ids() -> Tuple[str, str]:
        start_date_id = "ctl00_ContentPlaceHolder1_lblPeriodoInicialBolsa"
        end_date_id = "ctl00_ContentPlaceHolder1_lblPeriodoFinalBolsa"
        return start_date_id, end_date_id


class BrokerPassiveIncomesResponse(_BrokerResponseBase):
    @staticmethod
    async def _get_date_input_ids() -> Tuple[str, str]:
        start_date_id = "ctl00_ContentPlaceHolder1_lblPeriodoInicial"
        end_date_id = "ctl00_ContentPlaceHolder1_lblPeriodoFinal"
        return start_date_id, end_date_id


class BrokerAccountResponse:
    ACCOUNT_SELECT_ID = "ctl00_ContentPlaceHolder1_ddlContas"
    BROKERS_SELECT_ID = "ctl00_ContentPlaceHolder1_ddlAgentes"

    def __init__(self, response: ClientResponse, broker: Broker) -> None:
        self.response = response
        self.broker = broker

    async def data(self) -> Broker:
        html = await self.response.text()

        self.broker.accounts = await self._parse_accounts(html)

        return self.broker

    async def _parse_accounts(self, html: str) -> List[BrokerAccount]:
        soup = BeautifulSoup(html, "html.parser")
        brokers_select = soup.find("select", id=self.ACCOUNT_SELECT_ID)
        if not brokers_select:
            return []

        brokers_option = brokers_select.find_all("option")
        view_state = soup.find(id="__VIEWSTATE")["value"]
        view_state_generator = soup.find(id="__VIEWSTATEGENERATOR")["value"]
        event_validation = soup.find(id="__EVENTVALIDATION")["value"]

        parse_extra_data = BrokerAccountParseExtraData(
            view_state=view_state,
            view_state_generator=view_state_generator,
            event_validation=event_validation,
        )

        return [
            BrokerAccount(id=broker_option["value"], parse_extra_data=parse_extra_data)
            for broker_option in brokers_option
        ]


class BrokerAccountAssetExtractResponse:
    ASSETS_TABLE_ID = (
        "ctl00_ContentPlaceHolder1_rptAgenteBolsa_ctl00_rptContaBolsa_ctl00_"
        "pnAtivosNegociados"
    )

    def __init__(self, response: ClientResponse, broker_value: str) -> None:
        self.response = response
        self.broker_value = broker_value

    async def data(self) -> List[BrokerAssetExtract]:
        html = await self.response.text()
        return await self._parse_assets_extract(html)

    async def _parse_assets_extract(self, html: str) -> List[BrokerAssetExtract]:
        assets_extract = []
        soup = BeautifulSoup(html, "html.parser")
        assets_table = soup.find(id=self.ASSETS_TABLE_ID)

        logger.debug(
            f"BrokerAccountAssetExtractResponse start parsing asset extract"
            f" - broker value: {self.broker_value}"
        )

        table_body = assets_table.find("tbody") if assets_table else ResultSet(None)
        rows = table_body.find_all("tr") if table_body else []
        for row in rows:
            (
                operation_date,
                action,
                market_type,
                _,
                raw_negotiation_code,
                asset_specification,
                unit_amount,
                unit_price,
                total_price,
                quotation_factor,
            ) = row.find_all("td")
            assets_extract.append(
                await BrokerAssetExtract.create_from_response_fields(
                    operation_date=operation_date.get_text(strip=True),
                    action=action.get_text(strip=True),
                    market_type=market_type.get_text(strip=True),
                    raw_negotiation_code=raw_negotiation_code.get_text(strip=True),
                    asset_specification=asset_specification.get_text(strip=True),
                    unit_amount=unit_amount.get_text(strip=True),
                    unit_price=unit_price.get_text(strip=True),
                    total_price=total_price.get_text(strip=True),
                    quotation_factor=quotation_factor.get_text(strip=True),
                )
            )

        logger.debug(
            f"BrokerAccountAssetExtractResponse end parsing asset extract "
            f"- broker value: {self.broker_value}"
        )

        return assets_extract


class PassiveIncomesResponse:
    PASSIVE_INCOMES_DOCUMENT_ID = "ctl00_ContentPlaceHolder1_updFiltro"
    BROKER_TITLE_ID_REGEX = (
        r"ctl00_ContentPlaceHolder1_rptAgenteProventos.*lblAgenteProventos"
    )
    UNSUPPORTED_INCOME_TYPE = "Eventos em Ativos Creditado"

    def __init__(self, response: ClientResponse) -> None:
        self.response = response

    async def data(self) -> List[PassiveIncome]:
        html = await self.response.text()
        return await self._parse_data(html=html)

    @staticmethod
    async def _parse_passive_incomes(
        table: Tag, income_type: str
    ) -> AsyncGenerator[PassiveIncome, None]:
        for row in table.find_all("tr"):
            (
                raw_negotiation_name,
                asset_specification,
                raw_negotiation_code,
                operation_date,
                event_type,
                unit_amount,
                quotation_factor,
                gross_value,
                net_value,
            ) = row.find_all("td")
            yield await PassiveIncome.create_from_response_fields(
                raw_negotiation_name=raw_negotiation_name.get_text(strip=True),
                asset_specification=asset_specification.get_text(strip=True),
                raw_negotiation_code=raw_negotiation_code.get_text(strip=True),
                operation_date=operation_date.get_text(strip=True),
                event_type=event_type.get_text(strip=True),
                unit_amount=unit_amount.get_text(strip=True),
                quotation_factor=quotation_factor.get_text(strip=True),
                gross_value=gross_value.get_text(strip=True),
                net_value=net_value.get_text(strip=True),
                income_type=income_type,
            )

    @staticmethod
    async def _get_income_types(broker_tag: Tag, method_name: str) -> ResultSet:
        method = getattr(broker_tag, method_name)
        return method("p", class_="title")

    async def _parse_data(self, html: str) -> List[PassiveIncome]:
        passive_incomes = []
        soup = BeautifulSoup(html, "html.parser")
        document = soup.find(id=self.PASSIVE_INCOMES_DOCUMENT_ID)
        brokers = document.find_all(id=re.compile(self.BROKER_TITLE_ID_REGEX))
        num_of_brokers = len(brokers)

        for i in range(num_of_brokers):
            if i + 1 == num_of_brokers:  # last broker
                broker_tag = brokers[i]
                method_name = "find_all_next"
            else:
                broker_tag = brokers[i + 1]
                method_name = "find_all_previous"

            for income_type in await self._get_income_types(
                broker_tag=broker_tag, method_name=method_name
            ):
                if income_type.get_text(strip=True) == self.UNSUPPORTED_INCOME_TYPE:
                    continue

                async for passive_income in self._parse_passive_incomes(
                    table=income_type.find_next("tbody") or [],
                    income_type=income_type.get_text(strip=True).split()[-1],
                ):
                    passive_incomes.append(passive_income)

        return passive_incomes
