from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CryptomusConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "fleio.billing.gateways.cryptomus"
    verbose_name = _("Cryptomus")
    fleio_module_type = 'payment_gateway'
    module_settings = {
        'capabilities': {
            'can_process_payments': True,
            'returns_fee_information': False
        }
    }
