from datetime import datetime

from django.db import models

from Account.models import User
from django.core.validators import MinValueValidator

class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PROCESSING = 'PROCESSING', 'Processing'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'

# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField( default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        abstract = True

class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='orders')
    order_status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    order_name = models.CharField(max_length=255)
    address = models.TextField()
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    province = models.IntegerField(validators=[MinValueValidator(1)])
    ward = models.IntegerField(validators=[MinValueValidator(1)])
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total_quantity = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']
        db_table = 'order'

    @property
    def full_address(self):
        return f"{self.address}, {self.ward}, {self.province}"

class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book_title = models.CharField(max_length=255)
    book_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ['order', 'book_title']
        db_table = 'order_item'

    @property
    def book_details(self):
        return f"{self.book_title} by {self.book_author}"
    def save(self, *args, **kwargs):
        self.total_price = self.book_price * self.quantity
        super().save(*args, **kwargs)

class OrderHistory(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    note = models.TextField()

    class Meta:
        verbose_name = "Order History"
        verbose_name_plural = "Order Histories"
        ordering = ['-created_at']
        db_table = 'order_history'

    @property
    def short_note(self):
        return self.note[:50] + '...' if len(self.note) > 50 else self.note