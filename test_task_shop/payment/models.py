from decimal import Decimal
from typing import Optional

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from shop.models import Product


class ShippingAddress(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = "Shipping Address"
        verbose_name_plural = "Shipping Addresses"
        ordering = ["-id"]

    def __str__(self) -> str:
        """
        Returns a string representation of the Shipping Address.

        Returns:
            str: String representation of the Shipping Address.
        """
        return "Shipping Address - " + self.full_name

    @classmethod
    def create_default_shipping_address(cls, user: User) -> "ShippingAddress":
        """
        Creates a default shipping address for a given user.

        Args:
            user (User): The user for whom the default shipping address is created.

        Returns:
            ShippingAddress: The created default shipping address instance.
        """
        default_shipping_address = {
            "user": user,
            "full_name": "Noname",
            "email": "email@example.com",
            "street_address": "fill address",
            "apartment_address": "fill address",
            "country": "",
        }
        shipping_address = cls(**default_shipping_address)
        shipping_address.save()
        return shipping_address


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    shipping_address = models.ForeignKey(
        ShippingAddress, on_delete=models.CASCADE, blank=True, null=True
    )
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    discount = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(amount__gte=0), name="amount_gte_0"),
        ]

    def __str__(self) -> str:
        """
        Returns a string representation of the Order.

        Returns:
            str: String representation of the Order.
        """
        return "Order " + str(self.id)

    def get_absolute_url(self) -> str:
        """
        Returns the URL to access a particular order instance.

        Returns:
            str: URL for the order detail view.
        """
        return reverse("payment:order_detail", kwargs={"pk": self.pk})

    def get_total_cost_before_discount(self) -> Decimal:
        """
        Calculates the total cost of all items in the order before applying any discount.

        Returns:
            Decimal: The total cost before discount.
        """
        return sum(item.get_cost() for item in self.items.all())

    @property
    def get_discount(self) -> Decimal:
        """
        Calculates the discount amount based on the total cost and discount percentage.

        Returns:
            Decimal: The discount amount.
        """
        if (total_cost := self.get_total_cost_before_discount()) and self.discount:
            return total_cost * (self.discount / Decimal(100))
        return Decimal(0)

    def get_total_cost(self) -> Decimal:
        """
        Calculates the total cost of the order after applying the discount.

        Returns:
            Decimal: The final total cost of the order.
        """
        total_cost = self.get_total_cost_before_discount()
        return total_cost - self.get_discount


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, blank=True, null=True, related_name="items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True
    )
    price = models.DecimalField(max_digits=9, decimal_places=2)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = "OrderItem"
        verbose_name_plural = "OrderItems"
        ordering = ["-id"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0), name="quantity_gte_0"
            ),
        ]

    def __str__(self) -> str:
        """
        Returns a string representation of the OrderItem.

        Returns:
            str: String representation of the OrderItem.
        """
        return "OrderItem " + str(self.id)

    def get_cost(self) -> Decimal:
        """
        Calculates the total cost of this OrderItem.

        Returns:
            Decimal: The total cost of this item.
        """
        return self.price * self.quantity

    @property
    def total_cost(self) -> Decimal:
        """
        Returns the total cost for this OrderItem as a property.

        Returns:
            Decimal: Total cost of this OrderItem.
        """
        return self.get_cost()

    @classmethod
    def get_total_quantity_for_product(cls, product: Product) -> int:
        """
        Calculates the total quantity sold for a particular product.

        Args:
            product (Product): The product for which the quantity is calculated.

        Returns:
            int: Total quantity of the product sold.
        """
        return (
                cls.objects.filter(product=product).aggregate(
                    total_quantity=models.Sum("quantity")
                )["total_quantity"]
                or 0
        )

    @staticmethod
    def get_average_price() -> Optional[Decimal]:
        """
        Calculates the average price of all order items.

        Returns:
            Optional[Decimal]: The average price of items, or None if there are no items.
        """
        return OrderItem.objects.aggregate(average_price=models.Avg("price"))[
            "average_price"
        ]
