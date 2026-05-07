from django.db import models
from Account.models import User
from Book.models import Book

# ============ Cart Model ============
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"
    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())
    @property
    def total_price(self):
        return sum(item.book.price * item.quantity for item in self.items.all())
    
# ============ CartItem Model ============    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'book')

