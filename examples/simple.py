import asyncio
import logging

from bolsa import B3AsyncBackend

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s',
    datefmt='%Y-%m-%d,%H:%M:%S',
    level=logging.INFO
)


async def main():
    from datetime import datetime
    start_datetime = datetime.now()
    logging.info(f'Starting... {start_datetime}')
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
    print(assets_extract)
    await b3_httpclient.session_close()
    await b3_httpclient.connection_close()

    logging.info(f'Finish script... {datetime.now() - start_datetime}')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
