from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from shop.models import Category, Product


class ProductViewTest(TestCase):
    """
    Test case for testing the views related to products in the shop application.

    This class contains test methods to verify the behavior of product views, such as retrieving products and their details.

    Test Methods:
        - test_get_products: Tests the retrieval of products and verifies the response status code, product count, product list, and content.
    """
    def test_get_products(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )

        uploaded = SimpleUploadedFile('test_image.gif', small_gif, content_type='image/gif')
        category = Category.objects.create(name='django')
        product_1 = Product.objects.create(
            title='Product 1', category=category, image=uploaded, slug='product-1', available=True
        )
        product_2 = Product.objects.create(
            title='Product 2', category=category, image=uploaded, slug='product-2', available=True
        )

        response = self.client.get(reverse('shop:products'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['products'].count(), 2)
        self.assertEqual(list(response.context['products']), [product_1, product_2])
        self.assertContains(response, product_1)
        self.assertContains(response, product_2)


class ProductDetailViewTest(TestCase):
    """
    Test case for the Product Detail View.

    This class contains test methods to verify the behavior of the Product Detail View in the shop application.
    It tests the retrieval of a product by its slug, ensuring that the correct product is displayed and that the response is successful.

    """
    def test_get_product_by_slug(self):
        # Create a product
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            'small.gif', small_gif, content_type='image/gif')
        category = Category.objects.create(name='Category 1')
        product = Product.objects.create(
            title='Product 1', category=category, slug='product-1', image=uploaded, available=True
        )
        # Make a request to the product detail view with the product's slug
        response = self.client.get(
            reverse('shop:product_detail', kwargs={'slug': 'product-1'}))

        # Check that the response is a success
        self.assertEqual(response.status_code, 200)

        # Check that the product is in the response context
        self.assertEqual(response.context['product'], product)
        self.assertEqual(response.context['product'].slug, product.slug)


class CategoryListViewTest(TestCase):
    """
    Test case for testing the CategoryListView view.

    This class contains test methods to verify the behavior of the CategoryListView view in the shop application.
    The tests include checking the status code, the template used, and the context data returned by the view.

    """
    def setUp(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            'small.gif', small_gif, content_type='image/gif')
        self.category = Category.objects.create(
            name='Test Category', slug='test-category'
        )
        self.product = Product.availability.create(
            title='Test Product', slug='test-product', category=self.category, image=uploaded, available=True
        )

    def test_status_code(self):
        response = self.client.get(
            reverse('shop:category_list', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        response = self.client.get(
            reverse('shop:category_list', args=[self.category.slug]))
        self.assertTemplateUsed(response, 'shop/category_list.html')

    def test_context_data(self):
        response = self.client.get(
            reverse('shop:category_list', args=[self.category.slug]))
        self.assertEqual(response.context['category'], self.category)
        self.assertEqual(response.context['products'].first(), self.product)

