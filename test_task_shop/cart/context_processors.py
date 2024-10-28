from typing import Dict

from django.http import HttpRequest

from .cart import Cart


def cart(request: HttpRequest) -> Dict[str, Cart]:
    """
    Context processor to add the current cart instance to the context.

    This function allows the cart to be accessible in templates via the "cart" key,
    enabling easy display of cart items and totals in the template context.

    """
    return {"cart": Cart(request)}
