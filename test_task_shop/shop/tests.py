from typing import Optional
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.http import HttpResponse
from shop.models import Category, Product


class ProductViewTest(TestCase):
    """
    Test case for testing the views related to products in the shop application.

    This class contains test methods to verify the behavior
    of product views, such as retrieving products and their details.

    """

    def test_get_products(self) -> None:
        """
        Tests retrieving the list of products and verifies that the response
        status code is 200. Also checks that the correct products are returned
        and are displayed in the response content.
        """
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )

        uploaded = SimpleUploadedFile(
            "test_image.gif", small_gif, content_type="image/gif"
        )
        category = Category.objects.create(name="django")
        product_1 = Product.objects.create(
            title="Product 1",
            category=category,
            image=uploaded,
            slug="product-1",
            is_available=True,
        )
        product_2 = Product.objects.create(
            title="Product 2",
            category=category,
            image=uploaded,
            slug="product-2",
            is_available=True,
        )

        response: HttpResponse = self.client.get(reverse("shop:products"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["products"].count(), 2)
        self.assertEqual(list(response.context["products"]), [product_1, product_2])
        self.assertContains(response, product_1)
        self.assertContains(response, product_2)


class ProductDetailViewTest(TestCase):
    """
    Test case for the Product Detail View.

    This class contains test methods to verify the behavior of the
    Product Detail View in the shop application, specifically ensuring that the
    product detail page is accessible and returns the correct product.
    """

    def test_get_product_by_slug(self) -> None:
        """
        Tests retrieving a product by its slug. Verifies that the correct product
        is displayed in the context and that the response status code is 200.
        """
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        uploaded = SimpleUploadedFile("small.gif", small_gif, content_type="image/gif")
        category = Category.objects.create(name="Category 1")
        product = Product.objects.create(
            title="Product 1",
            category=category,
            slug="product-1",
            image=uploaded,
            available=True,
        )

        response: HttpResponse = self.client.get(
            reverse("shop:product_detail", kwargs={"slug": "product-1"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["product"], product)
        self.assertEqual(response.context["product"].slug, product.slug)


class CategoryListViewTest(TestCase):
    """
    Test case for testing the CategoryListView view.

    This class contains test methods to verify the
    behavior of the CategoryListView view in the shop application.
    The tests include checking the status code,
    the template used, and the context data returned by the view.
    """

    def setUp(self) -> None:
        """
        Sets up a category and a product for testing the CategoryListView view.
        """
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        uploaded = SimpleUploadedFile("small.gif", small_gif, content_type="image/gif")
        self.category: Category = Category.objects.create(
            name="Test Category", slug="test-category"
        )
        self.product: Product = Product.objects.create(
            title="Test Product",
            slug="test-product",
            category=self.category,
            image=uploaded,
            available=True,
        )

    def test_status_code(self) -> None:
        """
        Tests that the status code for the CategoryListView is 200 (OK).
        """
        response: HttpResponse = self.client.get(
            reverse("shop:category_list", args=[self.category.slug])
        )
        self.assertEqual(response.status_code, 200)

    def test_template_used(self) -> None:
        """
        Tests that the CategoryListView uses the correct template.
        """
        response: HttpResponse = self.client.get(
            reverse("shop:category_list", args=[self.category.slug])
        )
        self.assertTemplateUsed(response, "shop/category_list.html")

    def test_context_data(self) -> None:
        """
        Tests that the context data for the CategoryListView includes the correct
        category and products.
        """
        response: HttpResponse = self.client.get(
            reverse("shop:category_list", args=[self.category.slug])
        )
        self.assertEqual(response.context["category"], self.category)
        self.assertEqual(response.context["products"].first(), self.product)
