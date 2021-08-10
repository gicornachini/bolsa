from enum import Enum, unique


@unique
class BrokerAssetExtractAction(Enum):
    BUY = "buy"
    SELL = "sell"


@unique
class BrokerAssetExtractMarketType(Enum):
    FRACTIONAL = "fractional_share"
    UNIT = "unit"
    OPTIONS = "options"


ASSET_ACTION_TYPE_MAPPER = {
    "C": BrokerAssetExtractAction.BUY.value,
    "V": BrokerAssetExtractAction.SELL.value,
}

ASSET_MARKET_TYPE_MAPPER = {
    "Merc. Fracionário": BrokerAssetExtractMarketType.FRACTIONAL.value,
    "Mercado a Vista": BrokerAssetExtractMarketType.UNIT.value,
    "Opção de Compra": BrokerAssetExtractMarketType.OPTIONS.value,
    "Opção de Venda": BrokerAssetExtractMarketType.OPTIONS.value,
    "Exercicio de Opções": BrokerAssetExtractMarketType.OPTIONS.value,
}


@unique
class PassiveIncomeType(Enum):
    FUTURE = "provisioned"
    PAST = "credited"


PASSIVE_INCOME_TYPE_MAPPER = {
    "Provisionado": PassiveIncomeType.FUTURE.value,
    "Creditado": PassiveIncomeType.PAST.value,
}


@unique
class PassiveIncomeEventType(Enum):
    DIVIDEND = "dividend"
    JCP = "jcp"
    YIELD = "FII yield"


PASSIVE_INCOME_EVENT_TYPE_MAPPER = {
    "DIVIDENDO": PassiveIncomeEventType.DIVIDEND.value,
    "JUROS SOBRE CAPITAL PRÓPRIO": PassiveIncomeEventType.JCP.value,
    "RENDIMENTO": PassiveIncomeEventType.YIELD.value,
}
