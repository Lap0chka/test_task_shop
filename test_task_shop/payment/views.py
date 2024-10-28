from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse, JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse

from cart.cart import Cart
from payment.forms import ShippingForm
from payment.models import Order, OrderItem, ShippingAddress

import requests

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required(login_url="account:login")
def shipping_view(request: HttpRequest) -> HttpResponse:
    """
    Handle the user's shipping information. If a shipping address exists for the user,
    it is populated in the form; otherwise, a new form is provided for the user to complete.
    """
    try:
        shipping_address = ShippingAddress.objects.get(user=request.user)
    except (TypeError, ObjectDoesNotExist):
        shipping_address = None

    if request.method == 'POST':
        form = ShippingForm(request.POST, instance=shipping_address)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()
            return redirect('account:dashboard')
    else:
        form = ShippingForm(instance=shipping_address)

    return render(request, 'payment/shipping/shipping.html', {'form': form})


def checkout(request: HttpRequest) -> HttpResponse:
    """
    Displays the checkout page with the user's shipping address if available.
    """
    shipping_address = ShippingAddress.objects.filter(user=request.user).first() if request.user.is_authenticated else None
    shipping_form = ShippingForm(instance=shipping_address)
    return render(request, 'payment/checkout.html', {'shipping_address': shipping_form})


def complete_order(request: HttpRequest) -> HttpResponse:
    """
    Completes the order creation process. If payment is successful, redirects to the payment success page.
    """
    if request.method == 'POST':
        form = ShippingForm(request.POST)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            user = request.user if request.user.is_authenticated else None
            type_payment = request.POST.get('type_payment')

            if user:
                ShippingAddress.objects.filter(user=request.user).first().delete()

            shipping_address.user = user
            shipping_address.save()

        cart = Cart(request)
        total_price = cart.get_total_price()

        session_data = {
            'mode': 'payment',
            'success_url': request.build_absolute_uri(reverse('payment:payment_success')),
            'cancel_url': request.build_absolute_uri(reverse('payment:payment_failed')),
            'line_items': []
        }

        order = Order.objects.create(user=user, shipping_address=shipping_address, amount=total_price)

        for item in cart:
            OrderItem.objects.create(
                order=order, product=item['product'], price=item['price'], quantity=item['quantity'], user=user
            )
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(item['price'] * Decimal(100)),
                    'currency': 'usd',
                    'product_data': {
                        'name': item['product'],
                    },
                },
                'quantity': item['quantity']
            })

        if 'crypto-payment' not in type_payment:
            session_data['client_reference_id'] = order.id
            session = stripe.checkout.Session.create(**session_data)
            return redirect(session.url, code=303)
        return create_invoice_bit_pay(session_data, order.id)


def create_invoice_bit_pay(session_data: dict, order_id: int) -> HttpResponse:
    """
    Creates a BitPay invoice and provides the user with a link for payment.
    """
    token_bitpay = settings.BITPAY_SECRET
    total = quantity = 0
    names = []
    url = "https://test.bitpay.com/invoices"
    for item in session_data['line_items']:
        total += item['price_data']['unit_amount']
        quantity += item['quantity']
        product_name = item['price_data']['product_data']['name']
        names.append(product_name.title)

    names = '\n'.join(names)

    payload = {
        "token": token_bitpay,
        "price": float(total/100),
        "currency": 'USD',
        "orderId": order_id,
        "notificationURL": "https://236e-91-64-228-61.ngrok-free.app/payment/webhook-bitpay/",
        "itemDesc": names,
        "autoRedirect": True,
        "itemizedDetails": {
            "isFee": False,
            "amount": quantity,
        },
        "closeURL": "http://127.0.0.1:4421/payment/payment-failed/",
        "redirectURL": "http://127.0.0.1:4421/payment/payment-success/"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Ensures we capture HTTP errors
        data = response.json()
        payment_url = data['data']['url']
        return HttpResponse(f'Your link for pay: {payment_url}', content_type="text/html")
    except requests.exceptions.RequestException as e:
        error_message = f"HTTP error occurred: {e}"
        print(error_message)
        return JsonResponse({"error": error_message}, status=500)


def payment_success(request: HttpRequest) -> HttpResponse:
    """
    Clears the session cart data and renders the payment success page.
    """
    request.session.flush()  # Clears all session data
    return render(request, 'payment/payment-success.html')


def payment_failed(request: HttpRequest) -> HttpResponse:
    """
    Renders the payment failed page if the payment was unsuccessful.
    """
    return render(request, 'payment/payment-failed.html')


@staff_member_required
def admin_order_pdf(request: HttpRequest, order_id: int) -> HttpResponse:
    """
    Generates a PDF for a given order in the admin panel.
    """
    try:
        order = Order.objects.select_related('user', 'shipping_address').get(id=order_id)
    except Order.DoesNotExist:
        raise Http404('Order not found')

    html = render_to_string('payment/order/pdf/pdf_invoice.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    css_path = static('css/pdf.css').lstrip('/')
    # pdf generation logic (e.g., using a library) would go here
    return response
