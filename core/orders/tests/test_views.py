from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from catalog.models import Category, Product, ProductVariant
from cart.models import Cart, CartItem
from orders.models import Order

User = get_user_model()

class OrderCheckoutTests(APITestCase):
    def setUp(self):
        cache.clear()

        self.user = User.objects.create_user(
            email='order_user@example.com',
            password='password123'
        )

        self.category = Category.objects.create(name='Test Cat', slug='test-cat')
        self.product = Product.objects.create(
            name='Test Product', slug='test-product',
            category=self.category, base_price=100000
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku='TEST-ORDER-SKU',
            price=100000,
            stock=5,
            is_active=True
        )

        self.checkout_data = {
            'receiver_name': 'jhon doe',
            'province': 'Tehran',
            'city': 'Tehran',
            'postal_code': '1234567890',
            'full_address': 'valiasr st, no10',
            'shipping_cost': 50000
        }

    def test_guest_cannot_checkout(self):
        """guest user should'nt checkout"""
        response = self.client.post('/api/orders/checkout/', self.checkout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_checkout_with_empty_cart_fails(self):
        """should return 400"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/orders/checkout/', self.checkout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_checkout(self):
        """successful checkout: create order, empty cart and decrease inventory"""
        self.client.force_authenticate(user=self.user)

        # Add product to cart
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart, variant=self.variant, quantity=2, price_at_add=self.variant.price
        )
        # Checkout Request
        response = self.client.post('/api/orders/checkout/', self.checkout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check result. is order created
        self.assertTrue(Order.objects.filter(user=self.user).exists())
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.total_price + order.shipping_cost, 250000)

        # Is Cart get empty
        self.assertEqual(cart.items.count(), 0)
        # Inventry changed?
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 3)

    def test_checkout_insufficient_stock_fails(self):
        """Checkout should give an error and stop when there is insufficient balance"""
        self.client.force_authenticate(user=self.user)

        # A cart with 10 items, while the stock is 5.
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart, variant=self.variant, quantity=10, price_at_add=self.variant.price
        )

        # Checkout request
        response = self.client.post('/api/orders/checkout/', self.checkout_data, format='json')
        
        # Checking error and stock not changed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 5) # must be unchanged
