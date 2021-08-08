import asyncio
import logging
from datetime import date
from functools import cached_property
from typing import Any, Dict, List, Type, Union

from aiohttp import ClientSession
from aiohttp.connector import TCPConnector

from bolsa.http_client import B3HttpClient
from bolsa.models import (
    Broker,
    BrokerAccount,
    BrokerAssetExtract,
    PassiveIncome
)
from bolsa.responses import (
    BrokerAccountAssetExtractResponse,
    BrokerAccountResponse,
    BrokerAssetsResponse,
    BrokerPassiveIncomesResponse,
    PassiveIncomesResponse
)

logger = logging.getLogger(__name__)


class BaseCrawler:
    def __init__(
        self,
        connector: TCPConnector,
        username: str,
        password: str,
        captcha_service: Any,
    ) -> None:
        self.connector = connector
        self.username = username
        self.password = password
        self.captcha_service = captcha_service

    @cached_property
    def _session(self) -> ClientSession:
        logger.info(f"Creating session for username: {self.username}")
        return ClientSession(connector=self.connector, connector_owner=False)

    @cached_property
    def _http_client(self) -> B3HttpClient:
        return B3HttpClient(
            username=self.username,
            password=self.password,
            session=self._session,
            captcha_service=self.captcha_service,
            base_url=self.get_base_url(),
        )

    def get_base_url(self) -> str:
        raise NotImplementedError()

    def get_brokers_response_class(self) -> Any:
        raise NotImplementedError()

    def _get_broker_accounts_payload(
        self, broker: Broker
    ) -> Dict[str, Union[str, bool]]:
        raise NotImplementedError()

    async def session_close(self) -> None:
        await self._session.close()

    async def connection_close(self) -> None:
        await self.connector.close()

    async def get_brokers(self) -> List[Broker]:
        response = await self._http_client.get_brokers()
        ResponseClass = self.get_brokers_response_class()

        return await ResponseClass(response).data()

    async def get_broker_accounts(self, broker: Broker) -> Broker:
        logger.info(
            f"B3HttpClient getting brokers account - username: {self.username}"
            f" broker_value: {broker.value}"
        )

        response = await self._http_client.get_broker_accounts(
            self._get_broker_accounts_payload(broker=broker)
        )

        logger.info(
            f"B3HttpClient end getting brokers account - "
            f"username: {self.username} broker_value: {broker.value}"
        )

        return await BrokerAccountResponse(response=response, broker=broker).data()

    async def get_brokers_with_accounts(self) -> List[Broker]:
        brokers = await self.get_brokers()
        tasks = [
            asyncio.create_task(self.get_broker_accounts(broker)) for broker in brokers
        ]

        return await asyncio.gather(*tasks)


