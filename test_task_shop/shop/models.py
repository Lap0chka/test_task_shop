from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class ProductManage(models.Manager):
    """
    Custom manager for the Product model to filter available products.
    """

    def get_queryset(self):
        """
        Return a queryset of available products.
        """
        return super().get_queryset().filter(is_available=True)


class Category(models.Model):
    """
    Represents a category for organizing products.
    """
    name = models.CharField(max_length=124, db_index=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children'
    )
    slug = models.SlugField(max_length=140, unique=True, null=False)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (['slug', 'parent'])
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:category_list', args=[self.slug])

    def save(self, *args, **kwargs):
        """
        Save the category instance to the database.
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
    image = models.ImageField(upload_to='images/products/%d-%m-%Y',
                              blank=True, default='images/products/default/default.jpg')
    is_available = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products',)
    discount = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    available = ProductManage()
    objects = models.Manager()

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-create_at']

    def get_discounted_price(self):
        """
        Calculates the discounted price based on the product's price and discount.

        Returns:
            decimal.Decimal: The discounted price.
        """
        discounted_price = self.price - (self.price * self.discount / 100)
        return round(discounted_price, 2)

    def save(self, *args, **kwargs):
        """
        Save the category instance to the database.
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)