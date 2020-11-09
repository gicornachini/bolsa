import logging

from twocaptcha import TwoCaptcha
from twocaptcha.api import ApiException

from bolsa.captcha.CaptchaResolverServiceInterface import (
    CaptchaResolverServiceInterface
)
from bolsa.captcha.exceptions.CaptchaResolverException import (
    CaptchaResolverException
)

logger = logging.getLogger(__name__)


class TwoCaptchaResolverService(CaptchaResolverServiceInterface):

    def __init__(self, credential):
        self._credential = credential

    async def resolve(self, site_key, url):
        solver = TwoCaptcha(self._credential)
        logger.info(
            'Resolving captcha.'
        )
        try:
            solvedcaptcha = solver.recaptcha(site_key, url)
        except ApiException as error:
            raise CaptchaResolverException(
                f'Erro ao tentar resolver captcha: {error}'
            )

        logger.info(
            'Captcha resolved.'
        )

        return solvedcaptcha['code']
