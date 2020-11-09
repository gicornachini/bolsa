import logging

from bs4 import BeautifulSoup

from bolsa.models import (
    Broker,
    BrokerAccount,
    BrokerAccountParseExtraData,
    BrokerAssetExtract,
    BrokerParseExtraData
)

logger = logging.getLogger(__name__)


class GetBrokersResponse():
    BROKERS_SELECT_ID = 'ctl00_ContentPlaceHolder1_ddlAgentes'
    DEFAULT_INVALID_BROKER_VALUE = '-1'

    def __init__(self, response):
        self.response = response

    async def data(self):
        html = await self.response.text()
        return self._parse_get_brokers(html)

    def _parse_get_brokers(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        brokers_select = soup.find('select', id=self.BROKERS_SELECT_ID)
        brokers_option = brokers_select.find_all('option')

        start_date = soup.find(
            id='ctl00_ContentPlaceHolder1_txtDataDeBolsa'
        )['value']
        end_date = soup.find(
            id='ctl00_ContentPlaceHolder1_txtDataAteBolsa'
        )['value']

        return [
            Broker(
                name=broker_option.text,
                value=broker_option['value'],
                parse_extra_data=BrokerParseExtraData(start_date, end_date)
            )
            for broker_option in brokers_option
            if broker_option['value'] != self.DEFAULT_INVALID_BROKER_VALUE
        ]


class GetBrokerAccountResponse():
    ACCOUNT_SELECT_ID = 'ctl00_ContentPlaceHolder1_ddlContas'
    BROKERS_SELECT_ID = 'ctl00_ContentPlaceHolder1_ddlAgentes'

    def __init__(self, response, broker):
        self.response = response
        self.broker = broker

    async def data(self):
        html = await self.response.text()

        self.broker.accounts = self._parse_get_accounts(html)

        return self.broker

    def _parse_get_accounts(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        brokers_select = soup.find('select', id=self.ACCOUNT_SELECT_ID)
        if not brokers_select:
            return []

        brokers_option = brokers_select.find_all('option')

        view_state = soup.find(id='__VIEWSTATE')['value']
        view_state_generator = soup.find(id='__VIEWSTATEGENERATOR')['value']
        event_validation = soup.find(id='__EVENTVALIDATION')['value']

        parse_extra_data = BrokerAccountParseExtraData(
            view_state=view_state,
            view_state_generator=view_state_generator,
            event_validation=event_validation,
        )

        return [
            BrokerAccount(
                id=broker_option['value'],
                parse_extra_data=parse_extra_data
            )
            for broker_option in brokers_option
        ]


class GetBrokerAccountAssetExtractResponse:
    ASSETS_TABLE_ID = (
        'ctl00_ContentPlaceHolder1_rptAgenteBolsa_ctl00_rptContaBolsa_ctl00_'
        'pnAtivosNegociados'
    )

    def __init__(self, response, broker_value):
        self.response = response
        self.broker_value = broker_value

    async def data(self):
        html = await self.response.text()

        assets_extract = await self._parse_get_assets_extract(html)
        return assets_extract

    async def _parse_get_assets_extract(self, html):
        assets_extract = []
        soup = BeautifulSoup(html, 'html.parser')
        assets_table = soup.find(id=self.ASSETS_TABLE_ID)

        logger.debug(
            f'GetBrokerAccountAssetExtractResponse start parsing asset extract'
            f' - broker value: {self.broker_value}'
        )

        if not assets_table:
            return assets_extract

        table_body = assets_table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            operation_date, action, market_type, _, raw_negotiation_code, asset_specification, unit_amount, unit_price, total_price, quotation_factor = row.find_all(  # NOQA
                'td'
            )
            asset_extract = BrokerAssetExtract.create_from_response_fields(
                operation_date=operation_date.get_text(strip=True),
                action=action.get_text(strip=True),
                market_type=market_type.get_text(strip=True),
                raw_negotiation_code=raw_negotiation_code.get_text(strip=True),
                asset_specification=asset_specification.get_text(strip=True),
                unit_amount=unit_amount.get_text(strip=True),
                unit_price=unit_price.get_text(strip=True),
                total_price=total_price.get_text(strip=True),
                quotation_factor=quotation_factor.get_text(strip=True)
            )
            assets_extract.append(asset_extract)

        logger.debug(
            f'GetBrokerAccountAssetExtractResponse end parsing asset extract '
            f'- broker value: {self.broker_value}'
        )

        return assets_extract
