from typing import Any, Dict

from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from .models import Product


class ProductListView(ListView):
    """
    View to list all available products, with pagination support.
    """

    model = Product
    context_object_name: str = "products"
    paginate_by: int = 15
    template_name: str = "shop/products.html"

    def get_queryset(self) -> QuerySet[Product]:
        """
        Retrieve the queryset of available products.

        """
        return Product.available.all()


def product_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """
    View to display the details of a specific product.
    """
    product = get_object_or_404(Product, slug=slug)
    random_products = Product.available.order_by("?")[:4]
    context: Dict[str, Any] = {"product": product, "products": random_products}
    return render(request, "shop/product_detail.html", context)
