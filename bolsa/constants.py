from enum import Enum, unique


@unique
class BrokerAssetExtractAction(Enum):
    BUY = 'buy'
    SELL = 'sell'


@unique
class BrokerAssetExtractMarketType(Enum):
    FRACTIONAL = 'fractional_share'
    UNIT = 'unit'
    OPTIONS = 'options'


ASSET_ACTION_TYPE_MAPPER = {
    'C': BrokerAssetExtractAction.BUY.value,
    'V': BrokerAssetExtractAction.SELL.value,
}

ASSET_MARKET_TYPE_MAPPER = {
    'Merc. Fracionário': BrokerAssetExtractMarketType.FRACTIONAL.value,
    'Mercado a Vista': BrokerAssetExtractMarketType.UNIT.value,
    'Opção de Compra': BrokerAssetExtractMarketType.OPTIONS.value,
    'Opção de Venda': BrokerAssetExtractMarketType.OPTIONS.value,
    'Exercicio de Opções': BrokerAssetExtractMarketType.OPTIONS.value
}
