from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List

from bolsa.constants import (
    ASSET_ACTION_TYPE_MAPPER,
    ASSET_MARKET_TYPE_MAPPER,
    BrokerAssetExtractAction,
    BrokerAssetExtractMarketType
)


@dataclass
class BrokerParseExtraData():
    start_date: str
    end_date: str


@dataclass
class Broker():
    value: str
    name: str
    parse_extra_data: BrokerParseExtraData
    accounts: List = field(default_factory=lambda: [])


@dataclass
class BrokerAccountParseExtraData():
    """ Essential data to do other requests using account information. """

    view_state: str
    view_state_generator: str
    event_validation: str


@dataclass
class BrokerAccount():
    id: str
    parse_extra_data: BrokerAccountParseExtraData


@dataclass
class BrokerAssetExtract():
    operation_date: datetime
    action: BrokerAssetExtractAction
    market_type: BrokerAssetExtractMarketType
    raw_negotiation_code: str
    asset_specification: str
    unit_amount: int
    unit_price: Decimal
    total_price: Decimal
    quotation_factor: int

    @classmethod
    def create_from_response_fields(
        cls,
        operation_date,
        action,
        market_type,
        raw_negotiation_code,
        asset_specification,
        unit_amount,
        unit_price,
        total_price,
        quotation_factor
    ):
        action = ASSET_ACTION_TYPE_MAPPER[action]
        market_type = ASSET_MARKET_TYPE_MAPPER[market_type]
        operation_date = datetime.strptime(operation_date, '%d/%m/%Y').date()
        total_price = cls._format_string_to_decimal(total_price)
        unit_price = cls._format_string_to_decimal(unit_price)
        unit_amount = int(unit_amount)
        quotation_factor = int(quotation_factor)

        return cls(
            operation_date=operation_date,
            action=action,
            market_type=market_type,
            raw_negotiation_code=raw_negotiation_code,
            asset_specification=asset_specification,
            unit_amount=unit_amount,
            unit_price=unit_price,
            total_price=total_price,
            quotation_factor=quotation_factor
        )

    @staticmethod
    def _format_string_to_decimal(value):
        value = value.replace(',', '').replace('.', '')
        value = f'{value[:-2]}.{value[-2:]}'
        return Decimal(value)