class AssetsCrawler(BaseCrawler):
    def get_base_url(self) -> str:
        return "https://ceiapp.b3.com.br/CEI_Responsivo/negociacao-de-ativos.aspx"

    def get_brokers_response_class(self) -> Type[BrokerAssetsResponse]:
        return BrokerAssetsResponse

    def _get_broker_accounts_payload(
        self, broker: Broker
    ) -> Dict[str, Union[str, bool]]:
        default_account = "0"

        return {
            "ctl00$ContentPlaceHolder1$ToolkitScriptManager1": (
                "ctl00$ContentPlaceHolder1$updFiltro|ctl00$ContentPlaceHolder1"
                "$ddlAgentes"
            ),
            "__EVENTTARGET": "ctl00$ContentPlaceHolder1$ddlAgentes",
            "__VIEWSTATE": (
                "/wEPDwUKLTI2MTA0ODczNg9kFgJmD2QWAgIDD2QWCAIBDw8WAh4EVGV4dAUcR"
                "0lPVkFOTkkgQ09STkFDSElOSSBEQSBTSUxWQWRkAgMPZBYCAgEPFgIeB1Zpc2"
                "libGVoZAIFD2QWBAIBDw8WAh8ABRZOZWdvY2lhw6fDo28gZGUgYXRpdm9zZGQ"
                "CAw9kFgICAw8PFgIfAAUzIC8gRXh0cmF0b3MgZSBJbmZvcm1hdGl2b3MgLyBO"
                "ZWdvY2lhw6fDo28gZGUgYXRpdm9zZGQCBw9kFgICBQ9kFgJmD2QWCAIDDxBkE"
                "BUFCVNlbGVjaW9uZR85MCAtIEVBU1lOVkVTVCAtIFRJVFVMTyBDViBTLkEuHj"
                "MgLSBYUCBJTlZFU1RJTUVOVE9TIENDVFZNIFMvQSMzODYgLSBSSUNPIElOVkV"
                "TVElNRU5UT1MgLSBHUlVQTyBYUCAzMDggLSBDTEVBUiBDT1JSRVRPUkEgLSBH"
                "UlVQTyBYUBUFAi0xAjkwATMDMzg2AzMwOBQrAwVnZ2dnZxYBZmQCBQ8QDxYCH"
                "gdFbmFibGVkaGQQFQEMU2VsZWNpb25lLi4uFQEBMBQrAwFnFgFmZAIHDw8WAh"
                "8BZ2QWBAIFDw8WAh8ABQoxNS8wMy8yMDE5ZGQCBw8PFgIfAAUKMDQvMDkvMjA"
                "yMGRkAgkPZBYIAgEPDxYCHwAFCjE1LzAzLzIwMTlkZAIDDw8WAh8ABQowNC8"
                "wOS8yMDIwZGQCBQ8PFgIfAAUKMTUvMDMvMjAxOWRkAgcPDxYCHwAFCjA0LzA5"
                "LzIwMjBkZGRxwKn9JGbY4ybO1hczEjDtoMNWHA=="
            ),
            "__VIEWSTATEGENERATOR": "B345DEBA",
            "__EVENTVALIDATION": (
                "/wEdAA1HJ2+J0WZq5G92xJM7n1xbkdMq+p9EbLSDyFDpFsJg30jWLhbIoNprA"
                "gvONYSktR9kUdPnKtUYGLSZMc/L6M60Vx7WZDZAC7VL6Ff5PQQ8Ml0aq/zmKf"
                "YeYoLRE68kUnN+T4cvEJcdEKVEObT+JUFSdPwdZycbAgmz2rhziqC/I4jipT0"
                "jOBb54glnPZxI9VIJZJh1VhVVa0UQ15FhckhgajRdmhEnQj18gON7y5L4CwGM"
                "p96e++H/oSCxgpNo73nsffQOO+5kepETTltW2pZIXYv2PXYLNUXZnEOvnHkp6"
                "xZ0N94="
            ),
            "ctl00$ContentPlaceHolder1$ddlAgentes": broker.value,
            "ctl00$ContentPlaceHolder1$ddlContas": default_account,
            "ctl00$ContentPlaceHolder1$txtDataDeBolsa": broker.parse_extra_data.start_date,
            "ctl00$ContentPlaceHolder1$txtDataAteBolsa": broker.parse_extra_data.end_date,
            "__ASYNCPOST": True,
        }

    async def get_broker_account_portfolio_assets_extract(
        self,
        broker: Broker,
        account: BrokerAccount,
        start_date: Union[date, None] = None,
        end_date: Union[date, None] = None,
        as_dict: bool = False,
    ) -> Union[List[BrokerAssetExtract], List[Dict[str, Any]]]:
        response = await self._http_client.get_broker_account_portfolio_assets_extract(
            broker=broker,
            account=account,
            start_date=start_date,
            end_date=end_date,
        )
        return await BrokerAccountAssetExtractResponse(
            response=response, broker_value=broker.value
        ).data(as_dict=as_dict)

    async def get_brokers_account_portfolio_assets_extract(
        self,
        brokers: List[Broker],
        start_date: Union[date, None] = None,
        end_date: Union[date, None] = None,
        as_dict: bool = False,
    ) -> Union[List[BrokerAssetExtract], List[Dict[str, Any]]]:
        tasks = [
            asyncio.create_task(
                self.get_broker_account_portfolio_assets_extract(
                    broker=broker,
                    account=broker.accounts[0],
                    start_date=start_date,
                    end_date=end_date,
                    as_dict=as_dict,
                )
            )
            for broker in brokers
            if broker.accounts
        ]

        results = await asyncio.gather(*tasks)
        return [result for subresult in results for result in subresult]


