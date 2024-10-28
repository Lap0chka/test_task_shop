from decimal import Decimal
from typing import Any

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import QuerySet


class ProductManage(models.Manager):
    """
    Custom manager for the Product model to filter available products.
    """

    def get_queryset(self) -> QuerySet['Product']:
        """
        Returns a queryset of available products.
        """
        return super().get_queryset().filter(is_available=True)


class Category(models.Model):
    """
    Represents a category for organizing products.
    """

    name = models.CharField(max_length=124, db_index=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    slug = models.SlugField(max_length=140, unique=True, null=False)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["slug", "parent"]
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        """
        Return a string representation of the category instance.
        """
        return self.name

    def get_absolute_url(self) -> str:
        """
        Get the absolute URL for the category.
        This method returns the URL to access the category's product list.

        """
        return reverse("shop:category_list", args=[self.slug])

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Save the category instance to the database.
        If the `slug` field is not provided, it will be auto-generated from
        the category's name by using Django's `slugify` function. This method
        then calls the parent class's `save` method to handle the actual
        saving process.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Represents a product in the catalog.
    """

    title = models.CharField(max_length=248, db_index=True)
    slug = models.SlugField(max_length=264, unique=True)
    brand = models.CharField(max_length=248)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=99.99)
    image = models.ImageField(
        upload_to="images/products/%d-%m-%Y",
        blank=True,
        default="images/products/default/default.jpg",
    )
    is_available = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
    )
    discount = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    available = ProductManage()
    objects = models.Manager()

    def get_absolute_url(self) -> str:
        """
        Get the absolute URL for the product.
        This method returns the URL to access the product's detail page.
        """
        return reverse("shop:product_detail", args=[self.slug])

    def __str__(self) -> str:
        """
        Return a string representation of the product instance.
        """
        return self.title

    class Meta:
        ordering = ["-create_at"]

    def get_discounted_price(self) -> Decimal:
        """
        Calculate the discounted price based on the product's price and discount.

        The discount is calculated as a percentage of the price, and the result
        is rounded to two decimal places.
        """
        discounted_price = self.price - (self.price * self.discount / 100)
        return round(discounted_price, 2)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Save the category instance to the database.

        If the `slug` field is not provided, it will be auto-generated from
        the category's name by using Django's `slugify` function. This method
        then calls the parent class's `save` method to handle the actual
        saving process.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
