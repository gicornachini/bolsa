# Bolsa - Acesse facilmente seus investimentos na B3/CEI
Biblioteca feita em python com o objetivo de facilitar o acesso a dados de seus investimentos na bolsa de valores(B3/CEI).

![image](https://i.imgur.com/TBpVWm3.png)

# Requisitos
 - Python 3.8.x

## Instalação
```
$ pip install bolsa
```
Atualmente implementado usando [Asyncio](https://docs.python.org/3/library/asyncio.html) do Python.

## Como utilizar
Veja como é simples utilizar:
```python
from bolsa import B3AsyncBackend


b3_httpclient = B3AsyncBackend(
    username='SEU CPF/CNPJ',
    password='SUA SENHA',
    captcha_service=None  # `captcha_service` não é obrigatório ainda
)

brokers = await b3_httpclient.get_brokers_with_accounts()
assets_extract = (
    await b3_httpclient.get_brokers_account_portfolio_assets_extract(
        brokers=brokers
    )
)

print(assets_extract) # Todos os seus ativos consolidados no CEI

await b3_httpclient.session_close()
await b3_httpclient.connection_close()
```
Você pode acessar exemplos completos clicando [aqui](https://github.com/gicornachini/bolsa/tree/master/examples).


### Funções disponíveis

Através da classe de client `B3AsyncBackend`, você terá acesso as seguintes funções:

| Função        |  Parâmetros          | Descrição  |
| ------------- |:-------------:| -----|
| get_brokers      | - | Obtém os brokers disponíveis para aquela conta. Retorna um objeto Broker. (Ex: XP Inc, Clear, Easynvest...). |
| get_broker_accounts      | broker      |   Através de um broker passado como parâmetro, obtém suas respectivas contas na B3. Retorna um `Broker` com uma lista de `BrokerAccount`. |
| get_brokers_with_accounts | - | É uma junção entre os métodos `get_brokers` e `get_broker_accounts`. Retorna uma lista de `Broker` com uma lista de `BrokerAccount`. |
| get_broker_account_portfolio_assets_extract | account_id: Número da conta no broker, broker_value: id do broker, broker_parse_extra_data: dados obtidos junto ao broker, account_parse_extra_data: dados obtidos junto a conta na corretora. | Utilizado para obter todos os dados de ativos consolidados na b3. Retorna uma lista de `BrokerAssetExtract`. |
| get_brokers_account_portfolio_assets_extract | brokers      | Através dos brokers passados por parâmetro, é obtido uma lista de ativos para cada broker. Retorna uma lista de `BrokerAssetExtract`. |


### Models

#### Broker
Model responsável pelos dados do broker.

| Atributo        | Tipo           | Descrição  |
| :-------------: |:-------------:| -----|
| value      | str | Identificador da corretora na B3. |
| name      | str      |   Nome do broker na B3. |
| accounts | list      |    Lista de contas no broker. |


#### BrokerAccount
Model responsável pelos dados da conta no broker.

| Atributo        | Tipo           | Descrição  |
| :-------------: |:-------------:| -----|
| id      | str | Número da conta no broker. |


#### BrokerAssetExtract
Model responsável pelos dados do ativo.

| Atributo        | Tipo           | Descrição  |
| :-------------: |:-------------:| -----|
| operation_date      | datetime | Data de operação do ativo. |
| action      | BrokerAssetExtractAction      |   Identificador do tipo de operação compra/venda. |
| market_type | BrokerAssetExtractMarketType      |   Tipo de mercado, a vista ou fracionário. |
| raw_negotiation_code | str      |    Código de negociação. |
| asset_specification | str      |    Especificação do ativo no CEI. |
| unit_amount | int      |    Quantidade de ativo. |
| unit_price | decimal      |    Valor unitário do ativo. |
| total_price | decimal      |    Valor total do ativo. |
| quotation_factor | int      |    Fator de cotação. |
