import pytest

from bolsa.constants import (
    ASSET_ACTION_TYPE_MAPPER,
    ASSET_MARKET_TYPE_MAPPER,
    PASSIVE_INCOME_EVENT_TYPE_MAPPER,
    PASSIVE_INCOME_TYPE_MAPPER,
    BrokerAssetExtractAction,
    BrokerAssetExtractMarketType,
    PassiveIncomeEventType,
    PassiveIncomeType
)


class TestConstantsMapper:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "key, expected_value",
        [
            ("C", BrokerAssetExtractAction.BUY.value),
            ("V", BrokerAssetExtractAction.SELL.value),
        ],
    )
    async def test_asset_action_type_mapper(self, key, expected_value):
        assert ASSET_ACTION_TYPE_MAPPER[key] == expected_value

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "key, expected_value",
        [
            ("Merc. Fracionário", BrokerAssetExtractMarketType.FRACTIONAL.value),
            ("Mercado a Vista", BrokerAssetExtractMarketType.UNIT.value),
        ],
    )
    async def test_asset_market_type_mapper(self, key, expected_value):
        assert ASSET_MARKET_TYPE_MAPPER[key] == expected_value

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "key, expected_value",
        [
            ("DIVIDENDO", PassiveIncomeEventType.DIVIDEND.value),
            ("JUROS SOBRE CAPITAL PRÓPRIO", PassiveIncomeEventType.JCP.value),
            ("RENDIMENTO", PassiveIncomeEventType.YIELD.value),
        ],
    )
    async def test_passive_income_event_type_mapper(self, key, expected_value):
        assert PASSIVE_INCOME_EVENT_TYPE_MAPPER[key] == expected_value

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "key, expected_value",
        [
            ("Provisionado", PassiveIncomeType.FUTURE.value),
            ("Creditado", PassiveIncomeType.PAST.value),
        ],
    )
    async def test_passive_income_type_mapper(self, key, expected_value):
        assert PASSIVE_INCOME_TYPE_MAPPER[key] == expected_value
