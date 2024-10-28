from decimal import Decimal

import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.views import APIView

from api.serializers import ProductSerializer, ShippingAddressSerializer, CartItemSerializer
from payment.models import ShippingAddress, Order, OrderItem
from shop.models import Product

stripe.api_key = settings.STRIPE_SECRET_KEY

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.available.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class CompleteOrderAPIView(APIView):
    def post(self, request):
        shipping_serializer = ShippingAddressSerializer(data=request.data.get('shipping_address'))
        cart_serializer = CartItemSerializer(data=request.data.get('cart_items'), many=True)

        if not shipping_serializer.is_valid() or not cart_serializer.is_valid():
            return Response({
                'shipping_errors': shipping_serializer.errors,
                'cart_errors': cart_serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # Сохраняем адрес доставки
        shipping_data = shipping_serializer.validated_data
        shipping_address = ShippingAddress.objects.create(**shipping_data)
        user = request.user if request.user.is_authenticated else None
        shipping_address.user = user
        shipping_address.save()

        # Рассчитываем общую стоимость заказа
        cart_data = cart_serializer.validated_data
        total_price = sum(item['price'] * item['quantity'] for item in cart_data)

        # Создаем объект заказа
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            amount=total_price
        )

        # Создаем объекты OrderItem и формируем данные для Stripe
        session_data = {
            'mode': 'payment',
            'success_url': request.build_absolute_uri(reverse('payment:payment_success')),
            'cancel_url': request.build_absolute_uri(reverse('payment:payment_failed')),
            'line_items': [],
            'client_reference_id': order.id
        }

        for item in cart_data:
            product = get_object_or_404(Product)
            OrderItem.objects.create(
                order=order,
                product=product,
                price=item['price'],
                quantity=item['quantity'],
                user=user
            )
            session_data['line_items'].append({
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(item['price'] * Decimal(100)),
                    'product_data': {
                        'name': item['product_name'],
                    },
                },
                'quantity': item['quantity']
            })


        session = stripe.checkout.Session.create(**session_data)

        return Response({'checkout_url': session.url}, status=status.HTTP_201_CREATED)
