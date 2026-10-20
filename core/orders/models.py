from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
# Create your models here.

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending'
        PAID = 'paid'
        PROCESSING = 'processing'
        SHIPPED = 'shipped'
        DELIVERED = 'delivered'
        CANCELED = 'canceled'
        REFUNDED = 'refunded'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='orders'
        )
    receiver_name = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=11)
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    full_address = models.TextField()

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
        )

    total_price = models.DecimalField(
        max_digits=12, decimal_places=0,
        validators=[MinValueValidator(0)]
        )
    
    shipping_cost = models.DecimalField(
        max_digits=12, decimal_places=0, default=0
    )
    discount = models.DecimalField(
        max_digits=12, decimal_places=0, default=0
        )
    note = models.TextField('user notes',blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['user', 'status'])
        ]
    
    def __str__(self):
        return f'#{self.pk} - {self.user}'
    
    @property
    def payable_amount(self):
        return self.total_price + self.shipping_cost - self.discount
    
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items'
        )
    variant = models.ForeignKey(
        'catalog.ProductVariant',on_delete=models.PROTECT,
        related_name='order_items'
        )
    product_name = models.CharField('product name at the order',max_length=200)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=0)

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'

    def get_cost(self):
        return self.unit_price * self.quantity