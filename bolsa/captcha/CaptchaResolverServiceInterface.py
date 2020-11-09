from abc import ABCMeta, abstractmethod


class CaptchaResolverServiceInterface(metaclass=ABCMeta):
    @abstractmethod
    async def resolve(self, site_key, url):
        """ Return captcha solution. """
        raise NotImplementedError
