# Bolsa - Acesse facilmente seus investimentos na B3/CEI
Biblioteca feita em python com o objetivo de facilitar o acesso a dados de seus investimentos na bolsa de valores(B3/CEI).

# Requisitos
 - Python 3.8.x

## Instalação
```
$ pip install bolsa
```
Atualmente implementado usando [Asyncio](https://docs.python.org/3/library/asyncio.html) do Python.

## Como utilizar
Veja como é fácil utilizar:
```python
b3_httpclient = B3AsyncBackend(
    username='SEU CPF/CNPJ',
    password='SUA SENHA'
)
brokers = await b3_httpclient.get_brokers_with_accounts()
assets_extract = (
    await b3_httpclient.get_brokers_account_portfolio_assets_extract(
        brokers=brokers
    )
)
print(assets_extract) # Todos seus ativos consolidados no CEI
await b3_httpclient.session_close()
await b3_httpclient.connection_close()
```
