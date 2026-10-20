from django.db import models
from django.core.validators import MinValueValidator
# Create your models here.

class Payment(models.Model):
    class GateWay(models.TextChoices):
        ZARINPALL = 'zarinpal'
        IDPAY = 'idpay'
        MELLAT = 'mellat'
        SAMAN = 'saman'

    class Status(models.TextChoices):
        PENDING = 'pending'
        SUCCESS = 'success'
        FAILED = 'failed'
        CANCELED = 'canceled'
    
    order = models.ForeignKey(
        'orders.Order', on_delete=models.PROTECT, related_name='payments'
        )
    gateway = models.CharField(max_length=20, choices=GateWay.choices)
    amount = models.DecimalField(
        max_digits=12, decimal_places=0, validators=[MinValueValidator(0)]
        )
    authority = models.CharField(max_length=100, blank=True, db_index=True)
    transaction_id = models.CharField(
        max_length=100, blank=True, db_index=True
        )
    reference_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
        )
    gateway_response = models.JSONField(default=dict, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    paid_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_date']
        indexes = [
            models.Index(fields=['authority']),
            models.Index(fields=['status'])
        ]

    def __str__(self):
        return f'#{self.pk} - {self.get_status_display()}'