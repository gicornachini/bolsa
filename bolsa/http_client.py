import logging

from bs4 import BeautifulSoup

from bolsa.connector import B3HttpClientConnector

logger = logging.getLogger(__name__)

POOL_CONNECTOR = B3HttpClientConnector()


class B3HttpClient():
    IS_LOGGED = False
    SESSION = None
    LOGIN_URL = 'https://ceiapp.b3.com.br/CEI_Responsivo/login.aspx'

    ASSETS_HOME_URL = (
        'https://ceiapp.b3.com.br/CEI_Responsivo/negociacao-de-ativos.aspx'
    )
    BROKERS_ACCOUNT_URL = (
        'https://ceiapp.b3.com.br/CEI_Responsivo/negociacao-de-ativos.aspx'
    )
    ASSETS_URL = (
        'https://ceiapp.b3.com.br/CEI_Responsivo/negociacao-de-ativos.aspx'
    )

    def __init__(self, username, password, session, captcha_service):
        self.username = username
        self.password = password
        self.session = session
        self.captcha_service = captcha_service

    async def login(self):
        async with self.session.get(
            self.LOGIN_URL
        ) as response:
            loginPageContent = await response.text()
            loginPageParsed = BeautifulSoup(loginPageContent, "html.parser")
            view_state = loginPageParsed.find(id='__VIEWSTATE')['value']
            viewstate_generator = loginPageParsed.find(
                id='__VIEWSTATEGENERATOR'
            )['value']
            event_validation = loginPageParsed.find(
                id='__EVENTVALIDATION'
            )['value']

            solvedcaptcha = None
            if self.captcha_service:
                site_key = loginPageParsed.find(
                    id='ctl00_ContentPlaceHolder1_dvCaptcha'
                ).get(
                    'data-sitekey'
                )
                solvedcaptcha = await self.captcha_service.resolve(
                    site_key,
                    self.LOGIN_URL
                )

        payload = {
            'ctl00$ContentPlaceHolder1$smLoad': (
                'ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHold'
                'er1$btnLogar'
            ),
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATEGENERATOR': viewstate_generator,
            '__EVENTVALIDATION': event_validation,
            '__VIEWSTATE': view_state,
            'ctl00$ContentPlaceHolder1$txtLogin': self.username,
            'ctl00$ContentPlaceHolder1$txtSenha': self.password,
            '__ASYNCPOST': True,
            'g-recaptcha-response': solvedcaptcha,
            'ctl00$ContentPlaceHolder1$btnLogar': 'Entrar'
        }

        headers = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://cei.b3.com.br/CEI_Responsivo/login.aspx',
            'Origin': 'https://cei.b3.com.br',
            'Host': 'cei.b3.com.br',
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 '
                'Safari/537.36'
            ),
        }

        logger.info(f'B3HttpClient doing login - username: {self.username}')

        async with self.session.post(
            self.LOGIN_URL,
            data=payload,
            headers=headers,
        ) as response:
            logger.info(f'B3HttpClient login done - username: {self.username}')

            self.IS_LOGGED = True

            return await response.text()

    async def get_brokers(self):
        if not self.IS_LOGGED:
            await self.login()

        logger.info(
            f'B3HttpClient getting brokers - username: {self.username}'
        )

        response = await self.session.get(self.ASSETS_HOME_URL)
        logger.info(
            f'B3HttpClient end getting brokers - username: {self.username}'
        )

        return response

    async def get_broker_accounts(self, broker):
        if not self.IS_LOGGED:
            await self.login()

        default_account = '0'
        start_date = broker.parse_extra_data.start_date
        end_date = broker.parse_extra_data.end_date

        payload = {
            'ctl00$ContentPlaceHolder1$ToolkitScriptManager1': (
                'ctl00$ContentPlaceHolder1$updFiltro|ctl00$ContentPlaceHolder1'
                '$ddlAgentes'
            ),
            '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$ddlAgentes',
            '__VIEWSTATE': (
                '/wEPDwUKLTI2MTA0ODczNg9kFgJmD2QWAgIDD2QWCAIBDw8WAh4EVGV4dAUcR'
                '0lPVkFOTkkgQ09STkFDSElOSSBEQSBTSUxWQWRkAgMPZBYCAgEPFgIeB1Zpc2'
                'libGVoZAIFD2QWBAIBDw8WAh8ABRZOZWdvY2lhw6fDo28gZGUgYXRpdm9zZGQ'
                'CAw9kFgICAw8PFgIfAAUzIC8gRXh0cmF0b3MgZSBJbmZvcm1hdGl2b3MgLyBO'
                'ZWdvY2lhw6fDo28gZGUgYXRpdm9zZGQCBw9kFgICBQ9kFgJmD2QWCAIDDxBkE'
                'BUFCVNlbGVjaW9uZR85MCAtIEVBU1lOVkVTVCAtIFRJVFVMTyBDViBTLkEuHj'
                'MgLSBYUCBJTlZFU1RJTUVOVE9TIENDVFZNIFMvQSMzODYgLSBSSUNPIElOVkV'
                'TVElNRU5UT1MgLSBHUlVQTyBYUCAzMDggLSBDTEVBUiBDT1JSRVRPUkEgLSBH'
                'UlVQTyBYUBUFAi0xAjkwATMDMzg2AzMwOBQrAwVnZ2dnZxYBZmQCBQ8QDxYCH'
                'gdFbmFibGVkaGQQFQEMU2VsZWNpb25lLi4uFQEBMBQrAwFnFgFmZAIHDw8WAh'
                '8BZ2QWBAIFDw8WAh8ABQoxNS8wMy8yMDE5ZGQCBw8PFgIfAAUKMDQvMDkvMjA'
                'yMGRkAgkPZBYIAgEPDxYCHwAFCjE1LzAzLzIwMTlkZAIDDw8WAh8ABQowNC8'
                'wOS8yMDIwZGQCBQ8PFgIfAAUKMTUvMDMvMjAxOWRkAgcPDxYCHwAFCjA0LzA5'
                'LzIwMjBkZGRxwKn9JGbY4ybO1hczEjDtoMNWHA=='
            ),
            '__VIEWSTATEGENERATOR': 'B345DEBA',
            '__EVENTVALIDATION': (
                '/wEdAA1HJ2+J0WZq5G92xJM7n1xbkdMq+p9EbLSDyFDpFsJg30jWLhbIoNprA'
                'gvONYSktR9kUdPnKtUYGLSZMc/L6M60Vx7WZDZAC7VL6Ff5PQQ8Ml0aq/zmKf'
                'YeYoLRE68kUnN+T4cvEJcdEKVEObT+JUFSdPwdZycbAgmz2rhziqC/I4jipT0'
                'jOBb54glnPZxI9VIJZJh1VhVVa0UQ15FhckhgajRdmhEnQj18gON7y5L4CwGM'
                'p96e++H/oSCxgpNo73nsffQOO+5kepETTltW2pZIXYv2PXYLNUXZnEOvnHkp6'
                'xZ0N94='
            ),
            'ctl00$ContentPlaceHolder1$ddlAgentes': broker.value,
            'ctl00$ContentPlaceHolder1$ddlContas': default_account,
            'ctl00$ContentPlaceHolder1$txtDataDeBolsa': start_date,
            'ctl00$ContentPlaceHolder1$txtDataAteBolsa': end_date,
            '__ASYNCPOST': True
        }
        headers = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': (
                'https://cei.b3.com.br/CEI_Responsivo/negociacao-de-ativos.asp'
                'x'
            ),
            'Origin': 'https://cei.b3.com.br',
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 '
                'Safari/537.36')}

        logger.info(
            f'B3HttpClient getting brokers account - username: {self.username}'
            f' broker_value: {broker.value}'
        )

        response = await self.session.post(
            self.BROKERS_ACCOUNT_URL,
            data=payload,
            headers=headers
        )

        logger.info(
            f'B3HttpClient end getting brokers account - '
            f'username: {self.username} broker_value: {broker.value}'
        )

        return response

    async def get_broker_account_portfolio_assets_extract(
        self,
        account_id,
        broker_value,
        broker_parse_extra_data,
        account_parse_extra_data
    ):
        if not self.IS_LOGGED:
            await self.login()

        start_date = broker_parse_extra_data.start_date
        end_date = broker_parse_extra_data.end_date

        payload = {
            'ctl00$ContentPlaceHolder1$ToolkitScriptManager1': (
                'ctl00$ContentPlaceHolder1$updFiltro|ctl00$ContentPlaceHolder1'
                '$btnConsultar'
            ),
            '__EVENTTARGET': '',
            '__VIEWSTATE': account_parse_extra_data.view_state,
            '__VIEWSTATEGENERATOR': (
                account_parse_extra_data.view_state_generator
            ),
            '__EVENTVALIDATION': account_parse_extra_data.event_validation,
            'ctl00$ContentPlaceHolder1$ddlAgentes': broker_value,
            'ctl00$ContentPlaceHolder1$ddlContas': account_id,
            'ctl00$ContentPlaceHolder1$txtDataDeBolsa': start_date,
            'ctl00$ContentPlaceHolder1$txtDataAteBolsa': end_date,
            'ctl00$ContentPlaceHolder1$btnConsultar': 'Consultar',
            '__ASYNCPOST': True}

        headers = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': (
                'https://cei.b3.com.br/CEI_Responsivo/negociacao-de-ativos.as'
                'px'
            ),
            'Origin': 'https://cei.b3.com.br',
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 '
                'Safari/537.36')}

        logger.info(
            f'B3HttpClient getting broker account extract portfolio - '
            f'username: {self.username} '
            f'broker_value: {broker_value} '
            f'account_id: {account_id}'
        )

        response = await self.session.post(
            self.ASSETS_URL,
            data=payload,
            headers=headers
        )
        logger.info(
            f'B3HttpClient end getting broker account extract portfolio - '
            f'username: {self.username} '
            f'broker_value: {broker_value}'
        )
        return response
