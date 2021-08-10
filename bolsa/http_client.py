import logging
from datetime import date, datetime
from typing import Any, Dict, Union
from urllib.parse import urljoin, urlparse

from aiohttp import ClientSession
from aiohttp.client_reqrep import ClientResponse
from bs4 import BeautifulSoup

from bolsa.connector import B3HttpClientConnector
from bolsa.models import Broker

logger = logging.getLogger(__name__)

POOL_CONNECTOR = B3HttpClientConnector()


class B3HttpClient:
    IS_LOGGED = False
    SESSION = None
    LOGIN_URL = "https://ceiapp.b3.com.br/CEI_Responsivo/login.aspx"
    _HEADERS_ORIGIN_URL = "https://cei.b3.com.br"

    def __init__(
        self,
        username: str,
        password: str,
        session: ClientSession,
        captcha_service: Any,
        base_url: str,
    ) -> None:
        self.username = username
        self.password = password
        self.session = session
        self.captcha_service = captcha_service
        self.base_url = base_url

    async def _get_referer(self) -> str:
        return urljoin(self._HEADERS_ORIGIN_URL, urlparse(self.base_url).path)

    async def _get_headers(self) -> Dict[str, str]:
        return {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": await self._get_referer(),
            "Origin": self._HEADERS_ORIGIN_URL,
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 "
                "Safari/537.36"
            ),
        }

    async def login(self):
        async with self.session.get(self.LOGIN_URL) as response:
            loginPageContent = await response.text()
            loginPageParsed = BeautifulSoup(loginPageContent, "html.parser")
            view_state = loginPageParsed.find(id="__VIEWSTATE")["value"]
            viewstate_generator = loginPageParsed.find(id="__VIEWSTATEGENERATOR")[
                "value"
            ]
            event_validation = loginPageParsed.find(id="__EVENTVALIDATION")["value"]

            solvedcaptcha = None
            if self.captcha_service:
                site_key = loginPageParsed.find(
                    id="ctl00_ContentPlaceHolder1_dvCaptcha"
                ).get("data-sitekey")
                solvedcaptcha = await self.captcha_service.resolve(
                    site_key, self.LOGIN_URL
                )

        payload = {
            "ctl00$ContentPlaceHolder1$smLoad": (
                "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHold"
                "er1$btnLogar"
            ),
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATEGENERATOR": viewstate_generator,
            "__EVENTVALIDATION": event_validation,
            "__VIEWSTATE": view_state,
            "ctl00$ContentPlaceHolder1$txtLogin": self.username,
            "ctl00$ContentPlaceHolder1$txtSenha": self.password,
            "__ASYNCPOST": True,
            "g-recaptcha-response": solvedcaptcha,
            "ctl00$ContentPlaceHolder1$btnLogar": "Entrar",
        }

        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://cei.b3.com.br/CEI_Responsivo/login.aspx",
            "Origin": "https://cei.b3.com.br",
            "Host": "cei.b3.com.br",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 "
                "Safari/537.36"
            ),
        }

        logger.info(f"B3HttpClient doing login - username: {self.username}")

        async with self.session.post(
            self.LOGIN_URL,
            data=payload,
            headers=headers,
        ) as response:
            logger.info(f"B3HttpClient login done - username: {self.username}")

            self.IS_LOGGED = True

            return await response.text()

    async def get_brokers(self) -> ClientResponse:
        if not self.IS_LOGGED:
            await self.login()

        logger.info(f"B3HttpClient getting brokers - username: {self.username}")

        response = await self.session.get(self.base_url)
        logger.info(f"B3HttpClient end getting brokers - username: {self.username}")

        return response

    async def get_broker_accounts(
        self, payload: Dict[str, Union[str, bool]]
    ) -> ClientResponse:
        if not self.IS_LOGGED:
            await self.login()

        return await self.session.post(
            self.base_url, data=payload, headers=await self._get_headers()
        )

    async def get_broker_account_portfolio_assets_extract(
        self,
        account_id,
        broker_value,
        broker_parse_extra_data,
        account_parse_extra_data,
    ):
        if not self.IS_LOGGED:
            await self.login()

        start_date = broker_parse_extra_data.start_date
        end_date = broker_parse_extra_data.end_date

        payload = {
            "ctl00$ContentPlaceHolder1$ToolkitScriptManager1": (
                "ctl00$ContentPlaceHolder1$updFiltro|ctl00$ContentPlaceHolder1"
                "$btnConsultar"
            ),
            "__EVENTTARGET": "",
            "__VIEWSTATE": account_parse_extra_data.view_state,
            "__VIEWSTATEGENERATOR": account_parse_extra_data.view_state_generator,
            "__EVENTVALIDATION": account_parse_extra_data.event_validation,
            "ctl00$ContentPlaceHolder1$ddlAgentes": broker_value,
            "ctl00$ContentPlaceHolder1$ddlContas": account_id,
            "ctl00$ContentPlaceHolder1$txtDataDeBolsa": start_date,
            "ctl00$ContentPlaceHolder1$txtDataAteBolsa": end_date,
            "ctl00$ContentPlaceHolder1$btnConsultar": "Consultar",
            "__ASYNCPOST": True,
        }

        logger.info(
            f"B3HttpClient getting broker account extract portfolio - "
            f"username: {self.username} "
            f"broker_value: {broker_value} "
            f"account_id: {account_id}"
        )

        response = await self.session.post(
            self.base_url, data=payload, headers=await self._get_headers()
        )
        logger.info(
            f"B3HttpClient end getting broker account extract portfolio - "
            f"username: {self.username} "
            f"broker_value: {broker_value}"
        )
        return response

    @staticmethod
    async def _get_date_str(broker: Broker, date: Union[date, None]) -> str:
        if (
            date
            and datetime.strptime(broker.parse_extra_data.start_date, "%d/%m/%Y").date()
            <= date
            <= datetime.strptime(broker.parse_extra_data.end_date, "%d/%m/%Y").date()
        ):
            # By some reason, CEI will return some "nonsense" data if
            # we pass a date out of range
            return date.strftime("%d/%m/%Y")
        return broker.parse_extra_data.end_date

    async def get_passive_incomes_extract(
        self, broker: Broker, date: Union[date, None] = None
    ) -> ClientResponse:
        if not self.IS_LOGGED:
            await self.login()

        account = broker.accounts[0]  # accounts[0] it's relative to all accounts
        payload = {
            "ctl00$ContentPlaceHolder1$ToolkitScriptManager1": (
                "ctl00$ContentPlaceHolder1$updFiltro|ctl00$ContentPlaceHolder1"
                "$btnConsultar"
            ),
            "__EVENTTARGET": "",
            "__VIEWSTATE": account.parse_extra_data.view_state,
            "__VIEWSTATEGENERATOR": account.parse_extra_data.view_state_generator,
            "__EVENTVALIDATION": account.parse_extra_data.event_validation,
            "ctl00$ContentPlaceHolder1$ddlAgentes": broker.value,
            "ctl00$ContentPlaceHolder1$ddlContas": account.id,
            "ctl00$ContentPlaceHolder1$txtData": await self._get_date_str(
                broker=broker, date=date
            ),
            "ctl00$ContentPlaceHolder1$btnConsultar": "Consultar",
            "__ASYNCPOST": True,
        }

        return await self.session.post(
            self.base_url, data=payload, headers=await self._get_headers()
        )
