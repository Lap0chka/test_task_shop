from .cart import Cart


def cart(request):
    """
       Context processor cart to the context.
       """
    return {'cart': Cart(request)}
