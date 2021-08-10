from datetime import date
from decimal import Decimal

import pytest

from bolsa.constants import (
    BrokerAssetExtractAction,
    BrokerAssetExtractMarketType,
    PassiveIncomeEventType,
    PassiveIncomeType
)
from bolsa.models import (
    BrokerAssetExtract,
    PassiveIncome,
    _format_string_to_decimal
)


class TestBrokerAssetExtract:
    @pytest.mark.asyncio
    async def test_create_asset_from_response_data(self):
        action = "C"
        asset_specification = "AZUL        PN      N2"
        market_type = "Merc. Fracionário"
        operation_date = "05/06/2020"
        quotation_factor = "1"
        raw_negotiation_code = "AZUL4F"
        total_price = "42,18"
        unit_amount = "2"
        unit_price = "21,09"

        expected_obj = BrokerAssetExtract(
            action=BrokerAssetExtractAction.BUY.value,
            asset_specification="AZUL PN N2",
            market_type=BrokerAssetExtractMarketType.FRACTIONAL.value,
            operation_date=date(2020, 6, 5),
            quotation_factor=1,
            raw_negotiation_code=raw_negotiation_code,
            total_price=Decimal("42.18"),
            unit_amount=2,
            unit_price=Decimal("21.09"),
        )

        broker_asset_extract = await BrokerAssetExtract.create_from_response_fields(
            action=action,
            asset_specification=asset_specification,
            market_type=market_type,
            operation_date=operation_date,
            quotation_factor=quotation_factor,
            raw_negotiation_code=raw_negotiation_code,
            total_price=total_price,
            unit_amount=unit_amount,
            unit_price=unit_price,
        )

        assert broker_asset_extract == expected_obj

    @pytest.mark.asyncio
    async def test_format_string_to_decimal_with_high_value(self):
        expected_value = Decimal("1485.12")
        unit_price = "1.485.12"

        value = await _format_string_to_decimal(unit_price)

        assert value == expected_value

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "expected_value, unit_amount",
        [(1, "1"), (1100, "1.100"), (1000000, "1.000.000")],
    )
    async def test_should_format_asset_string_to_int(self, expected_value, unit_amount):
        # GIVEN

        # WHEN
        value = await BrokerAssetExtract._format_string_to_int(unit_amount)

        # THEN
        assert value == expected_value

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "expected_value, unit_amount",
        [
            (1, "1,00"),
            (100, "100,00"),
            (1100, "1.100,00"),
            (1000000, "1.000.000,00"),
        ],
    )
    async def test_should_format_passive_income_string_to_int(
        self, expected_value, unit_amount
    ):
        # GIVEN

        # WHEN
        value = await PassiveIncome._format_string_to_int(unit_amount)

        # THEN
        assert value == expected_value

    @pytest.mark.asyncio
    async def test_create_passive_income_from_response_data(self):
        # GIVEN
        raw_negotiation_name = "ALUPAR"
        asset_specification = "UNT      N2"
        raw_negotiation_code = "ALUP11"
        operation_date = "05/06/2020"
        event_type = "DIVIDENDO"
        unit_amount = "2"
        quotation_factor = "1"
        gross_value = "35,70"
        net_value = "35,70"
        income_type = "Provisionado"

        expected_obj = PassiveIncome(
            raw_negotiation_name=raw_negotiation_name,
            asset_specification="UNT N2",
            raw_negotiation_code=raw_negotiation_code,
            operation_date=date(2020, 6, 5),
            event_type=PassiveIncomeEventType.DIVIDEND.value,
            unit_amount=2,
            quotation_factor=1,
            gross_value=Decimal("35.70"),
            net_value=Decimal("35.70"),
            income_type=PassiveIncomeType.FUTURE.value,
        )

        # WHEN
        passive_income = await PassiveIncome.create_from_response_fields(
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

        # THEN
        assert passive_income == expected_obj
