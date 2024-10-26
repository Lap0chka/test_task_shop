import json

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from shop.models import Category, Product

from .views import cart_add, cart_update, cart_view, delete_product


class CartViewTest(TestCase):
    """
    Test case for the cart_view function in the views module.

    Attributes:
        client (Client): A Django test client for making requests.
        factory (RequestFactory): A factory for creating request objects.
        middleware (SessionMiddleware): Middleware for managing sessions.
    """
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory().get(reverse('cart:cart_view'))
        self.middleware = SessionMiddleware(self.factory)
        self.middleware.process_request(self.factory)
        self.factory.session.save()

    def test_cart_view(self):
        request = self.factory
        responce = cart_view(request)
        self.assertEqual(responce.status_code, 200)
        self.assertTemplateUsed(self.client.get(reverse('cart:cart_view')), 'cart/cart_view.html')


class CartAddViewTestCase(TestCase):
    """
    Test case for the cart_add view function.

    This test case sets up a category and a product, creates a request using the RequestFactory to simulate adding the product to the cart, and then tests the cart_add view function.
    The test checks if the response status code is 200, verifies the product title and quantity in the JSON response.

    Attributes:
    - setUp: Sets up the necessary data and request for testing.
    - test_cart_add: Tests the cart_add view function.

    """
    def setUp(self):
        self.category = Category.objects.create(name='Category 1', slug='category-1')
        self.product = Product.objects.create(title='Example Product', brand='Nike', available=True,
                                              price=10.0, category=self.category)

        self.factory = RequestFactory().post(reverse('cart:add_to_cart'), {
            'action': 'post',
            'product_id': self.product.id,
            'product_qty': 2,
        })
        self.middleware = SessionMiddleware(self.factory)
        self.middleware.process_request(self.factory)
        self.factory.session.save()

    def test_cart_add(self):
        request = self.factory
        response = cart_add(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['product'], 'Example Product')
        self.assertEqual(data['qty'], 2)


class CartDeleteViewTestCase(TestCase):
    """
    Test case for the CartDeleteViewTestCase class.

    This class tests the functionality of deleting a specified quantity of a product from the shopping cart.
    It sets up the necessary data for testing, including creating a category and a product, simulating a request to delete a product from the cart, and then asserts that the product is successfully deleted from the cart.
    Methods:
        setUp: Prepares the necessary data and environment for testing.
        test_cart_delete: Tests the functionality of deleting a product from the cart and asserts the expected outcome.
    """
    def setUp(self):
        self.category = Category.objects.create(name='Category 1')
        self.product = Product.availability.create(title='Example Product', price=10.0, brand='Nike',
                                                   available=True, category=self.category)

        self.factory = RequestFactory().post(reverse('cart:delete_to_cart'), {
            'action': 'post',
            'product_id': self.product.id,
            'product_qty': '2',
        })
        self.middleware = SessionMiddleware(self.factory)
        self.middleware.process_request(self.factory)
        self.factory.session.save()

    def test_cart_delete(self):
        request = self.factory
        response = delete_product(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['qty'], 0)


class CartUpdateViewTestCase(TestCase):
    """
    Test case for the cart update view functionality.

    This test case sets up a category and a product, creates request instances for adding and updating the cart,
    and tests the cart_update view function. It checks if the response status code is 200,
    and verifies the total price and quantity in the response JSON data.
    Methods:
        setUp(): Set up the necessary data and request instances for testing.
        test_cart_update(): Test the cart_update view function.
    """
    def setUp(self):
        self.category = Category.objects.create(name='Category 1', slug='category-1')
        self.product = Product.availability.create(title='Example Product', price=10.0, brand='Nike',
                                                   available=True, category=self.category)
        self.factory = RequestFactory().post(reverse('cart:add_to_cart'), {
            'action': 'post',
            'product_id': self.product.id,
            'product_qty': 2,
        })
        self.factory = RequestFactory().post(reverse('cart:update_to_cart'), {
            'action': 'post',
            'product_id': self.product.id,
            'product_qty': 5,
        })
        self.middleware = SessionMiddleware(self.factory)
        self.middleware.process_request(self.factory)
        self.factory.session.save()

    def test_cart_update(self):
        request = self.factory
        response = cart_add(request)
        response = cart_update(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['total'], '50.00')
        self.assertEqual(data['qty'], 5)
