from django.urls import path

from . import views
from .weebhook import bitpay_webhook, stripe_webhook

app_name = "payment"

urlpatterns = [
    path("shipping/", views.shipping_view, name="shipping"),
    path("payment-failed/", views.payment_failed, name="payment_failed"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("complete_order/", views.complete_order, name="complete_order"),
    path("checkout/", views.checkout, name="checkout"),
    path("pay_with_crypo", views.create_invoice_bit_pay, name="pay_with_crypo"),
    path("webhook-stripe/", stripe_webhook, name="webhook-stripe"),
    path("webhook-bitpay/", bitpay_webhook, name="webhook-bitpat"),
]
