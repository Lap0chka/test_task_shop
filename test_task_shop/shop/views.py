from PIL.ImagePalette import random
from django.shortcuts import get_object_or_404, render
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
    random_products = Product.available.order_by('?')[:4]
    context = {'product': product, 'products': random_products}
    return render(request, 'shop/product_detail.html', context)


