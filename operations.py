from dataclasses import dataclass
from typing import Dict
import logging
import datetime
import json
from fleio.activitylog.utils.activity_helper import activity_helper
from fleio.billing.gateways import exceptions
from fleio.billing.invoicing.tasks import invoice_add_payment
from fleio.billing.models import Gateway
from fleio.billing.models import Transaction
from fleio.billing.models.transaction import TransactionStatus
from fleio.billing.serializers import AddTransactionSerializer


LOG = logging.getLogger(__name__)


@dataclass
class PaymentProcess():

    rq_data: Dict[str, str]

    def charge_status(self, status: str) -> TransactionStatus:
        paid_statuses = ['paid', 'paid_over']
        error_statuses = ['fail', 'system_fail', 'wrong_amount', 'cancel']
        if status in paid_statuses:
            return TransactionStatus.SUCCESS
        elif status in error_statuses:
            return TransactionStatus.FAILURE

    def process_charge(self) -> None:
        gateway = Gateway.objects.get(name='cryptomus')
        external_id = self.rq_data.get('order_id', None)
        transaction_id = None
        transaction_status = self.charge_status(self.rq_data.get('status'))
        invoice_id = self.rq_data.get('order_id', None)
        if external_id is not None:
            try:
                existing_transaction = Transaction.objects.get(
                    external_id=external_id,
                    gateway=gateway)
                transaction_id = existing_transaction.id
            except Transaction.DoesNotExist:
                real_amount = round(float(self.rq_data.get('amount')), 2)
                serializer_data = {'invoice': invoice_id,
                                   'external_id': external_id,
                                   'amount': real_amount,
                                   'currency': 'EUR',
                                   'gateway': gateway.pk,
                                   'fee': gateway.get_fee(amount=real_amount),
                                   'date_initiated': datetime.datetime.now(),
                                   'extra': {},
                                   'status': transaction_status}
                tr_ser = AddTransactionSerializer(data=serializer_data)
                if tr_ser.is_valid(raise_exception=False):
                    new_transaction = tr_ser.save()
                    transaction_id = new_transaction.id
                else:
                    LOG.error('Could not process charge for cryptomus: {}'.format(json.dumps(tr_ser.errors)))
                    raise exceptions.InvoicePaymentException(
                        'Could not process charge for invoice {}.', invoice_id=invoice_id
                    )
            else:
                # Update the transaction status only
                existing_transaction.status = transaction_status
                existing_transaction.save(update_fields=['status'])
        gateway.log_callback(external_id=external_id,
                             status=self.rq_data.get('status'),
                             data=datetime.datetime.now(),
                             error=(self.rq_data.get('status') == 'fail'))
        if transaction_status == TransactionStatus.FAILURE:
            raise exceptions.GatewayException(f"Transaction is Fail. Status - {self.rq_data.get('status').upper()}")
        else:
            if transaction_status == TransactionStatus.SUCCESS:
                activity_helper.start_generic_activity(
                    category_name='cryptomus',
                    activity_class='cryptomus payment',
                    invoice_id=invoice_id
                )
                invoice_add_payment(
                    invoice_id=invoice_id, amount=self.rq_data.get('amount'),
                    currency_code='EUR', transaction_id=transaction_id,
                )

                activity_helper.end_activity()
