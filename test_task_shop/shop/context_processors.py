from typing import Any, Dict

from django.http import HttpRequest
from shop.models import Category


def categories(request: HttpRequest) -> Dict[str, Any]:
    """
    Context processor to add a list of top-level categories to the context.

    This function retrieves all top-level categories (categories with no parent)
    and adds them to the context dictionary under the key 'categories'.
    """
    categories = Category.objects.filter(parent=None)
    return {"categories": categories}
