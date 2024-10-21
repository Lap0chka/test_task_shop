from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView

from .models import Product


class ProductListView(ListView):
    model = Product
    context_object_name = "products"
    paginate_by = 15
    template_name = "shop/products.html"

    def get_queryset(self):
        return Product.available.all()



def product_detail(request, slug):
    """
    View to display the details of a specific product.
    """
    product = get_object_or_404(Product, slug=slug)
    context = {'product': product}
    return render(request, 'shop/product_detail.html', context)


