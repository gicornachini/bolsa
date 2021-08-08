import logging
from datetime import date, datetime
from typing import Union
from urllib.parse import urljoin, urlparse

from aiohttp.client_reqrep import ClientResponse
from bs4 import BeautifulSoup

from bolsa.connector import B3HttpClientConnector
from bolsa.exceptions import B3UnableToLoginException
from bolsa.models import Broker, BrokerAccount

logger = logging.getLogger(__name__)

POOL_CONNECTOR = B3HttpClientConnector()


class B3HttpClient:
    IS_LOGGED = False
    SESSION = None
    LOGIN_URL = "https://ceiapp.b3.com.br/CEI_Responsivo/login.aspx"
    _HEADERS_ORIGIN_URL = "https://cei.b3.com.br"

    def __init__(self, username, password, session, captcha_service, base_url):
        self.username = username
        self.password = password
        self.session = session
        self.captcha_service = captcha_service
        self.base_url = base_url

    def _get_referer(self):
        return urljoin(self._HEADERS_ORIGIN_URL, urlparse(self.base_url).path)

    def _get_headers(self):
        return {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": self._get_referer(),
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
            try:
                view_state = loginPageParsed.find(id="__VIEWSTATE")["value"]
                viewstate_generator = loginPageParsed.find(id="__VIEWSTATEGENERATOR")[
                    "value"
                ]
                event_validation = loginPageParsed.find(id="__EVENTVALIDATION")["value"]
            except TypeError as e:
                raise B3UnableToLoginException(repr(e))

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
            "Origin": self._HEADERS_ORIGIN_URL,
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

    async def get_brokers(self):
        if not self.IS_LOGGED:
            await self.login()

        logger.info(f"B3HttpClient getting brokers - username: {self.username}")

        response = await self.session.get(self.base_url)
        logger.info(f"B3HttpClient end getting brokers - username: {self.username}")

        return response

    async def get_broker_accounts(self, payload):
        if not self.IS_LOGGED:
            await self.login()

        return await self.session.post(
            self.base_url, data=payload, headers=self._get_headers()
        )

    async def get_broker_account_portfolio_assets_extract(
        self,
        broker: Broker,
        account: BrokerAccount,
        start_date: Union[date, None] = None,
        end_date: Union[date, None] = None,
    ):
        if not self.IS_LOGGED:
            await self.login()

        start_date_str = (
            start_date.strftime("%d/%m/%Y")
            if start_date is not None
            else broker.parse_extra_data.start_date
        )
        end_date_str = (
            end_date.strftime("%d/%m/%Y")
            if end_date is not None
            else broker.parse_extra_data.end_date
        )

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
            "ctl00$ContentPlaceHolder1$txtDataDeBolsa": start_date_str,
            "ctl00$ContentPlaceHolder1$txtDataAteBolsa": end_date_str,
            "ctl00$ContentPlaceHolder1$btnConsultar": "Consultar",
            "__ASYNCPOST": True,
        }

        logger.info(
            f"B3HttpClient getting broker account extract portfolio - "
            f"username: {self.username} "
            f"broker_value: {broker.value} "
            f"account_id: {account.id}"
        )

        response = await self.session.post(
            self.base_url, data=payload, headers=self._get_headers()
        )
        logger.info(
            f"B3HttpClient end getting broker account extract portfolio - "
            f"username: {self.username} "
            f"broker_value: {broker.value}"
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
            self.base_url, data=payload, headers=self._get_headers()
        )
