import json
from typing import Any, Dict

import stripe
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from payment.models import Order
from stripe import SignatureVerificationError


@csrf_exempt
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    """
    Handle Stripe webhook events for payment processing, specifically listening to
    'checkout.session.completed' events to mark orders as paid.
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    event = None

    try:
        # Construct the Stripe event to verify its authenticity
        event: Dict[str, Any] = stripe.Webhook.construct_event(  # type: ignore
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:

        return HttpResponse(status=400)
    except SignatureVerificationError:
        return HttpResponse(status=400)

    if event and event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Ensure the session has been paid before processing the order
        if session.get("mode") == "payment" and session.get("payment_status") == "paid":
            order_id = session.get("client_reference_id")
            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    order.is_paid = True
                    order.save()
                except Order.DoesNotExist:
                    # Order does not exist; return a 404 response.
                    return HttpResponse(status=404)

    return HttpResponse(status=200)


@csrf_exempt
def bitpay_webhook(request: HttpRequest) -> HttpResponse:
    """
    Handles BitPay webhook events, updating the order status if payment is confirmed.
    """
    data = json.loads(request.body.decode("utf-8"))
    status = data["data"]["status"]

    if status == "paid":
        order_id = data["data"].get("orderId")
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.is_paid = True
                order.save()
            except Order.DoesNotExist:
                return HttpResponse(status=404)

    return HttpResponse(status=200)
