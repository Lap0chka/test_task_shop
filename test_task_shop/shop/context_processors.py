from shop.models import Category


def categories(request):
    """
       Context processor to add a list of top-level categories to the context.
       """
    categories = Category.objects.filter(parent=None)
    return {'categories': categories}
