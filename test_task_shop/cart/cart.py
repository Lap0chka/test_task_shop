from shop.models import Product

from typing import Iterator, Dict, Any
from decimal import Decimal
from django.http import HttpRequest


class Cart:
    """
    Represents a shopping cart for storing and managing products and quantities.
    Allows adding, updating, deleting products, calculating total price,
    and iterating over cart items.
    """

    def __init__(self, request: HttpRequest) -> None:
        """
        Initialize the cart, setting up the session and loading the cart from the session data.

        Args:
            request (HttpRequest): The HTTP request object containing session information.
        """
        self.session = request.session
        self.cart: Dict[str, Dict[str, Any]] = self.cart_init()

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """
        Iterate over items in the cart, yielding product information along with
        quantity and price calculations.

        Yields:
            Dict[str, Any]: A dictionary containing product data and calculated total for each item.
        """
        product_ids = self.cart.keys()
        products = Product.available.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]["product"] = product

        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total"] = item["price"] * item["quantity"]
            yield item

    def __len__(self) -> int:
        """
        Returns the total number of items in the cart.

        Returns:
            int: The sum of quantities for each item in the cart.
        """
        return sum(item["quantity"] for item in self.cart.values())

    def cart_init(self) -> Dict[str, Dict[str, Any]]:
        """
        Initializes the cart in the session if it doesn't already exist.

        Returns:
            Dict[str, Dict[str, Any]]: The cart stored in the session.
        """
        cart = self.session.get("session_key")
        if not cart:
            cart = self.session["session_key"] = {}
        return cart

    def add(self, product: Product, quantity: int) -> None:
        """
        Add a product to the cart or update its quantity if it already exists.

        Args:
            product (Product): The product instance to add to the cart.
            quantity (int): The quantity of the product to add.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": quantity, "price": str(product.price)}
        else:
            self.cart[product_id]["quantity"] += quantity
        self.session.modified = True

    def get_total_price(self) -> Decimal:
        """
        Calculate the total price of all items in the cart.

        Returns:
            Decimal: The total price of items in the cart.
        """
        total_price = sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )
        return total_price

    def update(self, product_id: str, quantity: int) -> None:
        """
        Update the quantity of a specific product in the cart.

        Args:
            product_id (str): The ID of the product to update.
            quantity (int): The new quantity for the product.
        """
        if product_id in self.cart:
            self.cart[product_id]["quantity"] = quantity
            self.session.modified = True

    def delete(self, product_id: str, quantity: int = 2) -> None:
        """
        Delete a specified quantity of a product from the cart, removing the item if the quantity
        reaches zero or falls below the specified quantity.

        Args:
            product_id (str): The ID of the product to delete or decrement.
            quantity (int): The quantity to decrement (default is 2).
        """
        if product_id in self.cart:
            if self.cart[product_id]["quantity"] <= quantity:
                del self.cart[product_id]
            else:
                self.cart[product_id]["quantity"] -= quantity
            self.session.modified = True
