from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
# Create your models here.

class Cart(models.Model):
    """cart for users or guests"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
          related_name='cart', null=True, blank=True
    )
    session_key = models.CharField(max_length=40, null=40, blank=True, db_index=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'cart {self.user or self.session_key}'

    @property
    def total_price(self):
        return sum(item.get_cost() for item in self.items.all())

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items'
        )
    variant = models.ForeignKey(
        'catalog.ProductVariant', on_delete=models.CASCADE,
        related_name='cart_items'
        )
    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)]
        )
    price_at_add = models.DecimalField(max_digits=12, decimal_places=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('cart', 'variant')]

    def __str__ (self):
        return f'{self.variant} x {self.quantity}'

    def get_cost(self):
        return self.price_at_add * self.quantity