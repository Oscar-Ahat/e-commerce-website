from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from catalog.models import Category, Product, ProductVariant
from cart.models import Cart, CartItem

User = get_user_model()

class CartAPITests(APITestCase):
    def setUp(self):
        cache.clear()

        #Create user
        self.user = User.objects.create_user(
            email='cart_user@example.com',
            password='password123'
        )

        #Create Product and Variant for test
        self.category = Category.objects.create(name='Test Cat', slug='test-cat')
        self.product = Product.objects.create(
            name='Test Product', slug='test-prodcut',
            category=self.category, base_price=100000
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku='TEST-SKU-1',
            price=100000,
            stock=10,
            is_active=True
        )

    def test_guest_cannot_access_cart(self):
        """(401) guest user should'nt access to cart"""
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_item_to_cart(self):
        """login user can add product to cart"""
        self.client.force_authenticate(user=self.user)

        data = {'variant_id': self.variant.id, 'quantity': 2}
        response = self.client.post('/api/cart/items/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        #Is product added
        cart_item = CartItem.objects.get(cart__user=self.user, variant=self.variant)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.get_cost(), 200000) # 100000 * 2

    def test_add_more_than_stock_fails(self):
        """adding product more than of inventory (400)"""
        self.client.force_authenticate(user=self.user)

        data = {'variant_id':self.variant.id, 'quantity': 15}
        response = self.client.post('/api/cart/items/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_cart_item_quantity(self):
        """changing quantity of item in cart"""
        self.client.force_authenticate(user=self.user)

        #Adding one item
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(cart=cart, variant=self.variant, quantity=1, price_at_add=self.variant.price)

        # Change to 3 quantity
        data = {'quantity': 3}
        response = self.client.patch(f'/api/cart/items/{item.id}/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)