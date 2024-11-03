from typing import Optional

from cart.cart import Cart
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from shop.models import Product


def cart_view(request: HttpRequest) -> HttpResponse:
    """
    Renders the 'cart_view.html' template with the cart object created using the Cart class.
    """
    cart = Cart(request)
    return render(request, "cart/cart_view.html", {"cart": cart})


def cart_add(request: HttpRequest) -> Optional[JsonResponse]:
    """
    Add a product to the shopping cart.
    """
    cart = Cart(request)
    if request.POST.get("action") == "post":
        product_id = int(request.POST.get("product_id"))
        product_qty = int(request.POST.get("product_qty"))

        product = get_object_or_404(Product, pk=product_id)
        cart.add(product=product, quantity=product_qty)
        cart_qty = len(cart)  # Assuming Cart has a __len__ method

        return JsonResponse({"qty": cart_qty, "product": product.title})
    return None


def cart_update(request: HttpRequest) -> Optional[JsonResponse]:
    """
    Update the quantity of a product in the shopping cart.
    """
    cart = Cart(request)
    if request.POST.get("action") == "post":
        product_id = request.POST.get("product_id")
        product_qty = int(request.POST.get("product_qty"))
        cart.update(product_id, product_qty)
        cart_qty = len(cart)
        cart_total = cart.get_total_price()
        return JsonResponse({"qty": cart_qty, "total": cart_total})
    return None


def delete_product(request: HttpRequest) -> Optional[JsonResponse]:
    """
    Delete a specified quantity of a product from the shopping cart.
    """
    cart = Cart(request)
    if request.POST.get("action") == "post":
        product_id = request.POST.get("product_id")
        product_qty = int(request.POST.get("product_qty"))
        cart.delete(product_id, product_qty)
        cart_qty = len(cart)
        return JsonResponse({"qty": cart_qty})
    return None
