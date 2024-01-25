from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework.response import Response
from rest_framework import status

import logging
from .services.client import Client
from .services.request_builder import RequestBuilder
from .operations import PaymentProcess

from .conf import conf

from fleio.billing.gateways.decorators import gateway_action, staff_gateway_action
from fleio.billing.gateways import exceptions as gateway_exceptions
from fleio.billing.models import Invoice
from fleio.core.utils import fleio_join_url
from fleio.settings import FRONTEND_URL
 
LOG = logging.getLogger(__name__)

payment = Client.payment(
    conf.api_key,
    conf.merchant_id,
    conf.api_url)

@gateway_action(methods=['GET'])
def pay_invoice(request):
    invoice_id = request.query_params.get('invoice')
    if invoice_id is None:
        LOG.error("An 'invoice' parameter is required")
        raise gateway_exceptions.GatewayException("An 'invoice' parameter is required")
    try:
        inv = Invoice.objects.get(pk=invoice_id, client=request.user.get_active_client(request=request))
    except Invoice.DoesNotExist:
        LOG.error('Invoice {} does not exist'.format(invoice_id))
        raise gateway_exceptions.GatewayException('Invoice {} does not exist'.format(invoice_id))
    if inv.balance <= 0:
        LOG.info('Invoice {} is already paid'.format(invoice_id), invoice_id=invoice_id)
        raise gateway_exceptions.InvoicePaymentException('Invoice {} is already paid'.format(invoice_id), invoice_id=invoice_id)

    result = payment.create({
        "amount": str(inv.balance),
        "currency": inv.currency.code,
        "order_id": invoice_id,
        "url_callback": conf.url_callback
    })
    return HttpResponseRedirect(result.get('url'))

@gateway_action(methods=['POST'])
def callback(request):
    try:
        payment_info = payment.info({
            "order_id": request.data.get("order_id")})
        if payment_info.get('payment_status') == 'paid':
            payment_process = PaymentProcess(rq_data=request.data)
            payment_process.process_charge()
            return Response({'detail': 'OK'}, status=status.HTTP_200_OK)
        else:
            raise Exception(f"Payment is not paid. Status - {payment_info.get('payment_status').upper()}")
    except Exception as err:
        LOG.error(f"Payment error - {err}")
        return Response(
            {'detail': 'Error'},
            status=status.HTTP_400_BAD_REQUEST)
