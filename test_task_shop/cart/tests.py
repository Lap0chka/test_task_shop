import json

from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from shop.models import Category, Product

from .views import cart_add, cart_update, cart_view, delete_product


class CartViewTest(TestCase):
    """
    Test case for the `cart_view` function in the views module.

    Attributes:
        client (Client): A Django test client for making requests.
        factory (HttpRequest): A factory-generated GET request object for testing.
    """

    def setUp(self) -> None:
        """
        Sets up the test client and request factory for the test case.
        """
        self.client: Client = Client()
        self.factory: HttpRequest = RequestFactory().get(reverse("cart:cart_view"))
        self.middleware = SessionMiddleware()
        self.middleware.process_request(self.factory)
        self.factory.session.save()

    def test_cart_view(self) -> None:
        """
        Tests the `cart_view` function, ensuring that it returns a 200 status code
        and renders the correct template.
        """
        request = self.factory
        response: HttpResponse = cart_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            self.client.get(reverse("cart:cart_view")), "cart/cart_view.html"
        )


class CartAddViewTestCase(TestCase):
    """
    Test case for the `cart_add` view function.

    This test case sets up a category and a product, creates a request using the
    RequestFactory to simulate adding the product to the cart,
    and then tests the `cart_add` view function. The test checks if the response
    status code is 200 and verifies the product title and quantity in the JSON response.

    Attributes:
        category (Category): The category object for the test product.
        product (Product): The product object to be added to the cart.
        factory (HttpRequest): A factory-generated POST request object for testing.
    """

    def setUp(self) -> None:
        """
        Sets up a category and product, and prepares a POST request for
        adding the product to the cart.
        """
        self.category: Category = Category.objects.create(
            name="Category 1", slug="category-1"
        )
        self.product: Product = Product.objects.create(
            title="Example Product",
            brand="Nike",
            available=True,
            price=10.0,
            category=self.category,
        )

        self.factory: HttpRequest = RequestFactory().post(
            reverse("cart:add_to_cart"),
            {
                "action": "post",
                "product_id": self.product.id,
                "product_qty": 2,
            },
        )
        self.middleware = SessionMiddleware()
        self.middleware.process_request(self.factory)
        self.factory.session.save()

    def test_cart_add(self) -> None:
        """
        Tests the `cart_add` view function, ensuring the correct product title and quantity
        are in the JSON response.
        """
        request = self.factory
        response: JsonResponse = cart_add(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["product"], "Example Product")
        self.assertEqual(data["qty"], 2)


class CartDeleteViewTestCase(TestCase):
    """
    Test case for the `delete_product` view function.

    This class tests the functionality of deleting a specified quantity of a
    product from the shopping cart. It sets up a category and product,
    creates a request to delete a product from the cart, and then asserts that
    the product is successfully deleted from the cart.

    Attributes:
        category (Category): The category object for the test product.
        product (Product): The product object to be deleted from the cart.
        factory (HttpRequest): A factory-generated POST request object for testing.
    """

    def setUp(self) -> None:
        """
        Sets up a category and product, and prepares a POST request
        for deleting the product from the cart.
        """
        self.category: Category = Category.objects.create(
            name="Category 1", slug="category-1"
        )
        self.product: Product = Product.objects.create(
            title="Example Product",
            price=10.0,
            brand="Nike",
            available=True,
            category=self.category,
        )

        self.factory: HttpRequest = RequestFactory().post(
            reverse("cart:delete_to_cart"),
            {
                "action": "post",
                "product_id": self.product.id,
                "product_qty": "2",
            },
        )
        self.middleware = SessionMiddleware()
        self.middleware.process_request(self.factory)
        self.factory.session.save()

    def test_cart_delete(self) -> None:
        """
        Tests the `delete_product` view function, ensuring that the
        correct quantity is in the JSON response.
        """
        request = self.factory
        response: JsonResponse = delete_product(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["qty"], 0)


class CartUpdateViewTestCase(TestCase):
    """
    Test case for the `cart_update` view function.

    This test case sets up a category and a product, creates request
    instances for adding and updating the cart, and tests the `cart_update` view function.
    It checks if the response status code is 200 and verifies the total price
    and quantity in the response JSON data.

    Attributes:
        category (Category): The category object for the test product.
        product (Product): The product object to be updated in the cart.
        factory (HttpRequest): A factory-generated POST request object for testing.
    """

    def setUp(self) -> None:
        """
        Sets up a category and product, and prepares POST requests for adding and updating
        the product in the cart.
        """
        self.category: Category = Category.objects.create(
            name="Category 1", slug="category-1"
        )
        self.product: Product = Product.objects.create(
            title="Example Product",
            price=10.0,
            brand="Nike",
            available=True,
            category=self.category,
        )

        # Initial request to add product
        self.add_request: HttpRequest = RequestFactory().post(
            reverse("cart:add_to_cart"),
            {
                "action": "post",
                "product_id": self.product.id,
                "product_qty": 2,
            },
        )
        # Subsequent request to update product quantity
        self.update_request: HttpRequest = RequestFactory().post(
            reverse("cart:update_to_cart"),
            {
                "action": "post",
                "product_id": self.product.id,
                "product_qty": 5,
            },
        )

        # Apply session middleware to both requests
        for request in [self.add_request, self.update_request]:
            self.middleware = SessionMiddleware()
            self.middleware.process_request(request)
            request.session.save()

    def test_cart_update(self) -> None:
        """
        Tests the `cart_update` view function, ensuring the correct total price and quantity
        are in the JSON response.
        """
        cart_add(self.add_request)
        response: JsonResponse = cart_update(self.update_request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["total"], "50.00")
        self.assertEqual(data["qty"], 5)