class PassiveIncomesCrawler(BaseCrawler):
    def get_base_url(self) -> str:
        return "https://ceiapp.b3.com.br/CEI_Responsivo/ConsultarProventos.aspx"

    def get_brokers_response_class(self) -> Type[BrokerPassiveIncomesResponse]:
        return BrokerPassiveIncomesResponse

    def _get_broker_accounts_payload(
        self, broker: Broker
    ) -> Dict[str, Union[str, bool]]:
        default_account = "0"

        return {
            "ctl00$ContentPlaceHolder1$ToolkitScriptManager1": (
                "ctl00$ContentPlaceHolder1$updFiltro|ctl00$ContentPlaceHolder1"
                "$ddlAgentes"
            ),
            "__EVENTTARGET": "ctl00$ContentPlaceHolder1$ddlAgentes",
            "__VIEWSTATE": (
                "/wEPDwULLTEwMDg3NTU3MTAPZBYCZg9kFgICAw9kFggCAQ8PFgIeBFRleHQFF1dBR05"
                "FUiBWSUVMTU8gREUgQ0FNUE9TZGQCAw9kFgICAQ8WAh4HVmlzaWJsZWhkAgUPZBYEAgE"
                "PDxYCHwAFCVByb3ZlbnRvc2RkAgMPZBYCAgMPDxYCHwAFHCAvIEludmVzdGltZW50b3M"
                "gLyBQcm92ZW50b3NkZAIHD2QWAgIFD2QWAmYPZBYMAgEPZBYCAgEPEGQQFQMFVG9kb3M"
                "WMTk4MiAtIE1PREFMIERUVk0gTFREQSMzODYgLSBSSUNPIElOVkVTVElNRU5UT1MgLSB"
                "HUlVQTyBYUBUDATAEMTk4MgMzODYUKwMDZ2dnFgFmZAIDD2QWAgIBDxAPFgIeB0VuYWJ"
                "sZWRoZBAVAwVUb2RvcwYzNDUwMzAHMTg1OTAzNhUDATAGMzQ1MDMwBzE4NTkwMzYUKwM"
                "DZ2dnFgFmZAIFDxYCHwFoFgICAQ8QZGQWAGQCBw9kFgYCAQ8PFgQeCENzc0NsYXNzBQp"
                "kYXRlcGlja2VyHgRfIVNCAgJkZAIDDw8WAh8ABQoxNC8wNi8yMDIxZGQCBQ8PFgIfAAU"
                "KMTcvMDYvMjAyMWRkAgsPFgIfAWcWAgIBDw8WAh8ABSFBdHVhbGl6YWRvIGVtIDE3LzA"
                "2LzIwMjEgYXMgMjI6MDlkZAINDxYCHgtfIUl0ZW1Db3VudAIBFgJmD2QWBAIBDw8WAh8"
                "ABSMzODYgLSBSSUNPIElOVkVTVElNRU5UT1MgLSBHUlVQTyBYUGRkAgMPFgIfBQIBFgJ"
                "mD2QWCgIBDw8WAh8ABRNDb250YSBuwrogMTg1OTAzNi05ZGQCAw9kFgICAQ8WAh8FAgI"
                "WBgIBD2QWAmYPFQkMRU5FUkdJQVMgQlIgCk9OICAgICAgTk0MRU5CUjMgICAgICAgCjI"
                "zLzA2LzIwMjEcSlVST1MgU09CUkUgQ0FQSVRBTCBQUsOTUFJJTwU0LDAwMAExBDEsMDg"
                "EMCw5MmQCAg9kFgJmDxUJDEZJSSBDQVBJIFNFQwpDSSAgICAgICAgDENQVFMxMSAgICA"
                "gIAoxOC8wNi8yMDIxClJFTkRJTUVOVE8FMSwwMDABMQQxLDAwBDEsMDBkAgMPZBYEAgE"
                "PDxYCHwAFBDIsMDhkZAIDDw8WAh8ABQQxLDkyZGQCBQ9kFgICAQ8WAh8FAhEWJAIBD2Q"
                "WAmYPFQkMRklJIEJDIEZGSUkgCkNJICAgICAgICAMQkNGRjExICAgICAgCjE1LzA2LzIw"
                "MjEKUkVORElNRU5UTwUzLDAwMAExBDEsNTAEMSw1MGQCAg9kFgJmDxUJDEZJSSBCRUVTI"
                "ENSSQpDSSAgICAgICAgDEJDUkkxMSAgICAgIAoxNS8wNi8yMDIxClJFTkRJTUVOVE8GMT"
                "AsMDAwATEFMTUsOTAFMTUsOTBkAgMPZBYCZg8VCQxGSUkgQ1NIRyBMT0cKQ0kgICAgICAg"
                "IAxIR0xHMTEgICAgICAKMTUvMDYvMjAyMQpSRU5ESU1FTlRPBjExLDAwMAExBTExLDAwBT"
                "ExLDAwZAIED2QWAmYPFQkMRklJIENTSEcgVVJCCkNJICAgICAgICAMSEdSVTExICAgICAg"
                "CjE1LzA2LzIwMjEKUkVORElNRU5UTwYxMCwwMDABMQQ3LDAwBDcsMDBkAgUPZBYCZg8VCQ"
                "xGSUkgREVWQU5UICAKQ0kgICAgICAgIAxERVZBMTEgICAgICAKMTUvMDYvMjAyMQpSRU5E"
                "SU1FTlRPBjIwLDAwMAExBTIyLDAwBTIyLDAwZAIGD2QWAmYPFQkMRklJIERFVkFOVCAgCl"
                "JFQyAgICAgICAMREVWQTEzICAgICAgCjE1LzA2LzIwMjEKUkVORElNRU5UTwYxMSwwMDAB"
                "MQQxLDQzBDEsNDNkAgcPZBYCZg8VCQxGSUkgRkFUT1IgVkUKQ0kgICAgICAgIAxWUlRBMT"
                "EgICAgICAKMTUvMDYvMjAyMQpSRU5ESU1FTlRPBTEsMDAwATEEMSwwNAQxLDA0ZAIID2QW"
                "AmYPFQkMRklJIEhHIFJFQUwgCkNJICAgICAgICAMSEdSRTExICAgICAgCjE1LzA2LzIwMj"
                "EKUkVORElNRU5UTwU2LDAwMAExBDQsMTQENCwxNGQCCQ9kFgJmDxUJDEZJSSBJUklESVVN"
                "IApDSSAgICAgICAgDElSRE0xMSAgICAgIAoxNy8wNi8yMDIxClJFTkRJTUVOVE8GMjgsMD"
                "AwATEFMzIsMzAFMzIsMzBkAgoPZBYCZg8VCQxGSUkgS0lORUEgICAKQ0kgICAgICAgIAxL"
                "TlJJMTEgICAgICAKMTUvMDYvMjAyMQpSRU5ESU1FTlRPBjEwLDAwMAExBDYsOTAENiw5MG"
                "QCCw9kFgJmDxUJDEZJSSBLSU5FQSBJUApDSSAgICAgICAgDEtOSVAxMSAgICAgIAoxNC8w"
                "Ni8yMDIxClJFTkRJTUVOVE8FNSwwMDABMQQ1LDY1BDUsNjVkAgwPZBYCZg8VCQxGSUkgTU"
                "FYSSBSRU4KQ0kgICAgICAgIAxNWFJGMTEgICAgICAKMTUvMDYvMjAyMQpSRU5ESU1FTlRP"
                "BzE2NSwwMDABMQUxMSw1NQUxMSw1NWQCDQ9kFgJmDxUJDEZJSSBUT1JERSBFSQpDSSAgICA"
                "gICAgDFRPUkQxMSAgICAgIAoxNS8wNi8yMDIxClJFTkRJTUVOVE8GNDcsMDAwATEEMywyOQ"
                "QzLDI5ZAIOD2QWAmYPFQkMRklJIFRPUkRFIEVJClJFQyAgICAgICAMVE9SRDEzICAgICAgC"
                "jE1LzA2LzIwMjEKUkVORElNRU5UTwYxNSwwMDABMQQwLDU1BDAsNTVkAg8PZBYCZg8VCQxG"
                "SUkgVkVSUyBDUkkKQ0kgICAgICAgIAxWU0xIMTEgICAgICAKMTUvMDYvMjAyMQpSRU5ESU1"
                "FTlRPBTUsMDAwATEEMCw4NQQwLDg1ZAIQD2QWAmYPFQkMRklJIFZJTkNJTE9HCkNJICAgIC"
                "AgICAMVklMRzExICAgICAgCjE1LzA2LzIwMjEKUkVORElNRU5UTwU0LDAwMAExBDIsMjgEM"
                "iwyOGQCEQ9kFgJmDxUJDEZJSSBYUCBMT0cgIApDSSAgICAgICAgDFhQTEcxMSAgICAgIAox"
                "NS8wNi8yMDIxClJFTkRJTUVOVE8FNiwwMDABMQQzLDY2BDMsNjZkAhIPZBYEAgEPDxYCHwA"
                "FBjEzMSwwNGRkAgMPDxYCHwAFBjEzMSwwNGRkAgcPFgIfAWgWAgIBDxYCHwUC/////w9kAg"
                "kPZBYCAgEPFgIfBQIBFgQCAQ9kFgJmDxULDEZJSSBUT1JERSBFSQpSRUMgICAgICAgDFRPU"
                "kQxMyAgICAgIAtBVFVBTElaQUNBTwoxNy8wNi8yMDIxBjE1LDAwMAExDFRPUkQxMSAgICAg"
                "IAUxNSwwMAYxMDAsMDAEMCwwMGQCAg9kFgICAQ8PFgIfAAUEMCwwMGRkZNmTebZZFDui/ij"
                "Eax1lX4ugM/e1"
            ),
            "__VIEWSTATEGENERATOR": "60D025E9",
            "__EVENTVALIDATION": (
                "/wEdAAz3Yx2ES4cT5dCIgXUVBTgKSNYuFsig2msCC841hKS1H1GNyhN3N1osq"
                "BqqgaNItpdZDO+9C9gz5Aw/AZYSIzXhfk+HLxCXHRClRDm0/iVBUojipT0jOB"
                "b54glnPZxI9VIJZJh1VhVVa0UQ15FhckhgY2JNro3bvLeSMJrpn9aSiHkRxwu"
                "EE8o8LwrE2E6mACtDmhxe4pZ6Ibt8oBWfF3Ts7H30DjvuZHqRE05bVtqWSPOO"
                "FWTf/Hn+MVE/ujXYFJTWLVokCvgbtFxjrfYgYXuQJX3w9w=="
            ),
            "ctl00$ContentPlaceHolder1$ddlAgentes": broker.value,
            "ctl00$ContentPlaceHolder1$ddlContas": default_account,
            "ctl00$ContentPlaceHolder1$txtData": broker.parse_extra_data.end_date,
            "__ASYNCPOST": True,
        }

    async def get_passive_incomes_extract(
        self, date: Union[date, None] = None, as_dict: bool = False
    ) -> Union[List[PassiveIncome], List[Dict[str, Any]]]:
        brokers = await self.get_brokers_with_accounts()
        response = await self._http_client.get_passive_incomes_extract(
            broker=brokers[0],  # brokers[0] is the broker with all accounts
            date=date,
        )

        return await PassiveIncomesResponse(response=response).data(as_dict=as_dict)
