from django.conf import settings


class Conf(object):
    def __init__(self):
        self.cryptomus_settings = getattr(settings, 'CRYPTOMUS_SETTINGS', {})
        self.merchant_id = self.cryptomus_settings.get('merchant_id')
        self.api_key = self.cryptomus_settings.get('api_key')
        self.url_success = self.cryptomus_settings.get('url_success')
        self.url_callback = self.cryptomus_settings.get('url_callback')
        self.api_url = self.cryptomus_settings.get('api_url')


conf = Conf()