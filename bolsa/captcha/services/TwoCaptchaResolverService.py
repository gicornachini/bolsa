from twocaptcha import TwoCaptcha
from twocaptcha.api import ApiException
from bolsa.captcha.CaptchaResolverServiceInterface import CaptchaResolverServiceInterface
from bolsa.captcha.exceptions.CaptchaResolverException import CaptchaResolverException

class TwoCaptchaResolverService(CaptchaResolverServiceInterface):

    def __init__(self, credential):
        self._credential = credential

    async def resolve(self, site_key, url):
        solver = TwoCaptcha(self._credential)

        try:
            solvedcaptcha = solver.recaptcha(site_key, url)
        except ApiException as error:
            raise CaptchaResolverException(f'Erro ao tentar resolver captcha: {e}')
        return solvedcaptcha['code']
