from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.cache import cache
from catalog.models import Category, Brand, Product

User = get_user_model()

class CatalogAPITests(APITestCase):
    def setUp(self):
        cache.clear()

        self.user = User.objects.create_user(
            email='catalog_test@example.com',
            password='password123'
        )

        self.category = Category.objects.create(name='Electronic', slug='electronics')
        self.brand = Brand.objects.create(name='Sony', slug='sony')

        self.prodcut = Product.objects.create(
            name='Headphone',
            slug='headphone',
            category=self.category,
            brand=self.brand,
            base_price=5000000,
            is_active=True
        )
    # --- Tests whitout login ---
    def test_public_can_view_products(self):
        """Everybody should can see products"""
        response = self.client.get('/api/catalog/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_public_filter_by_category(self):
        response = self.client.get('/api/catalog/products/?category_slug=electronic')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Tests which needs login
    def test_guest_cannot_create_product(self):
        """guest should'nt create product (return 401)"""
        data = {
            'name': 'New Product',
            'slug': 'new-product',
            'category': self.category.id,
            'base_price': 100000,
        }
        response = self.client.post('/api/catalog/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logged_in_user_can_create_product(self):
        self.client.force_authenticate(user=self.user)

        data = {
            'name': 'Smart Tv',
            'slug': 'smart-tv',
            'category': self.category.id,
            'base_price': 15000000,
            'is_active': True
        }
        response = self.client.post('/api/catalog/products/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(slug='smart-tv').exists())

