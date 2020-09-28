from datetime import date
from decimal import Decimal

from bolsa.constants import (
    BrokerAssetExtractAction,
    BrokerAssetExtractMarketType
)
from bolsa.models import BrokerAssetExtract


class TestBrokerAssetExtract:

    async def test_create_object_from_response_data(self):
        action = 'C'
        asset_specification = 'AZUL        PN      N2'
        market_type = 'Merc. Fracionário'
        operation_date = '05/06/2020'
        quotation_factor = '1'
        raw_negotiation_code = 'AZUL4F'
        total_price = '42,18'
        unit_amount = '2'
        unit_price = '21,09'

        expected_obj = BrokerAssetExtract(
            action=BrokerAssetExtractAction.BUY.value,
            asset_specification=asset_specification,
            market_type=BrokerAssetExtractMarketType.FRACTIONAL.value,
            operation_date=date(2020, 6, 5),
            quotation_factor=1,
            raw_negotiation_code=raw_negotiation_code,
            total_price=Decimal('42.18'),
            unit_amount=2,
            unit_price=Decimal('21.09')
        )

        broker_asset_extract = BrokerAssetExtract.create_from_response_fields(
            action=action,
            asset_specification=asset_specification,
            market_type=market_type,
            operation_date=operation_date,
            quotation_factor=quotation_factor,
            raw_negotiation_code=raw_negotiation_code,
            total_price=total_price,
            unit_amount=unit_amount,
            unit_price=unit_price
        )

        assert broker_asset_extract == expected_obj

    async def test_format_string_to_decimal_with_high_value(self):
        expected_value = Decimal('1485.12')
        unit_price = '1.485.12'

        value = BrokerAssetExtract._format_string_to_decimal(unit_price)

        assert value == expected_value
