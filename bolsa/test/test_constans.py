import pytest

from bolsa.constants import (
    ASSET_ACTION_TYPE_MAPPER,
    ASSET_MARKET_TYPE_MAPPER,
    BrokerAssetExtractAction,
    BrokerAssetExtractMarketType
)


class TestConstantsMapper:

    @pytest.mark.parametrize(
        'key, expected_value',
        [
            ('C', BrokerAssetExtractAction.BUY.value),
            ('V', BrokerAssetExtractAction.SELL.value)
        ]
    )
    async def test_asset_action_type_mapper(self, key, expected_value):
        assert ASSET_ACTION_TYPE_MAPPER[key] == expected_value

    @pytest.mark.parametrize('key, expected_value',
                             [('Merc. Fracionário',
                               BrokerAssetExtractMarketType.FRACTIONAL.value),
                              ('Mercado a Vista',
                                 BrokerAssetExtractMarketType.UNIT.value)])
    async def test_asset_market_type_mapper(self, key, expected_value):
        assert ASSET_MARKET_TYPE_MAPPER[key] == expected_value
