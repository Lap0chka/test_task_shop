from payment.models import ShippingAddress
from rest_framework import serializers
from shop.models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "slug", "price", "category"]


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = [
            "full_name",
            "email",
            "street_address",
            "apartment_address",
            "city",
            "country",
        ]


class CartItemSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=255)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()
