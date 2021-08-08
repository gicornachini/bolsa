from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List

from bolsa.constants import (
    ASSET_ACTION_TYPE_MAPPER,
    ASSET_MARKET_TYPE_MAPPER,
    PASSIVE_INCOME_EVENT_TYPE_MAPPER,
    PASSIVE_INCOME_TYPE_MAPPER,
    BrokerAssetExtractAction,
    BrokerAssetExtractMarketType,
    PassiveIncomeEventType,
    PassiveIncomeType,
)


@dataclass
class BrokerParseExtraData:
    start_date: str
    end_date: str


@dataclass
class Broker:
    value: str
    name: str
    parse_extra_data: BrokerParseExtraData
    accounts: List = field(default_factory=lambda: [])


@dataclass
class BrokerAccountParseExtraData:
    """Essential data to do other requests using account information."""

    view_state: str
    view_state_generator: str
    event_validation: str


@dataclass
class BrokerAccount:
    id: str
    parse_extra_data: BrokerAccountParseExtraData


async def _format_string_to_decimal(value: str) -> Decimal:
    value = value.replace(",", "").replace(".", "")
    value = f"{value[:-2]}.{value[-2:]}"
    return Decimal(value)


async def _remove_extra_space(text: str) -> str:
    return re.sub(" +", " ", text)


@dataclass
class BrokerAssetExtract:
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
    async def create_from_response_fields(
        cls,
        operation_date,
        action,
        market_type,
        raw_negotiation_code,
        asset_specification,
        unit_amount,
        unit_price,
        total_price,
        quotation_factor,
    ) -> BrokerAssetExtract:
        action = ASSET_ACTION_TYPE_MAPPER[action]
        market_type = ASSET_MARKET_TYPE_MAPPER[market_type]
        asset_specification = await _remove_extra_space(asset_specification)
        operation_date = datetime.strptime(operation_date, "%d/%m/%Y").date()
        total_price = await _format_string_to_decimal(total_price)
        unit_price = await _format_string_to_decimal(unit_price)
        unit_amount = await cls._format_string_to_int(unit_amount)
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
            quotation_factor=quotation_factor,
        )

    @staticmethod
    async def _format_string_to_int(value: str) -> int:
        return int(value.replace(".", ""))


@dataclass
class PassiveIncome:
    raw_negotiation_name: str
    asset_specification: str
    raw_negotiation_code: str
    operation_date: datetime
    event_type: PassiveIncomeEventType
    unit_amount: int
    quotation_factor: int
    gross_value: Decimal
    net_value: Decimal
    income_type: PassiveIncomeType

    @classmethod
    async def create_from_response_fields(
        cls,
        raw_negotiation_name,
        asset_specification,
        raw_negotiation_code,
        operation_date,
        event_type,
        unit_amount,
        quotation_factor,
        gross_value,
        net_value,
        income_type,
    ) -> PassiveIncome:
        asset_specification = await _remove_extra_space(asset_specification)
        operation_date = datetime.strptime(operation_date, "%d/%m/%Y").date()
        event_type = PASSIVE_INCOME_EVENT_TYPE_MAPPER.get(event_type)
        unit_amount = await cls._format_string_to_int(unit_amount)
        quotation_factor = int(quotation_factor)
        gross_value = await _format_string_to_decimal(gross_value)
        net_value = await _format_string_to_decimal(net_value)
        income_type = PASSIVE_INCOME_TYPE_MAPPER.get(income_type)

        return cls(
            raw_negotiation_name=raw_negotiation_name,
            asset_specification=asset_specification,
            raw_negotiation_code=raw_negotiation_code,
            operation_date=operation_date,
            event_type=event_type,
            unit_amount=unit_amount,
            quotation_factor=quotation_factor,
            gross_value=gross_value,
            net_value=net_value,
            income_type=income_type,
        )

    @staticmethod
    async def _format_string_to_int(value: str) -> int:
        return int(value.split(",")[0].replace(".", ""))
