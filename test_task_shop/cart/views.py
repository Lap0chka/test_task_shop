from cart.cart import Cart
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from shop.models import Product


def cart_view(request):
    """
    Renders the 'cart_view.html' template with the cart object created using the Cart class.
    Returns:
        HttpResponse: The rendered template displaying the cart contents.
    """
    cart = Cart(request)
    return render(request, 'cart/cart_view.html', {'cart': cart})


def cart_add(request):
    """
    Add a product to the shopping cart.
    Returns:
    - JsonResponse: A JSON response containing the updated quantity and product title.
    """
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        product = get_object_or_404(Product, pk=product_id)
        cart.add(product=product, quantity=product_qty)
        cart_qty = cart.__len__()

        response = JsonResponse({'qty': cart_qty, 'product': product.title})
        return response


def cart_update(request):
    """
    Update the quantity of a product in the shopping cart.
    Returns:
    - HttpResponse: A response with status code 200 if the update is successful.
    """
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = request.POST.get('product_id')
        product_qty = int(request.POST.get('product_qty'))
        cart.update(product_id, product_qty)
        cart_qty = cart.__len__()
        cart_total = cart.get_total_price()
        return JsonResponse({'qty': cart_qty, 'total': cart_total})


def delete_product(request):
    """
    Delete a specified quantity of a product from the shopping cart.
    Returns:
    - HttpResponse object with a status code of 200 if the product is successfully deleted from the cart.
    """
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = request.POST.get('product_id')
        product_qty = int(request.POST.get('product_qty'))
        cart.delete(product_id, product_qty)
        cart_qty = cart.__len__()
        return JsonResponse({'qty': cart_qty})
