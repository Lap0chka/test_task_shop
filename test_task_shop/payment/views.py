from decimal import Decimal

import stripe
import weasyprint
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.templatetags.static import static

from cart.cart import Cart
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from payment.forms import ShippingForm, ShippingFormWithSave
from payment.models import Order, OrderItem, ShippingAddress

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required(login_url="account:login")
def shipping_view(request):
    try:
        shipping_address = ShippingAddress.objects.get(user=request.user)
    except TypeError:
        shipping_address = None

    if request.method == 'POST':
        form = ShippingForm(request.POST, instance=shipping_address)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()
            return redirect('account:dashboard')
    else:
        form = ShippingForm(instance=shipping_address, )

    return render(request, 'payment/shipping/shipping.html', {'form': form})


def checkout(request):
    if request.user.is_authenticated:
        try:
            shipping_address = ShippingAddress.objects.get(user=request.user)
        except TypeError:
            shipping_address = None

    shipping_address = ShippingFormWithSave(instance=shipping_address)
    return render(request, 'payment/checkout.html', {'shipping_address': shipping_address})


def complete_order(request):
    if request.method == 'POST':
        form = ShippingForm(request.POST)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            if request.user.is_authenticated:
                user = request.user
                shipping_address.user = user
                is_save = form.cleaned_data['is_save', False]
                if is_save:
                    try:
                        shipping_address_old = ShippingAddress.objects.get(user=user)
                        shipping_address_old.delete()
                    except TypeError:
                        pass
                shipping_address.save()
            else:
                user = None
                shipping_address.save()

        cart = Cart(request)
        total_price = cart.get_total_price()

        session_data = {
            'mode': 'payment',
            'success_url': request.build_absolute_uri(reverse('payment:payment_success')),
            'cancel_url': request.build_absolute_uri(reverse('payment:payment_failed')),
            'line_items': []
        }

        order = Order.objects.create(
            user=user, shipping_address=shipping_address, amount=total_price)

        for item in cart:
            OrderItem.objects.create(
                order=order, product=item['product'], price=item['price'], quantity=item['quantity'], user=user)
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
        session_data['client_reference_id'] = order.id
        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)


def payment_success(request):
    for key in list(request.session.keys()):
        del request.session[key]
    return render(request, 'payment/payment-success.html')


def payment_failed(request):
    return render(request, 'payment/payment-failed.html')


@staff_member_required
def admin_order_pdf(request, order_id):
    try:
        order = Order.objects.select_related('user', 'shipping_address').get(id=order_id)
    except Order.DoesNotExist:
        raise Http404('Заказ не найден')
    html = render_to_string('payment/order/pdf/pdf_invoice.html',
                            {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    css_path = static('css/pdf.css').lstrip('/')
    # css_path = 'static/payment/css/pdf.css'
    stylesheets = [weasyprint.CSS(css_path)]
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=stylesheets)
    return response
