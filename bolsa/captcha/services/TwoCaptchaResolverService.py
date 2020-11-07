from twocaptcha import TwoCaptcha
from twocaptcha.api import ApiException
from bolsa.captcha.CaptchaResolverServiceInterface import CaptchaResolverServiceInterface

class TwoCaptchaResolverService(CaptchaResolverServiceInterface):

    def __init__(self, credential):
        self._credential = credential

    async def resolve(self, site_key, url):
        solver = TwoCaptcha(self._credential)

        try:
            solvedcaptcha = solver.recaptcha(site_key, url)
        except ApiException as error:
            raise error
        except Exception as e:
            raise ValueError('captcha não pode ser resolvido')
        return solvedcaptcha['code']
